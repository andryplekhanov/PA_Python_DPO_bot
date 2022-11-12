from loader import bot, db
import handlers
from utils.set_bot_commands import set_default_commands
from keyboards.inline.filters import CityCallbackFilter
from telebot.custom_filters import StateFilter, IsDigitFilter
from database.models import User, History, SearchResult


if __name__ == '__main__':
    with db:
        db.create_tables([User, History, SearchResult])
    set_default_commands(bot)
    bot.add_custom_filter(StateFilter(bot))
    bot.add_custom_filter(IsDigitFilter())
    bot.add_custom_filter(CityCallbackFilter())
    bot.infinity_polling()
