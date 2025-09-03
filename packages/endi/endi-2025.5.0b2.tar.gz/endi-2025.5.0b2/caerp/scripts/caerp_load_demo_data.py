import argparse
import os
import sys
import subprocess
import logging

from caerp.scripts.utils import argparse_command
from caerp_base.models.base import DBSESSION


""" Fetch and load into DB the latest published anonymized demo data

OVERWRITE THE WHOLE CAERP DATABASE.

It requires the following CLI tools :

- bunzip2
- curl
- shasum
- mysql

Those tools are builtin or easy to install in OSX (w/ XCode) as well as
in GNU/Linux distros.
"""
logger = logging.getLogger(__name__)


class DumpFetcher:
    """
    Ensure existence and validity of reference dump (and fix it if needed).
    """

    # Hardcoded values, to be consistent accross dev envs
    DUMP_FILENAME = "caerp-anonymous-2025.4.sql"
    COMPRESSED_DUMP_FILENAME = DUMP_FILENAME + ".bz2"
    COMPRESSED_DUMP_URL = "https://upload.majerti.fr/" + COMPRESSED_DUMP_FILENAME
    # SHA256 sum of the *uncompressed* dump (.sql)
    DUMP_SHA256SUM = "028a17145a7729b499e57b4e7db8919886ef09e2e2ce2b787bcca346ed1bf055"

    @classmethod
    def checksum_ok(cls):
        if sys.platform.lower() == "darwin":
            command = ["shasum", "-a", "256", cls.DUMP_FILENAME]
        else:
            command = ["sha256sum", cls.DUMP_FILENAME]
        sha256_output = subprocess.check_output(command).decode("utf-8")
        sha256sum = sha256_output.split(" ")[0].strip()
        return sha256sum == cls.DUMP_SHA256SUM

    @classmethod
    def needs_download(cls):
        return not os.path.exists(cls.DUMP_FILENAME) or not cls.checksum_ok()

    @classmethod
    def fetch_reference_dump(cls, insecure_fetch=False):
        if cls.needs_download():
            logger.info(
                "{} not present or outdated,".format(cls.DUMP_FILENAME)
                + " fetching from {} (compressed).".format(
                    cls.COMPRESSED_DUMP_URL,
                )
            )
            curl_call = [
                "curl",
                cls.COMPRESSED_DUMP_URL,
                "-o",
                cls.COMPRESSED_DUMP_FILENAME,
            ]
            if insecure_fetch:
                logger.warning(
                    f"Insecure fetch : SSL cert of {cls.COMPRESSED_DUMP_URL} will not be validated."
                )
                curl_call.append("--insecure")

            subprocess.check_call(curl_call)
            subprocess.check_call(
                ["bunzip2", "-f", cls.COMPRESSED_DUMP_FILENAME],
            )
            if not cls.checksum_ok():
                raise Exception(
                    "Bad checksum on freshly downloaded {}".format(
                        cls.DUMP_FILENAME,
                    )
                )
        else:
            logger.info(
                "Dump {} already present, checksum OK.".format(
                    cls.DUMP_FILENAME,
                )
            )
        return cls.DUMP_FILENAME


def load_dump(dump_path):
    db = DBSESSION()
    db_params = db.connection().engine.url

    if db_params.drivername not in ("mysql", "mariadbconnector"):
        raise Exception("Only MySQL is supported (not {})".format(db_params.drivername))

    # Start fresh !
    logging.info("+ Dropping previous database")
    db.execute("DROP DATABASE IF EXISTS {}".format(db_params.database))
    logging.info("+ Creating an empty database")
    db.execute("CREATE DATABASE {}".format(db_params.database))
    db.execute("USE {}".format(db_params.database))

    logging.info("+ Loading the SQL dump")
    # Loading the dump from python uses too much resource and crashes
    subprocess.check_call(
        "mysql -u{} -p{} -h{} -P{} {} < {}".format(
            db_params.username,
            db_params.password,
            db_params.host,
            db_params.port or 3306,
            db_params.database,
            dump_path,
        ),
        shell=True,
    )


def load_demo_data_entry_point():
    """Download (if required) and load reference dump into database.
    Usage:
        caerp-load-demo-data <config_uri>

    Requires those tools installed : bunzip2, wget, sha256sum, mysql.
    Writes downloaded files in current dir
    """

    parser = argparse.ArgumentParser(description=load_demo_data_entry_point.__doc__)
    parser.add_argument("config_uri")
    parser.add_argument(
        "--insecure-fetch",
        help=(
            "Disable SSL validation. "
            "May be useful on a old OS with deprecated certificate store "
            "(symptom : curl returning error 60). "
            "File checksum will still be checked."
        ),
        default=False,
        action="store_true",
    )

    def callback(arguments, env):
        dump_path = DumpFetcher.fetch_reference_dump(
            insecure_fetch=arguments.insecure_fetch
        )
        logger.info("Loading {} into DB :".format(dump_path))
        load_dump(dump_path)
        logger.info("OK : Demo data dump {} loaded !".format(dump_path))

    try:
        return argparse_command(callback, parser)
    finally:
        pass
