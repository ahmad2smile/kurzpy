import inspect
from typing import Any

from sqlmodel import SQLModel

from lib.entity_service import EntityService
from lib.errors.mode_exceptions import InvalidModelException
from lib.rest_api import RestController
from lib.router_collection import REST_ROUTERS


def get_class_info[TModel: SQLModel](model_class: type[TModel]) -> tuple[str, type[Any], str]:  # pyright: ignore[reportExplicitAny]
    class_name = model_class.__name__
    fields = model_class.model_fields

    id_field = fields.get("id")
    # TODO: Find typesafe solution to id on model
    if id_field is None or not id_field.annotation:
        raise InvalidModelException(f"An id field is required to use {inspect.stack()[1][3]} on {class_name}")

    collection_name = f"{class_name.lower()}s"

    id_type = id_field.annotation

    return (class_name, id_type, collection_name)


class kurzpy[TModel: SQLModel]:
    @staticmethod
    def rest_api(model_class: type[TModel]):
        (class_name, id_type, collection_name) = get_class_info(model_class=model_class)

        model_class.__tablename__ = collection_name

        entity_service = EntityService[model_class, id_type](entity=class_name, model_class=model_class)

        rest_api = RestController[TModel, id_type](
            model_class=model_class,
            route_name=collection_name,
            class_name=class_name,
            id_type=id_type,
            entity_service=entity_service,
        )

        REST_ROUTERS[class_name] = rest_api.router

        return model_class
