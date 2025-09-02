import warnings
from pathlib import Path


class PackageEnvInfo:
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    project_root_dir = Path(__file__).parent
    TestEnv = ''
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d %(message)s",
                # "format": "%(asctime)s %(levelname)s %(message)s",
                "class": "pythonjsonlogger.json.JsonFormatter"
            },
            "standard": {
                "format": "%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d %(message)s"
            }
        },
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "level": "WARNING",
                "formatter": "standard"
            },
            # "file": {
            #     "class": "logging.FileHandler",
            #     "filename": "report/request_logs.log",
            #     "formatter": "json"
            # },
            # "timed_file": {
            #     "class": "logging.handlers.TimedRotatingFileHandler",
            #     "filename": "report/timed_request_logs.log",
            #     "formatter": "json",
            #     "when": "D",
            #     "backupCount": 5
            # },
            "sized_file": {
                "class": "concurrent_log_handler.ConcurrentRotatingFileHandler",
                "filename": "report/logs/sized_request_logs.log",
                "formatter": "json",
                "maxBytes": 1000000,
                "backupCount": 5
            }
        },
        "loggers": {"": {"handlers": ["stdout", "sized_file"], "level": "DEBUG", "propagate": False}}
    }
    SIT = {
        "backoffice": {
            "endpoint": "https://ovs-lx-vlo-01-backoffice.gcubut.gcp.uwccb/",
            "username": "super_tester",
            "password": "super_tester",
            "authorization": "un-auth"
        },
        "app": {
            "endpoint": "https://ovs-lx-vlo-01-app.gcubut.gcp.uwccb/",
            "client_secret": "TH4iHu6JFxYOlzNp1WuhNnKN7xGXoB65",
            "authorization": "un-auth"
        },
        "telco": {
            "endpoint": "https://ovs-lx-vcp-01-telcoapi.gcubut.gcp.uwccb/"
        },
        "dataapi": {
            "endpoint": "https://ovs-lx-vcp-01-dataapi.gcubut.gcp.uwccb/"
        },
        "msg-center": {
            "endpoint": "https://ovs-lx-vcp-01-msg-center.gcubut.gcp.uwccb/"
        },
        "data-centralized": {
            "endpoint": "https://ovs-lx-vcp-01-data-centralized.gcubut.gcp.uwccb/"
        },
        "customer-service": {
            "endpoint": "https://ovs-lx-vcp-01-customer-service.gcubut.gcp.uwccb/",
            "username": "super_tester",
            "password": "super_tester",
            "client_secret": "YcHMT1fPADHE4Bf3rOimkkrxVVrhMpl8",
            "authorization": "un-auth"
        },
        "middle-bo-cl": {
            "endpoint": "https://ovs-lx-vcp-01-middle-bo-cl.gcubut.gcp.uwccb/",
            "username": "super_tester2",
            "password": "super_tester2",
            "client_secret": "YcHMT1fPADHE4Bf3rOimkkrxVVrhMpl8",
            "authorization": "un-auth"  # share with cs due to middle-bo
        },
        "middle-bo-bff": {
            "endpoint": "https://dirhvcpbo01.cathdevelop.intra.uwccb:8443/middle-bo-bff/",
            "username": "super_tester2",
            "password": "super_tester2",
            "client_secret": "YcHMT1fPADHE4Bf3rOimkkrxVVrhMpl8",
            "authorization": "un-auth"  # share with cs due to middle-bo
        },
        "db_connection": {
            "ssl": {
                "sslmode": "verify-ca",
                "sslrootcert": Path(project_root_dir, "DataFiles/db_ssl/vcp/server-ca.pem"),
                "sslcert": Path(project_root_dir, "DataFiles/db_ssl/vcp/client-cert.pem"),
                "sslkey": Path(project_root_dir, "DataFiles/db_ssl/vcp/client-key.pem")
            },
            "vlo": {
                "user": "ovslxvlo01_00596338",
                "password": "rA@9wG@V2@885",
                "host": "10.171.129.233",
                "port": "5432",
                "sslmode": "verify-ca",
                "sslrootcert": Path(project_root_dir, "DataFiles/db_ssl/vlo/server-ca.pem"),
                "sslcert": Path(project_root_dir, "DataFiles/db_ssl/vlo/client-cert.pem"),
                "sslkey": Path(project_root_dir, "DataFiles/db_ssl/vlo/client-key.pem")
            },
            "vcp": {
                "user": "ovslxvcp01_00596338",
                "password": "cqs@@SM@bat599",
                "host": "10.171.129.230",
                "port": "5432",
                "sslmode": "verify-ca",
                "sslrootcert": Path(project_root_dir, "DataFiles/db_ssl/vcp/server-ca.pem"),
                "sslcert": Path(project_root_dir, "DataFiles/db_ssl/vcp/client-cert.pem"),
                "sslkey": Path(project_root_dir, "DataFiles/db_ssl/vcp/client-key.pem")
            }
        }
    }
    UAT = {
        "backoffice": {
            "endpoint": "https://ovs-lx-vlo-01-backoffice.gcubuat.gcp.uwccb/",
            "username": "super_tester",
            "password": "super_tester",
            "authorization": "un-auth"
        },
        "app": {
            "endpoint": "https://ovs-lx-vlo-01-app.gcubuat.gcp.uwccb/",
            "client_secret": "v3NfwHOqrT1lRLBC4NpESNeyBaa19IzL",
            "authorization": "un-auth"
        },
        "telco": {
            "endpoint": "https://ovs-lx-vcp-01-telcoapi.gcubuat.gcp.uwccb/"
        },
        "dataapi": {
            "endpoint": "https://ovs-lx-vcp-01-dataapi.gcubuat.gcp.uwccb/"
        },
        "msg-center": {
            "endpoint": "https://ovs-lx-vcp-01-msg-center.gcubuat.gcp.uwccb/"
        },
        "data-centralized": {
            "endpoint": "https://ovs-lx-vcp-01-data-centralized.gcubuat.gcp.uwccb/"
        },
        "customer-service": {
            "endpoint": "https://ovs-lx-vcp-01-customer-service.gcubuat.gcp.uwccb/",
            "username": "super_tester",
            "password": "super_tester",
            "client_secret": "YcHMT1fPADHE4Bf3rOimkkrxVVrhMpl8",
            "authorization": "un-auth"
        },
        "middle-bo-cl": {
            "endpoint": "https://ovs-lx-vcp-01-middle-bo-cl.gcubuat.gcp.uwccb/",
            "username": "super_tester2",
            "password": "super_tester2",
            "client_secret": "YcHMT1fPADHE4Bf3rOimkkrxVVrhMpl8",
            "authorization": "un-auth"  # same as cs due to middle-bo
        },
        "middle-bo-bff": {
            "endpoint": "https://dirhvcpbo01.cathayuat.intra.uwccb:8443/middle-bo-bff/",
            "username": "super_tester2",
            "password": "super_tester2",
            "client_secret": "YcHMT1fPADHE4Bf3rOimkkrxVVrhMpl8",
            "authorization": "un-auth"  # same as cs due to middle-bo
        }
    }

    @classmethod
    def build_url(cls, url, test_env):
        # override by env_info data
        pass

    @classmethod
    def build_header(cls, url, test_env: str):
        # override by env_info data
        pass
