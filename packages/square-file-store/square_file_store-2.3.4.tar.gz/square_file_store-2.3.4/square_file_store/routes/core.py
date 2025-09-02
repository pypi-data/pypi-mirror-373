from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Form, UploadFile, status
from fastapi.exceptions import HTTPException
from fastapi.params import Query
from fastapi.responses import JSONResponse
from square_commons import get_api_output_in_standard_format

from square_file_store.configuration import (
    global_object_square_logger,
)
from square_file_store.messages import messages
from square_file_store.utils.routes.core import (
    util_upload_file_v0,
    util_download_file_v0,
    util_delete_files_v0,
)

router = APIRouter(
    tags=["core"],
)


@router.post("/upload_file/v0", status_code=status.HTTP_201_CREATED)
@global_object_square_logger.auto_logger()
async def upload_file_v0(
    file: UploadFile,
    app_id: Annotated[
        Optional[int],
        Form(title="App id", description="Specify the app id"),
    ] = None,
    system_relative_path: Annotated[
        str,
        Form(
            title="System relative path",
            description="Specify the path using '/'. For e.g. home/user_document",
        ),
    ] = "others/misc",
):
    try:
        return await util_upload_file_v0(
            file=file, app_id=app_id, system_relative_path=system_relative_path
        )
    except HTTPException as he:
        global_object_square_logger.logger.error(he, exc_info=True)
        return JSONResponse(status_code=he.status_code, content=he.detail)
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.get("/download_file/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.auto_logger()
async def download_file_v0(file_storage_token: UUID):
    try:
        return util_download_file_v0(
            file_storage_token=file_storage_token,
        )
    except HTTPException as he:
        global_object_square_logger.logger.error(he, exc_info=True)
        return JSONResponse(status_code=he.status_code, content=he.detail)
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.delete("/delete_files/v0", status_code=status.HTTP_200_OK)
@global_object_square_logger.auto_logger()
async def delete_files_v0(file_storage_tokens: List[UUID] = Query()):
    try:
        return util_delete_files_v0(
            file_storage_tokens=file_storage_tokens,
        )
    except HTTPException as he:
        global_object_square_logger.logger.error(he, exc_info=True)
        return JSONResponse(status_code=he.status_code, content=he.detail)
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"], log=str(e)
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )
