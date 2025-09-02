import psycopg2

from maisaedu_utilities_prefect.dw import get_red_credentials
from maisaedu_utilities_prefect.constants.redshift import get_iam_role

class Connector:
    def __init__(self, env):
        self.env = env
        self.iam_role = get_iam_role(env)
        self.redshift = None

        self.has_connected = False

    def connect(self):
        red_credentials = get_red_credentials(self.env)
        self.redshift = psycopg2.connect(
            host=red_credentials["host"],
            database=red_credentials["database"],
            user=red_credentials["user"],
            password=red_credentials["password"],
            port=red_credentials["port"],
        )

        self.has_connected = True

    def close(self):
        if not self.has_connected:
            return
        
        self.redshift.close()
