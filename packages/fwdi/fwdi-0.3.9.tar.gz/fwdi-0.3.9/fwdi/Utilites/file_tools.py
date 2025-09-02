import hashlib
import base64

class FileTools():
    @staticmethod
    def hash_file(filename:str) -> str:
        h = hashlib.sha1()
        with open(filename,'rb') as file:
            chunk = 0
            while chunk != b'':
                chunk = file.read(1024)
                h.update(chunk)

        return h.hexdigest()
    
    @staticmethod
    def cmp_file(file1:str, file2:str) -> bool:
        h_f1 = FileTools.hash_file(file1)
        h_f2 = FileTools.hash_file(file2)

        return False if not h_f1 == h_f2 else True
    
    @staticmethod
    def encode_file_bytes_to_str(full_path_file:str) -> str:
        with open(full_path_file, 'rb') as f:
            binary_file = f.read()
        encode_binary_file = base64.standard_b64encode(binary_file).decode()
        return encode_binary_file

    @staticmethod
    def encode_bytes_to_str(data_bytes:bytes) -> str:
        encode_binary_file = base64.standard_b64encode(data_bytes).decode()
        return encode_binary_file
    
    @staticmethod
    def decode_str_to_bytes(data:str) -> bytes:
        decode_file = base64.standard_b64decode(data)
        return decode_file