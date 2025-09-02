from fastapi import status
from fastapi.exceptions import HTTPException
from square_commons import get_api_output_in_standard_format
from square_database_helper import SquareDatabaseHelper, FiltersV0
from square_database_helper.pydantic_models import FilterConditionsV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.file_storage import global_string_schema_name
from square_database_structure.square.file_storage.tables import File

from square_file_store.configuration import (
    config_str_square_database_protocol,
    config_str_square_database_ip,
    config_int_square_database_port,
    global_object_square_logger,
)
from square_file_store.messages import messages

local_object_square_database_helper = SquareDatabaseHelper(
    param_str_square_database_ip=config_str_square_database_ip,
    param_str_square_database_protocol=config_str_square_database_protocol,
    param_int_square_database_port=config_int_square_database_port,
)


@global_object_square_logger.auto_logger()
def create_entry_in_file_store(
    file_name_with_extension: str,
    content_type: str,
    system_file_name_with_extension: str,
    file_storage_token: str,
    app_id: int,
    system_relative_path: str,
):
    try:

        data = [
            {
                File.file_name_with_extension.name: file_name_with_extension,
                File.file_content_type.name: content_type,
                File.file_system_file_name_with_extension.name: system_file_name_with_extension,
                File.file_system_relative_path.name: system_relative_path,
                File.file_storage_token.name: file_storage_token,
                File.app_id.name: app_id,
            }
        ]

        response = local_object_square_database_helper.insert_rows_v0(
            data=data,
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=File.__tablename__,
        )["data"]["main"]

        return response
    except Exception as e:
        raise e


@global_object_square_logger.auto_logger()
def get_file_row(file_storage_token):
    try:
        response = local_object_square_database_helper.get_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=File.__tablename__,
            filters=FiltersV0(
                root={
                    File.file_storage_token.name: FilterConditionsV0(
                        eq=file_storage_token
                    ),
                }
            ),
        )["data"]["main"]
        if len(response) != 1:
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_400"],
                log=f"incorrect file_storage_token: {file_storage_token}.",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=output_content,
            )
        return response[0]
    except Exception as e:
        raise e
