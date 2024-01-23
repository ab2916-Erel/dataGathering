from datasources import DarkWebDataSource
import threading
import time
import re
from datetime import datetime
import logger_config
import logging

now = datetime.now()


def check_darkweb(target, data):
    try:
        darkweb_data_source = DarkWebDataSource()
        result_from_darkweb = darkweb_data_source.collect_data(target)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    if data == result_from_darkweb:
        return "no event"
    return result_from_darkweb


# Event listener class
class DarkwebEventListener(threading.Thread):
    def __init__(self, event_details, manager, user):
        super(DarkwebEventListener, self).__init__()
        self.event_details = event_details
        self.manager = manager
        self.user = user
        self.stopped = threading.Event()

    def run(self):
        try:
            while not self.stopped.is_set():
                # Check for events and notify the user
                data_type = self.event_details.get("data_type")
                details = self.event_details.get("details")
                date = self.event_details.get("date")

                # Define a regular expression pattern to extract the value of ahmiaScraper.yourqueryy
                pattern = re.compile(r'querry: (.+)', re.IGNORECASE)

                # Search for the pattern in the data string
                match = pattern.search(details)

                # If a match is found, extract and print the value
                if match:
                    yourqueryy_value = match.group(1)

                darkweb_result = check_darkweb(yourqueryy_value, details)

                # Check for events and notify the user
                if darkweb_result == "no event":
                    print("no event telegram")
                else:
                    event_id = self.manager.get_event_id_by_date(self.user, date)
                    self.manager.update_event_details(self.user, event_id, data_type, darkweb_result, now.strftime("%d/%m/%Y %H:%M:%S"))
                    self.notify_user("DARKWEB event! check DB", details, data_type, date)

                # Sleep for some time before checking again
                time.sleep(5)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def notify_user(self, message, details, data_type, date):
        print("now")
        self.manager.add_backup_event_to_user(self.user, data_type, details, date)
        print(f"{message}")

    def stop(self):
        self.stopped.set()

