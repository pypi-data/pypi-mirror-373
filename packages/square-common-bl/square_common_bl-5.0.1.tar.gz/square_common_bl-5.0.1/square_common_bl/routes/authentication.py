import json
import shutil
from typing import Annotated, Optional, List

from fastapi import APIRouter, Header, HTTPException, status, UploadFile
from fastapi.background import BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, Response
from requests import HTTPError
from square_commons import get_api_output_in_standard_format
from square_database_helper import FiltersV0
from square_database_helper.pydantic_models import FilterConditionsV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.authentication.enums import RecoveryMethodEnum
from square_database_structure.square.public import global_string_schema_name
from square_database_structure.square.public.tables import App

from square_common_bl.configuration import (
    global_object_square_logger,
    global_object_square_authentication_helper,
    global_object_square_database_helper,
    global_object_square_file_store_helper,
)
from square_common_bl.messages import messages
from square_common_bl.pydantic_models.authentication import (
    DeleteUserV0,
    LogoutAppsV0,
    ValidateEmailVerificationCodeV0,
    SendResetPasswordEmailV0,
)

router = APIRouter(
    tags=["authentication"],
)


def cleanup_task():
    shutil.rmtree("temp", True)


@router.post("/delete_user/v0")
@global_object_square_logger.auto_logger()
async def delete_user_v0(
    access_token: Annotated[str, Header()],
    body: DeleteUserV0,
):

    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.delete_user_v0(
            password=body.password,
            access_token=access_token,
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.patch("/update_username/v0")
@global_object_square_logger.auto_logger()
async def update_username_v0(
    new_username: str,
    access_token: Annotated[str, Header()],
):

    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.update_username_v0(
            new_username=new_username,
            access_token=access_token,
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.get("/get_user_details/v0")
@global_object_square_logger.auto_logger()
async def get_user_details_v0(
    access_token: Annotated[str, Header()],
):

    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.get_user_details_v0(
            access_token=access_token,
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.get("/get_user_profile_photo/v0")
@global_object_square_logger.auto_logger()
async def get_user_profile_photo_v0(
    access_token: Annotated[str, Header()],
):

    try:

        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.get_user_details_v0(
            access_token=access_token,
        )
        # not revalidating access token here
        user_profile_photo_storage_token = response["data"]["main"]["profile"][
            "user_profile_photo_storage_token"
        ]
        if not user_profile_photo_storage_token:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        profile_photo_path = global_object_square_file_store_helper.download_file_v0(
            file_storage_token=user_profile_photo_storage_token,
            output_folder_path="temp",
        )
        """
        return value
        """
        bg_tasks = BackgroundTasks()
        bg_tasks.add_task(cleanup_task)
        return FileResponse(
            status_code=status.HTTP_200_OK,
            path=profile_photo_path,
            background=bg_tasks,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        cleanup_task()
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        cleanup_task()
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        cleanup_task()
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.patch("/update_profile_photo/v0")
@global_object_square_logger.auto_logger()
async def update_profile_photo_v0(
    access_token: Annotated[str, Header()],
    profile_photo: Optional[UploadFile] = None,
):

    try:

        """
        validation
        """
        # pass
        """
        main process
        """
        if profile_photo:
            response = (
                global_object_square_authentication_helper.update_profile_photo_v0(
                    access_token=access_token,
                    profile_photo=(
                        profile_photo.filename,
                        profile_photo.file,
                        profile_photo.content_type,
                    ),
                )
            )
        else:
            response = (
                global_object_square_authentication_helper.update_profile_photo_v0(
                    access_token=access_token,
                    profile_photo=None,
                )
            )

        """
        return value
        """
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.delete("/logout/all/v0")
@global_object_square_logger.auto_logger()
async def logout_all_v0(
    access_token: Annotated[str, Header()],
):

    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.logout_all_v0(
            access_token=access_token,
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.delete("/logout/apps/v0")
@global_object_square_logger.auto_logger()
async def logout_apps_v0(
    access_token: Annotated[str, Header()],
    body: LogoutAppsV0,
):
    app_names = body.app_names
    try:
        """
        validation
        """
        unique_app_names = list(set(app_names))
        local_list_all_apps = global_object_square_database_helper.get_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=App.__tablename__,
            filters=FiltersV0(
                root={
                    App.app_name.name: FilterConditionsV0(in_=unique_app_names),
                }
            ),
        )["data"]["main"]
        if not len(local_list_all_apps) == len(unique_app_names):
            output_content = get_api_output_in_standard_format(
                message=messages["GENERIC_400"],
                log="invalid app names.",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=output_content,
            )
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.logout_apps_v0(
            access_token=access_token,
            app_ids=[x[App.app_id.name] for x in local_list_all_apps],
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.post("/validate_email_verification_code/v0")
@global_object_square_logger.auto_logger()
async def validate_email_verification_code_v0(
    access_token: Annotated[str, Header()],
    body: ValidateEmailVerificationCodeV0,
):
    verification_code = body.verification_code
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.validate_email_verification_code_v0(
            access_token=access_token, verification_code=verification_code
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.post("/send_verification_email/v0")
@global_object_square_logger.auto_logger()
async def send_verification_email_v0(
    access_token: Annotated[str, Header()],
):
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = (
            global_object_square_authentication_helper.send_verification_email_v0(
                access_token=access_token,
            )
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.patch("/update_profile_details/v0")
@global_object_square_logger.auto_logger()
async def update_profile_details_v0(
    access_token: Annotated[str, Header()],
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone_number_country_code: Optional[str] = None,
    phone_number: Optional[str] = None,
):
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.update_profile_details_v0(
            access_token=access_token,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number_country_code=phone_number_country_code,
            phone_number=phone_number,
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.post("/send_reset_password_email/v0")
@global_object_square_logger.auto_logger()
async def send_reset_password_email_v0(
    body: SendResetPasswordEmailV0,
):
    username = body.username
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = (
            global_object_square_authentication_helper.send_reset_password_email_v0(
                username=username
            )
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.post("/generate_account_backup_codes/v0")
@global_object_square_logger.auto_logger()
async def generate_account_backup_codes_v0(
    access_token: Annotated[str, Header()],
):

    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = (
            global_object_square_authentication_helper.generate_account_backup_codes_v0(
                access_token=access_token
            )
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )


@router.patch("/update_user_recovery_methods/v0")
@global_object_square_logger.auto_logger()
async def update_user_recovery_methods_v0(
    access_token: Annotated[str, Header()],
    recovery_methods_to_add: List[RecoveryMethodEnum] = None,
    recovery_methods_to_remove: List[RecoveryMethodEnum] = None,
):
    if not recovery_methods_to_add:
        recovery_methods_to_add = []
    if not recovery_methods_to_remove:
        recovery_methods_to_remove = []
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = (
            global_object_square_authentication_helper.update_user_recovery_methods_v0(
                access_token=access_token,
                recovery_methods_to_add=recovery_methods_to_add,
                recovery_methods_to_remove=recovery_methods_to_remove,
            )
        )
        """
        return value
        """

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )
    except HTTPError as http_error:
        global_object_square_logger.logger.error(http_error, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_error.response.status_code,
            content=json.loads(http_error.response.content),
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
        """
        rollback logic
        """
        # pass
        return JSONResponse(
            status_code=http_exception.status_code, content=http_exception.detail
        )
    except Exception as e:
        global_object_square_logger.logger.error(e, exc_info=True)
        """
        rollback logic
        """
        # pass
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=output_content
        )
