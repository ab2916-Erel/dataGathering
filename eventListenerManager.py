from telegramEventListener import TelegramEventListener
from facebookEventListener import FacebookEventListener
from urlEventListener import UrlEventListener
from darkwebEventListener import DarkwebEventListener
from fullEventListener import FullEventListener
import logger_config
import logging


def run(event_details, manager, user):
    try:
        data_type = event_details.get("data_type")
        details = event_details.get("details")
        date = event_details.get("date")
        if data_type == "URL":
            url_event = UrlEventListener(event_details, manager, user)
            url_event.run()
        elif data_type == "FACEBOOK":
            facebook_event = FacebookEventListener(event_details, manager, user)
            facebook_event.run()
        elif data_type == "TELEGRAM":
            telegram_event = TelegramEventListener(event_details, manager, user)
            telegram_event.run()
        elif data_type == "DARKWEB":
            darkweb_event = DarkwebEventListener(event_details, manager, user)
            darkweb_event.run()
        elif data_type == "FULL":
            full_event = FullEventListener(event_details, manager, user)
            full_event.run()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
