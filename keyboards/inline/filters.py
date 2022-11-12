from telebot import AdvancedCustomFilter
from telebot.callback_data import CallbackDataFilter
from telebot import types


class CityCallbackFilter(AdvancedCustomFilter):
    key = 'city_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)


class HistoryCallbackFilter(AdvancedCustomFilter):
    key = 'history_config'

    def check(self, call: types.CallbackQuery, config: CallbackDataFilter):
        return config.check(query=call)
