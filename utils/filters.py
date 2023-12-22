from pyrogram import filters

languages = ['en', 'uz', 'ru', 'tr']


async def func(_, __, query):
    if query.data in languages:
        return query.data


async def lang(_, __, query):
    if query.text in languages:
        return query.text


data_filter_lang = filters.create(func)
filter_text_lang = filters.create(lang)
