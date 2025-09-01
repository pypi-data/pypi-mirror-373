import pyarrow as pa
import argparse
import sys
import pandas as pd


def read_arrow_file(file_path, max_rows=None):
    """读取 Arrow 文件并返回相关信息"""
    try:
        with pa.ipc.RecordBatchFileReader(file_path) as reader:
            column_names = reader.schema.names
            num_rows = 0
            table_data = []

            for batch_idx in range(reader.num_record_batches):
                batch = reader.get_batch(batch_idx)
                num_rows += batch.num_rows
                df = batch.to_pandas()

                # 限制读取行数
                if max_rows is not None:
                    remaining = max_rows - len(table_data)
                    if remaining <= 0:
                        break
                    table_data.extend(df.to_dict('records')[:remaining])
                else:
                    table_data.extend(df.to_dict('records'))

        return {
            'num_rows': num_rows,
            'column_names': column_names,
            'data': table_data
        }

    except Exception as e:
        print(f"读取文件时出错: {e}")
        return None


def display_data_info(data_info, show_data=True, max_display_rows=10):
    """纯文本完整显示所有列（无截断）"""
    column_names = data_info['column_names']
    total_cols = len(column_names)
    total_rows = data_info['num_rows']

    # 显示总行数和列数
    print(f"总行数: {total_rows}")
    print(f"总列数: {total_cols}\n")

    # 显示完整列名（无分组）
    print("列名称:")
    print("  " + ", ".join(column_names) + "\n")

    # 显示数据内容（完整列）
    if show_data and data_info['data']:
        print("数据内容（制表符分隔）:")
        display_rows = data_info['data'][:max_display_rows]

        # 打印表头（完整列名）
        header = "\t".join(column_names)
        print(header)

        # 打印分隔线（与表头对齐）
        print("\t".join(["-" * len(col) for col in column_names]))

        # 打印数据行（完整内容）
        for idx, row in enumerate(display_rows):
            row_cells = [str(row.get(col, "")) for col in column_names]
            print("\t".join(row_cells))

            # 超过显示行数时添加省略提示
            if idx == max_display_rows - 1 and total_rows > max_display_rows:
                print("...")
                print(f"（注：仅显示前 {max_display_rows} 行，共 {total_rows} 行）")


def main():
    """主函数，简化参数"""
    parser = argparse.ArgumentParser(description='读取 Arrow 文件并显示完整列（无截断）')
    parser.add_argument('file_path', help='Arrow 文件路径')
    parser.add_argument('--no-data', action='store_true', help='不显示数据内容')
    parser.add_argument('--max-rows', type=int, help='读取的最大行数（用于大文件）')
    parser.add_argument('--max-display', type=int, default=10, help='显示的最大行数')

    args = parser.parse_args()

    data_info = read_arrow_file(args.file_path, args.max_rows)
    if data_info:
        display_data_info(
            data_info,
            not args.no_data,
            args.max_display
        )

if __name__ == "__main__":
    #main()
    data_info = read_arrow_file("D:\\hqr\\workspace\\csvfiles\\output\\xlsx\\Sheet1\\Sheet1.arrow")

    if data_info:
        display_data_info(data_info)