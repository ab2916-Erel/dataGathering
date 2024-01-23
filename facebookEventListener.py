from datasources import FacebookDataSource
import threading
import time
import re
from datetime import datetime
import logger_config
import logging

now = datetime.now()

def check_facebook_user(name, data):
    try:
        facebook_data_source = FacebookDataSource()

        dataFromFacebook = facebook_data_source.collect_data(name)

        result_from_facebook = dataFromFacebook + "\nTarget: " + name + '\n'
        if data == result_from_facebook:
            return "no event"
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return result_from_facebook


# Event listener class
class FacebookEventListener(threading.Thread):
    def __init__(self, event_details, manager, user):
        super(FacebookEventListener, self).__init__()
        self.event_details = event_details
        self.manager = manager
        self.user = user
        self.stopped = threading.Event()

    def run(self):
        try:
            while not self.stopped.is_set():
                nameFB = None
                data_type = self.event_details.get("data_type")
                details = self.event_details.get("details")
                date = self.event_details.get("date")

                target_pattern = re.compile(r'Target: (.+)\n', re.MULTILINE)

                match = target_pattern.search(details)

                if match:
                    nameFB = match.group(1)

                facebook_result = check_facebook_user(nameFB, details)

                if facebook_result == "no event":
                    print("no event facebook")
                else:
                    event_id = self.manager.get_event_id_by_date(self.user, date)
                    self.manager.update_event_details(self.user, event_id, data_type, facebook_result, now.strftime("%d/%m/%Y %H:%M:%S"))
                    self.notify_user("FACEBOOK event! check DB", details, data_type, date)

                time.sleep(5)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def notify_user(self, message, details, data_type, date):
        print("now")
        self.manager.add_backup_event_to_user(self.user, data_type, details, date)
        print(f"{message}")

    def stop(self):
        self.stopped.set()

