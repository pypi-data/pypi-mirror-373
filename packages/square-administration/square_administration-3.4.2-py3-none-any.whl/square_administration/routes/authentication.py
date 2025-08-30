import json
from datetime import datetime
from typing import Annotated

import bcrypt
from fastapi import APIRouter, status, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from requests import HTTPError
from square_authentication_helper import TokenType
from square_commons import get_api_output_in_standard_format
from square_commons.api_utils import create_cookie
from square_database_helper.pydantic_models import FilterConditionsV0, FiltersV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.authentication import global_string_schema_name
from square_database_structure.square.authentication.tables import User, UserCredential

from square_administration.configuration import (
    global_object_square_logger,
    config_str_admin_password_hash,
    global_object_square_authentication_helper,
    config_str_cookie_domain,
    global_object_square_database_helper,
)
from square_administration.messages import messages
from square_administration.pydantic_models.authentication import (
    RegisterUsernameV0,
    LoginUsernameV0,
    RemoveAppForSelfV0,
    RegisterLoginGoogleV0,
    ResetPasswordAndLoginUsingBackupCodeV0,
    ResetPasswordAndLoginUsingResetEmailCodeV0,
    UpdatePasswordV0,
)
from square_administration.utils.common import is_https, global_int_app_id

router = APIRouter(
    tags=["authentication"],
)


@router.post("/register_username/v0")
@global_object_square_logger.auto_logger()
async def register_username_v0(
    body: RegisterUsernameV0,
):
    username = body.username
    password = body.password
    admin_password = body.admin_password

    username = username.lower()
    try:
        """
        validation
        """

        # validation for admin_password
        if not (
            bcrypt.checkpw(
                admin_password.encode("utf-8"),
                config_str_admin_password_hash.encode("utf-8"),
            )
        ):
            output_content = get_api_output_in_standard_format(
                message=messages["INCORRECT_PASSWORD"],
                log=f"incorrect admin password.",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=output_content,
            )

        """
        main process
        """
        response = global_object_square_authentication_helper.register_username_v0(
            username=username,
            password=password,
            app_id=global_int_app_id,
        )
        """
        return value
        """
        refresh_token = response["data"]["main"]["refresh_token"]
        refresh_token_expiry_time = response["data"]["main"][
            "refresh_token_expiry_time"
        ]
        del response["data"]["main"]["refresh_token"]
        del response["data"]["main"]["refresh_token_expiry_time"]
        output_content = get_api_output_in_standard_format(
            message=messages["REGISTRATION_SUCCESSFUL"],
            data={"main": response["data"]["main"]},
        )
        json_response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=output_content,
        )
        json_response.set_cookie(
            **create_cookie(
                key="refresh_token|" + str(global_int_app_id),
                value=refresh_token,
                domain=config_str_cookie_domain,
                expires=datetime.fromisoformat(refresh_token_expiry_time),
                secure=is_https(),
                http_only=True,
            )
        )
        return json_response
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


@router.post("/login_username/v0")
@global_object_square_logger.auto_logger()
async def login_username_v0(
    body: LoginUsernameV0,
):
    username = body.username
    password = body.password

    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.login_username_v0(
            username=username,
            password=password,
            app_id=global_int_app_id,
            assign_app_id_if_missing=False,
        )
        """
        return value
        """
        refresh_token = response["data"]["main"]["refresh_token"]
        refresh_token_expiry_time = response["data"]["main"][
            "refresh_token_expiry_time"
        ]
        del response["data"]["main"]["refresh_token"]
        del response["data"]["main"]["refresh_token_expiry_time"]
        output_content = get_api_output_in_standard_format(
            message=messages["LOGIN_SUCCESSFUL"],
            data={"main": response["data"]["main"]},
        )
        json_response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=output_content,
        )
        json_response.set_cookie(
            **create_cookie(
                key="refresh_token|" + str(global_int_app_id),
                value=refresh_token,
                domain=config_str_cookie_domain,
                expires=datetime.fromisoformat(refresh_token_expiry_time),
                secure=is_https(),
                http_only=True,
            )
        )
        return json_response
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


@router.patch("/remove_app_for_self/v0")
@global_object_square_logger.auto_logger()
async def remove_app_for_self_v0(
    access_token: Annotated[str, Header()],
    body: RemoveAppForSelfV0,
):
    password = body.password
    try:
        """
        validation
        """
        access_token_payload = global_object_square_authentication_helper.validate_and_get_payload_from_token_v0(
            access_token, TokenType.access_token, app_id=global_int_app_id
        )
        user_id = access_token_payload["data"]["main"]["user_id"]
        user_credentials_response = global_object_square_database_helper.get_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=UserCredential.__tablename__,
            filters=FiltersV0(
                root={
                    User.user_id.name: FilterConditionsV0(eq=user_id),
                }
            ),
            columns=[UserCredential.user_credential_hashed_password.name],
        )
        hashed_password = user_credentials_response["data"]["main"][0][
            UserCredential.user_credential_hashed_password.name
        ]

        if not (
            bcrypt.checkpw(
                password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        ):
            output_content = get_api_output_in_standard_format(
                message=messages["INCORRECT_PASSWORD"],
                log=f"incorrect password for user_id {user_id}.",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=output_content,
            )
        """
        main process
        """
        response = global_object_square_authentication_helper.update_user_app_ids_v0(
            access_token=access_token,
            app_ids_to_add=[],
            app_ids_to_remove=[global_int_app_id],
        )
        """
        return value
        """
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_UPDATE_SUCCESSFUL"],
            data={"main": response["data"]["main"]},
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=output_content,
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


@router.delete("/logout/v0")
@global_object_square_logger.auto_logger()
async def logout_v0(request: Request):

    try:
        """
        validation
        """

        refresh_token = request.cookies.get("refresh_token|" + str(global_int_app_id))
        if refresh_token is None:
            output_content = get_api_output_in_standard_format(
                message=messages["REFRESH_TOKEN_NOT_FOUND"],
                log=f"refresh token not found.",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=output_content,
            )
        refresh_token_payload = global_object_square_authentication_helper.validate_and_get_payload_from_token_v0(
            refresh_token, TokenType.refresh_token, app_id=global_int_app_id
        )[
            "data"
        ][
            "main"
        ]
        if refresh_token_payload["app_id"] != global_int_app_id:
            output_content = get_api_output_in_standard_format(
                message=messages["INCORRECT_REFRESH_TOKEN"],
                log=f"refresh token is for different app id. intended app id: {global_int_app_id}, actual app id: {refresh_token_payload['app_id']}.",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=output_content,
            )
        """
        main process
        """
        response = global_object_square_authentication_helper.logout_v0(
            refresh_token=refresh_token
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


@router.get("/generate_access_token/v0")
@global_object_square_logger.auto_logger()
async def generate_access_token_v0(
    request: Request,
):

    try:
        """
        validation
        """
        refresh_token = request.cookies.get("refresh_token|" + str(global_int_app_id))
        if refresh_token is None:
            output_content = get_api_output_in_standard_format(
                message=messages["REFRESH_TOKEN_NOT_FOUND"],
                log=f"refresh token not found.",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=output_content,
            )
        refresh_token_payload = global_object_square_authentication_helper.validate_and_get_payload_from_token_v0(
            refresh_token, TokenType.refresh_token, app_id=global_int_app_id
        )[
            "data"
        ][
            "main"
        ]
        if refresh_token_payload["app_id"] != global_int_app_id:
            output_content = get_api_output_in_standard_format(
                message=messages["INCORRECT_REFRESH_TOKEN"],
                log=f"refresh token is for different app id. intended app id: {global_int_app_id}, actual app id: {refresh_token_payload['app_id']}.",
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=output_content,
            )
        """
        main process
        """
        response = global_object_square_authentication_helper.generate_access_token_v0(
            refresh_token=refresh_token
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


@router.post("/register_login_google/v0")
@global_object_square_logger.auto_logger()
async def register_login_google_v0(body: RegisterLoginGoogleV0):
    google_id = body.google_id
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.register_login_google_v0(
            google_id=google_id,
            assign_app_id_if_missing=False,
            app_id=global_int_app_id,
        )
        """
        return value
        """
        refresh_token = response["data"]["main"]["refresh_token"]
        refresh_token_expiry_time = response["data"]["main"][
            "refresh_token_expiry_time"
        ]
        del response["data"]["main"]["refresh_token"]
        del response["data"]["main"]["refresh_token_expiry_time"]
        output_content = get_api_output_in_standard_format(
            message=messages["LOGIN_SUCCESSFUL"],
            data={"main": response["data"]["main"]},
        )
        json_response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=output_content,
        )
        json_response.set_cookie(
            **create_cookie(
                key="refresh_token|" + str(global_int_app_id),
                value=refresh_token,
                domain=config_str_cookie_domain,
                expires=datetime.fromisoformat(refresh_token_expiry_time),
                secure=is_https(),
                http_only=True,
            )
        )
        return json_response
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


@router.post("/reset_password_and_login_using_backup_code/v0")
@global_object_square_logger.auto_logger()
async def reset_password_and_login_using_backup_code_v0(
    body: ResetPasswordAndLoginUsingBackupCodeV0,
):
    backup_code = body.backup_code
    username = body.username
    new_password = body.new_password
    logout_other_sessions = body.logout_other_sessions
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.reset_password_and_login_using_backup_code_v0(
            backup_code=backup_code,
            username=username,
            new_password=new_password,
            app_id=global_int_app_id,
            logout_other_sessions=logout_other_sessions,
        )
        """
        return value
        """
        refresh_token = response["data"]["main"]["refresh_token"]
        refresh_token_expiry_time = response["data"]["main"][
            "refresh_token_expiry_time"
        ]
        del response["data"]["main"]["refresh_token"]
        del response["data"]["main"]["refresh_token_expiry_time"]
        output_content = get_api_output_in_standard_format(
            message=messages["LOGIN_SUCCESSFUL"],
            data={"main": response["data"]["main"]},
        )
        json_response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=output_content,
        )
        json_response.set_cookie(
            **create_cookie(
                key="refresh_token|" + str(global_int_app_id),
                value=refresh_token,
                domain=config_str_cookie_domain,
                expires=datetime.fromisoformat(refresh_token_expiry_time),
                secure=is_https(),
                http_only=True,
            )
        )
        return json_response
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


@router.post("/reset_password_and_login_using_reset_email_code/v0")
@global_object_square_logger.auto_logger()
async def reset_password_and_login_using_reset_email_code_v0(
    body: ResetPasswordAndLoginUsingResetEmailCodeV0,
):
    reset_email_code = body.reset_email_code
    username = body.username
    new_password = body.new_password
    logout_other_sessions = body.logout_other_sessions
    try:
        """
        validation
        """
        # pass
        """
        main process
        """
        response = global_object_square_authentication_helper.reset_password_and_login_using_reset_email_code_v0(
            reset_email_code=reset_email_code,
            username=username,
            new_password=new_password,
            app_id=global_int_app_id,
            logout_other_sessions=logout_other_sessions,
        )
        """
        return value
        """
        refresh_token = response["data"]["main"]["refresh_token"]
        refresh_token_expiry_time = response["data"]["main"][
            "refresh_token_expiry_time"
        ]
        del response["data"]["main"]["refresh_token"]
        del response["data"]["main"]["refresh_token_expiry_time"]
        output_content = get_api_output_in_standard_format(
            message=messages["LOGIN_SUCCESSFUL"],
            data={"main": response["data"]["main"]},
        )
        json_response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content=output_content,
        )
        json_response.set_cookie(
            **create_cookie(
                key="refresh_token|" + str(global_int_app_id),
                value=refresh_token,
                domain=config_str_cookie_domain,
                expires=datetime.fromisoformat(refresh_token_expiry_time),
                secure=is_https(),
                http_only=True,
            )
        )
        return json_response
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


@router.patch("/update_password/v0")
@global_object_square_logger.auto_logger()
async def update_password_v0(
    request: Request,
    body: UpdatePasswordV0,
    access_token: Annotated[str, Header()],
):
    old_password = body.old_password
    new_password = body.new_password
    logout_other_sessions = body.logout_other_sessions
    try:
        """
        validation
        """
        refresh_token = request.cookies.get("refresh_token|" + str(global_int_app_id))
        preserve_session_refresh_token = refresh_token
        if refresh_token is None:
            preserve_session_refresh_token = None
        refresh_token_payload = global_object_square_authentication_helper.validate_and_get_payload_from_token_v0(
            refresh_token, TokenType.refresh_token, app_id=global_int_app_id
        )[
            "data"
        ][
            "main"
        ]
        if refresh_token_payload["app_id"] != global_int_app_id:
            preserve_session_refresh_token = None
        """
        main process
        """
        response = global_object_square_authentication_helper.update_password_v0(
            old_password=old_password,
            new_password=new_password,
            access_token=access_token,
            logout_other_sessions=logout_other_sessions,
            preserve_session_refresh_token=preserve_session_refresh_token,
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
