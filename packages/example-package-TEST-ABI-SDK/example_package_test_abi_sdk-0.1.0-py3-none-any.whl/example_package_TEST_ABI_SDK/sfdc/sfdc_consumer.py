"""
SFDC consumer required to communicate with SFDC API.
"""

import json
from copy import deepcopy
from time import sleep
from typing import Union, List, Dict, Tuple

import requests
from logbook import Logger, lookup_level
from requests import Response

from example_package_TEST_ABI_SDK.config import constants as const
from example_package_TEST_ABI_SDK.exceptions.base_exceptions import (
    InvalidCredentialsException,
    SFDCBadRequestException,
    WrongJobTypeException,
)


def print_from_sfdc_connector():
    print("hello from sfdc_connector")


class SFDCConsumer:
    """
    SFDC Consumer provides interface to query and update records via SFDC Rest API.
    """

    def __init__(
            self,
            username: str,
            password: str,
            client_id: str,
            client_secret: str,
            sfdc_test: bool = False,
            log_level: str = 'DEBUG'
    ) -> None:
        self.logger = Logger(self.__class__.__name__, level=lookup_level(log_level))
        self.sfdc_username = username
        self.sfdc_password = password
        self.sfdc_client_id = client_id
        self.sfdc_client_secret = client_secret
        self.sfdc_test = sfdc_test
        self.access_token = None
        self.instance_url = None
        self._get_sf_token_and_url()

        self.headers = {
            'Content-type': 'application/json',
            'Accept-Encoding': 'gzip',
            'Authorization': f'Bearer {self.access_token}'
        }

        self.logger.info(f"SFDC consumer initialized. SFDC sandbox is {bool(self.sfdc_test)}")

    def _get_sf_token_and_url(self) -> None:
        url = f"https://{'test' if self.sfdc_test else 'login'}.salesforce.com/services/oauth2/token"
        params = {
            "grant_type": "password",
            "client_id": self.sfdc_client_id,
            "client_secret": self.sfdc_client_secret,
            "username": self.sfdc_username,
            "password": self.sfdc_password
        }

        token_response = requests.post(url=url, params=params, timeout=const.REQUEST_TIMEOUT)

        if token_response.status_code != const.HTTP_RESPONSE_STATUS_OK:
            self.logger.error(token_response.json())
            raise InvalidCredentialsException("SFDC token is not retrieved. Check credentials.")

        json_data = token_response.json()
        self.access_token = json_data.get("access_token")
        self.instance_url = json_data.get("instance_url")

        self.logger.debug("SFDC Bearer token acquired successfully")

    def call(self, url: str, method: str, params: dict = None,
             data: Union[dict, str] = None, json_: dict = None, headers: dict = None) -> Response:

        attempt = 0
        while attempt < 3:
            try:
                attempt += 1
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers if headers else self.headers,
                    data=data,
                    params=params,
                    json=json_,
                    timeout=const.REQUEST_TIMEOUT
                )

                self.logger.debug(f"Sending {method} request to: {url}")

                if response.status_code < const.HTTP_RESPONSE_STATUS_ALL_OK_LAST:
                    if response.status_code != const.HTTP_RESPONSE_STATUS_NO_DATA:
                        return response
                    return None

                if response.status_code == const.HTTP_RESPONSE_STATUS_UNAUTHORIZED:
                    self.logger.error("Token invalid or expired. Retrying auth.")
                    self._get_sf_token_and_url()
                    continue

                if response.status_code == const.HTTP_RESPONSE_STATUS_BAD_REQUEST:
                    self.logger.error(f"Bad request: {response.json()}")
                    raise SFDCBadRequestException("SFDC responded with Bad Request")

            except requests.exceptions.Timeout:
                self.logger.warning("Request timeout. Retrying...")
                sleep(1)

        raise TimeoutError("SFDC request failed after 3 attempts.")

    def query(self, method: str, params: dict = None, data: dict = None) -> Dict:
        url = self.instance_url + const.SFDC_QUERY_PATH
        return self.call(url, method, params, data).json()

    def composite_batch(self, queries: List[str]) -> Dict:
        url = self.instance_url + const.SFDC_COMPOSITE_BATCH
        data = json.dumps({
            "batchRequests": [
                {"method": "get", "url": f"v57.0/query?q={self.convert_sql_to_soql(query)}"}
                for query in queries
            ]
        })
        return self.call(url, const.HTTP_POST, data=data).json()

    @staticmethod
    def convert_sql_to_soql(query: str) -> str:
        return "+".join(query.split())

    def apply_bulk_job_query(self, query: str) -> str:
        data = {
            "operation": "query",
            "query": query
        }
        response = self.call(
            url=self.instance_url + const.SFDC_BULK_QUERY_URL,
            method=const.HTTP_POST,
            json_=data
        )
        return response.json()['id']

    def get_bulk_job_results(self, job_id: str, locator: str = None) -> Tuple[str, str]:
        job_completed = locator is not None

        while not job_completed:
            job_completed = self.check_job_completed(job_id, const.JOB_TYPE_QUERY)
            if not job_completed:
                sleep(60)

        url = f"{self.instance_url}{const.SFDC_BULK_QUERY_URL}{job_id}/results"
        params = {"maxRecords": const.BULK_JOB_RECORDS_NUMBER}
        if locator:
            self.logger.debug(f"Requesting records with locator: {locator}")
            params["locator"] = locator

        while True:
            response = self.call(url, const.HTTP_GET, params=params)
            if response and response.status_code == 200:
                sf_locator = response.headers.get('Sforce-Locator')
                return response.text, (sf_locator if sf_locator != 'null' else None)
            sleep(60)

    def initiate_sfdc_job(self, options: dict) -> str:
        url = f"{self.instance_url}{const.SFDC_BULK_JOB_URL}"
        response = self.call(url, const.HTTP_POST, json_=options)
        return response.json()['id']

    def upload_sfdc_job_data(self, job_id: str, csv_data: str) -> int:
        url = f"{self.instance_url}{const.SFDC_BULK_JOB_URL}{job_id}/batches/"
        headers = deepcopy(self.headers)
        headers["Content-Type"] = "text/csv"
        response = self.call(url, const.HTTP_PUT, data=csv_data, headers=headers)
        return response.status_code

    def update_bulk_job_after_load(self, job_id: str) -> Response:
        url = f"{self.instance_url}{const.SFDC_BULK_JOB_URL}{job_id}/"
        return self.call(url, const.HTTP_PATCH, json_={"state": "UploadComplete"})

    def check_job_completed(self, job_id: str, job_type: str) -> bool:
        self.logger.debug(f"Checking Job {job_id} status.")

        if job_type == const.JOB_TYPE_QUERY:
            url = f"{self.instance_url}{const.SFDC_BULK_QUERY_URL}{job_id}"
        elif job_type == const.JOB_TYPE_INGEST:
            url = f"{self.instance_url}{const.SFDC_BULK_JOB_URL}{job_id}"
        else:
            raise WrongJobTypeException()

        response = self.call(url, const.HTTP_GET)
        state = response.json()['state']
        self.logger.debug(f"Job status: {state}")
        return state == "JobComplete"

    def get_job_results(self, job_id: str) -> str:
        url = f"{self.instance_url}{const.SFDC_BULK_JOB_URL}{job_id}/failedResults"
        response = self.call(url, const.HTTP_GET)
        return response.text
