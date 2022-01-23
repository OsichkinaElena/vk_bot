from vk_api import VkUpload, vk_api
from config import TOKEN_VK, TOKEN
import requests
from io import BytesIO


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
    token = TOKEN
    attachments = []
    vk = vk_api.VkApi(token=token)
    upload = VkUpload(vk)
    for url in url_list:
        img = requests.get(url).content
        f = BytesIO(img)
        upload_ph = upload.photo_messages(f)[0]
        attachments.append(f"photo{upload_ph['owner_id']}_{upload_ph['id']}")
    return attachments
