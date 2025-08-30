import os
import sys

from square_commons import ConfigReader
from square_logger.main import SquareLogger

try:

    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "config.ini"
    )
    config_sample_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "config.sample.ini"
    )
    ldict_configuration = ConfigReader(
        config_file_path, config_sample_file_path
    ).read_configuration()

    # get all vars and typecast
    # ===========================================
    # general
    config_str_module_name = ldict_configuration["GENERAL"]["MODULE_NAME"]
    # ===========================================

    # ===========================================
    # environment
    config_str_host_ip = ldict_configuration["ENVIRONMENT"]["HOST_IP"]
    config_int_host_port = int(ldict_configuration["ENVIRONMENT"]["HOST_PORT"])
    config_list_allow_origins = eval(
        ldict_configuration["ENVIRONMENT"]["ALLOW_ORIGINS"]
    )

    config_str_log_file_name = ldict_configuration["ENVIRONMENT"]["LOG_FILE_NAME"]
    config_str_local_storage_folder_path = ldict_configuration["ENVIRONMENT"][
        "LOCAL_STORAGE_PATH"
    ]
    config_str_ssl_crt_file_path = ldict_configuration["ENVIRONMENT"][
        "SSL_CRT_FILE_PATH"
    ]
    config_str_ssl_key_file_path = ldict_configuration["ENVIRONMENT"][
        "SSL_KEY_FILE_PATH"
    ]

    config_str_db_ip = ldict_configuration["ENVIRONMENT"]["DB_IP"]
    config_int_db_port = int(ldict_configuration["ENVIRONMENT"]["DB_PORT"])
    config_str_db_username = ldict_configuration["ENVIRONMENT"]["DB_USERNAME"]
    config_str_db_password = ldict_configuration["ENVIRONMENT"]["DB_PASSWORD"]

    # ===========================================

    # ===========================================
    # square_logger
    config_int_log_level = int(ldict_configuration["SQUARE_LOGGER"]["LOG_LEVEL"])
    config_str_log_path = ldict_configuration["SQUARE_LOGGER"]["LOG_PATH"]
    config_int_log_backup_count = int(
        ldict_configuration["SQUARE_LOGGER"]["LOG_BACKUP_COUNT"]
    )
    # ===========================================
    # ===========================================
    # square_database_helper

    config_str_square_database_protocol = ldict_configuration["SQUARE_DATABASE_HELPER"][
        "SQUARE_DATABASE_PROTOCOL"
    ]
    config_str_square_database_ip = ldict_configuration["SQUARE_DATABASE_HELPER"][
        "SQUARE_DATABASE_IP"
    ]
    config_int_square_database_port = int(
        ldict_configuration["SQUARE_DATABASE_HELPER"]["SQUARE_DATABASE_PORT"]
    )
    # ===========================================
    # initialize logger

    global_object_square_logger = SquareLogger(
        pstr_log_file_name=config_str_log_file_name,
        pint_log_level=config_int_log_level,
        pstr_log_path=config_str_log_path,
        pint_log_backup_count=config_int_log_backup_count,
    )
except Exception as e:
    print(
        "\033[91mMissing or incorrect config.ini file.\n"
        "Error details: " + str(e) + "\033[0m"
    )
    sys.exit()

# extra logic for this module

try:
    global_absolute_path_local_storage = os.path.abspath(
        config_str_local_storage_folder_path
    )
    if not os.path.exists(global_absolute_path_local_storage):
        os.makedirs(global_absolute_path_local_storage)
except Exception as e:
    print(
        "\033[91mIncorrect value for LOCAL_STORAGE_PATH in config.ini file.\n"
        "Error details: " + str(e) + "\033[0m"
    )
    sys.exit()
