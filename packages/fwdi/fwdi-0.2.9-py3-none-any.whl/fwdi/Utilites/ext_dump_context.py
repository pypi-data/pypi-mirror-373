
class ExtDumpContext():

    @staticmethod
    def dump_context(filename:str, dataset:list[dict], fields:list[str])->bool:
        try:
            with open(filename, 'a', encoding='utf-8') as fl:
                for line in dataset:
                    line_str:str = ''
                    for field in fields:
                        line_str += f"{field}:{line[field]}\n"
                    fl.write(f"{line_str}\n")

            return True
        except Exception as ex:
            print(ex)
            return False

    @staticmethod
    def dump_sentences(filename:str, dataset:list[dict])->bool:
        try:
            with open(filename, 'a', encoding='utf-8') as fl:
                for line in dataset:
                    art_id = line['art_id']
                    fl.write(f"art_id:{art_id}\n")
                    for sentence in line['sentences']:
                        fl.write(f"{sentence}\n")
                    fl.write(f"\n")

            return True
        except Exception as ex:
            print(ex)
            return False