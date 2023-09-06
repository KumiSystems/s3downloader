from configparser import ConfigParser

import logging

class Config:
    def __init__(self, config_file=[], section="S3"):
        logging.debug(f"Reading configuration file(s): {config_file}")

        self.config = ConfigParser()
        self.config.read(config_file)

        self.section = section

    @property
    def access_key(self):
        return self.config[self.section]["access_key"]

    @property
    def secret_key(self):
        return self.config[self.section]["secret_key"]

    @property
    def bucket_name(self):
        return self.config[self.section]["bucket_name"]

    @property
    def path(self):
        return self.config[self.section].get("path", "")

    @property
    def final_dir(self):
        return self.config[self.section]["final_dir"]

    @property
    def delete(self):
        return self.config[self.section].getboolean("delete")

    @property
    def kwargs(self):
        kwargs = {}
        for key, value in self.config[self.section].items():
            if not key in [
                "access_key",
                "secret_key",
                "bucket_name",
                "path",
                "final_dir",
                "delete",
            ]:
                kwargs[key] = value
        return kwargs
