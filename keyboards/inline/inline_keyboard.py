from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

change_lang = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🇺🇿 uz', callback_data='uz'),
            InlineKeyboardButton(text='🇷🇺 ru', callback_data='ru'),
            InlineKeyboardButton(text='🇬🇧 en', callback_data='en'),
            InlineKeyboardButton(text='🇹🇷 turk', callback_data='tr'),
        ],

    ],

)


convertor_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Convertor',callback_data='Convertor'),

        ],
    ],

)


typepost = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="TEXT", callback_data="text"),
            InlineKeyboardButton(text="PHOTO", callback_data="photo")
        ]
    ]
)


keyboard_admin_obuna = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text="➕ Qo'shish", callback_data="kanal_qoshish"),
            InlineKeyboardButton(text="➖ Olib tashlash", callback_data="kanal_olib_tashlash"),
        ]
    ]
)

check_button_subs = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(text="Obunani tekshirish", callback_data="check_subs")
    ]]
)
