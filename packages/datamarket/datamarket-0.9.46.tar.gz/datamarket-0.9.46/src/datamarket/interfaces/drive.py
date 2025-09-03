########################################################################################################################
# IMPORTS

import logging

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

########################################################################################################################
# CLASSES

logger = logging.getLogger(__name__)
logging.getLogger("googleapicliet.discovery_cache").setLevel(logging.ERROR)


class DriveInterface:
    def __init__(self, config):
        if "drive" in config:
            self.config = config["drive"]

            GoogleAuth.DEFAULT_SETTINGS[
                "client_config_file"
            ] = f'{self.config["config_path"]}/credentials.json'

            self.gauth = GoogleAuth(
                settings_file=f'{self.config["config_path"]}/settings.yaml'
            )
            self.gauth.LocalWebserverAuth()

            self.drive = GoogleDrive(self.gauth)

            self.team_id = self.config["team_id"]

        else:
            logger.warning("no drive section in config")

    def delete_old_files(self, filename, folder_id):
        for drive_file in self.drive.ListFile(
            {
                "q": f"'{folder_id}' in parents and trashed=false",
                "corpora": "teamDrive",
                "teamDriveId": self.team_id,
                "includeTeamDriveItems": True,
                "supportsTeamDrives": True,
            }
        ).GetList():
            if drive_file["title"] == filename:
                logger.info(f"deleting old {filename}...")
                drive_file.Delete(param={"supportsTeamDrives": True})

    def upload_file(self, local_filename, drive_filename, folder_id):
        self.delete_old_files(drive_filename, folder_id)

        f = self.drive.CreateFile(
            {
                "title": drive_filename,
                "parents": [
                    {
                        "kind": "drive#fileLink",
                        "teamDriveId": self.team_id,
                        "id": folder_id,
                    }
                ],
            }
        )
        f.SetContentFile(local_filename)

        logger.info(f"uploading {drive_filename} to folder: {folder_id}...")
        f.Upload(param={"supportsTeamDrives": True})

    def validate_file(self, filename, folder_id):
        for drive_file in self.drive.ListFile(
            {
                "q": f"'{folder_id}' in parents and trashed=false",
                "corpora": "teamDrive",
                "teamDriveId": self.team_id,
                "includeTeamDriveItems": True,
                "supportsTeamDrives": True,
            }
        ).GetList():
            if drive_file["title"] == filename:
                logger.info(f"{filename} correctly uploaded.")
                return

        raise FileNotFoundError(f"{filename} has not been correctly uploaded.")
