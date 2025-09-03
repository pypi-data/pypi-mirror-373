import concurrent
from asyncio import as_completed
from concurrent.futures import ProcessPoolExecutor
import pyarrow.feather as feather
import pandas as pd
import warnings
import multiprocessing as mp
import tempfile
import os
import time
import signal
import psutil  # 需要安装: pip install psutil


def _read_sheet_worker(input_path, sheet_name,engine, has_header):
    """独立进程函数：读取Excel工作表并返回结果"""
    try:
        # 删除：忽略 SIGTERM 可能带来副作用，改为默认处理方式
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        df = None
        # 在子进程中创建ExcelFile对象
        excel = pd.ExcelFile(input_path, engine=engine)
        try :
            df = excel.parse(sheet_name, data_only=True, header=0 if has_header else None)
        except Exception as e:
            print(f"读取{input_path}工作表{sheet_name}失败，尝试使用数据类型强制转换")
            df = excel.parse(sheet_name, data_only=True, header=0 if has_header else None,dtype=str)
        finally:
            if df is not None:
                print(f"工作表[{sheet_name}]转换成功")
            else:
                print(f"工作表[{sheet_name}]转换失败")
                return None

        # 使用临时文件避免大数据通过队列传递
        with tempfile.NamedTemporaryFile(delete=False, suffix='.parquet') as f:
            temp_path = f.name
            write_feather(df, temp_path)  # 保存为feather格式，高效且保留数据类型
            return temp_path

        # output_queue.put(temp_path)  # 输出临时文件路径而不是DataFrame本身
    except Exception as e:
        warnings.warn(str(e))
        # error_queue.put(str(e))  # 传递错误信息


def kill_process_and_children(pid, timeout=5):
    """强制终止进程及其所有子进程"""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # 先尝试优雅终止
        for proc in [parent] + children:
            try:
                proc.send_signal(signal.SIGTERM)
            except psutil.NoSuchProcess:
                pass

        # 等待进程终止
        _, still_alive = psutil.wait_procs(
            [parent] + children,
            timeout=timeout
        )

        # 如果还有进程存活，强制杀死
        if still_alive:
            print(f"进程 {pid} 及其子进程未响应SIGTERM，正在发送SIGKILL...")
            for proc in still_alive:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass

            # 再次等待
            psutil.wait_procs(still_alive, timeout=timeout)

        print(f"进程 {pid} 及其子进程已成功终止")
        return True
    except Exception as e:
        print(f"终止进程 {pid} 时出错: {e}")
        return False


def read_sheet_with_timeout(input_path, sheet_name, engine = "openpyxl", timeout=20, data_only=True):
    """带超时控制的工作表读取函数（增强版）"""
    # 创建进程间通信队列
    output_queue = mp.Queue()
    error_queue = mp.Queue()

    # 创建并启动进程
    p = mp.Process(
        target=_read_sheet_worker,
        args=(input_path, sheet_name, engine, data_only, output_queue, error_queue)
    )
    p.start()
    print(f"已启动进程 {p.pid} 读取工作表 {sheet_name}")

    # 等待结果或超时
    start_time = time.time()
    while time.time() - start_time < timeout:
        if p.is_alive():
            time.sleep(0.1)  # 避免CPU占用过高
        else:
            break

    # 检查是否超时
    if p.is_alive():
        print(f"读取工作表 {sheet_name} 超时（{timeout}秒），正在尝试终止进程 {p.pid}...")

        # 多阶段终止策略
        try:
            # 第一阶段：尝试优雅终止
            p.terminate()
            p.join(2.0)  # 等待2秒

            if p.is_alive():
                # 第二阶段：使用psutil终止进程树
                print(f"进程 {p.pid} 未响应terminate()，正在使用psutil终止...")
                kill_process_and_children(p.pid, timeout=3)

                # 再次检查
                if p.is_alive():
                    print(f"进程 {p.pid} 仍然存活，最后尝试使用SIGKILL...")
                    os.kill(p.pid, signal.SIGKILL)
                    p.join(1.0)

            if p.is_alive():
                print(f"警告：进程 {p.pid} 无法被终止！系统可能会卡死。")
            else:
                print(f"进程 {p.pid} 已成功终止")
        except Exception as e:
            print(f"终止进程 {p.pid} 时发生异常: {e}")

        # 清理可能残留的临时文件
        while not output_queue.empty():
            try:
                temp_path = output_queue.get_nowait()
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except:
                pass

        return None

    # 检查错误队列
    if not error_queue.empty():
        error = error_queue.get()
        print(f"读取工作表 {sheet_name} 发生异常: {error}")
        return None

    # 获取结果
    if not output_queue.empty():
        temp_path = output_queue.get()
        try:
            df = pd.read_parquet(temp_path)  # 从临时文件加载数据
            os.remove(temp_path)  # 删除临时文件
            return df
        except Exception as e:
            print(f"加载数据时发生错误: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return None

    print(f"读取工作表 {sheet_name} 没有返回结果")
    return None


def read_sheet_parallel_with_timeout(input_path, sheet_name, engine="openpyxl", has_header = False, timeout=20):
    """并发读取指定sheet，支持超时强制终止"""
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import psutil

    with ProcessPoolExecutor() as executor:
        future_to_sheet = {}

        # 提交指定sheet的任务
        future = executor.submit(_read_sheet_worker, input_path, sheet_name, engine, has_header)
        future_to_sheet[future] = sheet_name

        try:
            print(f"开始等待任务完成（PID: {os.getpid()}）")  # 添加调试信息
            for future in as_completed(future_to_sheet, timeout=timeout):
                sheet = future_to_sheet[future]
                print(f"检测到任务 {sheet} 完成状态: {future.done()}, 异常: {future.exception()}")  # 新增日志
                try:
                    temp_path = future.result(timeout=timeout)

                    if temp_path and os.path.exists(temp_path):
                        df = feather.read_feather(temp_path)
                        # df = pd.read_parquet(temp_path)
                        os.remove(temp_path)
                        return df
                    else:
                        print(f"工作表 {sheet} 返回空路径或文件不存在")
                        return None

                except concurrent.futures.TimeoutError:
                    print(f"工作表 {sheet} 读取超时（{timeout}秒），正在尝试终止进程...")
                    future.cancel()

                    if future._state == "RUNNING":
                        pid = getattr(future, '_process', None)
                        if pid:
                            # 强制终止整个进程树（递归杀掉所有子进程）
                            try:
                                process = psutil.Process(pid)
                                # 递归终止所有子进程
                                for child in process.children(recursive=True):
                                    child.kill()
                                process.kill()  # 杀掉主子进程
                            except psutil.NoSuchProcess:
                                pass  # 子进程可能已经结束
                            # 等待一段时间让系统回收资源
                                # 等待系统回收
                                gone, alive = psutil.wait_procs([process], timeout=3)
                                if alive:
                                    print(f"警告：子进程 {pid} 仍未退出，可能需要手动干预")

                    # 清理可能残留的临时文件
                    try:
                        if temp_path and os.path.exists(temp_path):
                            os.remove(temp_path)
                    finally:
                        return None

                except Exception as e:
                    print(f"读取工作表 {sheet} 时发生错误: {e}")
                    return None

        except TimeoutError:
            print("所有任务等待超时")
            # 主动检查所有future的状态和关联进程
            for future in future_to_sheet:
                if future._state == "RUNNING":
                    pid = getattr(future, '_process', None)
                    if pid:
                        print(f"发现运行中进程 {pid}，尝试强制终止...")
                        try:
                            process = psutil.Process(pid)
                            for child in process.children(recursive=True):
                                child.kill()
                            process.kill()
                            gone, alive = psutil.wait_procs([process], timeout=3)
                            if alive:
                                print(f"警告：进程 {pid} 仍未退出，请检查系统资源")
                        except psutil.NoSuchProcess:
                            pass
            return None

def write_feather(df, file_path):
    """
    将 DataFrame 写入 Feather 文件
    :param df: pandas.DataFrame
    :param file_path: 输出路径（.feather）
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 确保所有列都是可序列化的类型
    for col in df.columns:
        if df[col].dtype == object:
            # 尝试转换为字符串类型
            try:
                df[col] = df[col].astype(str)
            except Exception as e:
                print(f"无法转换列 {col} 到字符串: {e}")

    feather.write_feather(df, file_path)


def read_sheet_parallel_with_timeout_new(input_path, sheet_name, engine="openpyxl", has_header=False, timeout=20):
    """并发读取指定sheet，支持超时强制终止"""
    import multiprocessing as mp

    # 创建用于通信的队列
    result_queue = mp.Queue()
    error_queue = mp.Queue()

    # 启动子进程
    p = mp.Process(
        target=_read_sheet_worker_with_queue,
        args=(input_path, sheet_name, engine, has_header, result_queue, error_queue)
    )
    p.start()
    print(f"已启动子进程 PID={p.pid}")

    # 等待完成或超时
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not result_queue.empty():
            temp_path = result_queue.get()
            if temp_path and os.path.exists(temp_path):
                df = feather.read_feather(temp_path)
                os.remove(temp_path)
                p.join()
                return df
        elif not error_queue.empty():
            error = error_queue.get()
            print(f"子进程发生错误: {error}")
            p.terminate()
            p.join()
            return None
        time.sleep(0.2)

    # 超时处理
    print(f"工作表 {sheet_name} 读取超时（{timeout}s），尝试强制终止子进程...")
    if p.is_alive():
        kill_process_and_children(p.pid)  # 使用之前定义的函数递归杀掉所有子进程
    try:
        p.terminate()
        p.kill()
        p.join()
    except Exception as e:
        print(f"终止进程失败: {e}")

    # 清理残留文件
    while not result_queue.empty():
        try:
            path = result_queue.get_nowait()
            if os.path.exists(path):
                os.remove(path)
        except:
            pass

    return None


def _read_sheet_worker_with_queue(input_path, sheet_name, engine, has_header, result_queue, error_queue):
    """带队列通信的子进程函数"""
    try:
        excel = pd.ExcelFile(input_path, engine=engine)
        df = excel.parse(sheet_name, data_only=True, header=0 if has_header else None)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.feather') as f:
            write_feather(df, f.name)
            result_queue.put(f.name)
    except Exception as e:
        error_queue.put(str(e))