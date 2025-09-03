########################################################################################################################
# IMPORTS

import io
import logging
import boto3
from typing import Optional, List, Dict, Any

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)


class AWSInterface:
    def __init__(self, config) -> None:
        self.profiles: List[Dict[str, Any]] = []
        self.config = config

        for section in getattr(self.config, "sections", lambda: [])():
            if section.startswith("aws:"):
                profile_name = section.split(":", 1)[1]
                bucket_value = self.config[section].get("buckets", "")
                buckets = [b.strip() for b in bucket_value.split(",") if b.strip()]
                session = boto3.Session(profile_name=profile_name)

                self.profiles.append(
                    {
                        "profile": profile_name,
                        "buckets": buckets,
                        "session": session,
                    }
                )

        if not self.profiles:
            logger.warning("No AWS profiles found in config file")

        self.current_profile: Optional[Dict[str, Any]] = self.profiles[0] if self.profiles else None
        self._update_resources()

    def _update_resources(self) -> None:
        """Refresh S3 resources for the current profile and set default bucket (first in list)"""
        if self.current_profile:
            self.s3 = self.current_profile["session"].resource("s3")
            self.s3_client = self.s3.meta.client
            buckets = self.current_profile.get("buckets", [])
            self.bucket = buckets[0] if buckets else None
        else:
            self.s3 = None
            self.s3_client = None
            self.bucket = None

    def switch_profile(self, profile_name: str) -> None:
        for profile in self.profiles:
            if profile["profile"] == profile_name:
                self.current_profile = profile
                self._update_resources()
                return
        logger.warning(f"Profile {profile_name} not found")

    def switch_bucket(self, bucket: str) -> None:
        if not self.current_profile:
            logger.warning("No current AWS profile to switch bucket on")
            return

        buckets = self.current_profile.get("buckets") or []
        if bucket not in buckets:
            logger.warning(f"Bucket {bucket} not found in profile {self.current_profile.get('profile')}")
            return

        self.bucket = bucket

    def switch_bucket_for_profile(self, profile_name: str, bucket: str) -> None:
        """
        Select a profile and then switch its active bucket.
        """
        for profile in self.profiles:
            if profile["profile"] == profile_name:
                self.current_profile = profile
                self._update_resources()  # sets default bucket & s3 clients
                self.switch_bucket(bucket)  # only sets self.bucket if valid
                return
        logger.warning(f"Profile {profile_name} not found")

    def get_file(self, s3_path: str):
        if not self.bucket:
            logger.warning("No active bucket selected")
            return None
        try:
            return self.s3.Object(self.bucket, s3_path).get()
        except self.s3_client.exceptions.NoSuchKey:
            logger.info(f"{s3_path} does not exist")
            return None

    def read_file_as_bytes(self, s3_path: str) -> Optional[io.BytesIO]:
        obj = self.get_file(s3_path)
        if not obj:
            return None
        return io.BytesIO(obj["Body"].read())

    def upload_file(self, local_path: str, s3_path: str) -> None:
        if not self.bucket:
            logger.warning("No active bucket selected")
            return
        self.s3.Bucket(self.bucket).upload_file(local_path, s3_path)
