from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from square_commons import get_api_output_in_standard_format
from square_database_helper.pydantic_models import FilterConditionsV0, FiltersV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.public import global_string_schema_name
from square_database_structure.square.public.tables import App

from square_common_bl.configuration import (
    global_object_square_logger,
    global_object_square_database_helper,
)
from square_common_bl.messages import messages

router = APIRouter(
    tags=["utils"],
)


@router.get("/get_app_id/v0")
@global_object_square_logger.auto_logger()
async def get_app_id_v0(app_name: str):
    try:

        """
        validation
        """
        # pass
        """
        main process
        """

        local_list = global_object_square_database_helper.get_rows_v0(
            database_name=global_string_database_name,
            schema_name=global_string_schema_name,
            table_name=App.__tablename__,
            columns=[App.app_id.name],
            filters=FiltersV0(
                root={App.app_name.name: FilterConditionsV0(eq=app_name)}
            ),
        )["data"]["main"]
        if len(local_list) != 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=get_api_output_in_standard_format(
                    message=messages["GENERIC_400"],
                    log=f"invalid app name: {app_name}.",
                ),
            )

        """
        return value
        """

        output_content = get_api_output_in_standard_format(
            message=messages["GENERIC_READ_SUCCESSFUL"],
            data={"main": local_list[0][App.app_id.name]},
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=output_content,
        )
    except HTTPException as http_exception:
        global_object_square_logger.logger.error(http_exception, exc_info=True)
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
