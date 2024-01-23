from datasource_manager import DataSourceManager
from datasources import WebsiteDataSource, TelegramDataSource, FacebookDataSource, DarkWebDataSource
from Database import UserEventManager
import re
import hashlib
from eventListenerManager import run
import threading
from datetime import datetime
import logger_config
import logging

now = datetime.now()


user_threads_dict = {}


def add_thread(username, thread):
    try:
        if username in user_threads_dict:
            user_threads_dict[username].add(thread)
        else:
            user_threads_dict[username] = {thread}
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


'''def kill_threads(username):
    if username in user_threads_dict:
        for thread in user_threads_dict[username]:
            thread.stop()
        del user_threads_dict[username]
        print(f"All threads for {username} have been killed.")
    else:
        print(f"No threads found for {username}.")'''


def display_menu(manager, username):
    try:
        parsed_data = None
        data = None
        id = 0
        while True:
            print("\n=== User Menu ===")
            print("1. Full Search")
            print("2. URL Search")
            print("3. Facebook Search")
            print("4. Telegram Search")
            print("5. Darkweb Search")
            print("6. Quit")

            choice = input("Enter your choice (1-6): ")

            try:
                choice = int(choice)
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")

            if choice == 1:
                data = url()
                parsed_data = parse(data)
                data += facebook(parsed_data)
                data += telegram()
                data += darkweb()
                id = manager.add_event_to_user(username, "FULL", data, now.strftime("%d/%m/%Y %H:%M:%S"))
                print(id)

                thread = threading.Thread(target=run, args=(manager.get_event_details_by_id(username, id), manager, username))
                thread.start()
                add_thread(username, thread)

                print(data)
            elif choice == 2:
                data = url()
                id = manager.add_event_to_user(username, "URL", data, now.strftime("%d/%m/%Y %H:%M:%S"))
                print(id)

                thread = threading.Thread(target=run, args=(manager.get_event_details_by_id(username, id), manager, username))
                thread.start()
                add_thread(username, thread)

                print(data)
                parsed_data = parse(data)
            elif choice == 3:
                data = facebook(parsed_data)
                id = manager.add_event_to_user(username, "FACEBOOK", data, now.strftime("%d/%m/%Y %H:%M:%S"))

                thread = threading.Thread(target=run, args=(manager.get_event_details_by_id(username, id), manager, username))
                thread.start()
                add_thread(username, thread)

                print(data)
            elif choice == 4:
                data = telegram()
                id = manager.add_event_to_user(username, "TELEGRAM", data, now.strftime("%d/%m/%Y %H:%M:%S"))

                thread = threading.Thread(target=run, args=(manager.get_event_details_by_id(username, id), manager, username))
                thread.start()
                add_thread(username, thread)

                print(data)
            elif choice == 5:
                data = darkweb()
                id = manager.add_event_to_user(username, "DARKWEB", data, now.strftime("%d/%m/%Y %H:%M:%S"))

                thread = threading.Thread(target=run, args=(manager.get_event_details_by_id(username, id), manager, username))
                thread.start()
                add_thread(username, thread)

                print(data)
            elif choice == 6:
                print("Exiting. Goodbye!")
                #kill_threads(username)
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


def parse(data):
    try:
        phone_numbers = re.findall(r'\+\d+\s\d+\s\d+', data)
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', data)
        registrant_names = re.findall(r'"registrant_name":\s*\[\s*"(.*?)"\s*,\s*"(.*?)"\s*\]', data)
        parsed_data = {
            "phone_numbers": phone_numbers,
            "emails": emails,
            "registrant_names": registrant_names
        }
        print(parsed_data)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return parsed_data


def url():
    try:
        data_source_manager = DataSourceManager()
        data_source_manager.register_data_source(WebsiteDataSource())
        target = input("Enter the target (url): ")

        gathered_data = data_source_manager.gather_data(target)
        d = ""

        for data in gathered_data:
            d += data
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return "Data from the website " + target + ":\n" + d + '\n'


def facebook(parsed_data):
    try:
        facebook_data_source = FacebookDataSource()
        pick = int(
            input("Enter 1 if you want to enter a name yourself or 2 if you want to use information from url searches: "))
        if pick == 1:
            targetFacebook = input("Enter the target (username from facebook): ")
            dataFromFacebook = facebook_data_source.collect_data(targetFacebook)
        else:
            chosen_name = None
            index = 0
            if parsed_data["registrant_names"]:
                print("Registrant Names:")
                for names_tuple in parsed_data["registrant_names"]:
                    for name in names_tuple:
                        print(f"{index}.{name}")
                        index += 1
                choice = input("Enter the number corresponding to the name you want to choose (or 'q' to quit): ")

                choice = int(choice)
                if 0 <= choice <= index:
                    i = 0
                    for names_tuple in parsed_data["registrant_names"]:
                        for name in names_tuple:
                            if i == choice:
                                chosen_name = name
                            i += 1
                    print(f"Chosen Name: {chosen_name}")
                    targetFacebook = chosen_name
                    dataFromFacebook = facebook_data_source.collect_data(targetFacebook)
                else:
                    print("Invalid choice. Please enter a valid number.")
            else:
                print("No registrant names found.")
                targetFacebook = input("Enter the target (username from facebook): ")
                dataFromFacebook = facebook_data_source.collect_data(targetFacebook)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return dataFromFacebook + "\nTarget: " + targetFacebook + '\n'


def telegram():
    try:
        telegram_data_source = TelegramDataSource()
        api_id = input("Enter your Telegram api id: ")
        api_hash = input("Enter your Telegram api hash: ")
        channel_name = input("Enter the name of the Telegram channel from which you want to take information(with @, for example: @channel): ")
        target_to_search = input("Insert content you want to search for in the channel: ")
        dataFromTelegram = telegram_data_source.collect_data('example.com', api_id, api_hash, channel_name,target_to_search)
        dataFromTelegram += "\napi id: " + api_id + "\napi hash: " + api_hash + "\nchannel name: " + channel_name + "\ntarget to search: " + target_to_search + '\n'
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return dataFromTelegram


def darkweb():
    try:
        darkweb_data_source = DarkWebDataSource()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return darkweb_data_source.collect_data("")


def main():
    db_url = "mongodb://localhost:27017"
    db_name = "Rsecurity"
    try:
        manager = UserEventManager(db_url, db_name)

        def run_event_listener():
            try:
                event_count = manager.get_user_event_count(username)
                if event_count > 0:
                    user_events = manager.get_user_event_details(username)

                    if user_events:
                        for event in user_events:
                            run(event, manager, username)
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")

        while True:
            print("\n=== Main Menu ===")
            print("1. Sign Up")
            print("2. Login")
            print("3. Quit")

            main_choice = input("Enter your choice (1-3): ")

            try:
                main_choice = int(main_choice)
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if main_choice == 1:
                username = input("Enter username: ")
                password = input("Enter password: ")

                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                if manager.user_exists(username):
                    print("Username already exists. Please choose a different username.")
                else:
                    manager.add_user(username, hashed_password)
                    print(f"User '{username}' successfully created.")
                    display_menu(manager, username)
            elif main_choice == 2:
                username = input("Enter username: ")
                password = input("Enter password: ")
                if manager.check_password(username, hashlib.sha256(password.encode()).hexdigest()):
                    print(f"Welcome, {username}!")
                    event_count = manager.get_user_event_count(username)
                    print(event_count)
                    if event_count > 0:
                        event_listener_thread = threading.Thread(target=run_event_listener)
                        event_listener_thread.start()
                        add_thread(username, event_listener_thread)
                    display_menu(manager, username)
                else:
                    print("Invalid username or password.")
            elif main_choice == 3:
                print("Exiting. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 3.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()

