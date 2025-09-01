
class Process_Output_Info:
    def __init__(self, output_format="parquet"):
        self.table_id = None
        self.results = {}
        self.is_parquet_proceed = False
        self.is_statistics_proceed = False
        self.is_fts_index_proceed = False
        self.statistics_file_path = None
        self.fts_index_file_path = None
        self.parquet_file_path = None
        self.split = {}
        self.is_splited = False
        self.split_num = 0
        self.split_size = 0
        self.log_file_path = None
        self.processing_start_time = None
        self.processing_end_time = None
        self.output_format = output_format

    def generate_output_info(self):
        self.split = {
            "isSplit": self.is_splited,
            "splitNum": self.split_num,
            "splitSize": self.split_size
        }

        self.results = {
            f"{self.output_format}": self.is_parquet_proceed,
            "statistics": self.is_statistics_proceed,
            "indexdb": self.is_fts_index_proceed,
        }

        final_file_processing_result = {
            "table_id": self.table_id,
            "results": self.results,
            f"{self.output_format}Files": self.parquet_file_path,
            "statisticsFile": self.statistics_file_path,
            "indexdbFile": self.fts_index_file_path,
            "split": self.split,
            "logFile": self.log_file_path,
            "start_time": self.processing_start_time,
            "end_time": self.processing_end_time
        }
        return final_file_processing_result

class FileProcessingStrategy:
    def process(self, file_path):
        raise NotImplementedError
