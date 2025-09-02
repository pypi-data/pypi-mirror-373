import mimetypes
import os
import uuid

from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, JSONResponse
from square_commons import get_api_output_in_standard_format
from square_database_helper import FiltersV0
from square_database_helper.pydantic_models import FilterConditionsV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.file_storage import global_string_schema_name
from square_database_structure.square.file_storage.tables import File

from square_file_store.configuration import (
    global_absolute_path_local_storage,
    global_object_square_logger,
)
from square_file_store.messages import messages
from square_file_store.utils.helper import (
    create_entry_in_file_store,
    local_object_square_database_helper,
    get_file_row,
)


@global_object_square_logger.auto_logger()
async def util_upload_file_v0(file, app_id, system_relative_path):
    system_file_absolute_path = None
    file_storage_token = None
    try:
        """
        validation
        """
        # pass
        """
        main
        """
        file_bytes = await file.read()
        filename = file.filename
        content_type = file.content_type

        file_storage_token = str(uuid.uuid4())
        system_file_name = str(uuid.uuid4())
        file_extension = filename.rsplit(".", 1)[-1]
        system_file_name_with_extension = system_file_name + "." + file_extension
        response = create_entry_in_file_store(
            file_name_with_extension=filename,
            content_type=content_type,
            file_storage_token=file_storage_token,
            app_id=app_id,
            system_relative_path=system_relative_path,
            system_file_name_with_extension=system_file_name_with_extension,
        )

        # create folder
        system_absolute_path = os.path.join(
            global_absolute_path_local_storage,
            os.sep.join(system_relative_path.split("/")),
        )

        # create path if it doesn't exist.
        if not os.path.exists(system_absolute_path):
            os.makedirs(system_absolute_path)

        system_file_absolute_path = os.path.join(
            system_absolute_path, system_file_name_with_extension
        )
        with open(system_file_absolute_path, "wb") as file:
            file.write(file_bytes)

        # Check if the file exists
        if not os.path.exists(system_file_absolute_path):
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_500"],
                log=f"file creation failed at {system_file_absolute_path}.",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=output_content,
            )
        """
        return value
        """
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_CREATION_SUCCESSFUL"],
            data={"main": response[0][File.file_storage_token.name]},
        )
        return JSONResponse(content=output_content, status_code=status.HTTP_201_CREATED)
    except HTTPException as http_exception:
        """
        rollback logic
        """
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        if os.path.exists(system_file_absolute_path):
            os.remove(system_file_absolute_path)
        if file_storage_token:
            local_object_square_database_helper.delete_rows_v0(
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
            )
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        """
        rollback logic
        """
        if system_file_absolute_path and os.path.exists(system_file_absolute_path):
            os.remove(system_file_absolute_path)
        if file_storage_token:
            local_object_square_database_helper.delete_rows_v0(
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
            )
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@global_object_square_logger.auto_logger()
def util_download_file_v0(file_storage_token):
    file_storage_token = str(file_storage_token)
    try:
        """
        validation
        """
        # pass
        """
        main
        """
        local_dict_file_row = get_file_row(file_storage_token)
        local_string_system_absolute_file_path = str(
            os.path.join(
                global_absolute_path_local_storage,
                os.sep.join(
                    local_dict_file_row[File.file_system_relative_path.name].split("/")
                ),
                local_dict_file_row[File.file_system_file_name_with_extension.name],
            )
        )
        if not os.path.exists(local_string_system_absolute_file_path):
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_500"],
                log=f"file: {file_storage_token} not found in path {local_string_system_absolute_file_path}.",
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=output_content,
            )
        """
        return value
        """
        content_type, _ = mimetypes.guess_type(local_string_system_absolute_file_path)

        return FileResponse(
            local_string_system_absolute_file_path,
            media_type=content_type,
            filename=local_dict_file_row[File.file_name_with_extension.name],
        )
    except HTTPException as http_exception:
        """
        rollback logic
        """
        # pass
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        """
        rollback logic
        """
        # pass
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@global_object_square_logger.auto_logger()
def util_delete_files_v0(file_storage_tokens):
    list_file_storage_tokens = list(set(str(x) for x in file_storage_tokens))
    deleted_file_storage_tokens = []
    try:
        """
        validation
        """
        # pass
        """
        main
        """
        for file_storage_token in list_file_storage_tokens:
            # get file path
            local_dict_file_row = get_file_row(file_storage_token)
            local_string_system_absolute_file_path = str(
                os.path.join(
                    global_absolute_path_local_storage,
                    os.sep.join(
                        local_dict_file_row[File.file_system_relative_path.name].split(
                            "/"
                        )
                    ),
                    local_dict_file_row[File.file_system_file_name_with_extension.name],
                )
            )

            # delete file
            if os.path.exists(local_string_system_absolute_file_path):
                os.remove(local_string_system_absolute_file_path)
            else:
                global_object_square_logger.logger.warning(
                    f"file {local_string_system_absolute_file_path} should have existed but doesn't."
                )

            deleted_file_storage_tokens.append(file_storage_token)
        local_object_square_database_helper.delete_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=File.__tablename__,
            filters=FiltersV0(
                root={
                    File.file_storage_token.name: FilterConditionsV0(
                        in_=deleted_file_storage_tokens
                    ),
                }
            ),
        )
        """
        return value
        """
        output_content = get_api_output_in_standard_format(
            data={"main": deleted_file_storage_tokens},
            message=messages["GENERIC_DELETE_SUCCESSFUL"],
        )
        return JSONResponse(content=output_content)
    except HTTPException as http_exception:
        """
        rollback logic
        """
        # pass
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        return JSONResponse(
            status_code=http_exception.status_code,
            content=http_exception.detail,
        )
    except Exception as e:
        """
        rollback logic
        """
        # pass
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=output_content,
        )
