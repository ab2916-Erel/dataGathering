import logger_config
import logging
class DataSourceManager:
    def __init__(self):
        self.data_sources = []

    def register_data_source(self, data_source):
        try:
            self.data_sources.append(data_source)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def gather_data(self, target):
        try:
            gathered_data = []
            for data_source in self.data_sources:
                data = data_source.collect_data(target)
                gathered_data.extend(data)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        return gathered_data