import deepl
import config
from typing import Dict, Optional, List
from copy import copy
from functools import lru_cache, wraps
import os
import logging
import re
import ujson

LANGUAGES = {'EN-US': '🇺🇸 English',
             'RU': '🇷🇺 Russian',
             'DE': '🇩🇪 German',
             'FR': '🇫🇷 French',
             'ES': '🇪🇸 Spanish',
             'ZH': '🇨🇳 Chinese'}

translator = deepl.Translator(config.DEEPL_API_KEY)


def get_text_translations(lang: str, text: str):

    result = translator.translate_text(text, target_lang=lang)

    return result.text


def get_online_translations(lang: str, data: List[str]):
    dump_text = "\r\n".join(data)

    result = translator.translate_text(dump_text, target_lang=lang)
    result_list = result.text.split("\r\n")

    translations = {key: result_list[index] for index, key in enumerate(data)}

    return translations


def get_html_translation(path: str, file_name: str, lang: str):
    with open(f'{path}/{file_name}') as f:
        data = f.read()
        texts = re.findall(r'(?<=##).*?(?=##)', data)
        dump_text = "\r\n".join(texts)

        result = translator.translate_text(dump_text, target_lang=lang)

        result_list = result.text.split("\r\n")
        for index, text in enumerate(texts):
            data = data.replace(f'##{text}##', result_list[index])

    name, ext = os.path.splitext(file_name)

    with open(f'{path}/{name}.{lang}{ext}', 'w') as f:
        f.write(data)


@lru_cache
def get_localisation(lang: str) -> Dict[str, str]:
    with open(f'./i18n/{lang}.json') as f:
        return ujson.load(f)


def update_translations(lang: str, translations: Dict[str, str]):
    pass


def tg_bot_translations(func):
    @wraps(func)
    def wrapped(bot, update, context, *args, **kwargs):
        lang = bot.user_lang.get(update.effective_user.id)
        translations = get_localisation(lang)

        # _ = lang_pt.gettext
        def t_(msg): return translations.get(msg, msg)

        result = func(bot, update, context, t_, *args, **kwargs)
        return result

    return wrapped


def generate_python_translation(file_path: str, lang: str, output_file_path: str):
    try:
        with open(output_file_path, 'r') as f:
            translation_data = ujson.load(f)
    except FileNotFoundError:
        translation_data = {}

    with open(file_path, 'r') as f:
        code = f.read()
        texts = re.findall(r'(?<=t_\(\").*?(?=\")', code)
        translations = get_online_translations(lang, texts)

    with open(output_file_path, 'w') as f:
        translation_data.update(translations)
        ujson.dump(translation_data, f, indent=4, ensure_ascii=False)


def generate_localizations():
    for lang in LANGUAGES:
        logging.info(f"Process {lang}")
        get_html_translation("./static", "webapp.html", lang)
        generate_python_translation('./telegram_bot.py', lang, f'./i18n/{lang}.json')


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    generate_localizations()
