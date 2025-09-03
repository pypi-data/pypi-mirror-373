########################################################################################################################
# IMPORTS

import io
import logging
import boto3
from dynaconf import Dynaconf

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class AWSInterface:
    def __init__(self, config: Dynaconf) -> None:
        self.profiles = []
        self.config = config

        for profile_name, values in self.config.get("aws", {}).items():
            self.profiles.append(
                {
                    "profile": profile_name,
                    "buckets": values["buckets"],
                    "session": boto3.Session(profile_name=profile_name),
                }
            )

        if not self.profiles:
            logger.warning("No AWS profiles found in config file")

        self.current_profile = self.profiles[0] if self.profiles else None
        self._update_resources()

    def _update_resources(self) -> None:
        if self.current_profile:
            self.s3 = self.current_profile["session"].resource("s3")
            self.s3_client = self.s3.meta.client
            self.bucket = self.current_profile["buckets"][0]

    def switch_profile(self, profile_name: str) -> None:
        for profile in self.profiles:
            if profile["profile"] == profile_name:
                self.current_profile = profile
                self._update_resources()
                return
        logger.warning(f"Profile {profile_name} not found")

    def switch_bucket(self, bucket: str) -> None:
        if bucket not in self.current_profile["buckets"]:
            logger.warning(
                f"Bucket {bucket} not found in profile {self.current_profile['profile']}"
            )
            return

        self.bucket = bucket

    def get_file(self, s3_path: str) -> None:
        try:
            return self.s3.Object(self.bucket, s3_path).get()
        except self.s3_client.exceptions.NoSuchKey:
            logger.info(f"{s3_path} does not exist")

    def read_file_as_bytes(self, s3_path: str) -> io.BytesIO:
        return io.BytesIO(self.get_file(s3_path)["Body"].read())

    def upload_file(self, local_path: str, s3_path: str) -> None:
        self.s3.Bucket(self.bucket).upload_file(local_path, s3_path)
