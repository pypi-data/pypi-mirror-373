from datetime import datetime
import os

class ExtFile():
    
    @staticmethod
    def save_file(full_path_file:str, data_bytes:bytes)->bool:
        try:
            with open(full_path_file, 'wb') as f:
                f.write(data_bytes)
            return True
        except Exception as ex:
            return False

    @staticmethod
    def exists(file_path:str)->bool:
        return os.path.exists(file_path)

    @staticmethod
    def delete(file_path:str)->bool:
        try:
            if ExtFile.exists(file_path):
                os.remove(file_path)
                return True
            
            return False
        except Exception as ex:
            print(ex)
            return False
    
    @staticmethod
    def write(full_path_file:str, datas:list)->bool:
        try:
            with open(full_path_file, 'w') as f:
                for item in datas:
                    f.write(f'"{item}",\n')
                
            return True
        except Exception as ex:
            return False

    @staticmethod
    def write_text(full_path_file:str, datas:str)->bool:
        try:
            with open(full_path_file, 'w') as f:
                f.write(datas)
                
            return True
        except Exception as ex:
            return False

    @staticmethod
    def get_folder_files(folder_path:str)->list[dict]:
        lst_file:list[dict] = []
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_info = os.stat(file_path)
                    lst_file.append({'path': os.path.abspath(root), 'file_name': file, 'size': file_info.st_size, 'last_modify': datetime.fromtimestamp(file_info.st_mtime)})

            return lst_file
        except FileNotFoundError:
            print(f"Error: Folder not found at {folder_path}")
            return []