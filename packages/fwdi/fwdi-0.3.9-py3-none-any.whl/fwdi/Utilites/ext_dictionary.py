import pandas as pd

class ExtDictionary():
    @staticmethod
    def merge(x:dict, y:dict):
        z = x.copy()
        z.update(y)

        return z

    @staticmethod
    def get_select_field(data:list[dict], column:str)->list[dict]:
        lst_select_field = [item[column] for item in data]        

        return lst_select_field

    @staticmethod
    def get_select_fields(data:list[dict], columns:list[str])->list[dict]:
        df = pd.DataFrame(data)
        select_columns = df[columns]
        select_columns = select_columns.to_dict('records')

        return select_columns

    @staticmethod
    def get_concat_fields(data:list[dict], columns:list[str])->list[dict]:
        df = pd.DataFrame(data)
        df['context'] = df[columns].agg(''.join, axis=1)

        return df.to_dict('records')

    @staticmethod
    def get_intersection(lst1:list, lst2:list):
        return list(set(lst1) & set(lst2))
    
    @staticmethod
    def to_pandas(data:dict)->pd.DataFrame:
        df = pd.DataFrame([data])

        return df    