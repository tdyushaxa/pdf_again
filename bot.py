import gettext
import os

from pikepdf import PdfImage, Pdf
import time
from pyrogram import Client, filters, types
from pyrogram.types import CallbackQuery, ReplyKeyboardRemove
from data.config import API_HASH, BOT_TOKEN, API_ID, CHANNELS
from data.sqlite import Database
from keyboards.default.default_keyboard import adminpanelbtn, agree, cencelbtn, back_button, get_pdf, convertor_btn, \
    get_text_key, ex_pdf_conv, convert_word, get_images_key, convertor, image_text_lang_btn
from keyboards.inline.inline_keyboard import change_lang, keyboard_admin_obuna, typepost, check_button_subs
from data.config import ADMINS
from miidleware.channel_middleware import BigBrother
from states.admin_state import Reklam_State, Matn_state, FeedbackTo, KanalOlish, KanalQoshish
from pyrogram_patch import patch
from pyrogram_patch.fsm.storages import MemoryStorage
from pyrogram_patch.fsm import State
from pyrogram_patch.fsm.filter import StateFilter
from PIL import Image
from states.file_state import ImageTopdf, ImageTotext, Excel_to_pdf_state, FileStateWord, ImageToGet_text, FileState
from utils.check_subs import check
from utils.excel_to_pdf import excel_to_pdf
from utils.filters import data_filter_lang, filter_text_lang
from utils.imageget_text import image_to_text_async
from utils.pdf_to_word import submit_pdf_conversion_task, get_conversion_task_status, download_result
from utils.word_to_pdf import convert_to

app = Client("pdfconvertor", api_hash=API_HASH, bot_token=BOT_TOKEN, api_id=API_ID)
patch_manager = patch(app)
patch_manager.set_storage(MemoryStorage())
patch_manager.include_middleware(BigBrother())

commands = [
    ('start', 'Start bot'),
    ('setlang', 'Set lenguage'),
]

try:
    db = Database(path_to_db="data/main.db")
    db.create_table_users()
    db.create_table_active_users()

except:
    pass
with app:
    app.set_bot_commands(
        [
            types.BotCommand('start', 'Start bot'),
            types.BotCommand('setlang', 'Set lenguage'),

        ]
    )

DEFAULT_LANGUAGE = "en"


def get_text(language, message_key):
    localedir = 'locales'
    translation = gettext.translation("messages", localedir=localedir, languages=[language], fallback=True)
    translation.install()
    return translation.gettext(message_key)


@app.on_message(filters.command("start"))
async def start(client: patch_manager.client, message: types.Message):
    id = message.chat.id
    global fullname
    if message.chat.last_name:
        fullname = f"{message.from_user.first_name} {message.from_user.last_name}"
    fullname = f"{message.from_user.first_name}"
    try:
        db.add_user(id=id, name=fullname)
        db.add_active_user(id=id, name=fullname)
    except:
        pass
    channels_format = str()
    for channel in CHANNELS:
        chat = await client.get_chat(channel)
        invite_link = await chat.export_invite_link()
        channels_format += f"👉 <a href='{invite_link}'>{chat.title}</a>\n"
    user_lang = db.select_user(id=id)[-1]
    if user_lang:
        message_text = get_text(user_lang, 'channel_membership')
        await message.reply(f"{message_text}\n"
                            f"{channels_format}",
                            reply_markup=check_button_subs,
                            disable_web_page_preview=True)
    else:
        message_text = get_text(DEFAULT_LANGUAGE, 'channel_membership')
        await message.reply(f"{message_text}\n"
                            f"{channels_format}",
                            reply_markup=check_button_subs,
                            disable_web_page_preview=True)
    # user_lang = db.select_user(id=id)[-1]
    # if user_lang:
    #     text = get_text(user_lang, "hello")
    #     await client.send_message(message.chat.id, f"{text} <b>{fullname.title()}</b> !!!", reply_markup=convertor_btn)
    # else:
    #     text = get_text(DEFAULT_LANGUAGE, "hello")
    #     await client.send_message(message.chat.id, f"{text} <b>{fullname.title()}</b> !!!", reply_markup=convertor_btn)


@app.on_callback_query(filters.regex("check_subs"))
async def checker(client: patch_manager.client, call: types.CallbackQuery):
    await call.answer()
    user_lang = db.select_user(id=call.from_user.id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=call.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
            if status:
                await call.message.reply(result, reply_markup=convertor_btn, disable_web_page_preview=True)
            else:
                await call.message.reply(result, disable_web_page_preview=True)
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
            if status:
                await call.message.reply(result, reply_markup=convertor_btn, disable_web_page_preview=True)
            else:
                await call.message.reply(result, disable_web_page_preview=True)


@app.on_message(filters.command('setlang'))
async def set_lang(client: Client, msg: types.Message):
    user_lang = db.select_user(id=msg.chat.id)[-1]
    global message_id
    if user_lang:
        text = get_text(user_lang, "choose")
        message_id = await client.send_message(chat_id=msg.chat.id, text=text, reply_markup=change_lang)
    else:
        text = get_text(DEFAULT_LANGUAGE, "choose")
        message_id = await msg.reply(text, reply_markup=change_lang)


@app.on_callback_query(data_filter_lang)
async def lang(client: Client, call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data
    db.update_user_langugae(id=user_id, language=data)
    user_lang = db.select_user(id=user_id)[-1]
    if user_lang:
        change = get_text(user_lang, 'change_lang')
        text = get_text(user_lang, "choose")
        await call.answer(change, cache_time=60)
        await client.edit_message_text(chat_id=call.from_user.id, message_id=message_id.id, text=text,
                                       reply_markup=change_lang)
    else:
        change = get_text(DEFAULT_LANGUAGE, 'change_lang')
        await call.answer(change, cache_time=60)
        text = get_text(DEFAULT_LANGUAGE, "choose")
        await client.edit_message_text(chat_id=call.from_user.id, message_id=message_id.id, text=text,
                                       reply_markup=change_lang)


@app.on_message(filters.regex('Image ➡️ Pdf'))
async def bot_start_img_to_pdf(client: patch_manager.client, message: types.Message, state: State):
    user_id = message.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=message.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} /a>\n\n")
        if status:
            if user_lang:
                rasm_text = get_text(user_lang, 'image_pdf')
                await client.send_message(user_id, rasm_text, reply_markup=ReplyKeyboardRemove())
                rasm_state = get_text(user_lang, 'recive__pic_state')
                await client.send_message(user_id, text=rasm_state, reply_markup=back_button)
                await state.set_state(ImageTopdf.image)
                time.sleep(2)
            else:
                rasm_text = get_text(DEFAULT_LANGUAGE, 'image_pdf')
                await message.reply(rasm_text, reply_markup=ReplyKeyboardRemove())
                rasm_state = get_text(DEFAULT_LANGUAGE, 'recive__pic_state')
                await message.reply(text=rasm_state, reply_markup=back_button)
                await state.set_state(ImageTopdf.image)
                time.sleep(2)
        else:
            await message.reply(result, disable_web_page_preview=True)


@app.on_message(filters.photo & StateFilter(ImageTopdf.image))
async def get_photo(client: Client, msg: types.Message, state: State):
    global photo_name1
    photo_name1 = msg.chat.id
    time.sleep(5)
    await client.download_media(message=msg, file_name=f'{photo_name1}.png')
    await state.finish()
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    if user_lang:
        rasm_agree = get_text(user_lang, 'recive_pic_agree')
        await msg.reply(rasm_agree, reply_markup=get_pdf)
    else:
        rasm_agree = get_text(user_lang, 'recive_pic_agree')
        await msg.reply(rasm_agree, reply_markup=get_pdf)


@app.on_message(filters.regex('📃 PDFga aylantirish!'))
async def convert_to_text(client: Client, msg: types.Message):
    photo_names = f'{photo_name1}.pdf'
    try:
        img = Image.open(f'downloads/{photo_name1}.png')
        save = img.convert('RGB')
        save.save(photo_names)
        time.sleep(1)
        with open(photo_names, 'rb') as file:
            await msg.reply_document(document=file, caption=photo_names, reply_markup=convertor_btn)
            time.sleep(1)
    except:
        user_id = msg.chat.id
        user_lang = db.select_user(id=user_id)[-1]
        if user_lang:
            quality_pic = get_text(user_lang, 'recive_pic_agree')
            await msg.reply(quality_pic, reply_markup=ReplyKeyboardRemove())
            come_back = get_text(user_lang, 'back')
            await msg.reply(text=come_back, reply_markup=back_button)
        else:
            quality_pic = get_text(DEFAULT_LANGUAGE, 'recive_pic_agree')
            await msg.reply(quality_pic, reply_markup=ReplyKeyboardRemove())
            come_back = get_text(DEFAULT_LANGUAGE, 'back')
            await msg.reply(text=come_back, reply_markup=back_button)
    try:
        os.remove(photo_names)
        os.remove(f'{photo_name1}.png')
    except:
        pass


@app.on_message(filters.regex('Image  ➡️ text'))
async def get_photo_text(client: Client, message: types.Message, state: State):
    user_id = message.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=message.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} /a>\n\n")
        if status:
            if user_lang:
                image_text = get_text(user_lang, 'pic_get_text_state')
                await message.reply(image_text, reply_markup=ReplyKeyboardRemove())
                send_pic_text = get_text(user_lang, 'send_pic')
                await message.reply(send_pic_text, reply_markup=back_button)
                time.sleep(1)
                await state.set_state(ImageTotext.image)
            else:
                image_text = get_text(user_lang, 'pic_get_text_state')
                await message.reply(image_text, reply_markup=ReplyKeyboardRemove())
                send_pic_text = get_text(user_lang, 'send_pic')
                await message.reply(send_pic_text, reply_markup=back_button)
                time.sleep(1)
                await state.set_state(ImageTotext.image)
        else:
            await message.reply(result, disable_web_page_preview=True)


@app.on_message(filters.photo & StateFilter(ImageTotext.image))
async def get_photo(client: Client, msg: types.Message, state: State):
    global photo_name
    photo_name = msg.chat.id
    photo_file_id = msg
    await client.download_media(message=msg, file_name=f'{photo_name}.png')
    time.sleep(1)
    user_lang = db.select_user(id=msg.chat.id)[-1]
    if user_lang:
        pic_agreec = get_text(user_lang, 'recive_pic_agree')
        await msg.reply(pic_agreec)
    else:
        pic_agreec = get_text(DEFAULT_LANGUAGE, 'recive_pic_agree')
        await msg.reply(pic_agreec)
    await state.set_state(ImageTotext.language)
    if user_lang:
        text = get_text(user_lang, "choose")
        await client.send_message(chat_id=msg.chat.id, text=text, reply_markup=image_text_lang_btn)
    else:
        text = get_text(DEFAULT_LANGUAGE, "choose")
        await msg.reply(text, reply_markup=image_text_lang_btn)


@app.on_message(filter_text_lang & StateFilter(ImageTotext.language))
async def get_photo(client: Client, msg: types.Message, state: State):
    language = msg.text
    await state.set_data({
        'language': language
    })
    user_lang = db.select_user(id=msg.chat.id)[-1]
    if user_lang:
        change = get_text(user_lang, 'change_lang')
        await msg.reply(change, reply_markup=get_text_key)
    else:
        change_lang = get_text(DEFAULT_LANGUAGE, 'change_lang')
        await msg.reply(change_lang, reply_markup=get_text_key)


@app.on_message(filters.regex('📝 Textga aylantirish!') & StateFilter(ImageTotext.language))
async def convert_to_text(client: Client, msg: types.Message, state: State):
    data = await state.get_data()
    lang = data.get('language')

    try:
        text = await image_to_text_async(path=f'downloads/{photo_name}.png', lang=lang)
        time.sleep(1)
        await msg.reply(text, reply_markup=convertor_btn)

        if photo_name:
            os.remove(f'downloads/{photo_name}.png')
    except:
        user_lang = db.select_user(id=msg.chat.id)[-1]
        if user_lang:
            quality_picture_text = get_text(user_lang, 'quality_pic_check')
            await msg.reply(quality_picture_text, reply_markup=ReplyKeyboardRemove())
            back = get_text(user_lang, 'back')
            await msg.reply(text=back, reply_markup=back_button)
        else:
            quality_picture_text = get_text(DEFAULT_LANGUAGE, 'quality_pic_check')
            await msg.reply(quality_picture_text, reply_markup=ReplyKeyboardRemove())
            back = get_text(DEFAULT_LANGUAGE, 'back')
            await msg.reply(text=back, reply_markup=back_button)
        try:
            os.remove(f'downloads/{photo_name}.png')
        except:
            pass
    await state.finish()


@app.on_message(filters.regex('Excel ➡️ PDF'))
async def excel_to(client: Client, message: types.Message, state: State):
    user_id = message.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=message.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} /a>\n\n")
        if status:
            if user_lang:
                excel_text = get_text(user_lang, 'excel_file')
                await message.reply(excel_text, reply_markup=ReplyKeyboardRemove())
                excel_state = get_text(user_lang, 'recive_excel_state')
                await message.reply(text=excel_state, reply_markup=back_button
                                    )
                time.sleep(1)
                await state.set_state(Excel_to_pdf_state.file)
            else:
                excel_text = get_text(DEFAULT_LANGUAGE, 'excel_file')
                await message.reply(excel_text, reply_markup=ReplyKeyboardRemove())
                excel_state = get_text(DEFAULT_LANGUAGE, 'recive_excel_state')
                await message.reply(text=excel_state, reply_markup=back_button
                                    )
                time.sleep(1)
                await state.set_state(Excel_to_pdf_state.file)
        else:
            await message.reply(result, disable_web_page_preview=True)


@app.on_message(filters.document & StateFilter(Excel_to_pdf_state.file))
async def get_data_file(client: Client, msg: types.Message, state: State):
    global file_name_5
    file_name = msg.document.file_name
    file_name_5 = file_name.split('.')[0]
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):

        time.sleep(5)
        await client.download_media(message=msg, file_name=f'{msg.from_user.id}.xlsx')
        if user_lang:
            excel_agree = get_text(user_lang, 'recive_excel_agree')
            await msg.reply(excel_agree, reply_markup=ex_pdf_conv)
        else:
            excel_agree = get_text(DEFAULT_LANGUAGE, 'recive_excel_agree')
            await msg.reply(excel_agree, reply_markup=ex_pdf_conv)
        await state.finish()
    else:
        if user_lang:
            excel_errors = get_text(user_lang, 'excel_errors')
            await msg.reply(excel_errors, reply_markup=back_button)
            excel_state_again = get_text(user_lang, 'again_recive_excel_state')
            await msg.reply(excel_state_again)
            await state.set_state(Excel_to_pdf_state.file)
        else:
            pass


@app.on_message(filters.regex('Converor Pdf'))
async def converter_to_pdf_file(client: Client, msg: types.Message):
    excel_file = f'downloads/{msg.from_user.id}.xlsx'
    pdf_file = f'downloads/{msg.from_user.id}.pdf'
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    try:
        output = excel_to_pdf(excel_file, pdf_file)
        with open(pdf_file, 'rb') as file:
            time.sleep(3)
            await msg.reply_document(document=file, caption=file_name_5, reply_markup=ReplyKeyboardRemove())
    except:
        if user_lang:
            excel_file_error = get_text(user_lang, 'excel_file_errors')
            await msg.reply(excel_file_error, reply_markup=convertor_btn)
        else:
            excel_file_error = get_text(DEFAULT_LANGUAGE, 'excel_file_errors')
            await msg.reply(excel_file_error, reply_markup=convertor_btn)
    try:
        os.remove(excel_file)
        os.remove(pdf_file)
    except:
        pass


@app.on_message(filters.regex('Word ➡️ PDF'))
async def bot_start(client: Client, message: types.Message, state: State):
    user_id = message.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=message.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} /a>\n\n")
        if status:
            if user_lang:
                word_text = get_text(user_lang, 'word_file')
                await message.reply(word_text, reply_markup=ReplyKeyboardRemove())
                word_text_state = get_text(user_lang, 'word_file_recive_state')
                await message.reply(text=word_text_state, reply_markup=back_button)
                await state.set_state(FileStateWord.file)
                time.sleep(1)
            else:
                word_text = get_text(DEFAULT_LANGUAGE, 'word_file')
                await message.reply(word_text, reply_markup=ReplyKeyboardRemove())
                word_text_state = get_text(DEFAULT_LANGUAGE, 'word_file_recive_state')
                await message.reply(text=word_text_state, reply_markup=back_button)
                await state.set_state(FileStateWord.file)
                time.sleep(1)
        else:
            await message.reply(result, disable_web_page_preview=True)


@app.on_message(filters.document & StateFilter(FileStateWord.file))
async def set_data_word(client: Client, msg: types.Message, state: State):
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    global file_name_2
    file_name = msg.document.file_name
    file_name_2 = file_name.split('.doc')[0]
    if file_name.endswith('.doc') or file_name.endswith('docx'):
        file_id = msg.document.file_id
        await client.download_media(message=msg, file_name=f'{msg.from_user.id}.docx')
        if user_lang:
            word_file_recive_agree = get_text(user_lang, 'word_file_recive_agree')
            await msg.reply(word_file_recive_agree, reply_markup=convert_word)
            await state.finish()
            time.sleep(1)
        else:
            word_file_recive_agree = get_text(DEFAULT_LANGUAGE, 'word_file_recive_agree')
            await msg.reply(word_file_recive_agree, reply_markup=convert_word)
            await state.finish()
            time.sleep(1)
    else:
        if user_lang:
            word_file_errors = get_text(user_lang, 'word_file_errors')
            await msg.reply(word_file_errors, reply_markup=back_button)
            word_file_again = get_text(user_lang, 'word_file_again')
            await msg.reply(word_file_again)
        else:
            word_file_errors = get_text(DEFAULT_LANGUAGE, 'word_file_errors')
            await msg.reply(word_file_errors, reply_markup=back_button)
            word_file_again = get_text(DEFAULT_LANGUAGE, 'word_file_again')
            await msg.reply(word_file_again)


@app.on_message(filters.regex('Convertor PDF'))
async def converter_to_word(client: Client, msg: types.Message):
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    try:
        if user_lang:
            word_file_change = get_text(user_lang, 'word_file_change')
            await msg.reply(word_file_change)
            file_path = f'downloads/{msg.from_user.id}.docx'
            await convert_to('downloads', file_path, timeout=15)
            time.sleep(1)
            pdf_file = f'downloads/{msg.from_user.id}.pdf'
            with open(pdf_file, 'rb') as file:
                await msg.reply_document(document=file, caption=file_name_2, reply_markup=ReplyKeyboardRemove())
                word_file_changed = get_text(user_lang, 'word_file_changed')
                await msg.reply(word_file_changed, reply_markup=convertor_btn)
                time.sleep(1)
        else:
            word_file_change = get_text(DEFAULT_LANGUAGE, 'word_file_change')
            await msg.reply(word_file_change)
            file_path = f'downloads/{msg.from_user.id}.docx'
            await convert_to('downloads', file_path, timeout=15)
            time.sleep(1)
            pdf_file = f'downloads/{msg.from_user.id}.pdf'
            with open(pdf_file, 'rb') as file:
                await msg.reply_document(document=file, caption=file_name_2, reply_markup=ReplyKeyboardRemove())
                word_file_changed = get_text(DEFAULT_LANGUAGE, 'word_file_changed')
                await msg.reply(word_file_changed, reply_markup=convertor_btn)
                time.sleep(1)
        os.remove(file_path)
        os.remove(pdf_file)
    except:
        if user_lang:
            word_file_errors_file = get_text(user_lang, 'word_file_errors_file')
            await msg.reply(word_file_errors_file, reply_markup=convertor_btn)
        else:
            word_file_errors_file = get_text(DEFAULT_LANGUAGE, 'word_file_errors_file')
            await msg.reply(word_file_errors_file, reply_markup=convertor_btn)


@app.on_message(filters.regex('PDF ➡️ Get image'))
async def get_images(client: Client, msg: types.Message, state: State):
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=msg.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        if status:
            if user_lang:
                pdf_get_image = get_text(user_lang, 'pdf_get_image')
                await state.set_state(ImageToGet_text.file)
                await msg.reply(pdf_get_image)
                pdf_get_image_state = get_text(user_lang, 'pdf_get_image_state')
                await msg.reply(text=pdf_get_image_state, reply_markup=back_button)
                time.sleep(2)
            else:
                pdf_get_image = get_text(DEFAULT_LANGUAGE, 'pdf_get_image')
                await state.set_state(ImageToGet_text.file)
                await msg.reply(pdf_get_image)
                pdf_get_image_state = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_state')
                await msg.reply(text=pdf_get_image_state, reply_markup=back_button)
                time.sleep(2)
        else:
            await msg.reply(result, disable_web_page_preview=True)


@app.on_message(filters.document & StateFilter(ImageToGet_text.file))
async def set_images(client: Client, msg: types.Message, state: State):
    file_name = msg.document.file_name
    file_name_3 = file_name.split('.pdf')[0]
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    try:
        if file_name.endswith('.pdf'):
            file_id = msg.document.file_id
            time.sleep(3)
            await client.download_media(message=msg, file_name=f'{msg.from_user.id}.pdf')
            if user_lang:
                pdf_get_image_recieve = get_text(user_lang, 'pdf_get_image_recieve')
                await msg.reply(pdf_get_image_recieve, reply_markup=get_images_key)
            else:
                pdf_get_image_recieve = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_recieve')
                await msg.reply(pdf_get_image_recieve, reply_markup=get_images_key)

            await state.finish()
        else:
            if user_lang:
                pdf_get_image_errors = get_text(user_lang, 'pdf_get_image_errors')
                await msg.reply(pdf_get_image_errors, reply_markup=back_button)
                pdf_get_image_again_state = get_text(user_lang, 'pdf_get_image_again_state')
                await msg.reply(pdf_get_image_again_state)
            else:
                pdf_get_image_errors = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_errors')
                await msg.reply(pdf_get_image_errors, reply_markup=back_button)
                pdf_get_image_again_state = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_again_state')
                await msg.reply(pdf_get_image_again_state)

    except:
        if user_lang:
            pdf_get_image_file_errors = get_text(user_lang, 'pdf_get_image_file_errors')
            await msg.reply(pdf_get_image_file_errors, reply_markup=ReplyKeyboardRemove())
            back = get_text(user_lang, 'back')
            await msg.reply(text=back, reply_markup=back_button)
        else:
            pdf_get_image_file_errors = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_file_errors')
            await msg.reply(pdf_get_image_file_errors, reply_markup=ReplyKeyboardRemove())
            back = get_text(DEFAULT_LANGUAGE, 'back')
            await msg.reply(text=back, reply_markup=back_button)


@app.on_message(filters.regex('Get Image'))
async def converter_get_image(client: Client, msg: types.Message):
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    if user_lang:
        pdf_get_image_file_sending = get_text(user_lang, 'pdf_get_image_file_sending')
        await msg.reply(pdf_get_image_file_sending)
    else:
        pdf_get_image_file_sending = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_file_sending')
        await msg.reply(pdf_get_image_file_sending)
    file_path = f'downloads/{msg.from_user.id}.pdf'
    try:
        pdf_page = Pdf.open(file_path)
        for page in pdf_page.pages:
            for image in page.images.keys():
                raw_image = page.images[image]
                pdf_image = PdfImage(raw_image)
                time.sleep(3)
                pdf_get_image = pdf_image.extract_to(fileprefix=f"{msg.chat.id}")
                with open(f'{msg.chat.id}.jpg', 'rb') as file:
                    await msg.reply_photo(file, caption=pdf_page.filename, reply_markup=ReplyKeyboardRemove())
        if user_lang:
            pdf_get_image_file_send = get_text(user_lang, 'pdf_get_image_file_send')
            await msg.reply_photo(pdf_get_image_file_send, reply_markup=convertor_btn)
        else:
            pdf_get_image_file_send = get_text(DEFAULT_LANGUAGE, 'pdf_get_image_file_send')
            await msg.reply_photo(pdf_get_image_file_send, reply_markup=convertor_btn)
    except:
        if user_lang:
            pdf_get_image_files_errors = get_text(user_lang, 'pdf_get_image_files_errors')
            await msg.reply(pdf_get_image_files_errors, reply_markup=ReplyKeyboardRemove())
            back = get_text(user_lang, 'back')
            await msg.reply(text=back, reply_markup=back_button)
    else:
        pass
    try:
        os.remove(file_path)
        os.remove(f"{msg.chat.id}.jpg")
        os.remove(f"{msg.chat.id}.png")
    except:
        pass


@app.on_message(filters.regex('PDF ➡️ Word'))
async def bot_start(client: Client, message: types.Message, state: State):
    user_id = message.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    result = str()
    for channel in CHANNELS:
        status = await check(client, user_id=message.from_user.id,
                             channel=channel)
        channel = await app.get_chat(channel)
        if user_lang:
            chnalel_member_enter = get_text(user_lang, 'channel_membership')
            membership = get_text(user_lang, 'membership')
            membership_close = get_text(user_lang, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} </a>\n\n")
        else:
            chnalel_member_enter = get_text(DEFAULT_LANGUAGE, 'channel_membership')
            membership = get_text(DEFAULT_LANGUAGE, 'membership')
            membership_close = get_text(DEFAULT_LANGUAGE, 'membership_close')
            if status:
                result += f"<b>{channel.title}</b> {chnalel_member_enter}!\n\n"
            else:
                invite_link = await channel.export_invite_link()
                result += (f"<b>{channel.title}</b> {membership_close} "
                           f"<a href='{invite_link}'>{membership} /a>\n\n")
        if status:
            if user_lang:
                pdf_file = get_text(user_lang, 'pdf_file')
                await message.reply(pdf_file, reply_markup=ReplyKeyboardRemove())
                pdf_file_state = get_text(user_lang, 'pdf_file_state')
                await message.reply(text=pdf_file_state, reply_markup=back_button
                                    )
            else:
                pdf_file = get_text(user_lang, 'pdf_file')
                await message.reply(pdf_file, reply_markup=ReplyKeyboardRemove())
                pdf_file_state = get_text(DEFAULT_LANGUAGE, 'pdf_file_state')
                await message.reply(text=pdf_file_state, reply_markup=back_button)

            await state.set_state(FileState.file)
            time.sleep(2)
        else:
            await message.reply(result, disable_web_page_preview=True)


@app.on_message(filters.document & StateFilter(FileState.file))
async def set_data(client: Client, msg: types.Message, state: State):
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    global file_name_1
    file_name = msg.document.file_name
    file_name_1 = file_name.split('.pdf')[0]
    if file_name.endswith('.pdf'):
        fil_id = msg.document.file_id
        await client.download_media(message=msg, file_name=f'{msg.from_user.id}.pdf')
        if user_lang:
            pdf_file_agree = get_text(user_lang, 'pdf_file_agree')
            await msg.reply(pdf_file_agree, reply_markup=convertor)

        else:
            pdf_file_agree = get_text(DEFAULT_LANGUAGE, 'pdf_file_agree')
            await msg.reply(pdf_file_agree, reply_markup=convertor)
        await state.finish()
        time.sleep(3)
    else:
        if user_lang:
            pdf_files_errors = get_text(user_lang, 'pdf_files_errors')
            await msg.reply(pdf_files_errors, reply_markup=back_button)
            pdf_file_state_again = get_text(user_lang, 'pdf_file_state_again')
            await msg.reply(pdf_file_state_again)
        else:
            pdf_files_errors = get_text(DEFAULT_LANGUAGE, 'pdf_files_errors')
            await msg.reply(pdf_files_errors, reply_markup=back_button)
            pdf_file_state_again = get_text(DEFAULT_LANGUAGE, 'pdf_file_state_again')
            await msg.reply(pdf_file_state_again)


@app.on_message(filters.regex('️️️️️️️️️️️Convertor'))
async def converter_to_word(client: Client, msg: types.Message):
    user_id = msg.chat.id
    user_lang = db.select_user(id=user_id)[-1]
    file_path = f'downloads/{msg.from_user.id}.pdf'
    rapid_api_key = "d7a9295da7msh823ef302ae4316ep1ffd78jsnb470f2bd6e94"
    try:
        docx_file = f'{file_name_1}.docx'
        task_id = await submit_pdf_conversion_task(file_path, rapid_api_key)
        status = await get_conversion_task_status(task_id, rapid_api_key)
        retry_count = 0
        if user_lang:
            pdf_file_changing = get_text(user_lang, 'pdf_file_changing')
            change_msg = await msg.reply(pdf_file_changing)
            pdf_file_changing_wait = get_text(user_lang, 'pdf_file_changing_wait')
            wait = await msg.reply(pdf_file_changing_wait)
        else:
            pdf_file_changing = get_text(DEFAULT_LANGUAGE, 'pdf_file_changing')
            change_msg = await msg.reply(pdf_file_changing)
            pdf_file_changing_wait = get_text(DEFAULT_LANGUAGE, 'pdf_file_changing_wait')
            wait = await msg.reply(pdf_file_changing_wait)
        while retry_count < 100:
            retry_count += 1
            time.sleep(5)
            status = await get_conversion_task_status(task_id, rapid_api_key)
            if status == 'Completed':
                file_bytes = await download_result(task_id, rapid_api_key)
                with open(docx_file, mode='wb') as binary_pdf:
                    binary_pdf.write(file_bytes)
                break
            elif status == 'Waiting':
                continue
            elif status == 'Failed':
                raise Exception('Cannot convert file')
            else:
                raise Exception('Invalid status')
        await msg.reply_document(document=docx_file, reply_markup=ReplyKeyboardRemove())
        await client.delete_messages(chat_id=msg.chat.id, message_ids=wait.id)
        if user_lang:
            pdf_file_changed = get_text(user_lang, 'pdf_file_changed')
            await client.edit_message_text(chat_id=msg.chat.id, message_id=change_msg.id, text=pdf_file_changed)
        else:
            pdf_file_changed = get_text(DEFAULT_LANGUAGE, 'pdf_file_changed')
            await client.edit_message_text(chat_id=msg.chat.id, message_id=change_msg.id, text=pdf_file_changed)

        os.remove(docx_file)
    except:
        if user_lang:
            pdf_file_change_error = get_text(user_lang, 'pdf_file_change_error')
            await msg.reply(pdf_file_change_error, reply_markup=convertor_btn)
        else:
            pdf_file_change_error = get_text(DEFAULT_LANGUAGE, 'pdf_file_change_error')
            await msg.reply(pdf_file_change_error, reply_markup=convertor_btn)
        os.remove(file_path)


sendfeedback = []
ADMINS = [int(x) for x in ADMINS]


@app.on_message(filters.command('admin'))
async def adminpanel(client: Client, message: types.Message):
    if message.chat.id in ADMINS:
        await message.reply("<b>Admin panel</b>", reply_markup=adminpanelbtn)


@app.on_message(filters.command("admins"))
async def adminlar(clinet: Client, message: types.Message):
    if message.chat.id == ADMINS[0]:
        await message.reply(f"{ADMINS}")


@app.on_message(filters.command("addadmin"))
async def adminadd(client: Client, message: types.Message):
    if message.chat.id in ADMINS:
        newadmin = message.text
        ADMINS.append(int(newadmin))
        await message.reply("Admin qo'shildi!")


@app.on_message(filters.command("removeadmin"))
async def adminadd(client: Client, message: types.Message):
    if message.chat.id in ADMINS:
        radmin = message.text
        try:
            ADMINS.remove(int(radmin))
            await message.reply("Admin olib tashlandi!")
        except:
            await message.reply(f"{radmin} adminlar ro'yxatida yo'q!")


@app.on_message(filters.regex("📊 Statistika"))
async def adminpanel(client: Client, message: types.Message):
    count = db.count_users()[0]
    if message.chat.id in ADMINS:
        await message.reply(f"👥 <b>Bot obunachilari:</b> {count}")


@app.on_message(filters.regex("📤 Tarqatish"))
async def totarqatish(client: Client, message: types.Message):
    if message.chat.id in ADMINS:
        await message.reply("Tanlang:", reply_markup=typepost)


@app.on_callback_query(filters.regex('photo') & StateFilter())
async def bot_photo_reklama(client: Client, call: CallbackQuery, state: State):
    await call.message.reply('rasmni yuboring')
    await call.answer(cache_time=60)
    await state.set_state(Reklam_State.photo)


@app.on_message(filters.photo & StateFilter(Reklam_State.photo))
async def get_bot_photo_reklama(client: Client, message: types.Message, state: State):
    if message.from_user.id in ADMINS:
        if message.photo:
            photo_file_id = message.photo.file_id
            await state.set_data({
                'photo': photo_file_id
            })
        await message.reply('textni kiriting')
        await state.set_state(Reklam_State.caption)

    else:
        await message.reply('xato malumot yuborildi! ')


@app.on_message(filters.text & StateFilter(Reklam_State.caption))
async def get_bot_text_reklama(client: Client, message: types.Message, state: State):
    if message.from_user.id in ADMINS:
        text = message.text
        await state.set_data({
            'caption': text
        })

        data = await state.get_data()
        photo = data.get('photo')
        caption = data.get('caption')
        print(caption)
        await message.reply_photo(photo=photo, caption=caption)
        await message.reply('malumotlar to\'g\'riligini tekshiring', reply_markup=agree)
        await state.set_state(Reklam_State.finish)
    else:
        await message.reply('xato malumot yuborildi! ')


@app.on_message(filters.text & StateFilter(Reklam_State.finish))
async def set_reklama_finish(client: Client, msg: types.Message, state: State):
    if msg.from_user.id in ADMINS:
        soni = 0
        text = msg.text
        if text == 'Ha':
            data = await state.get_data()
            photo = data.get('photo')
            caption = data.get('caption')
            await state.finish()
            await msg.reply('Xabar yuborilmoqda', reply_markup=ReplyKeyboardRemove())
            for id in db.select_all_users():
                user_id = id[0]
                try:
                    soni += 1
                    time.sleep(0.1)
                    print(f"shuncha odamga xabar yuborilmoqda {soni}")
                    await client.send_photo(chat_id=user_id, photo=photo, caption=caption)
                except Exception as e:
                    db.delete_active_user(id=user_id)
                    continue
            await msg.reply('reklama yuborildi')
            await msg.reply(f'{soni} yuborildi')
        else:
            await state.finish()
            await msg.reply('reklama qabul qilinmadi', reply_markup=ReplyKeyboardRemove())
            await msg.reply('Tanlang', reply_markup=typepost)
    else:
        await msg.reply('xato malumot yuborildi! ')


@app.on_callback_query(filters.regex("text") & StateFilter())
async def bot_photo_reklama(cleint: Client, call: CallbackQuery, state: State):
    await call.message.reply('Reklama matnini kiriting')
    await call.answer(cache_time=60)
    await state.set_state(Matn_state.matn)


@app.on_message(filters.text & StateFilter(Matn_state.matn))
async def get_bot_photo_reklama(client: Client, message: types.Message, state: State):
    if message.from_user.id in ADMINS:
        if message.text:
            reklama_matn = message.text
            await state.set_data({
                'reklama_matn': reklama_matn
            })

            data = await state.get_data()
            reklama_matn = data.get('reklama_matn')
            await message.reply(reklama_matn)
            await message.reply('malumotlar to\'g\'riligini tekshiring', reply_markup=agree)
            await state.set_state(Matn_state.finish)

    else:
        await message.reply('xato malumot yuborildi! ')


@app.on_message(filters.text & StateFilter(Matn_state.finish))
async def set_reklama_finish(client: Client, msg: types.Message, state: State):
    if msg.from_user.id in ADMINS:
        soni = 0
        text = msg.text
        if text == 'Ha':
            data = await state.get_data()
            reklama_matn = data.get('reklama_matn')
            await state.finish()
            await msg.reply('Xabar yuborilmoqda', reply_markup=ReplyKeyboardRemove())
            for id in db.select_all_users():
                user_id = id[0]
                try:
                    soni += 1
                    time.sleep(0.1)

                    print(f"shuncha odamga xabar yuborilmoqda {soni}")
                    await client.send_message(chat_id=user_id, text=reklama_matn)
                except:
                    db.delete_active_user(id=user_id)
                    continue
            await msg.reply('reklama yuborildi')
            await msg.reply(f'{soni} yuborildi')
        else:
            await state.finish()
            await msg.reply('reklama qabul qilinmadi', reply_markup=ReplyKeyboardRemove())
            await msg.reply('Tanlang', reply_markup=typepost)
    else:
        await msg.reply('xato malumot yuborildi! ')


@app.on_message(filters.regex("Xabar yuborish"))
async def totarqatish(cleint: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        await message.reply("Kimga xabar yubormoqchisiz? IDsini yuboring:", reply_markup=cencelbtn)
        await state.set_state(FeedbackTo.getid)


@app.on_message(filters.text & StateFilter(FeedbackTo.getid))
async def totarqatish(client: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        idto = message.text
        if idto == "Bekor qilish.":
            await message.reply("Bekor qilindi!", reply_markup=adminpanelbtn)
            await state.finish()
        else:
            sendfeedback.append(idto)
            await message.reply("Endi javob yozmoqchi bo'lgan xabar IDsini yuboring: ", reply_markup=cencelbtn)
            await state.set_state(FeedbackTo.getmsgid)


@app.on_message(filters.text & StateFilter(FeedbackTo.getmsgid))
async def totarqatish(cleint: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        msgid = message.text
        if msgid == "Bekor qilish.":
            await message.reply("Bekor qilindi!", reply_markup=adminpanelbtn)
            await state.finish()
        else:
            sendfeedback.append(msgid)
            await message.reply("Endi Yubormoqchi bo'lgan matnni kiriting: ", reply_markup=cencelbtn)
            await state.set_state(FeedbackTo.sendto)


@app.on_message(filters.text & StateFilter(FeedbackTo.sendto))
async def totarqatish(cleint: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        xabar = message.text
        if xabar == "Bekor qilish.":
            await message.reply("Bekor qilindi!", reply_markup=adminpanelbtn)
        else:
            try:
                await cleint.send_message(chat_id=sendfeedback[-2],
                                          text=f"{xabar}\n\n<code>(Murojaatingizga adminimiz tomonidan javob)</code>",
                                          reply_to_message_id=sendfeedback[-1])
                await message.reply("<b>Xabaringiz yuborildi!</b>", reply_markup=adminpanelbtn)
                sendfeedback.remove(sendfeedback[-1])
                sendfeedback.remove(sendfeedback[-1])
            except:
                await message.reply("Xatolik yuz berdi!", reply_markup=adminpanelbtn)
        await state.finish()


@app.on_message(filters.regex("✅ Majburiy obuna"))
async def majburiy_obuna_admin(client: Client, message: types.Message):
    if message.chat.id in ADMINS:
        txt = "<b>Majburiy obuna.\n\nKanallar:</b>\n"
        for ch in CHANNELS:
            chinfo = await client.get_chat(ch)
            txt += f"<b>Nomi:</b> {chinfo.title}\n"
            txt += f"<b>Username:</b> {chinfo.username}\n"
            txt += f"<b>ID:</b> {ch}\n\n"

        await message.reply(txt, reply_markup=keyboard_admin_obuna)


@app.on_callback_query(filters.regex("kanal_qoshish") & StateFilter())
async def kanal_qoshish(client: Client, call: CallbackQuery, state: State):
    if call.from_user.id in ADMINS:
        await call.message.delete()
        await call.message.reply(f"Qo'shmoqchi bo'lgan kanalingizni IDsini yuboring:", reply_markup=cencelbtn)
        await state.set_state(KanalQoshish.kanal_id)


@app.on_message(filters.text & StateFilter(KanalQoshish.kanal_id))
async def kanal_qoshildi(client: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        new_kanal = message.text
        if new_kanal[0] == "-":
            CHANNELS.append(new_kanal)
            await message.reply(f"Endi kanal linkini yuboring!", reply_markup=cencelbtn)
            await state.set_state(KanalQoshish.kanal_url)
        elif new_kanal == "🚫 Bekor qilish.":
            await message.reply(f"Kanal qo'shish bekor qilindi.", reply_markup=adminpanelbtn)
            await state.finish()
        else:
            await message.reply(f"Iltimos faqat ID yuboring!")


@app.on_message(filters.text & StateFilter(KanalQoshish.kanal_url))
async def kanal_qoshildi(client: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        new_url = message.text
        if new_url[0:12] == "https://t.me":
            await message.reply(f"{new_url} qo'shildi.", reply_markup=adminpanelbtn)
            await state.finish()
        elif new_url == "🚫 Bekor qilish":
            CHANNELS.remove(CHANNELS[-1])
            await message.reply(f"Kanal qo'shish bekor qilindi.", reply_markup=adminpanelbtn)
            await state.finish()
        else:
            await message.reply(f"Iltimos faqat kanal linkini yuboring!")


@app.on_callback_query(filters.regex("kanal_olib_tashlash") & StateFilter())
async def olib_tashlash(client: Client, call: CallbackQuery, state: State):
    if call.from_user.id in ADMINS:
        await call.message.reply(f"Olib tashlamoqchi bo'lgan kanalingizni IDsini kiriting:", reply_markup=cencelbtn)
        await state.set_state(KanalOlish.kanal_olish)


@app.on_message(filters.text & StateFilter(KanalOlish.kanal_olish))
async def kanal_qoshildi(client: Client, message: types.Message, state: State):
    if message.chat.id in ADMINS:
        olinadigan_kanal = message.text
        if olinadigan_kanal in CHANNELS:
            CHANNELS.remove(olinadigan_kanal)
            await message.reply(f"{olinadigan_kanal} olib tashlandi.", reply_markup=adminpanelbtn)
            await state.finish()
        elif olinadigan_kanal[0] == "-":
            await message.reply(f"{olinadigan_kanal} kanallar ro'yxatida yo'q!")
        elif olinadigan_kanal == "🚫 Bekor qilish":
            await message.reply(f"Kanal olish bekor qilindi.", reply_markup=adminpanelbtn)
            await state.finish()
        else:
            await message.reply(f"Iltimos faqat ID yuboring!")


@app.on_message(filters.regex("Active"))
async def adminpanel(client: Client, message: types.Message):
    if message.chat.id in ADMINS:
        count = db.count_users()[0]
        active_count = db.count_active_users()[0]
        await message.reply(
            f"👥 <b>Bot obunachilari:</b> {count}\n<b>Aktiv obunachilar: {active_count}</b> ")


@app.on_message(filters.regex("🔙 Back"))
async def adminpanel(client: Client, message: types.Message):
    await message.reply('Main menu', reply_markup=convertor_btn)


if __name__ == "__main__":
    # executor.start_polling(dp)
    app.run()
