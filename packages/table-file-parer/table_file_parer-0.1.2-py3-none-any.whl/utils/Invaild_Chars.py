import platform

def get_invalid_chars():
    """返回当前操作系统的文件名非法字符"""
    system = platform.system()
    if system == 'Windows':
        # Windows 非法字符（包括保留名称如 CON, PRN 等）
        return r'<>:"/\|?*' + ''.join(chr(i) for i in range(0, 32))
    elif system == 'Linux':
        return '/\0'
    elif system == 'Darwin':  # macOS
        return '/:'
    else:
        return '/\\<>:"|?*\0'  # 默认保守规则

# 补充：Windows 保留文件名（如 CON, PRN, AUX 等）
RESERVED_NAMES = {
    'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
    'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
    'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
}