from pyrogram import Client, StopPropagation
from pyrogram_patch.middlewares.middleware_types import OnUpdateMiddleware,OnDisconnectMiddleware
from pyrogram_patch.middlewares import PatchHelper

from data.config import CHANNELS
from utils.check_subs import check


class BigBrother(OnUpdateMiddleware):
    async def __call__(self, update, client, patch_helper: PatchHelper):
        if update == 'Message':
            user = update.from_user.id
            if update.text in ['/start', '/help']:
                return
        elif update == 'CallbackQuery':
            user = update.from_user.id
            if update.data == "check_subs":
                return
        else:
            return

        result = "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:\n"
        final_status = True
        for channel in CHANNELS:
            status = await check(client, user_id=user,
                                 channel=channel)
            final_status *= status
            channel = await client.get_chat(channel)
            if not status:
                invite_link = await channel.export_invite_link()
                result += (f"👉 <a href='{invite_link}'>{channel.title}</a>\n")

        if not final_status:
            await update.reply(result, disable_web_page_preview=True)
            raise client.on_disconnect()
