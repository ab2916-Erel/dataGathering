from datasources import WebsiteDataSource
from datasource_manager import DataSourceManager
import threading
import time
import re
from datetime import datetime
import logger_config
import logging

now = datetime.now()

def check_url(url, data):
    try:
        data_source_manager = DataSourceManager()
        data_source_manager.register_data_source(WebsiteDataSource())

        gathered_data = data_source_manager.gather_data(url)
        d = ""

        for data_from_url in gathered_data:
            d += str(data_from_url)
        result_from_url = "Data from the website " + url + ":\n" + d + '\n'
        if data == result_from_url:
            return "no event"
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return result_from_url


# Event listener class
class UrlEventListener(threading.Thread):
    def __init__(self, event_details, manager, user):
        super(UrlEventListener, self).__init__()
        self.event_details = event_details
        self.manager = manager
        self.user = user
        self.stopped = threading.Event()

    def run(self):
        try:
            while not self.stopped.is_set():
                url = None

                data_type = self.event_details.get("data_type")
                details = self.event_details.get("details")
                date = self.event_details.get("date")

                url_pattern = re.compile(r"Data from the website (https://[^\s]+):")
                match = url_pattern.search(details)
                if match:
                    url = match.group(1)

                url_result = check_url(url, details)

                if url_result == "no event":
                    print("no event url")
                else:
                    event_id = self.manager.get_event_id_by_date(self.user, date)
                    self.manager.update_event_details(self.user, event_id, data_type, url_result, now.strftime("%d/%m/%Y %H:%M:%S"))
                    self.notify_user("URL event! check DB", details, data_type, date)
    
                time.sleep(5)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def notify_user(self, message, details, data_type, date):
        print("now")
        self.manager.add_backup_event_to_user(self.user, data_type, details, date)
        print(f"{message}")

    def stop(self):
        self.stopped.set()
