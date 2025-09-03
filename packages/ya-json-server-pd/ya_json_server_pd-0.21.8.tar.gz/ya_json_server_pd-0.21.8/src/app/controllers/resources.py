import json
import os

from fastapi import status

from app.config import DB_JSON_FILENAME
from app.handlers.commons import convert_csv_bytes_to_json, to_kebabCase
from app.handlers.exceptions import APIException
from app.models.db_json_content import JsonContentModel


class ResourcesController:
    json_content_mdl: JsonContentModel
    page: int = 1
    limit: int = 10

    def __init__(self):
        self.json_content_mdl: JsonContentModel = JsonContentModel(DB_JSON_FILENAME)

    def get_resources_list(self):
        resources_list = self.json_content_mdl.get_resources_list()
        return resources_list

    def get_resource_data(self, resource, page, limit):
        result: dict = self.json_content_mdl.get_data_by_resource_name(
            resource, page, limit
        )
        if not result:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Resourse ({resource}) not found.",
            )

        return result

    def retrieve_resources_by_id(self, resource, id: int | str):
        result = self.json_content_mdl.get_data_resource_by_id(resource, id)
        if result is False:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Resourse ({resource}) not found.",
            )

        if result is None:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"The {resource} resourse has not an 'id' like attribute.",
            )

        if not result:
            raise APIException(
                status_code=status.HTTP_404_NOT_FOUND,
                message=f"Data with id {id} not found for the {resource} resourse.",
            )

        return result

    async def update_db_json_from_csv(self, csv_file):
        resource = csv_file.filename
        csv_data_bytes = await csv_file.read()
        await csv_file.close()

        resource = resource[:-4] if ".csv" in resource else resource
        resource = " ".join(resource.split("_"))
        resource = to_kebabCase(resource)

        obj_json: list[dict] = convert_csv_bytes_to_json(csv_data_bytes)
        db_json_data = {
            f"{resource}": obj_json,
        }

        os.makedirs(os.path.dirname(DB_JSON_FILENAME), exist_ok=True)

        with open(DB_JSON_FILENAME, mode="w+", encoding="utf-8") as jsonfile:
            json.dump(db_json_data, jsonfile, indent=4)

        self.json_content_mdl.set(db_json_data)

        return {
            "message": "Updated DB JSON ({}) from the {} content.".format(
                DB_JSON_FILENAME, csv_file.filename
            ),
            f"{resource}": obj_json[:5],
        }
