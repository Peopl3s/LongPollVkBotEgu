import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
import json
import random

def answer(path):
    '''Генерирует случайный ответ (строку) из текстового файла path
    
    '''
    with open(path, "r", encoding='windows-1251') as file:
        return random.choice(list(file.read().split('\n')))
    
def parseJson(jsonFile='Res/content.json', jsonList='Res/listcontent.json'):
    '''Получает данные из json-файлов, необходимых для работы бота.

      jsonFile - json-файл, хранит acces_token и необходимый набор атрибутов
      для каждой запращиваемой команды.
      Имеет вид:
      "command":
      { 
	"owner_id":"o_id",  - id страницы хоста
	"id_content":"c_id", - id файла-контента(фото, видео, аудио, документ, ' ')
	"type":"photo", - тип контента (файла) расположенного по id_content
	"message":"Контакты" - текстовое сообщение для собеседника
      }
      
      jsonList - json-файл, хранит список возможных команд вида:
      "команда":"соответсвующее заничение команды в файле jsonFile"
      
    Оба файла необходимы для заполнения словаря,
    посредством которого реализовано распознавание команд пользователя ботом.
    
    '''
    content = {}
    try:
        jsObj = open(jsonFile, "r")
        pObj = json.load(jsObj)
    except ValueError as VErr:
        print(VErr)
    except IOError as IOErr:
        print(IOErr)
    finally:
        jsObj.close()  
    with open(jsonList, "r") as jsObj2:
        pObj2 = json.load(jsObj2)  
    for k,v in zip(pObj2.keys(),pObj2.values()):
         content[k] = pObj[v]
    return content

def getName(vk_session, uid):
    '''Получает имя собеcедника, с помощью метода VK API
    
    '''
     with vk_api.VkRequestsPool(vk_session) as pool:
         name = pool.method_one_param('users.get', key='user_id', values=(uid,))
     return name.result[uid][0]['first_name']

def main():
    '''Функция, реализующая непосредственно работу бота
    
    '''
    content = parseJson()
    session = requests.Session()
    vk_session = vk_api.VkApi(token=content['token'])
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            print('id{}: "{}"'.format(event.user_id, event.text), end=' ')
            attachments = []
            msg = ""
            if(len(event.text) > 0 and event.text in content):
                attachments.append('{}{}_{}'.format(
                                                   content[event.text]['type'],
                                                   content[event.text]['owner_id'],
                                                   content[event.text]['id_content']
                                                   ))
                msg=content[event.text]['message']
            elif (len(event.text) > 0 and event.text.lower() in list(open('Res/hello.txt', "r", encoding='windows-1251').read().split('\n'))):
                firstname = getName(vk_session, event.user_id)
                msg = answer('Res/helloansw.txt').format(firstname)
            else:
                msg = 'Ошибка. Список возможных команд: https://vk.com/id439685153?w=wall439685153_2'
            vk.messages.send(
                    user_id=event.user_id,
                    attachment=','.join(attachments),
                    message=msg 
                )
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
