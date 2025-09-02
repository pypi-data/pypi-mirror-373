import json
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound='BaseModel')

class ExtDeserializableGeneric():

    @staticmethod
    def json_to_obj_v1(json_object:str, obj_type:type[T])->T:
        try:
            json_obj = json.loads(str(json_object, encoding='utf-8').replace( "'", '"'))
            serializable_data = obj_type(**json_obj)

            return serializable_data
        except Exception as ex:
            print(f"Error ExtDeserializableGeneric.json_to_obj converter: {ex}")

    @staticmethod
    def json_to_obj_v2(json_object:str, obj_type:type[T])->T:
        try:
            serializable_data = obj_type.model_validate_json(json_object)

            return serializable_data
        except Exception as ex:
            print(f"Error ExtDeserializableGeneric.json_to_obj converter: {ex}")            