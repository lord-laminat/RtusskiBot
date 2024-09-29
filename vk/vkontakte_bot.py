from json import load
from queue import Queue
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

with open("vk/config.json", "r") as config_file:
    config: map = load(config_file)

vk_session = vk_api.VkApi(token=config["token"])
longpoll = VkBotLongPoll(vk_session, group_id=config["group_id"])
vk = vk_session.get_api()


def get_author(message_data: map) -> str:
	...


def get_attachments(message_data: map) -> list[str]:
	res = []
	for attachment in message_data["attachments"]:
		if "photo" in attachment:
			res.append(attachment["photo"]["orig_photo"]["url"])
		elif "doc" in attachment:
			res.append(attachment["doc"]["url"])
		else:
			print("WARN: Unknown attachment type.")
	return res


def get_text(message_data: map) -> str:
	return message_data["text"]


def launch(queue: Queue):
	try:
		for event in longpoll.listen():
			queue.put(( get_text(event.message), get_attachments(event.message) ))
			# print(queue.get())
	except Exception as ex:
		print(ex)


if __name__ == "__main__":
	launch(Queue())