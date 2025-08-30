import json
from typing import Annotated

from fastapi import APIRouter, Header, status, HTTPException
from fastapi.responses import JSONResponse
from requests import HTTPError
from square_authentication_helper import TokenType
from square_commons import get_api_output_in_standard_format
from square_database_helper import FiltersV0
from square_database_helper.pydantic_models import FilterConditionsV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.authentication import (
    global_string_schema_name as global_string_schema_name_authentication,
)
from square_database_structure.square.authentication.tables import UserProfile
from square_database_structure.square.greeting import global_string_schema_name
from square_database_structure.square.greeting.tables import Greeting

from square_administration.configuration import (
    global_object_square_logger,
    global_object_square_database_helper,
    global_object_square_authentication_helper,
)
from square_administration.messages import messages
from square_administration.pydantic_models.core import GetAllGreetingsV0
from square_administration.utils.common import global_int_app_id

router = APIRouter(
    tags=["core"],
)


@router.post("/get_all_greetings/v0")
@global_object_square_logger.auto_logger()
async def get_all_greetings_v0(
    access_token: Annotated[str, Header()], body: GetAllGreetingsV0
):
    order_by = body.order_by
    limit = body.limit
    offset = body.offset

    try:
        """
        validation
        """
        access_token_payload = global_object_square_authentication_helper.validate_and_get_payload_from_token_v0(
            token=access_token,
            token_type=TokenType.access_token,
            app_id=global_int_app_id,
        )[
            "data"
        ][
            "main"
        ]
        if access_token_payload["app_id"] != global_int_app_id:
            output_content = get_api_output_in_standard_format(
                message=messages["INCORRECT_ACCESS_TOKEN"], log="app id is incorrect."
            )
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=output_content,
            )

        """
        main process
        """
        response = global_object_square_database_helper.get_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=Greeting.__tablename__,
            filters=FiltersV0(root={}),
            apply_filters=False,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
        all_user_ids = {
            x[Greeting.user_id.name]
            for x in response["data"]["main"]
            if x[Greeting.user_id.name] is not None
        }
        user_profile_response = global_object_square_database_helper.get_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name_authentication,
            table_name=UserProfile.__tablename__,
            filters=FiltersV0(
                root={
                    UserProfile.user_id.name: FilterConditionsV0(in_=list(all_user_ids))
                }
            ),
            columns=[
                UserProfile.user_id.name,
                UserProfile.user_profile_username.name,
            ],
        )["data"]["main"]
        user_map = {
            x[UserProfile.user_id.name]: x[UserProfile.user_profile_username.name]
            for x in user_profile_response
        }
        response_clone = response
        response_clone["data"]["main"] = [
            {
                **greeting,
                UserProfile.user_profile_username.name: user_map.get(
                    greeting[Greeting.user_id.name]
                ),
            }
            for greeting in response["data"]["main"]
        ]

        """
        return value
        """
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_READ_SUCCESSFUL"],
            data=response_clone["data"],
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
