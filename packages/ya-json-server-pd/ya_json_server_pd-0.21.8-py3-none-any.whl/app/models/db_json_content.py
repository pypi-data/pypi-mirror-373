import json
import os

from app.config import DB_JSON_FILENAME
from app.handlers.singleton import Singleton


class JsonContentModel(metaclass=Singleton):
    _json_data: dict

    def __init__(self, db_json_filename: str):
        self._db_json_filename = db_json_filename
        self._retrieve_db_json_content()

    def _init_db_json(self):

        db_sample_if_not_exists = {
            "yetAnotherJsonServerSample": [
                {
                    "companyId": 1,
                    "company": "Miller and Sons",
                    "city": "Johnborough",
                    "country": "New Caledonia",
                    "postcode": 5184,
                    "pricetag": 682668.58,
                },
                {
                    "companyId": 2,
                    "company": "Pitts LLC",
                    "city": "Frederickfurt",
                    "country": "Jamaica",
                    "postcode": 69412,
                    "pricetag": 248.23,
                },
                {
                    "companyId": 3,
                    "company": "Nguyen and Sons",
                    "city": "Yolandaside",
                    "country": "Cocos (Keeling) Islands",
                    "postcode": 58911,
                    "pricetag": 48859.55,
                },
                {
                    "companyId": 153,
                    "company": "Sullivan-Lynch",
                    "city": "South David",
                    "country": "Norway",
                    "postcode": 59906,
                    "pricetag": 48.75,
                },
                {
                    "companyId": 157,
                    "company": "Oconnell-Sullivan",
                    "city": "New Allisonfort",
                    "country": "Dominican Republic",
                    "postcode": 63476,
                    "pricetag": 348.79,
                },
            ],
            "posts": [{"id": 1, "title": "json-server", "author": "typicode"}],
            "comments": [{"id": 1, "body": "some comment", "postId": 1}],
            "products": [
                {
                    "id": 7,
                    "title": "Jeans",
                    "brand": "Gucci",
                    "price": 37,
                    "reviewScore": 1.3567503747,
                    "color": "White",
                    "size": "XL",
                    "image": "http://products.net/img/",
                },
                {
                    "productId": 375,
                    "title": "Dress",
                    "brand": "Adidas",
                    "price": 40,
                    "reviewScore": 1.0431592108,
                    "color": "Black",
                    "size": "XL",
                    "image": "http://products.net/img/",
                },
            ],
            "stoke-exchange": [
                {
                    "company": "Chuchu e Melão S/A",
                    "city": "Belo Horizonte",
                    "ceoUserId": "99273502-9448-4197-abc4-422d4c792264",
                    "state": "Minas Gerais",
                    "id": 17,
                    "country": "Brasil",
                    "postcode": 40256,
                    "idProduct": 19,
                    "priceTag": "45,593,820",
                    "shareValue": "617.00",
                }
            ],
        }

        if not os.path.exists(DB_JSON_FILENAME):
            os.makedirs(name=os.path.dirname(DB_JSON_FILENAME), exist_ok=True)
            with open(DB_JSON_FILENAME, mode="w+") as jsonfile:
                json.dump(db_sample_if_not_exists, jsonfile, indent=4)

    def get_resources_list(self):
        resources = self._json_data.keys()

        result = [{resource: len(self._json_data[resource])} for resource in resources]

        return result

    def get_data_by_resource_name(self, resource, page, limit):
        if resource not in self._json_data:
            return {}
        result = self._json_data[resource]

        low_limit = page * limit - limit
        high_limit = page * limit
        result = result[low_limit:high_limit]

        return result

    def get_data_resource_by_id(
        self, resource: str, id: int | str
    ) -> bool | None | dict:
        """
        Returns:
            - bool | None | dict: _Returns `False` if resource not found or
                `None` if resourse has not an 'id' like attribute._
        """
        if resource not in self._json_data:
            return False
        # Get the keys with the ID like in it, to get the first one,
        # e.g: 'id', 'idProduct', or 'productId'
        id_idx = list(
            filter(
                lambda x: x == "id"
                or (x[:2] == "id" and x[:3][-1:].isupper())
                or x[-2:] == "Id",
                self._json_data[resource][0].keys(),
            )
        )
        if not id_idx:
            return None

        id_idx_zero = id_idx[0]
        resource_data = self._json_data[resource]

        result = (
            list(filter(lambda r: r[id_idx_zero] == id, resource_data))
            if isinstance(id, str) and not id.isdigit()
            else list(filter(lambda r: r[id_idx_zero] == int(id), resource_data))
        )

        return result

    def set(self, json_data):
        self._json_data = json_data

    def _retrieve_db_json_content(self):
        if not os.path.exists(self._db_json_filename):
            self._init_db_json()
        with open(self._db_json_filename, mode="r") as db_json:
            self._json_data: dict[list[dict]] = json.load(db_json)

        return self._json_data
        return self._json_data
