import json
import string
from io import BytesIO
from re import sub

import pandas as pd
from unidecode import unidecode


def to_camelCase(statement: str):
    """_Convert statement string in camel case (camelCase) convention._

    example:
    - from: `'Suspéndisse dictum diam àc magna varius, in susçipit elit luctus?'`
    - into: `'suspendisseDictumDiamAcMagnaVariusInSuscipitElitLuctus'`
    """
    statement = unidecode(statement)
    statement = statement.translate(str.maketrans("", "", string.punctuation))
    statement = sub(r"(_|-)+", " ", statement).title().replace(" ", "")
    return statement[0].lower() + statement[1:]


def to_kebabCase(statement: str):
    """_Convert statement string in kebab case (kebab-case) convention._

    example:
    - from: `'Suspéndisse dictum diam àc Magna varius, in susçipit elit Luctus?'`
    - into: `'suspendisse-dictum-diam-ac-magna-varius-in-suscipit-elit-luctus'`
    """
    statement = unidecode(statement)
    statement = statement.translate(str.maketrans(" ", "-", string.punctuation))
    return statement.lower()


def convert_csv_bytes_to_json(csv_data):
    """_Convert csv data into json._

    Keyword arguments:
    - csv_data -- the csv content
    """
    data_frame = pd.read_csv(BytesIO(csv_data))
    columns_new_names = {c: to_camelCase(c) for c in data_frame.columns}
    data_frame = data_frame.rename(columns=columns_new_names)
    obj_data_json = json.loads(data_frame.to_json(orient="records"))

    return obj_data_json
