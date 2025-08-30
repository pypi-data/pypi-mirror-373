import os

from square_database_helper import FiltersV0
from square_database_helper.pydantic_models import FilterConditionsV0
from square_database_structure.square import global_string_database_name
from square_database_structure.square.public import global_string_schema_name
from square_database_structure.square.public.tables import App

from square_administration.configuration import (
    config_str_ssl_key_file_path,
    config_str_ssl_crt_file_path,
    global_object_square_logger,
    global_object_square_database_helper,
    config_str_app_name,
)


@global_object_square_logger.auto_logger()
def is_https() -> bool:
    return os.path.exists(config_str_ssl_key_file_path) and os.path.exists(
        config_str_ssl_crt_file_path
    )


# get app id
global_int_app_id = global_object_square_database_helper.get_rows_v0(
    database_name=global_string_database_name,
    schema_name=global_string_schema_name,
    table_name=App.__tablename__,
    filters=FiltersV0(
        root={
            App.app_name.name: FilterConditionsV0(eq=config_str_app_name),
        }
    ),
    columns=[App.app_id.name],
)["data"]["main"][0][App.app_id.name]
