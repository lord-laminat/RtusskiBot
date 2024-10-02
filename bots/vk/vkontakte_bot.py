from json import load, dump
from queue import Queue
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from telebot.types import InputMediaPhoto, InputMediaDocument, InputMediaVideo
import requests

with open("bots/vk/config.json", "r") as config_file:
    config: map = load(config_file)

vk_session = vk_api.VkApi(token=config["token"])
longpoll = VkBotLongPoll(vk_session, group_id=config["group_id"])
vk = vk_session.get_api()


def get_attachment_url(attachment):
    match (attachment["type"]):
        case "doc":
            response = requests.get(attachment["doc"]["url"])
            if response.status_code == 200:
                return InputMediaDocument(media=response.content, caption=attachment["doc"]["title"])
        case "photo":
            return InputMediaPhoto(attachment["photo"]["orig_photo"]["url"])
        #case "video":
            #response = requests.get(
            #    "https://vk.com/video_ext.php?oid={}id={}&hd=4&autoplay=1".format(attachment["video"]["owner_id"], attachment["video"]["id"])
            #)
            #print(response.content)
            #if response.status_code == 200:
            #print("https://vk.com/video_ext.php?oid={}id={}&hd=2&autoplay=1".format(attachment["video"]["owner_id"], attachment["video"]["id"]))
            #return InputMediaVideo(media="https://vk.com/video_ext.php?oid={}id={}&hd=2&autoplay=1".format(attachment["video"]["owner_id"], attachment["video"]["id"]))


def get_attachments(message_data: map, type: str) -> list[InputMediaPhoto]:
    res = []
    with open("text.json", "w+") as file:
        dump(message_data, file)

    for attachment in message_data["attachments"]:
        if attachment["type"] == type:
            res.append(get_attachment_url(attachment))
    return res


def get_text(message_data: map) -> str:
    return message_data["text"]


def launch(tg_posts: Queue, ds_posts: Queue):
    print("Launching: VK listener")
    while True:
        try:
            for event in longpoll.listen():
                #print(event)
                post = {
					"text": get_text(event.message),
					"photo": get_attachments(event.message, "photo"),
					"doc": get_attachments(event.message, "doc"),
					"video": get_attachments(event.message, "video"),
				}
                tg_posts.put(post)
                ds_posts.put(post)

                if __name__ == "__main__":
                    ds_posts.get()
                    print(tg_posts.get())
        except requests.exceptions.ReadTimeout:...