
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import TOKEN


def write_msg(sender, message, attachments=None):
    token = TOKEN
    vk = vk_api.VkApi(token=token)
    if attachments is None:
        vk.method('messages.send', {'user_id': sender, 'message': message, 'random_id': get_random_id()})
    else:
        vk.method('messages.send', {'user_id': sender, 'message': message,  'random_id': get_random_id(),
                                    'attachment': ','.join(attachments)})


def view_event(text):
    token = TOKEN
    vk = vk_api.VkApi(token=token)
    longpoll = VkLongPoll(vk)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text.lower()
            sender = event.user_id
            write_msg(sender, f"{text}", )
            return request
