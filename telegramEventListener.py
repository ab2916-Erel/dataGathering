from datasources import TelegramDataSource
import threading
import time
import re
from datetime import datetime
import logger_config
import logging

now = datetime.now()


def check_telegram(api_id, api_hash, channel_name, target, data):
    try:
        telegram_data_source = TelegramDataSource()

        dataFromTelegram = telegram_data_source.collect_data('example.com', api_id, api_hash, channel_name, target)

        result_from_telegram = dataFromTelegram + "\napi id: " + api_id + "\napi hash: " + api_hash + "\nchannel name: " + channel_name + "\ntarget to search: " + target + '\n'
        if data == result_from_telegram:
            return "no event"
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return result_from_telegram


# Event listener class
class TelegramEventListener(threading.Thread):
    def __init__(self, event_details, manager, user):
        super(TelegramEventListener, self).__init__()
        self.event_details = event_details
        self.manager = manager
        self.user = user
        self.stopped = threading.Event()

    def run(self):
        try:
            while not self.stopped.is_set():
                data_type = self.event_details.get("data_type")
                details = self.event_details.get("details")
                date = self.event_details.get("date")

                api_id_pattern = re.compile(r'api id: (\d+)', re.IGNORECASE)
                api_hash_pattern = re.compile(r'api hash: (\w+)', re.IGNORECASE)
                channel_name_pattern = re.compile(r'channel name: (.+)', re.IGNORECASE)
                target_pattern = re.compile(r'target to search: (.+)', re.IGNORECASE)

                api_id_match = api_id_pattern.search(details)
                api_hash_match = api_hash_pattern.search(details)
                channel_name_match = channel_name_pattern.search(details)
                target_match = target_pattern.search(details)

                if api_id_match:
                    api_id = api_id_match.group(1)

                if api_hash_match:
                    api_hash = api_hash_match.group(1)

                if channel_name_match:
                    channel_name = channel_name_match.group(1)

                if target_match:
                    target_value = target_match.group(1)

                telegram_result = check_telegram(api_id, api_hash, channel_name, target_value, details)

                if telegram_result == "no event":
                    print("no event telegram")
                else:
                    event_id = self.manager.get_event_id_by_date(self.user, date)
                    self.manager.update_event_details(self.user, event_id, data_type, telegram_result, now.strftime("%d/%m/%Y %H:%M:%S"))
                    self.notify_user("TELEGRAM event! check DB", details, data_type, date)

                time.sleep(5)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def notify_user(self, message, details, data_type, date):
        print("now")
        self.manager.add_backup_event_to_user(self.user, data_type, details, date)
        print(f"{message}")

    def stop(self):
        self.stopped.set()

