from pyrogram_patch.fsm import StatesGroup, StateItem


class Contact(StatesGroup):
    contact = StateItem()


class FeedbackTo(StatesGroup):
    getid = StateItem()
    getmsgid = StateItem()
    sendto = StateItem()


class Qoshish(StatesGroup):
    nameApp = StateItem()
    fileApp = StateItem()


class KanalQoshish(StatesGroup):
    kanal_id = StateItem()
    kanal_url = StateItem()


class KanalOlish(StatesGroup):
    kanal_olish = StateItem()


class Reklam_State(StatesGroup):
    photo = StateItem()
    caption = StateItem()
    finish = StateItem()


class Matn_state(StatesGroup):
    matn = StateItem()
    finish = StateItem()


class Music_State(StatesGroup):
    matn = StateItem()
