from io import StringIO
import pandas as pd
import os
from utils.header_detector import *

class CsvChunkReader:
    def __init__(self, csv_path="", chunk_size=10_000):
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.MAX_COLUMN = 1024  # 最大列数限制

    def read_csv_in_chunks(self, input_path, chunk_size=10_000, field_max_bytes=20*1024*1024):
        encoding = self.detect_file_encoding(input_path)
        print(f"使用编码: {encoding} 读取文件 {os.path.basename(input_path)}")

        # 关键调整：全局设置 csv 模块的字段大小限制（替代 engine_kwargs）
        csv.field_size_limit(field_max_bytes)

        # 检测表头和列数
        try:
            # 检测表头和列数
            with open(input_path, 'r', encoding=encoding, errors='replace') as f:
                has_header = self.detect_is_csv_header(input_path, f, encoding)
                f.seek(0)
                # first_line = f.readline()
                # col_count = len(first_line.split(','))
                #
                # # 固定列名：表头存在时用表头，否则自动生成
                # if has_header:
                #     column_names = first_line.strip().split(',')  # 表头作为列名
                #     lines_processed = 1  # 表头行已处理，后续从第二行开始
                # else:
                #     column_names = [f"col_{str(i).zfill(3)}" for i in range(1, col_count + 1)]  # 自动生成列名
                #     lines_processed = 0  # 无表头，从第一行开始处理

                # 使用csv.reader解析首行（替代split(',')）
                csv_reader = csv.reader(f)
                try:
                    first_row = next(csv_reader)  # 首行（表头或首数据行）
                    if len(first_row) > self.MAX_COLUMN:
                        raise ValueError(f"列数超过限制: {self.MAX_COLUMN}")
                except StopIteration:
                    raise ValueError("文件为空，无法解析列名")

                # 步骤2：处理空列名（标记并替换）
                if has_header:
                    # 读取数据样本（后3行）验证空列是否有效
                    data_sample = []
                    for _ in range(3):
                        try:
                            data_sample.append(next(csv_reader))
                        except StopIteration:
                            break

                    # 生成列名（替换无效空列名）
                    column_names = []
                    for col_idx, col_name in enumerate(first_row):
                        # 原始列名为空（去除空格后仍为空）
                        if col_name.strip() == "":
                            # 检查数据样本中该列是否有值（判断是否为有效空列名）
                            has_data = any(
                                col_idx < len(row) and row[col_idx].strip() != ""
                                for row in data_sample
                            )
                            if has_data:
                                # 数据列有值 → 替换为unnamed_col_{index}（保留位置）
                                column_names.append(f"unnamed_col_{col_idx}")
                            else:
                                # 数据列无值 → 标记为无效列（可忽略或替换）
                                column_names.append(f"invalid_col_{col_idx}")
                        else:
                            column_names.append(col_name)

                    lines_processed = 1  # 表头行已处理
                else:
                    # 无表头时自动生成列名（如col_001）
                    column_names = [f"col_{str(i).zfill(3)}" for i in range(1, len(first_row) + 1)]
                    lines_processed = 0

            # 创建新的迭代器，跳过已经处理的行
            with open(input_path, 'r', encoding=encoding, errors='replace') as f:
                if has_header:
                    header = f.readline()

                # 跳过已经处理的行
                # for _ in range(lines_processed):
                #     f.readline()

                # 使用Python引擎创建迭代器
                reader = pd.read_csv(
                    f,
                    chunksize=chunk_size,
                    iterator=True,
                    on_bad_lines='warn',
                    # header=None if not has_header else 0,
                    # names=auto_cols if not has_header else None,
                    header=None,  # 表头已提前处理，数据行无表头
                    names=column_names,  # 统一使用固定列名
                    engine='python',
                    dtype='object'
                )
                try:
                    while True:
                        # 尝试读取下一个块
                        chunk = next(reader)
                        lines_in_chunk = len(chunk)

                        # 更新已处理行数
                        lines_processed += lines_in_chunk

                        print(f"成功处理块: {lines_processed} - {lines_processed + lines_in_chunk - 1} 行")
                        yield chunk

                except Exception as e:
                    print(f"块解析错误: {str(e)}. 尝试逐行处理...")

                    # 打开文件，跳过已经处理的行
                    with open(input_path, 'r', encoding=encoding, errors='replace') as f:
                        # 跳过已经处理的行
                        for _ in range(lines_processed):
                            f.readline()

                        # 逐行读取，直到达到chunk_size或文件结束
                        lines = []
                        for _ in range(chunk_size):
                            line = f.readline()
                            if not line:
                                break
                            if not self._are_quotes_balanced(line):
                                line = self.fix_unclosed_quotes(line)
                            lines.append(line)

                        # if not lines:
                        #     break

                        # 处理这组行
                        chunk_data = ''.join(lines)

                        try:
                            # 尝试使用C引擎解析
                            df = pd.read_csv(
                                StringIO(chunk_data),
                                # header=None if not has_header else 0,
                                # names=auto_cols if not has_header else None,
                                header=None,  # 表头已提前处理，数据行无表头
                                names=column_names,  # 统一使用固定列名
                                engine='c',
                                dtype='object'
                            )
                            lines_processed += len(lines)
                            print(f"使用C引擎成功处理 {len(lines)} 行")
                            yield df
                        except pd.errors.ParserError:
                            # 逐行处理
                            fixed_df = self._process_lines_individually(lines, column_names)
                            if not fixed_df:
                                lines_processed += len(lines)
                                print(f"逐行处理成功: {len(lines)} 行有效")
                                yield fixed_df
                            else:
                                print(f"警告: 处理后没有有效数据")
                                lines_processed += len(lines)  # 即使没有有效数据，也标记这些行为已处理
        except Exception as es:
            raise RuntimeError(f"Error reading CSV file {input_path}: {str(es)}")

    def detect_file_encoding(self, file_path, sample_size=4096) -> str:
        """检测文件编码 - 增强文件结束检测"""
        import chardet

        # 获取文件大小
        file_size = os.path.getsize(file_path)

        # 尝试常见编码
        common_encodings = ['utf-8-sig', 'utf-8', 'gb18030', 'gbk', 'latin1', 'iso-8859-1', 'cp1252']

        # 方法1: 使用chardet检测整个文件
        if file_size < 10 * 1024 * 1024:  # <10MB
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                    result = chardet.detect(raw_data)
                    confidence = result.get('confidence', 0)
                    encoding = result.get('encoding')

                    if confidence > 0.7 and encoding:
                        print(f"检测到编码: {encoding} (置信度: {confidence:.2f})")
                        return encoding
            except:
                pass

        # 方法2: 尝试常见编码（优先 utf-8-sig）
        for enc in common_encodings:
            try:
                with open(file_path, 'r', encoding=enc, errors='replace') as f:
                    # 读取部分数据测试编码是否有效
                    sample = f.read(1024)
                    # 可选：检查是否有大量无效字符
                    if '\ufffd' not in sample:  # ufffd 是 Unicode 替换字符，表示 decode 失败
                        print(f"使用编码: {enc} 成功验证文件")
                        return enc
            except Exception as e:
                print(f"尝试编码 {enc} 失败: {e}")
                continue

        # 方法2: 尝试常见编码
        # for enc in common_encodings:
        #     try:
        #         with open(file_path, 'r', encoding=enc, errors='strict') as f:
        #             # 检查文件结尾是否完整
        #             f.seek(0, os.SEEK_END)
        #             end_pos = f.tell()
        #
        #             # 检查最后100字节
        #             f.seek(max(0, end_pos - 100))
        #             last_chars = f.read(100)
        #
        #             # 检查是否有未闭合的引号
        #             if last_chars.count('"') % 2 != 0:
        #                 print(f"文件结尾可能不完整，尝试修复")
        #
        #             return enc
        #     except UnicodeDecodeError:
        #         continue

        # 方法3: 回退到宽松处理
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                f.read()
                print("使用UTF-8忽略错误模式")
                return 'utf-8'
        except:
            print("所有编码尝试失败，使用GB18030忽略错误模式")
            return 'gb18030'

    def detect_is_csv_header(self, csv_path, f, encoding):
        # with open(csv_path, 'r', encoding='utf-8') as f:
        return detect_csv_header(csv_path, f, encoding)

    def fix_unclosed_quotes(self, line):
        """修复未闭合的引号 - 增强版"""
        if not line:
            return ""

        # 统计引号数量
        # 检测有效引号对（排除转义引号）
        clean_line = line.replace('\\"', '')  # 忽略转义引号
        quote_pairs = clean_line.count('""')
        single_quotes = clean_line.count('"') - quote_pairs * 2

        # 奇数个引号表示未闭合
        if single_quotes % 2 == 1:
            # 添加闭合引号
            line = line.rstrip('\n') + '"\n'

        # 确保行以换行符结束
        if not line.endswith('\n'):
            line += '\n'

        # 处理混合引号
        if "'" in line and '"' in line:
            # 统一使用双引号
            line = line.replace("'", '"')

        return line

    def _are_quotes_balanced(self, line):
        """检查行中的引号是否平衡（不考虑转义引号）"""
        quote_count = 0
        for char in line:
            if char == '"':
                quote_count += 1
        return quote_count % 2 == 0

    def _process_lines_individually(self, lines, column_names):
        """逐行处理作为最后手段"""
        for line in lines:
            try:
                df = pd.read_csv(
                    StringIO(line),
                    header=None,
                    names=column_names,
                    engine='python',
                    dtype='object'
                )
                yield df
            except:
                # 手动创建单行DataFrame
                df = self._create_dataframe_manually([line], column_names)
                yield df
                # row = line.strip().split(',')
                # num_columns = len(column_names)
                # if len(row) > num_columns:
                #     row = row[:num_columns]
                # elif len(row) < num_columns:
                #     row += [''] * (num_columns - len(row))
                # yield pd.DataFrame([row], columns=column_names)