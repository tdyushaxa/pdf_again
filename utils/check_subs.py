from typing import Union
from pyrogram import Client, filters


async def check(client: Client, user_id, channel: Union[int, str]):
    try:
        await client.get_chat_member(user_id=user_id, chat_id=channel)
        return True
    except:
        return False
