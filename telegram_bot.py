#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

from typing import Optional, Set, Dict, Callable
from threading import Thread
import ujson
from enum import Enum
from i18n import tg_bot_translations, get_localisation, LANGUAGES, get_text_translations

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, \
    Update, constants, KeyboardButton, WebAppInfo

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, WEB_APP_URL
from log import setup_logger
from ai import generate_ai_text, make_ai_prompt
from json_db import JsonDB

translations = {}

logger = setup_logger(log_name="tg_bot")


def get_user_info(update: Update):
    return f'{update.effective_user.username}#{update.effective_user.id}'


class TelegramBot:
    def __init__(self):
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", self._on_start))
        application.add_handler(CallbackQueryHandler(self._on_language_select_callback,
                                                     pattern=f"^{'|'.join(LANGUAGES.keys())}$"))
        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self._on_web_app_data))

        self.app = application
        self.user_lang: Dict[int, str] = {}

    def run(self):
        stored_data = JsonDB.load_data()
        self.user_lang = {int(k): v['lang'] for k, v in stored_data.items()}
        self.app.run_polling()

    async def _on_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info(f'{get_user_info(update)} - start')
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(v, callback_data=k)]
                                             for k, v in LANGUAGES.items()])
        await update.message.reply_html("Select your language", reply_markup=reply_markup)

    def get_user_lang(self, update: Update) -> str:
        return self.user_lang.get(update.effective_user.id)

    @tg_bot_translations
    async def _init_user_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, t_: Callable):
        button_caption = t_("🪗 Create!")
        web_app = WebAppInfo(url=f"{WEB_APP_URL}webapp.{self.get_user_lang(update)}.html")
        greetings_msg = t_("Greetings <b>@{un}</b>, I'm 🤖 that generates marketing offers!")\
            .format(un=update.effective_user.username)
        btn_msg = t_("Press button to start ⬇️")
        await context.bot.send_message(text=f"{greetings_msg}\r\n\r\n{btn_msg}",
                                       chat_id=update.effective_chat.id,
                                       parse_mode=constants.ParseMode.HTML,
                                       reply_markup=ReplyKeyboardMarkup.from_button(
                                           KeyboardButton(
                                               text=button_caption,
                                               web_app=web_app,
                                           )
                                       ))

    async def _on_language_select_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        lang_selected = query.data
        user_id = update.effective_user.id
        JsonDB.save_user_data(user_id, "lang", lang_selected)
        self.user_lang[user_id] = lang_selected
        logger.info(f'{get_user_info(update)} - select lang {lang_selected}')
        await query.delete_message()
        # await query.edit_message_text(text=f'{LANGUAGES.get(lang_selected)}',
        #                               parse_mode=constants.ParseMode.HTML)

        await self._init_user_menu(update, context)

    def get_preview_prompt_text(self, data: Dict[str, str], lang: str):
        offer_type = data['offer-type'].capitalize()
        name = data['offer-name']
        description = data['description']
        seed_words = data.get("seed-words", False)
        location = data.get("location", False)
        result = data.get("result", False)

        translations = get_localisation(lang)

        def t_(msg):
            return translations.get(msg, msg)

        # HACK: TO generate extra translations
        # t_("slogan")
        # t_("short offer")
        # t_("long offer")

        preview = f'💭 <b>{name.capitalize()}</b>\r\n' \
                  f'🔹 {t_("Description:")} <i>{description}</i>.\r\n'

        if seed_words:
            preview += f'🔹 {t_("Key words")}: <i>{seed_words}</i>\r\n'
        if location:
            preview += f'🔹 {t_("Location")}: <i>{location}</i>\r\n'

        if result:
            preview += f'🔹 {t_("With expected effects")}: <i>{result}</i>\r\n'
        return preview

    @tg_bot_translations
    async def _on_web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE, t_: Callable) -> None:
        try:
            data = ujson.loads(update.effective_message.web_app_data.data)
            offer_name = data['offer-name']
            prompt = make_ai_prompt(data)
            lang = self.get_user_lang(update)
            preview = self.get_preview_prompt_text(data, lang)
            logger.info(f'{get_user_info(update)} - make request: {prompt}')
            await update.message.reply_html(text=f'{preview}')
            delay_info = t_("⏳ Please wait until AI generate your offer(up to 2 minutes)")
            await update.message.reply_html(text=f'{delay_info}')
            await update.message.delete()
            # print(msg)
            text = generate_ai_text(prompt)
            translated_text = text # get_text_translations(lang, text)
            logger.info(f'{get_user_info(update)} - get result: {translated_text}')
            await update.message.reply_html(text=f'{t_("Your offer is ready:")}\r\n')
            await update.message.reply_html(text=f'🪗 <b>{offer_name.capitalize()}</b> '
                                                 f'<code>{translated_text}</code>\r\n'
                                                 f'<i>{t_("Created by")} @bot_army_smm_bot</i>')

        except Exception as e:
            await update.message.reply_html(text=f'{t_("💀 Kernel panic! 🤖 Please try later...")}')

            logger.error(e)


if __name__ == "__main__":
    TelegramBot().run()
