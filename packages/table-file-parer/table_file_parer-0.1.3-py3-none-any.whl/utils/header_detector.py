import ast
import csv
import re
from ast import literal_eval

import pandas as pd


def eval_cell(x):
    try:
        return literal_eval(x.strip())
    except (ValueError, SyntaxError):
        return x


def is_valid_header(candidate_row, data_sample):
    """改进后的表头检测逻辑"""
    # if all(x.strip().isdigit() for x in candidate_row):
    #     return False

    # 特征2：检查字段命名规范性（新增专利数据特征）
    # valid_naming = sum(
    #     1 for x in candidate_row
    #     if re.match(r'^[a-zA-Z_][\w\s-]*$', x) and not x.isupper()
    # ) / len(candidate_row) > 0.7  # 70%以上符合命名规范
    # 特征2：命名规范性计算（排除空列影响）
    # 步骤1：确定哪些列是"非空列"（采样数据中该列至少有一个非空值）
    non_empty_columns = []
    for col_idx in range(len(candidate_row)):
        # 检查该列在所有采样行中是否全为空
        column_is_empty = True
        for row in data_sample:
            # 处理数据行长度不足的情况（视为空）
            if col_idx >= len(row):
                continue
            # 检查单元格内容（去除首尾空格后非空）
            if row[col_idx].strip() != "":
                column_is_empty = False
                break
        if not column_is_empty:
            non_empty_columns.append(col_idx)  # 记录非空列索引

    # 步骤2：计算有效命名比例（仅考虑非空列）
    if not non_empty_columns:  # 所有列都是空列，无法验证命名规范
        valid_naming = False
    else:
        valid_count = 0
        for col_idx in non_empty_columns:
            col_name = candidate_row[col_idx]
            # 检查命名规范（允许中英文、下划线、空格、短横线，且非全大写）
            if re.match(r'^[\u4e00-\u9fff_a-zA-Z][\u4e00-\u9fff_\w\s-]*$', col_name) and not col_name.isupper():
                valid_count += 1
        valid_naming = valid_count / len(non_empty_columns) > 0.7  # 基于非空列计算比例
        #     # 检查命名规范（字母/下划线开头，允许字母数字下划线空格短横线，非全大写）
        #     if re.match(r'^[a-zA-Z_][\w\s-]*$', col_name) and not col_name.isupper():
        #         valid_count += 1
        # valid_naming = valid_count / len(non_empty_columns) > 0.7  # 基于非空列计算比例

    # 特征3：类型分布检测（增强版）
    type_dist = {}
    for cell in candidate_row:
        try:
            val = ast.literal_eval(cell) if cell else cell
            t = type(val).__name__
        except:
            t = 'string'
        type_dist[t] = type_dist.get(t, 0) + 1

    # 专利数据特征：排除包含长文本(>50字符)的"列名"
    has_long_text = any(len(x) > 50 for x in candidate_row)

    is_valid = valid_naming and not has_long_text and type_dist.get('string', 0) / len(non_empty_columns) > 0.8
    #is_valid = valid_naming and not has_long_text and type_dist.get('string', 0) / len(candidate_row) > 0.8

    return is_valid


def dynamic_comparison(csv_path, encoding, sample_size=5):
    with open(csv_path, 'r', encoding=encoding) as f:
        reader = csv.reader(f)
        candidate = next(reader)
        data_rows = [next(reader) for _ in range(min(sample_size, 5))]

    # 计算特征相似度
    def get_row_features(row):
        return {
            'avg_len': sum(len(x) for x in row) / len(row),
            'num_count': sum(x.isdigit() for x in row),
            'json_like': sum(x.startswith('[') and x.endswith(']') for x in row)
        }

    candidate_feat = get_row_features(candidate)
    data_feats = [get_row_features(r) for r in data_rows]

    # 差异度计算（专利数据通常有更高的一致性）
    diff_scores = [
        abs(candidate_feat['avg_len'] - d['avg_len']) +
        abs(candidate_feat['num_count'] - d['num_count']) * 10
        for d in data_feats
    ]

    result = sum(diff_scores) / len(diff_scores)

    return result > 14  # 调整经验阈值

def is_patent_data_row(row):
    """检测专利数据特征"""
    patent_indicators = [
        any(x.startswith(('KR','CN','US','EP')) and x[-1].isalpha() for x in row),  # 专利号
        any(re.search(r'\d{4}[-\/]\d{1,2}[-\/]\d{1,2}', x) for x in row),  # 日期格式
        sum(len(x) > 100 for x in row) >= 2  # 包含长文本描述
    ]
    return sum(patent_indicators) >= 2


def detect_csv_header(csv_path, f, encoding):
    # with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    candidate = next(reader)

    # 先进行快速排除
    if is_patent_data_row(candidate):
        return False

    # 特征1：全数字列名但非连续递增时返回False
    if all(x.strip().isdigit() for x in candidate):
        try:
            # 转换为整数列表（处理可能的超大数问题）
            nums = [int(x.strip()) for x in candidate]
        except ValueError:
            return False  # 无法转换为整数，视为非递增序列

        if len(nums) == 0:
            return False  # 空行已提前过滤

        # 检查是否为连续递增序列（如1,2,3 或 5,6,7等）
        expected_sequence = list(range(nums[0], nums[0] + len(nums)))
        if nums != expected_sequence:
            return False  # 全数字但非连续递增，判定为无效表头
        else:
            return True  # 全数字且连续递增，视为有效表头

    # 动态采样验证
    sample = [next(reader) for _ in range(5)]
    if not dynamic_comparison(csv_path, encoding, len(sample)):
        return False

    # 最终特征验证
    return is_valid_header(candidate, sample)

def detect_excel_sheet_header(excel, sheet_name) -> bool:
    """
    检测Excel文件（.xls, .xlsx）是否具有有效表头
    :param excel: Excel文件路径
    :param sheet_name: 工作表名称
    :return: bool - 是否具有有效表头
    """
    try:
        # 使用 pandas 读取 Excel 文件
        df = pd.read_excel(excel, sheet_name=sheet_name, nrows=6)

        # 如果 DataFrame 已经有列名，则使用列名作为候选表头
        if isinstance(df.columns, pd.Index) and not df.columns.empty:
            candidate = df.columns.astype(str).tolist()
            # 样本数据从第一行开始（跳过列名行）
            data_sample = df.iloc[0:5].apply(lambda row: row.astype(str).tolist(), axis=1).tolist()
        else:
            # 候选表头是第一行
            candidate = df.iloc[0].astype(str).tolist()
            # 样本数据是接下来的5行
            data_sample = df.iloc[1:6].apply(lambda row: row.astype(str).tolist(), axis=1).tolist()

        # 先进行快速排除（专利数据特征）
        if is_patent_data_row(candidate):
            return False

        # 特征1：全数字列名但非连续递增时返回False
        if all(x.strip().isdigit() for x in candidate):
            try:
                nums = [int(x.strip()) for x in candidate]
            except ValueError:
                return False

            if len(nums) == 0:
                return False

            expected_sequence = list(range(nums[0], nums[0] + len(nums)))
            if nums != expected_sequence:
                return False
            else:
                return True

        # 最终特征验证
        return is_valid_header(candidate, data_sample)

    except Exception as e:
        print(f"读取Excel文件时发生错误: {e}")
        return False