import logging
from time import sleep
from telegram.ext import Updater
from telegram.ext import Filters
from telegram import ChatAction as CA
from telegram.ext import CommandHandler as CH
from telegram.ext import MessageHandler as MS

from model.class_engine import generator, utils


TOKEN = "<activation token>"
models = {
    "lofi": None,
    "anime": None,
    "mozart": None,
    "beethoven": None,
    "maestro_2017": None,
    "maestro_2018": None,
}

class AlphaMusicBot():
    def __init__(self, token, debug=False) -> None:
        
        self.ADMIN = ['@god_mod']

        self.create_models()

        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.handlers()
        self.updater.start_polling()
    
    @staticmethod
    def create_models():

        for model_name in models:
            if models[model_name] is None:
                models[model_name] = generator.AlphaGenerate(model_name=model_name)

    def handlers(self):
        handlers_func = {
            'start': self.start,
            'help': self.help,

            'generate': self.generate,
            'soundcloud': self.get_soundcloud,
            'youtube': self.get_youtube,
        }

        for function_name, function in handlers_func.items():
            handle = CH(function_name, function, pass_args=True, filters=Filters.user(username=self.ADMIN))
            self.dispatcher.add_handler(handle)
        
        self.dispatcher.add_handler(MS(Filters.command, self.default_function))

    @staticmethod
    def start(bot, update, args):
        """ greet the user """
        bot.send_message(
            chat_id=update.message.chat_id,
            text="Greeting, i am the alpha_music bot.\r\n"
                 "and i can do a lot of functions.\r\n"
                 "tap the command 'help' to see all commands"
        )

    @staticmethod
    def help(bot, update, args):
        bot.send_chat_action(chat_id=update.message.chat_id, action=CA.TYPING)
        sleep(1)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="i can help you with a lot of things, all you need is to "
                 "ask.\r\nhere are my functions:\r\n"
                 "/start - greets you\r\n"
                 "/generate - generate songs\r\n"
                 "/help - get you to this menu to see all the functions"
        )

    def generate(self, bot, update, args):
        if len(args) == 4:
            music_model, instrument, background_music, number_of_songs = args
            model = generator.AlphaGenerate(model_name=music_model)
            songs_created = utils.generate_songs(music_model, instrument, background_music, number_of_songs, model=model)

            bot.send_chat_action(chat_id=update.message.chat_id, action=CA.UPLOAD_DOCUMENT)

            for song_path, _ in songs_created:
                bot.send_document(chat_id=update.message.chat_id, document=open(f"/app//static//{song_path}.mp3", 'rb'))
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Usage: /generate music model, instrument, background music, number of songs\r\n"
                        "music model: anime, lofi, maestro_2017, maestro_2018, mozart, beethoven\r\n"
                        "instrument: piano, guitar\t\n"
                        "background music: rain, storm, thunder"
            )

    @staticmethod
    def get_soundcloud(bot, update, args):
        bot.send_chat_action(chat_id=update.message.chat_id, action=CA.TYPING)
        sleep(1)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="https://soundcloud.com/alpha-music-416482025"
        )
    
    @staticmethod
    def get_youtube(bot, update, args):
        bot.send_chat_action(chat_id=update.message.chat_id, action=CA.TYPING)
        sleep(1)
        bot.send_message(
            chat_id=update.message.chat_id,
            text="https://www.youtube.com/channel/UCOsZtY6Wl13tZB_Zie_W0Fg/featured"
        )

    @staticmethod
    def default_function(bot, update):
        """ handle an unknown commands """
        bot.send_chat_action(chat_id=update.message.chat_id, action=CA.TYPING)
        sleep(1)
        bot.send_message(
            chat_id=update.message.chat_id,
            text=f"'{update.message.text}' is not recognized as an internal or external command\r\npress /help for command list"
        )


if __name__ == '__main__':
    AlphaMusicBot(TOKEN)
