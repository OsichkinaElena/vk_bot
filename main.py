import requests
from sqlalchemy import create_engine
import vk_api
from vk_api import VkUpload
from pprint import pprint
from io import BytesIO
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN_VK, TOKEN, PASSWORD


def user_search(hometown, sex, status, age_from, age_to):
    list_id = []
    token_vk = TOKEN_VK
    url = "https://api.vk.com/method/users.search"
    params = {"access_token": token_vk, 'hometown': hometown, "sex": sex, "status": status,
              "age_from": age_from, "age_to": age_to, "v": "5.131", 'fields': 'is_closed'}
    headers = {"Accept": "application/json", "Content-Type": "application/json",
               "Authorization": "OAuth {}".format(token_vk)}
    req = requests.get(url, params=params, headers=headers)
    req_ = req.json()["response"]["items"]
    for user_id in req_:
        if user_id['is_closed'] is False:
            list_id.append(user_id['id'])
    return list_id


def get_photo(owner_id):
    token_vk = TOKEN_VK
    url = "https://api.vk.com/method/photos.get"
    params = {"access_token": token_vk, "v": "5.131", "owner_id": owner_id, "album_id": 'profile',
              "count": 7, "extended": 1}
    headers = {"Accept": "application/json", "Content-Type": "application/json",
               "Authorization": "OAuth {}".format(token_vk)}
    req = requests.get(url, params=params, headers=headers)
    req_ = req.json()["response"]["items"]
    pprint(req.json())
    top_photo = {}
    for likes in req_:
        sizes_dict = {}
        url_photo = ''
        for size in likes["sizes"]:
            sizes_dict[size["type"]] = size["url"]
        if "w" in sizes_dict.keys():
            url_photo = sizes_dict["w"]
        elif "z" in sizes_dict.keys():
            url_photo = sizes_dict["z"]
        elif "y" in sizes_dict.keys():
            url_photo = sizes_dict["y"]
        elif "r" in sizes_dict.keys():
            url_photo = sizes_dict["r"]
        likes = likes['likes']['count']
        top_photo[likes] = url_photo
    top_photo = list(top_photo.items())
    top_photo = sorted(top_photo, reverse=True)
    top_photo = top_photo[:3]
    url_list = [x[1] for x in top_photo]
    return url_list


def upload_photo(url_list):
    attachments = []
    upload = VkUpload(vk)
    for url in url_list:
        img = requests.get(url).content
        f = BytesIO(img)
        upload_ph = upload.photo_messages(f)[0]
        attachments.append(f"photo{upload_ph['owner_id']}_{upload_ph['id']}")
    return attachments


def write_msg(sender, message, attachments=None):
    if attachments is None:
        vk.method('messages.send',
                  {'user_id': sender, 'message': message, 'random_id': get_random_id()})
    else:
        vk.method('messages.send', {'user_id': sender, 'message': message,  'random_id': get_random_id(),
                                    'attachment': ','.join(attachments)})


if __name__ == '__main__':
    token = TOKEN
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text.lower()
            sender = event.user_id
            if request == "найти":
                write_msg(sender, "Город, в котором ищешь пару", )
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        request = event.text.lower()
                        sender = event.user_id
                        res = vk.method('messages.getById', {'message_ids': event.message_id, 'group_id': 209802793})
                        hometown = request
                        write_msg(sender, "Кого ты ищешь: 1-жен, 2-муж", )
                        break
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        sex = int(event.text.lower())
                        write_msg(sender, "Желаемый возраст в формате: 'от-до'", )
                        break
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        res = event.text.lower()
                        age_from = int(res[:2])
                        age_to = int(res[-2:])
                        write_msg(sender, "Семейное положение: "
                                          "1 — не женат/не замужем; "
                                          "2 — есть друг / есть подруга; "
                                          "3 — помолвлен/помолвлена; "
                                          "4 — женат/замужем;"
                                          "5 — всё сложно; "
                                          "6 — в активном поиске; "
                                          "7 — влюблён/влюблена; "
                                          "8 — в гражданском браке;"
                                          "0 — не указано ")
                        break
                for event in longpoll.listen():
                    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                        status = int(event.text.lower())
                        list_id = user_search(hometown, sex, status, age_from, age_to)
                        write_msg(sender, f"Найдено {len(list_id)} результатов, для просмотра набирайте 'далее'")
                        break
            if request == "далее":
                if len(list_id) == 0:
                    write_msg(sender,
                              "Больше никого нет, если вы хотите начать новый поиск, набирайте 'найти'")
                    break
                owner_id = int(list_id[0])
                engine = create_engine(f"postgresql+psycopg2://bot_vk:{PASSWORD}@localhost:5432/bot_vk")
                cursor = engine.connect()
                k = cursor.execute(f"select user_id from users ").fetchall()
                id_list = [x[0] for x in k]
                if sender not in id_list:
                    cursor.execute(f"insert into users (user_id) values ({sender})")
                u_id = cursor.execute(f"select id from users where user_id = {sender}").fetchone()
                u_id = u_id[0]
                cursor.execute(f"insert into featured_users (user_id, id_user) values ({owner_id}, {u_id})")
                link = f'https://vk.com/id{list_id[0]}'
                url_list = get_photo(owner_id)
                attachments = upload_photo(url_list)
                write_msg(sender, link, attachments=attachments)
                list_id.pop(0)
           
