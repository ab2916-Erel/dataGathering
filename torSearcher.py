import logger_config
import logging

def torSearcher(url):

    import requests
    import random
    def get_tor_session():
        try:
            session = requests.session()
            # Tor uses the 9050 port as the default socks port
            session.proxies = {'http': 'socks5h://127.0.0.1:9050',
                               'https': 'socks5h://127.0.0.1:9050'}
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return session
    try:
        session = get_tor_session()

        result = session.get(url).text

        import string
        filename = ''.join(random.choice(string.ascii_lowercase) for i in range(16))
        with open(f"{filename}.txt", "w+", encoding="utf-8") as newthing:
            newthing.write(result)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

def runProg(urlPart):
    try:
        url = "http://" + urlPart
        torSearcher(url)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

    import sys
    import os

    programname = os.path.basename(sys.argv[0])

    try:
        thelist = sys.argv[1]
        with open(thelist, "r", encoding="utf-8") as newfile:
            data = newfile.readlines()
            try:
                #
                for k in data:
                    k = k.replace("\n", "")
                    k = "http://" + k
                    torSearcher(k)
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
