import re


PATTERN = re.compile(r'\[(\S+)\|(.+)\]')


def resolve_vk_links(text):
    res = PATTERN.sub(r"<a href='https://vk.com/\1'>\2</a>", text)
    return res
