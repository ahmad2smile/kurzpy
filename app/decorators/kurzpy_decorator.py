import inspect
from typing import Any

from sqlmodel import SQLModel

from app.decorators.entity_service import EntityService
from app.decorators.rest_api import RestController


def get_class_info[TModel: SQLModel](
    model_class: type[TModel],
) -> tuple[str, type[Any], str]:
    class_name = model_class.__name__
    fields = model_class.model_fields

    # TODO: Find typesafe solution to id on model
    if "id" not in fields:
        raise Exception(
            f"An id field is required to use {inspect.stack()[1][3]} on {class_name}"
        )

    id_field = fields["id"]
    collection_name = f"{class_name.lower()}s"
    # NOTE: Checked above already
    id_type: type[Any] = id_field.annotation  # type: ignore[valid-type]

    return (class_name, id_type, collection_name)


class kurzpy[TModel: SQLModel]:
    @staticmethod
    def rest_api(model_class: type[TModel]):
        (class_name, id_type, collection_name) = get_class_info(model_class=model_class)

        model_class.__tablename__ = collection_name

        entity_service = EntityService[model_class, id_type](
            entity=class_name, model_class=model_class
        )

        rest_api = RestController[TModel, id_type](
            model_class=model_class,
            route_name=collection_name,
            class_name=class_name,
            id_type=id_type,
            entity_service=entity_service,
        )

        model_class.router = rest_api.router

        return model_class
