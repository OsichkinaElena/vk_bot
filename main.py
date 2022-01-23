
import data_base
import vk_api
import bot
import api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import TOKEN


if __name__ == '__main__':
    token = TOKEN
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text.lower()
            sender = event.user_id
            if request == "найти":
                bot.write_msg(sender, "Город, в котором ищешь пару", )
                hometown = bot.view_event("Кого ты ищешь: 1-жен, 2-муж")
                sex = int(bot.view_event("Желаемый возраст в формате: 'от-до'"))
                res = bot.view_event("Семейное положение: "
                                          "1 — не женат/не замужем; "
                                          "2 — есть друг / есть подруга; "
                                          "3 — помолвлен/помолвлена; "
                                          "4 — женат/замужем;"
                                          "5 — всё сложно; "
                                          "6 — в активном поиске; "
                                          "7 — влюблён/влюблена; "
                                          "8 — в гражданском браке;"
                                          "0 — не указано ")
                age_from = int(res[:2])
                age_to = int(res[-2:])
                status = int(bot.view_event("Для просмотра набирайте 'далее'"))
                list_id = api.user_search(hometown, sex, status, age_from, age_to)
            if request == "далее":
                if len(list_id) == 0:
                    bot.write_msg(sender,
                              "Больше никого нет, если вы хотите начать новый поиск, набирайте 'найти'")
                    break
                owner_id = int(list_id[0])
                id_list = data_base.get_id_list()
                if sender not in id_list:
                    data_base.insert_db('users', 'user_id', sender)
                u_id = data_base.get_user_id(sender)
                data_base.insert_db('featured_users', column='user_id, id_user', values=f'{owner_id}, {u_id}')
                link = f'https://vk.com/id{list_id[0]}'
                url_list = api.get_photo(owner_id)
                attachments = api.upload_photo(url_list)
                bot.write_msg(sender, link, attachments=attachments)
                list_id.pop(0)
           
