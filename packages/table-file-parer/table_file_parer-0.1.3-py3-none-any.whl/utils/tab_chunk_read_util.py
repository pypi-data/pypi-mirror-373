
def is_table_tab(file_path, check_lines=10):
    """判断.tab文件是否为表格类型（非GIS格式）"""
    # GIS类型.tab文件的特征关键字（如MapInfo格式）
    gis_signatures = {'!table', '!version', '!charset', '!fields', '!index'}
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in range(check_lines):
                line = f.readline().strip().lower()
                if any(sig in line for sig in gis_signatures):
                    return False  # 含GIS特征，不是表格类型
        return True  # 未检测到GIS特征，视为表格类型
    except Exception as e:
        print(f"检测.tab文件类型时出错: {str(e)}")
        return False  # 异常时默认视为非表格类型


def find_data_start(file_path):
    """找到数据开始的行号（跳过/* */包裹的注释块）"""
    in_comment = False  # 是否处于/* */注释块内
    start_row = 0  # 数据起始行（0-based）
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f):
                stripped_line = line.strip()
                if not in_comment:
                    # 未在注释块中，检查是否出现/*
                    if '/*' in stripped_line:
                        in_comment = True
                        # 若同一行包含*/，则注释块结束
                        if '*/' in stripped_line:
                            in_comment = False
                            start_row = line_num + 1  # 数据从下一行开始
                    else:
                        # 未找到注释块起始，数据从当前行开始
                        start_row = line_num
                        break
                else:
                    # 在注释块中，检查是否出现*/
                    if '*/' in stripped_line:
                        in_comment = False
                        start_row = line_num + 1  # 数据从下一行开始
                        break
            # 若文件结束仍在注释块中，默认从最后一行之后开始（容错处理）
            return start_row
    except Exception as e:
        print(f"查找数据起始行时出错: {str(e)}")
        return 0  # 异常时默认从第一行开始


def tab_has_header(file_path, start_row, sample_lines=5):
    """判断数据部分是否包含表头（从start_row开始读取样本）"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            # 跳过注释块及之前的行
            for _ in range(start_row):
                f.readline()
            # 读取数据部分的前N行样本
            lines = [line.strip() for line in f.readlines()[:sample_lines] if line.strip()]

        if len(lines) < 2:  # 数据行不足，默认无表头
            return False

        # 按制表符分割第一行和其他行
        first_row = lines[0].split('\t')
        other_rows = [line.split('\t') for line in lines[1:]]

        # 列数不一致时，第一行视为表头
        if len(first_row) != len(other_rows[0]):
            return True

        # 检测数据类型差异（字符串vs数值）
        def is_numeric(s):
            try:
                float(s)
                return True
            except (ValueError, TypeError):
                return False

        # 计算第一行与其他行的数值占比
        first_numeric_ratio = sum(is_numeric(cell) for cell in first_row) / len(first_row)
        other_numeric_ratio = sum(
            sum(is_numeric(cell) for cell in row) / len(row)
            for row in other_rows
        ) / len(other_rows)

        # 第一行数值占比显著低于其他行时，视为表头
        return first_numeric_ratio < other_numeric_ratio - 0.5

    except Exception as e:
        print(f"检测表头时出错: {str(e)}")
        return False