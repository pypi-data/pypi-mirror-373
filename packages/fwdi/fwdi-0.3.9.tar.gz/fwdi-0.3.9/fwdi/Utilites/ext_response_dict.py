
class ExtResponseDict():
    @staticmethod
    def get_response_from_dict(lst_dict:list[dict]):
        index_data:list = []
        for item in lst_dict:
            tmp_data:list = []
            for key in item:
                tmp_data.append(item[key])
            
            index_data.append(tmp_data)
        
        return index_data
    
    @staticmethod
    def uniq_answer(lst_answer: list[dict])->list | None:
        
        if not lst_answer:
            ExtResponseDict.__log__('No relevant answer in vector base, using lsi/lda search.', 'error')
            if not lst_answer:
                return None
        try:
            uniq_answer_lst = []
            for result in lst_answer:
                for i in uniq_answer_lst:
                    if i['art_id'] == result['art_id']:
                        break
                
                else:
                    uniq_answer_lst.append(result)

            if len(uniq_answer_lst) == 1:
                return uniq_answer_lst

            return uniq_answer_lst
        except Exception as ex:
            print(ex)
            return []