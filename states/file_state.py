from pyrogram_patch.fsm import StatesGroup, StateItem


class FileState(StatesGroup):
    file = StateItem()


class FileStateWord(StatesGroup):
    file = StateItem()


class ImageTotext(StatesGroup):
    image = StateItem()
    language = StateItem()


class ImageTopdf(StatesGroup):
    image = StateItem()


class ImageToGet_text(StatesGroup):
    file = StateItem()


class Excel_to_pdf_state(StatesGroup):
    file = StateItem()
