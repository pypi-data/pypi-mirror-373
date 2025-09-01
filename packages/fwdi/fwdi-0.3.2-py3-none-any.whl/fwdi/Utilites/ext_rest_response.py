from pydantic import BaseModel

class ExtRestResponse():

    @staticmethod
    def make_response(message:str)->tuple[dict, int]:
        return {
            'Message':message
        }, 200

    @staticmethod
    def response_200(m_base:list[BaseModel] | BaseModel | None)->tuple[str|list[str], int]:
        if m_base == None:
            return "{'result': 'OK'}", 200
        else:
            if isinstance(m_base, list):
                lst_m_base:list[str] = [model.model_dump_json() for model in m_base]
                return lst_m_base, 200
            else:
                return m_base.model_dump_json(), 200
    
    @staticmethod
    def abort_400(error:str)->tuple[dict, int]:
        return {
            'result': error if error else 'error'
        }, 400
    
    @staticmethod
    def make_error_response(error:str)->tuple[str, int]:
        return error, 404
    
    @staticmethod
    def make_error(error:str, code:int):
        return error, code
    
    @staticmethod
    def make_response_200(text:str, key:str|None = None)->tuple[dict, int]:
        if key == None:
            return {'Message': text}, 200
        else:
            return {
                key: text
            }, 200