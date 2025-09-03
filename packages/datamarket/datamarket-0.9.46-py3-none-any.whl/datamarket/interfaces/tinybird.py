########################################################################################################################
# IMPORTS

import datetime
import json
import logging

import requests
from requests.exceptions import ConnectionError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class TinybirdInterface:
    def __init__(self, config):
        if "tinybird" in config:
            self.config = config["tinybird"]

            self.post_url = "https://api.tinybird.co/v0/events"

            self.request_params = {
                "name": self.config["name"],
                "token": self.config["token"],
            }

        else:
            logger.warning("no tinybird section in config")

    @staticmethod
    def __converter(obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

    @staticmethod
    def __dict_lists_to_string(obj):
        return {
            key: json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else value
            for key, value in obj.items()
        }

    def __prepare_json_row(self, obj_dict):
        return json.dumps(
            self.__dict_lists_to_string(obj_dict), default=self.__converter
        )

    @staticmethod
    def __handle_api_response(json_response):
        successful_rows = json_response["successful_rows"]
        quarantined_rows = json_response["quarantined_rows"]

        if quarantined_rows > 0:
            logger.error(
                f"wrong insertion of {quarantined_rows} records to Tinybird API..."
            )
        else:
            logger.info(
                f"successfully inserted {successful_rows} records to Tinybird API!"
            )

        return successful_rows, quarantined_rows

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(ConnectionError))
    def __insert_data_to_endpoint(self, data):
        r = requests.post(self.post_url, params=self.request_params, data=data, timeout=30)
        return self.__handle_api_response(r.json())

    def insert_record_to_api(self, obj_dict):
        return self.__insert_data_to_endpoint(self.__prepare_json_row(obj_dict))

    def insert_batch_to_api(self, batch):
        return self.__insert_data_to_endpoint(
            "\n".join([self.__prepare_json_row(x) for x in batch])
        )

    def insert_pandas_df_to_api(self, df):
        return self.__insert_data_to_endpoint(df.to_json(orient="records", lines=True))
