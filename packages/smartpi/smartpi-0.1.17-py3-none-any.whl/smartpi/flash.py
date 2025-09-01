import os
import struct
import fcntl

# 配置文件路径 (当前目录下的flash.bin)
FLASH_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/home/Interface/flash/flash.bin")
FLASH_FILE_2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "/home/Interface/flash/flash_2.bin")

DATA_SIZE = 2  # 每个数据2字节
TOTAL_SLOTS = 100  # 100个数据槽

def _init_flash_file():
    """初始化存储文件"""
    if not os.path.exists(FLASH_FILE):
        with open(FLASH_FILE, "wb") as f:
            f.write(b'\x00' * DATA_SIZE * TOTAL_SLOTS)

def write(address, data):
    """
    写入数据到指定地址
    :param address: 地址编号 (1-100)
    :param data: 要写入的整数数据 (2字节范围)
    """
    if not 1 <= address <= TOTAL_SLOTS:
        raise ValueError(f"地址必须在1-{TOTAL_SLOTS}范围内")
    
    # 2字节数据范围: 0-65535 (0xFFFF)
    if not 0 <= data <= 0xFFFF:
        raise ValueError("数据必须在0-65535范围内")
    
    _init_flash_file()
    
    # 计算文件偏移量 (每个地址2字节)
    offset = (address - 1) * DATA_SIZE
    
    with open(FLASH_FILE, "r+b") as f:
        # 使用文件锁确保写入安全
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(offset)
        # 将整数打包为2字节小端格式
        f.write(struct.pack('<H', data))
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)

def read(address):
    """
    从指定地址读取数据
    :param address: 地址编号 (1-100)
    :return: 读取到的整数数据
    """
    if not 1 <= address <= TOTAL_SLOTS:
        raise ValueError(f"地址必须在1-{TOTAL_SLOTS}范围内")
    
    _init_flash_file()
    
    offset = (address - 1) * DATA_SIZE
    
    with open(FLASH_FILE, "rb") as f:
        fcntl.flock(f, fcntl.LOCK_SH)  # 共享锁
        f.seek(offset)
        # 读取2字节并解包为整数
        data_bytes = f.read(DATA_SIZE)
        fcntl.flock(f, fcntl.LOCK_UN)
        
        if len(data_bytes) != DATA_SIZE:
            return 0  # 返回默认值0
            
        return struct.unpack('<H', data_bytes)[0]

# 可选扩展功能
def erase_all():
    """擦除所有数据(重置为0)"""
    with open(FLASH_FILE, "wb") as f:
        f.write(b'\x00' * DATA_SIZE * TOTAL_SLOTS)
        
            
def _init_flash_file_2():
    """初始化存储文件"""
    if not os.path.exists(FLASH_FILE_2):
        with open(FLASH_FILE_2, "wb") as f:
            f.write(b'\x00' * DATA_SIZE * TOTAL_SLOTS)
        
def write_2(address, data):
    if not 1 <= address <= TOTAL_SLOTS:
        raise ValueError(f"地址必须在1-{TOTAL_SLOTS}范围内")
    
    # 2字节数据范围: 0-65535 (0xFFFF)
    if not 0 <= data <= 0xFFFF:
        raise ValueError("数据必须在0-65535范围内")
    
    _init_flash_file_2()
    
    # 计算文件偏移量 (每个地址2字节)
    offset = (address - 1) * DATA_SIZE
    
    with open(FLASH_FILE_2, "r+b") as f:
        # 使用文件锁确保写入安全
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(offset)
        # 将整数打包为2字节小端格式
        f.write(struct.pack('<H', data))
        f.flush()
        fcntl.flock(f, fcntl.LOCK_UN)

def read_2(address):
    if not 1 <= address <= TOTAL_SLOTS:
        raise ValueError(f"地址必须在1-{TOTAL_SLOTS}范围内")
    
    _init_flash_file_2()
    
    offset = (address - 1) * DATA_SIZE
    
    with open(FLASH_FILE_2, "rb") as f:
        fcntl.flock(f, fcntl.LOCK_SH)  # 共享锁
        f.seek(offset)
        # 读取2字节并解包为整数
        data_bytes = f.read(DATA_SIZE)
        fcntl.flock(f, fcntl.LOCK_UN)
        
        if len(data_bytes) != DATA_SIZE:
            return 0  # 返回默认值0
            
        return struct.unpack('<H', data_bytes)[0]

# 可选扩展功能
def erase_all_2():
    """擦除所有数据(重置为0)"""
    with open(FLASH_FILE_2, "wb") as f:
        f.write(b'\x00' * DATA_SIZE * TOTAL_SLOTS)
        