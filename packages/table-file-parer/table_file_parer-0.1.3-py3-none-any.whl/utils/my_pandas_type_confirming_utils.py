import pandas as pd
import pandas.api.types as pdt
from datetime import datetime, date
from typing import Union, Optional
import re

class MyPandasTypeConfirmingUtils:
    """
    A utility class for confirming the data types of pandas DataFrame columns.
    """

    #用于判断字符串类型数据是不是只有时分秒
    def _is_time_only(self, s: str) -> bool:
        #"""严格匹配纯时分秒格式（如 10:04:07 或 9:5:30）"""
        return bool(re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$", str(s)))

    def detect_date_format(sample: str) -> Optional[str]:
        """通过样本智能推断日期格式"""
        patterns = [
            # 年-月-日格式（支持 - 和 / 分隔符）
            (r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$", ["%Y-%m-%d", "%Y/%m/%d"]),
            # 日-月-年格式（支持 - 和 / 分隔符）
            (r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", ["%d-%m-%Y", "%d/%m/%Y"]),
            # 月-日-年格式（支持 - 和 / 分隔符）
            (r"^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$", ["%m-%d-%Y", "%m/%d/%Y"]),
        ]

        for regex, formats in patterns:
            if re.match(regex, sample):
                # 根据分隔符选择格式
                separator = "-" if "-" in sample else "/"
                for fmt in formats:
                    if separator in fmt:
                        return fmt
        return None

    def _is_valid_date(self, s: str) -> bool:
        """检查字符串是否为有效日期（支持多种格式，过滤无效年份）"""
        try:
            # 过滤纯数字和明显无效值（如 "2901100"）
            if str(s).isdigit() or len(str(s)) < 6:
                return False
            # 尝试解析常见格式
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                try:
                    parsed = datetime.strptime(str(s), fmt)
                    if 1 <= parsed.year <= 9999:
                        return True
                except:
                    continue
            return False
        except:
            return False

    @staticmethod
    def is_datetime_type(self, series: pd.Series) -> bool:
        """
        Check if the value is a datetime or date object.
        """
        #先判断是不是pandas中的datetime类型
        if pdt.is_datetime64_any_dtype(series):
            return True

        # 检查元素是否为 Python 的 date/datetime 对象（适用于 object 类型列）
        if series.dtype == 'object':
            # Check if the series contains datetime-like strings
            non_null_series = series.dropna()
            if not non_null_series.empty:
                return all(
                    isinstance(x, (date, datetime))
                    for x in non_null_series
                )

    def _string_to_datetime(self, series: pd.Series) -> pd.Series:
        """安全解析日期，过滤无效数据"""
        """安全解析日期，始终返回 Series"""
        try:
            # 预处理：过滤无效日期字符串（如纯数字）
            clean_series = series.copy()
            clean_series.loc[~clean_series.apply(self._is_valid_date)] = pd.NA

            # 根据 Pandas 版本选择解析方式
            if pd.__version__ >= '2.0.0':
                converted = pd.to_datetime(clean_series, format="mixed", errors="coerce")
            else:
                # 旧版本：优先尝试常见格式
                # for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]:
                #     try:
                #         converted = pd.to_datetime(clean_series, format=fmt, errors="coerce")
                #         if not converted.isna().all():
                #             return converted
                #     except:
                #         continue
                # 回退到自动推断
                converted = pd.to_datetime(clean_series, errors="coerce")
            return converted
        except Exception as e:
            print(f"日期解析失败: {e}")
            return pd.Series([pd.NaT] * len(series), index=series.index)
        # return pd.to_datetime(series, format="mixed")

    def string_is_datetime(self, series: pd.Series) -> bool:
        """If we can transform data to datetime and at least one is valid date."""
        try:
            non_null_series = series.dropna()
            if not non_null_series.empty:
                if all(self._is_time_only(x) for x in non_null_series):
                    return False  # 不转换纯时间列

            return not self._string_to_datetime(series).isna().all()
        except Exception as e:
            print(f"Error {str(e)}")
            return False

    def try_convert_to_datetime(self, series: pd.Series) -> Union[pd.Series]:
        """尝试将字符串列转换为日期时间，失败返回 None"""
        try:
            # 判断是否可能为日期时间
            if self.string_is_datetime(series):  # 使用你之前定义的 string_is_datetime
                converted = self._string_to_datetime(series)  # 使用你之前定义的 string_to_datetime
                return converted
        except:
            pass
        return None


if __name__ == '__main__':
    my_util = MyPandasTypeConfirmingUtils()
    # 读取 CSV 文件
    df = pd.read_csv("D:\hqr\workspace\csvfiles\csv\\landsat8_m20136.csv")
    for col in df.columns:
        if my_util.is_datetime_type(df[col]):
            print(f"列 '{col}' 的类型是: datetime")
            continue

        if pdt.is_string_dtype(df[col]) :
            converted_series = my_util.try_convert_to_datetime(df[col])
            if converted_series is not None:
                df[col] = converted_series
                print(f"列 '{col}' 转换为: datetime")


