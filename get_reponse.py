import json
from wit import Wit



def run(message_text = 'Hello world '):
    with open (r'C:\Users\Administrator\Desktop\old_mess.txt',mode = "r+", encoding="utf-8") as f:
        file = f.read()

        if file == message_text:
            return  
        else:
            with open(r'C:\Users\Administrator\Desktop\old_mess.txt',mode = "w+", encoding="utf-8") as e:
                e.write(message_text)
    
    #gửi lên wit tìm nhận dạng
    appID = "2312110155545084"
    ServerAccessToken = "STSHBSEWET4OGR3WUA5Y2UZLGB42KHVP"
    client = Wit(ServerAccessToken)
    data = client.message(message_text)

    #xử lý json wit
    list_keywords = []
    for keys in tuple(data.get('entities').keys()):
        # print(keys)
        for x in data.get('entities').get(keys):
            confi = x.get('confidence')
            if confi >= 0.5:
                value = x.get('value')
                if {"entity":keys,'value':value} not in list_keywords:
                    dict_entity={"entity":keys,"value":value}
                    list_keywords.append(dict_entity)
                # print(float(round(confi,2)) ,"\t\t\t\t" ,value)
    # print('log: ', list_keywords)
    #tìm câu trả lời trong export.json
    with open('export.json' , 'r' ,encoding='utf-8') as f:
        export = json.load(f)
    # print(data)
    keylist = []
    list_reponse = []
    for key in list_keywords:                 # trượt key trong list keys
        # print(key.values())

        Keyword = tuple(key.items())    # convert tuple cho tất cả item trong key
        keylist.append(Keyword)             
    keyset = set(keylist)   
    count = 0

    if len(keyset) == 0:
        return "Hân hạnh giải đáp thắc mắc của bạn"
    if len(keyset) == 1:
        for datalist in export.get('data'):
            entities_list = (datalist.get('entities'))
            entities_listtotup = []                                 # bắt đầu list nhận từng tuple thực thể
            for entity in entities_list:                            # 1 thực thể = 1 tupple // 1 list thực thể = 1 câu
                entities_listtotup.append(tuple(entity.items()))    # chuyển items thành tuple mới set dc 
            entity_set = set(entities_listtotup)
            # print("entities: ", entity_set)                
            diff = keyset ^ entity_set                          # ^ tìm thực thể (tuple) khác nhau giữa 2 set
            lendiff = len(diff)
            if lendiff == 0 :                                   # chạy len(diff) để tìm câu thiếu hoặc dư 1-4 thực thể
                # print("KEYSET    :  ",keyset        )
                # print("ENTITY_SET:  ",entity_set    )
                # print(datalist.get('text')          )
                # print("DIFF      :  ",diff          )
                # print("lendiff   :  ",lendiff       )
                return datalist.get('reponse')
            else:
                return "Hân hạnh giải đáp thắc mắc của bạn"
    if len(keyset) >  1:         
        for x in range(0,4):
            for datalist in export.get('data'):
                entities_list = (datalist.get('entities'))
                entities_listtotup = []                                 # bắt đầu list nhận từng tuple thực thể
                for entity in entities_list:                            # 1 thực thể = 1 tupple // 1 list thực thể = 1 câu
                    entities_listtotup.append(tuple(entity.items()))    # chuyển items thành tuple mới set dc 
                entity_set = set(entities_listtotup)
                # print("entities: ", entity_set)                
                diff = keyset ^ entity_set                          # ^ tìm thực thể (tuple) khác nhau giữa 2 set
                lendiff = len(diff)
                if lendiff == x :                                   # chạy len(diff) để tìm câu thiếu hoặc dư 1-4 thực thể
                        # print("KEYSET    :  ",keyset        )
                        # print("ENTITY_SET:  ",entity_set    )
                        # print(datalist.get('text')          )
                        # print("DIFF      :  ",diff          )
                        # print("lendiff   :  ",lendiff       )
                        return datalist.get('reponse')
                    # if datalist.get('reponse') != None:

def get_reponse(message_text):
    a= run(message_text)
    if a == None:                                               # k có reponse / hỏi trùng
        return "vâng"
    else:
        return a

aa = get_reponse(' chào')
print(aa)

