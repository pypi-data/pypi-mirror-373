import inspect


class Utilities():
    
    @staticmethod
    def get_value_by_key(lst_data:list, name_key:str):
        for item in lst_data:
            if item.name == name_key and item.default is not inspect._empty:
                return item

        return None

    @staticmethod
    def search_key(lst_param:list, key:str)->bool:
        search_item_key = [item for item in lst_param if item['name'] == key]
        if len(search_item_key) > 0:
            return True
        else:
            return False
    
    @staticmethod
    def check_key(theList:list[dict], search_key:str)->bool:
        for listItem in theList:
            if search_key == listItem.name:
                return True
        return False