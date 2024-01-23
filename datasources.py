from datasource import DataSource
import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning
import whois
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from facebook_scraper import get_profile
import os
import torSearcher
import ahmiaScraper
import mainScraper
import socket
import http.client
import logger_config
import logging
import tweepy


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class WebsiteDataSource(DataSource):
    def collect_data(self, target):
        try:
            website_data = []

            security_data = self.check_security_and_weaknesses(target)
            osint_data = self.osint(target)
            open_ports = self.scan_ports(target)
            banner = self.banner_grabbing(target)

            website_data.extend([security_data, osint_data, open_ports, banner])
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        return website_data

    def banner_grabbing(self, url):
        try:
            conn = http.client.HTTPConnection(url)
            conn.request("GET", "/")
            response = conn.getresponse()
            print(f"Server banner: {response.getheader('server')}")
            conn.close()
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def scan_ports(self, target):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

        def pscan(port):
            try:
                con = s.connect((target, port))
                return True
            except:
                return False

        data = ""
        try:
            for x in range(4000):
                if pscan(x):
                    data += "Port " + x + "is open"
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return data


    def check_security_and_weaknesses(self, url):
        data = ""
        try:
            response = requests.get(url, verify=False)

            if response.url.startswith('https://'):
                data += "Website uses HTTPS\n"
            else:
                data += "Website does not use HTTPS\n"

            headers = response.headers
            security_headers = {
                'Strict-Transport-Security': 'HTTP Strict Transport Security (HSTS) not enabled',
                'X-Content-Type-Options': 'X-Content-Type-Options header not set',
                'X-Frame-Options': 'X-Frame-Options header not set',
                'Content-Security-Policy': 'Content Security Policy (CSP) header not set'
            }

            for header, description in security_headers.items():
                if header in headers:
                    data += f"{header}: Present\n"
                else:
                    data += f"{header}: {description}\n"

            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')

            if len(forms) > 0:
                data += f"Forms found on the page: {len(forms)}\n"

                for form in forms:
                    inputs = form.find_all('input', {'name': True})
                    for input_tag in inputs:
                        input_name = input_tag['name']
                        payload = f"' OR '1'='1"
                        post_data = {input_name: payload}
                        post_response = requests.post(url, data=post_data, verify=False)
                        if payload in post_response.text:
                            data += f"Potential SQL Injection Point Detected in Form: {form}\n"

            else:
                data += "No forms found on the page\n"
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return data

    def osint(self, domain):
        data = ""
        try:
            domain_info = whois.whois(domain)
            data += "Domain WHOIS Information:\n"
            data += str(domain_info) + '\n'
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return data

class TelegramDataSource(DataSource):
    async def search_mentions(self, api_id, api_hash, channel_username, target, limit):
        try:
            async with TelegramClient('osint_session', api_id, api_hash) as client:
                messages = await client(SearchRequest(
                    peer=channel_username,
                    q=target,
                    limit=limit,
                    filter=InputMessagesFilterEmpty(),
                    min_date=None,
                    max_date=None,
                    offset_id=0,
                    add_offset=0,
                    max_id=0,
                    min_id=0,
                    hash=0,
                ))

                results = []
                for message in messages.messages:
                    results.append({
                        'message_id': message.id,
                        'text': message.message,
                        'username': message.from_id,
                        'date': message.date,
                    })

                return results
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def collect_data(self, target, id_api, hash_api, channel_name, search_target):
        data = ""
        channel_username = channel_name
        target_to_search = search_target
        limit = 10

        async def search_mentions_async():
            data = ""
            try:
                results = await self.search_mentions(id_api, hash_api, channel_username, target_to_search, limit)
                if results:
                    for result in results:
                        data += f"Message ID: {result['message_id']}"
                        data += f"Username/From ID: {result['username']}"
                        data += f"Date: {result['date']}"
                        data += f"Text: {result['text']}"
                        data += "-" * 50
                else:
                    data += "No results found."
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
            return data
        try:
            data = asyncio.run(search_mentions_async())
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return data

class FacebookDataSource(DataSource):
    def collect_data(self, target):
        try:
            profile = get_profile(target)
            data = str(profile)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return data

class DarkWebDataSource(DataSource):
    def collect_data(self, target):
        try:
            os.startfile("tor.exe")
            if target == "":
                ahmiaScraper.yourqueryy = str(input("Enter whatever you want to find on the dark web: "))
            else:
                ahmiaScraper.yourqueryy = target
            mainScraper.runProgram()
            filename = ahmiaScraper.ran
            first_line = ""
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        try:
            with open(filename, 'r') as file:
                first_line = file.readline().strip()
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        torSearcher.runProg(str(first_line))
        data = "A text file containing the site's HTML code should be created\n" + "querry: " + ahmiaScraper.yourqueryy + '\n'
        return data

class TwitterDataSource(DataSource):
    def collect_data(self, target):
        consumer_key = 'jphLeND5h5mOSKaM0nlRnGI5h'
        consumer_secret = 'txlMyqCcknFDHEHhq8u6RnkThTrqQ2xQ0zmDt8thNwq2yjOo9U'
        access_token = '1744785841384288256-awrqjwQ4vmrRPjkEN5Eo9VjhYsCE48'
        access_token_secret = 'PWbu6fVUmONK18tK33PtJjydyc0MQwbCm9LjggVscK48u'

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)


        def get_user_info(username):
            data = ""
            try:
                user = api.get_user(screen_name=username)
                data += "User ID: " + user.id_str
                data += "Username: " + user.screen_name
                data += "Followers: " + user.followers_count
                data += "Description: " + user.description
            except Exception as e:
                if hasattr(e, 'response') and e.response.status_code == 403:
                    logging.error(f"Access to the user's information is forbidden. You may need a different access level.")
                else:
                    logging.error(f"An error occurred: {str(e)}")

        # Replace 'elonmusk' with the target Twitter username
        get_user_info(target)