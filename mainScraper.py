import logger_config
import logging

def runProgram():
    import ahmiaScraper
    try:
        filename = ahmiaScraper.Scraper()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    return filename