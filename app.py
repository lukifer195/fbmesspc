import os
import sys
import json
import datetime
import json
import wit
from wit import Wit
import requests
from flask import Flask, request

################ Init ###########################
PAGE_ID = os.environ["PAGE_ID"]                 #
MASTER_FBID = os.environ["MASTER_FBID"]         #
ServerAccessToken = os.environ["WIT_SERVER"]    #
command_state = 0                               #
mode = ''                                       #
#################################################

app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "App running ", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    # log(data)  # you may not want to log every incoming message in production, but it's good for testing

    # data_có mess = {"object":"page", 
    #                     "entry": [{ "id": "2517603138253655", "time": 1564197467552, 
    #                                 "messaging": [{"sender": {"id": "1871904392870179"}, 
    #                                                 "recipient": {"id": "2517603138253655"}, 
    #                                 "timestamp": 1564197467228, 
    #                    =>>>         "message": {"mid": "VdjM_jwTN8tOgFBa4YfGv3g9Ir51k7s_PVp7YmkG2Th2hK8aMhoZ_T04TNxdIq1yQhxSEiUto_TrraC13Rj4rA", 
    #                                             "seq": 0,
    #                                             "text": "gi\u00fap"}}]}]}            
    # data_dilivery = {"object": "page", 
    #                 "entry": [{ "id": "2517603138253655", "time": 1564197285745, 
    #                             "messaging": [{ "sender": {"id": "1871904392870179"}, 
    #                                             "recipient": {"id": "2517603138253655"}, 
    #                             "timestamp": 1564197285730, 
    #                   =>>>      "delivery": { "seq": 0,                               # đã xem
    #                                           "mids": ["_5aZWy9Erfv8b1m_dqMs4Xg9Ir51k7s_PVp7YmkG2Tiu5DbkAW9GCfB0jVTZaH_nkwgnW6sn9oV3VxPgSlSSOQ"], 
    #                                           "watermark": 1564197284781}}]}]}                     
    

    try:
        if data["object"] == "page":

            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:

                    if messaging_event.get("message"):  # someone sent us a message

                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                        message_text = messaging_event["message"]["text"]  # the message's text
                        log("RECEIVE: {sender_id}  o>>> {recipient} [Me] :   {text}".format(sender_id=sender_id,recipient=recipient_id, text=message_text))
                        try:
                            response= get_reponse(message_text)
                        except:
                            response= '@KtrLoi'                     # k get dc câu trả lời thì k trả lời
                        send_message(recipient_id, sender_id, response)

                    if messaging_event.get("delivery"):  # delivery confirmation
                        log('Đã xem')
                    if messaging_event.get("optin"):  # optin confirmation
                        log('Đã optin')
                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        log('Đã postback')

        return "ok", 200
    except KeyError :
        pass
        

def send_message(sender_id,recipient_id, message_text):
    if message_text == '@KtrLoi' or message_text == None:
        pass
    else:
        log("SEND: {sender_id} [Me]  o>>> {recipient} :   {text}".format(sender_id=sender_id,recipient=recipient_id, text=message_text))

        params = {
            "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        }
        headers = {
            "Content-Type": "application/json"
        }
        data = json.dumps({
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": message_text
            }
        })
        # https://graph.facebook.com/v2.6/me/messages
        r = requests.post("https://graph.facebook.com/v8.0/me/messages", params=params, headers=headers, data=data)
        if r.status_code != 200:
            log(r.status_code)
            log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = str(msg).format(*args, **kwargs)
        print("<<{}>> : {}".format(datetime.datetime.now()+datetime.timedelta(hours = 7), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    except KeyError:
        pass
    except TypeError:
        pass
    sys.stdout.flush()

def get_reponse(message_text):
    """ <Hàm bao> -> chuyển hướng -> CMM -> set_mode
    ............................-> get_list_keyword ->query_reponse
    """
    print('get_reponse')
    rep = Direct_CMM_or_nor(message_text)   # Nếu vào CMM sẽ trả về "@Ktraloi" 
    if rep == '@KtrLoi':                     # kết thúc send_message ngay 
        return '@KtrLoi'
    else:                                   # Chuyển hướng vào NOR -> get list key -> query rep
        return rep


def Direct_CMM_or_nor(message_text):
    """ Hàm chuyển hướng 
    """
    print('Direct_CMM , command_state : ',command_state)

    if command_state == 1:                  # CMM
        command_mode(message_text) 
    elif command_state == 0:                # Nor
        keyword = get_list_keyword(message_text)
        rep = query_reponse(keyword)
        if rep == None:
            return "Bạn cần hỗ trợ gì k "
        else:
            return rep
################################## COMMAND MODE ###################################
def command_mode(message_text):
    """ Hàm kiểm tra mode
    """
    print('command_mode  ON , mode : ' , mode)
    if mode == "add_question":
        add_question(message_text)
    elif mode == "add_response":
        add_response(message_text)
    elif mode == "del":
        del_mode(message_text)
    elif mode == "update":
        update_mode(message_text)
    elif mode == "debug":
        list_keywords = get_list_keyword(message_text)
        debug_mode(list_keywords)
    elif mode == '' :
        set_mode(message_text)
    else: 
        print('No MODE cant setmode ')
  
def set_mode(message_text):
    """ Hàm set mode nếu mode rỗng
    """
    global mode
    global command_state
    print('set mode')
    if message_text.strip() == 'add':                
        mode = 'add_question'
        send_message(PAGE_ID,MASTER_FBID, 'Nhập câu hỏi ?')
    elif message_text.strip() == 'del':
        mode =  'del'
        print('command_state:  ' , command_state , 'mode:  ' , mode)
        send_message(PAGE_ID,MASTER_FBID, 'del câu nào ?')
    elif message_text.strip() == 'update':
        print('command_state:  ' , command_state , 'mode:  ' , mode)
        send_message(PAGE_ID,MASTER_FBID, 'update câu nào ?')
        mode =  'update'
    elif message_text.strip() == 'debug':
        print('command_state:  ' , command_state , 'mode:  ' , mode)
        send_message(PAGE_ID,MASTER_FBID, 'debug câu nào ?')
        mode =  'debug'
    elif message_text.strip() == 'exit':
        command_state = 0
        mode = ''
        print('set_command_state_off')
        send_message(PAGE_ID,MASTER_FBID, 'Command mode OFF')
    else:
        mode = ''
        print('command_state:  ' , command_state , 'mode:  ' , mode)
        send_message(PAGE_ID, MASTER_FBID , 'Command list\nadd:  Thêm câu hỏi và trả lời \ndel:  Xóa câu hỏi và trả lời \nupdate:  Update data \ndebug:  Kiểm tra bot hiểu câu hỏi của bạn ra sao\neixt:  để thoát Command Mode')


def add_question(message_text):
    global mode 
    print('add_question_mode '+ mode + '  ' + message_text)
    send_message(PAGE_ID, MASTER_FBID, 'Nhập câu trả lời')
    mode = 'add_response'
def add_response(message_text):
    global mode
    print('add_response_mode' + mode + '  '+ message_text)
    send_message(PAGE_ID, MASTER_FBID, 'Hoàn tất')
    mode = ''
def del_mode(message_text):
    global mode
    print('del_mode')
    print(message_text)
    mode = ''
    send_message(PAGE_ID, MASTER_FBID, 'Đã xóa')
def update_mode(message_text):
    global mode 
    print('update_mode')
    print(message_text)
    mode = ''
    send_message(PAGE_ID, MASTER_FBID, 'Đã update')
def debug_mode(list_keywords):
    global mode 
    print('debug_mode')
    send_message(PAGE_ID, MASTER_FBID, 'debug câu:'+ list_keywords)
    mode = ''

####################### NOR ############################
def get_list_keyword(message_text):   
    print('get_list_keyword')
    ##  gửi lên wit tìm nhận dạng
    client = Wit(ServerAccessToken)
    data = client.message(message_text)
    print(data)
    #xử lý json wit
    list_keywords = []
         # data  {  '_text':    '@cmm', 
            #       'entities'  : {'__debug__': [{'confidence': 1, 'value': '@cmm', 'type': 'value'}]},
            #       'msg_id':   '1VNu6WveQrN1pCBae'}
    for keys in tuple(data.get('entities').keys()):  #'entities': {'__debug__': [{'confidence': 1, 'value': '@cmm', 'type': 'value'}]}
        # print(keys)
        for x in data.get('entities').get(keys):     # trượt qua keys các giá trị entities :
            confi = x.get('confidence')              #                       {'confidence': 1, 'value':'menu'}
            if confi >= 0.6:
                value = x.get('value')               #                                                 'menu'
                # print(value)
                if value == '@cmm':
                    global command_state
                    command_state = 1
                    print('set_command_state_on')
                    send_message(PAGE_ID, MASTER_FBID, 'Command mode ON')
                    return "@KtrLoi"
                elif {"entity":keys,'value':value} not in list_keywords:
                    dict_entity = {"entity":keys,"value":value}                 # tạo dict {"entity":"Noun","value":"menu"}  
                    list_keywords.append(dict_entity)                           # nối vào list các dict entities
    print(list_keywords)
    return list_keywords


def query_reponse(list_keywords):
    """ Hàm tìm câu trả lời trong export.json
    """
    print('query_reponse')
    print(list_keywords)
    print('-------------------------------------------------')
    if list_keywords == "@KtrLoi" :
        return "@KtrLoi"
    else:
        with open('export.json' , 'r' ,encoding='utf-8') as f:
            export = json.load(f)
            # print(data)
            keylist = []
            for key in list_keywords:                 # trượt key trong list keys
                # print(key.values())
                Keyword = tuple(key.items())    # convert tuple cho tất cả item trong key
                keylist.append(Keyword)             
            keyset = set(keylist)   
            count = 0
            # print(keyset)
            if len(keyset) == 0:
                return "Bạn cần hỗ trợ gì ạ "
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
                        print('text :\t\t',datalist.get('text'))
                        print("KEYSET    :  ",keyset        )
                        print("ENTITY_SET:  ",entity_set    )
                        print("Độ sai lệch:    ",lendiff    )
                        return datalist.get('reponse')

            if len(keyset) >=  1:         
                for x in range(0,3):
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
                            print('text :\t\t',datalist.get('text'))
                            print("KEYSET    :  ",keyset        )
                            print("ENTITY_SET:  ",entity_set    )
                            print("Độ sai lệch:    ",lendiff   )
                            return datalist.get('reponse')


if __name__ == '__main__':
    app.run(debug=True)
