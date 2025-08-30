import json

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from requests import HTTPError
from square_commons import get_api_output_in_standard_format
from square_database_structure.square import global_string_database_name
from square_database_structure.square.greeting import global_string_schema_name
from square_database_structure.square.greeting.tables import Greeting

from square_common_bl.configuration import (
    global_object_square_logger,
    global_object_square_database_helper,
)
from square_common_bl.messages import messages
from square_common_bl.pydantic_models.greeting import (
    CreateAnonymousGreetingV0,
)

router = APIRouter(
    tags=["greeting"],
)


@router.post("/create_anonymous_greeting/v0")
@global_object_square_logger.auto_logger()
async def create_anonymous_greeting_v0(body: CreateAnonymousGreetingV0):
    greeting_anonymous_sender_name = body.greeting_anonymous_sender_name
    greeting_text = body.greeting_text

    try:

        """
        validation
        """
        # pass
        """
        main process
        """
        # add greeting to the table
        local_list = global_object_square_database_helper.insert_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=Greeting.__tablename__,
            data=[
                {
                    Greeting.greeting_is_anonymous.name: True,
                    Greeting.greeting_anonymous_sender_name.name: greeting_anonymous_sender_name,
                    Greeting.greeting_text.name: greeting_text,
                },
            ],
        )

        """
        return value
        """

        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_CREATION_SUCCESSFUL"],
            data={"main": local_list["data"]["main"]},
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
        """
        rollback logic
        """
        global_object_square_logger.logger.error(e, exc_info=True)
        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_500"],
            log=str(e),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=output_content,
        )
