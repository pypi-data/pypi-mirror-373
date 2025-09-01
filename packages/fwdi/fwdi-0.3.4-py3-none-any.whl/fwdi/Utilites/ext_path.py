import os
import shutil
import tempfile

class ExtPath():
    @staticmethod
    def get_tmp_folder():
        return tempfile.gettempdir()

    @staticmethod
    def exists_path(path:str)->bool:
        if os.path.exists(path):
            return True
        
        return False

    @staticmethod
    def remove_folder(path:str)->bool:
        try:
            shutil.rmtree(path)
            print(f'Folder and its content removed: {path}')
            return True
        except Exception as ex:
            if isinstance(ex, FileNotFoundError):
                return True
            
            print(f'Folder not deleted: {path}')
            return False

    @staticmethod
    def exists_or_create_path(path:str)->bool:
        isExist:bool = False
        if not ExtPath.exists_path(path):
           os.makedirs(path)
           isExist = True
        return isExist
    
    @staticmethod
    def get_only_path(fullname:str)->str:
        return os.path.dirname(os.path.abspath(fullname))
    
    @staticmethod
    def delete_file(fullname:str)->bool:
        try:
            if os.path.isfile(fullname):
                os.remove(fullname)
                return True
            
            return False
        except Exception as ex:
            print(ex)
            return False
    
    @staticmethod
    def folder_move(src_folder:str, dst_folder:str)->bool:
        try:
            new_path = shutil.move(src_folder, dst_folder)
            
            return True
        except Exception as ex:
            print(ex)
            return False