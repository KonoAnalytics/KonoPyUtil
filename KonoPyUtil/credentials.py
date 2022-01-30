import os
import json
from environs import Env


def set_credentials(file_and_path_to_credential_file=".env", recurse=False):
    """
    Loads credential file into O/S environment if a file_and_path_to_credential_file is not None
    overwrites DB_CREDENTIALS O/S environment variable
    returns DB_CREDENTIALS as a dictionary

    credential_file should be formatted as follows:
    DB_CREDENTIALS='{"DBNAME": "postgres", "SCHEMA": "public", "USERID": "useridhere", "PASSWORD": "passwordhere", "HOST": "path_to_database_here", "PORT": "port_here"}'

    :param file_and_path_to_dot_env: defaults to .env, uf yi
    :param recurse: Boolean = if True recursively search upward for a .env file
    :return: dictionary of database credentials if present, or empty dictionary otherwise
    """
    if file_and_path_to_credential_file:
        # clear existing "DB_CREDENTIALS" environment variable
        try:
            del os.environ["DB_CREDENTIALS"]
        except KeyError:
            pass
        finally:
            env = Env()
            file_and_path_formatted = os.path.abspath(file_and_path_to_credential_file)
            env.read_env(file_and_path_formatted, recurse=recurse)
    if "DB_CREDENTIALS" in os.environ:
        return dict(json.loads(os.environ["DB_CREDENTIALS"]))
    else:
        return {}
