import threading
import time
import re
from datetime import datetime
from datasources import WebsiteDataSource
from datasource_manager import DataSourceManager
from datasources import FacebookDataSource
from datasources import TelegramDataSource
from datasources import DarkWebDataSource
import logger_config
import logging


now = datetime.now()


def check_full(url, name, api_id, api_hash, channel_name, target, darkweb_target, data):
    try:
        data_source_manager = DataSourceManager()
        data_source_manager.register_data_source(WebsiteDataSource())

        facebook_data_source = FacebookDataSource()
        dataFromFacebook = facebook_data_source.collect_data(name)

        telegram_data_source = TelegramDataSource()
        dataFromTelegram = telegram_data_source.collect_data('example.com', api_id, api_hash, channel_name, target)

        darkweb_data_source = DarkWebDataSource()

        gathered_data = data_source_manager.gather_data(url)
        d = ""

        for data_from_url in gathered_data:
            d += data_from_url

        result_from_search = "Data from the website " + url + ":\n" + d + '\n'

        result_from_search += dataFromFacebook + "\nTarget: " + name + '\n'

        result_from_search += dataFromTelegram + "\napi id: " + api_id + "\napi hash: " + api_hash + "\nchannel name: " + channel_name + "\ntarget to search: " + target + '\n'

        result_from_search += darkweb_data_source.collect_data(darkweb_target)

        if data == result_from_search:
            return "no event"
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return result_from_search


# Event listener class
class FullEventListener(threading.Thread):
    def __init__(self, event_details, manager, user):
        super(FullEventListener, self).__init__()
        self.event_details = event_details
        self.manager = manager
        self.user = user
        self.stopped = threading.Event()

    def run(self):
        try:
            while not self.stopped.is_set():
                url = None
                nameFB = None

                data_type = self.event_details.get("data_type")
                details = self.event_details.get("details")
                date = self.event_details.get("date")

                url_pattern = re.compile(r"Data from the website (https://[^\s]+):")
                match_url = url_pattern.search(details)
                if match_url:
                    url = match_url.group(1)

                target_pattern = re.compile(r'Target: (.+)\n', re.MULTILINE)

                match_telegram = target_pattern.search(details)

                if match_telegram:
                    nameFB = match_telegram.group(1)

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

                darkweb_pattern = re.compile(r'querry: (.+)', re.IGNORECASE)

                darkweb_match = darkweb_pattern.search(details)

                if darkweb_match:
                    yourqueryy_value = darkweb_match.group(1)

                search_result = check_full(url, nameFB, api_id, api_hash, channel_name, target_value, yourqueryy_value, details)

                if search_result == "no event":
                    print("no event telegram")
                else:
                    event_id = self.manager.get_event_id_by_date(self.user, date)
                    self.manager.update_event_details(self.user, event_id, data_type, search_result, now.strftime("%d/%m/%Y %H:%M:%S"))
                    self.notify_user("FULL event! check DB", details, data_type, date)

                time.sleep(5)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def notify_user(self, message, details, data_type, date):
        print("now")
        self.manager.add_backup_event_to_user(self.user, data_type, details, date)
        print(f"{message}")

    def stop(self):
        self.stopped.set()

