########################################################################################################################
# IMPORTS

import logging
from ftplib import FTP, FTP_TLS
from pathlib import Path

from dynaconf import Dynaconf

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)

class FTPInterface:
    def __init__(self, config: Dynaconf):
        if "ftp" in config:
            self.config = config["ftp"]

            self.ftp = self.get_ftp()
        else:
            logger.warning("no ftp section in config")

    def get_ftp(self):
        if self.config["ftps"]:
            ftp_conn = FTP_TLS(self.config["server"])

        else:
            ftp_conn = FTP(self.config["server"])

        ftp_conn.login(self.config["username"], self.config["password"])

        return ftp_conn

    def upload_file(self, local_file, remote_folder, remote_file=None):
        if not remote_file:
            remote_file = Path(local_file).name

        self._create_remote_dir_tree(full_path=f"{remote_folder}{remote_file}")

        self.ftp.cwd(remote_folder)

        with open(local_file, "rb") as f:
            self.ftp.storbinary(f"STOR {remote_file}", f)

    def download_file(self, local_file, remote_file):
        with open(local_file, "wb") as f:
            self.ftp.retrbinary(f"RETR {remote_file}", f.write)

    def _create_remote_dir_tree(self, full_path):
        dir_tree = full_path.split("/")[0:-1]  # Exclude filename

        for part in dir_tree:
            if not part:
                continue

            try:
                self.ftp.cwd(part)
            except Exception as e:
                logger.warning(f"Error while creating remote directory: {e}")
                self.ftp.mkd(part)
                self.ftp.cwd(part)
