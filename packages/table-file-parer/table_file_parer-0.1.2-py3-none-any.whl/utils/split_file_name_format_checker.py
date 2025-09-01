import os
import re

class FormatChecker:
    def __init__(self, pattern: str = None):
        self.pattern = pattern


    def check_file_name_format(self, file_name: str, split_pattern) -> bool:
        """
        检查文件名格式是否符合要求
        :param split_pattern:
        :param file_name: 文件名
        :return: True if format is correct, False otherwise
        """
        # 这里假设文件名格式为 "station_catalogue_YYYYMMDD.csv"
        """检查文件名是否符合指定的正则表达式模式"""
        pure_name = os.path.basename(file_name)  # 去除路径，保留纯文件名
        return re.fullmatch(split_pattern, pure_name) is not None

    def get_file_extension(self, file_path):
        """提取文件后缀（如 .txt、.csv），无后缀时返回空字符串"""
        _, ext = os.path.splitext(file_path)
        return ext.lower()  # 可选：统一转换为小写

    def check_index_generate_format(self, file_name: str, ext: str) -> bool:
        """
        检查分割文件名格式是否符合要求
        :param file_name: 文件名
        :return: True if format is correct, False otherwise
        """
        split_pattern = r'^[\w\s-]+_part\d{3}\.' + f'{ext}$'
        split_pattern_00 = r'^[\w\s-]+_part000\.' + f'{ext}$'

        #如果没分块，即没有partxxx部分，则直接返回True
        #如果分块了，则只检查partxxx部分，只有是part000的文件才返回True

        if (not self.check_file_name_format(file_name, split_pattern)) and \
                (self.get_file_extension(file_name) == f'.{ext}'):
            return True
        else:
            if self.check_file_name_format(file_name, split_pattern_00):
                return True
            else:
                return False


if __name__ == '__main__':
    # data_root = 'D:\hqr\workspace\csvfiles\output\csv\station_catalogue\\'
    # file_name_list = os.listdir(data_root)
    # format_checker = FormatChecker()
    # for file_name in file_name_list:
    #     if format_checker.check_index_generate_format(file_name, 'parquet'):
    #         print(f"文件名 {file_name} 符合格式要求")
    file_name = 'patents_detail_cs_part007.parquet'
    format_checker = FormatChecker()
    print(format_checker.check_index_generate_format(file_name, 'parquet'))
