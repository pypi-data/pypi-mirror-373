# coding=utf-8
import serial,time,struct,threading,fcntl
from typing import List, Optional
from collections import deque
from . import servo,motor,cw2015,gui

# 创建全局线程锁
serial_lock = threading.RLock()

# 命令常量
BOOT_UPDATE_H = 0XFF
BOOT_UPDATE_L = 0XFF
READ_MODEL_H = 0XFF
READ_MODEL_L = 0X01
READ_VERSION_H = 0XFF
READ_VERSION_L = 0X02
READ_FACTORY_H = 0XFF
READ_FACTORY_L = 0X03
READ_HW_ID_H = 0XFF
READ_HW_ID_L = 0X04
READ_NAME_H = 0XFF
READ_NAME_L = 0X05
WRITE_NAME_H = 0XFF
WRITE_NAME_L = 0X06
READ_CONNECT_H = 0XFF
READ_CONNECT_L = 0X07
READ_BAT_H = 0XFF
READ_BAT_L = 0X0C

UPDATE_REQUEST_H = 0XFF
UPDATE_REQUEST_L = 0X10
MAX_COM_LEN_H = 0XFF
MAX_COM_LEN_L = 0X11
DL_MESSAGE_H = 0XFF
DL_MESSAGE_L = 0X12
READ_STATUS_H = 0XFF
READ_STATUS_L = 0X13
PAGE_CHECK_H = 0XFF
PAGE_CHECK_L = 0X14
PAGE_SEND_H = 0XFF
PAGE_SEND_L = 0X15

READ_PERIPH_H = 0X01
READ_PERIPH_L = 0X01
SINGLE_OP_H = 0X01
SINGLE_OP_L = 0X02
MODE_CHANGE_H = 0X01
MODE_CHANGE_L = 0X03
SEND_CYCLE_H = 0X01
SEND_CYCLE_L = 0X04

frames_queue = deque()
buffer = bytearray()
HEADER = bytes.fromhex('86 AB')  # 帧头
FOOTER = bytes.fromhex('CF')     # 帧尾
MIN_FRAME_LEN = 9                # 最小帧长度

# 串口配置参数
SERIAL_PORT = "/dev/ttyS3"  # 串口设备路径
BAUD_RATE = 921600          # 波特率
TIMEOUT = 0.1                # 读取超时时间（秒）

ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,  # 8位数据位
            parity=serial.PARITY_NONE,  # 无校验位
            stopbits=serial.STOPBITS_ONE,  # 1位停止位
            timeout=TIMEOUT,
            xonxoff=False,  # 关闭软件流控
            rtscts=False,   # 关闭硬件流控        
        )

def is_lock_locked(lock):
    """检查锁是否被占用"""
    acquired = serial_lock.acquire(blocking=True)
    if acquired:
        serial_lock.release()
        return False
    return True

def uart3_init() -> Optional[serial.Serial]:
    """初始化串口"""
    try:        
        if ser.is_open:
#            print("UART3初始化成功")
            return ser
        else:
            print("Error opening UART3")
            return None
    except Exception as e:
        print(f"Error opening UART3: {e}")
        return None

def calculate_pro_check(command_h: int, command_l: int, data: List[bytes] = None) -> int:    
    if data:
        len_data = len(data)
        base_sum = 0x86 + 0xAB + 0x00 + 0x09 + len_data + command_h + command_l + 0x01 + 0xCF
        base_sum += sum(data)
    else:
        base_sum = 0x86 + 0xAB + 0x00 + 0x09 + command_h + command_l + 0x01 + 0xCF
        
    return base_sum % 256  # 确保结果为单字节（原C代码未取模，需根据实际协议调整）

def write_data(command_h: int, command_l: int, send_data: bytes= None) -> Optional[bytes]:
    #with serial_lock:                   
        buffer = bytearray()
        HEADER = bytes.fromhex('86 AB')  # 帧头
        FOOTER = bytes.fromhex('CF')     # 帧尾
        MIN_FRAME_LEN = 9                # 最小帧长度           
        if send_data:            
            pro_check = calculate_pro_check(command_h, command_l, list(send_data))
            send_packet = [0x86, 0xAB, (0x09+len(send_data))//256, (0x09+len(send_data))%256, command_h, command_l, *send_data, 0x01, pro_check, 0xCF]
        else:
            pro_check = calculate_pro_check(command_h, command_l)
            send_packet = [0x86, 0xAB, 0x00, 0x09, command_h, command_l, 0x01, pro_check, 0xCF]
        send_bytes = bytes(send_packet)
        
#        for x in send_bytes:
#            print(f"{x:02X}", end=' ')
#        print("\n")
        
        ser.write(send_bytes)
                 
        
def check_frame(frame: bytes) -> bool:
    # 简化版校验，实际应根据协议实现
    if len(frame) < 9:
        return False
        
    # 计算校验和
    calculated_checksum = (sum(frame[:-2])+frame[-1])%256
    frame_checksum = frame[-2]  # 倒数第二个字节是校验和
    
    return calculated_checksum == frame_checksum

def process_received_data():
    #with serial_lock:
        global buffer
        # 读取所有可用数据
        data = ser.read(ser.in_waiting or 1)
        
#        if data:
#            buffer.extend(data)
#            
#            # 检查缓冲区中是否有0xCF
#            if 0xCF in buffer:
#                # 找到0xCF的位置
#                cf_index = buffer.index(0xCF)
#                # 提取从开始到0xCF的完整帧（包括0xCF）
#                frame = buffer[:cf_index + 1]
#                # 从缓冲区中移除已处理的数据
#                buffer = buffer[cf_index + 1:]
#                return bytes(frame)          
        
        if data:
            buffer.extend(data)
        while len(buffer)>=2:
#            for x in buffer:
#                print(f"{x:02X}", end=' ')
#            print("\n")
            # 1. 查找帧头
            start_idx = buffer.find(HEADER)
            if start_idx == -1:
                # 没有找到帧头，清空无效数据（保留最后可能的部分帧头）
                #print("Header no found")
                if len(buffer) > len(HEADER) - 1:
                    buffer = buffer[-len(HEADER) + 1:]
                return                 
            # 2. 检查帧头后的长度字段是否足够
            if start_idx + 4 > len(buffer):
                # 长度字段不完整，等待更多数据
                return                
            # 3. 解析帧长度
            frame_length = (buffer[start_idx + 2] << 8) + buffer[start_idx + 3]          
            # 4. 检查完整帧是否已到达
            end_idx = start_idx + frame_length - 1
            if end_idx >= len(buffer):
                # 完整帧尚未完全到达
                return                
            # 5. 检查帧尾
            if buffer[end_idx] != ord(FOOTER):
                # 跳过当前帧头，继续查找
                print("End no found")
                buffer = buffer[start_idx + 1:]
                continue               
            # 6. 提取完整帧
            frame = buffer[start_idx:end_idx + 1]
            frames_queue.append(frame)            
            # 7. 从缓冲区移除已处理帧
            buffer = buffer[end_idx + 1:]        
        # 处理所有完整帧
        if len(frames_queue) > 0:
            frame = frames_queue.popleft()
            if check_frame(frame):
                return frame
            else:
                print("Check byte error")
                
# 功能函数类
##############################################################################读取设备信息
"""读取设备型号"""
def read_device_model() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(READ_MODEL_H, READ_MODEL_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"设备型号: {display_data}")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None

"""读取版本号"""
def read_version() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(READ_VERSION_H, READ_VERSION_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"版本号: {display_data}")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None

"""读取工厂信息"""
def read_factory_data() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(READ_FACTORY_H, READ_FACTORY_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"厂家信息: {display_data}")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None

"""读取硬件ID"""
def read_hardware_ID() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(READ_HW_ID_H, READ_HW_ID_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"硬件ID: {display_data}")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None
        
"""读取设备名称"""
def read_device_name() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程       
    write_data(READ_NAME_H, READ_NAME_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"设备名称: {display_data}")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None
        
"""设置设备名称"""
def write_device_name(send_data: str) -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    data_bytes = send_data.encode('utf-8')
    write_data(WRITE_NAME_H, WRITE_NAME_L, data_bytes)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"设置状态: {display_data}")
            return 0
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None
        
"""读取连接方式"""
def read_connected() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(READ_CONNECT_H, READ_CONNECT_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3].decode(errors="ignore")
#            print(f"连接方式: {display_data}")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear()
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None
    
"""读取电池电量百分比"""        
def read_battery() -> Optional[bytes]: 
    sensor = cw2015.CW2015()    
    if sensor.init():
        return sensor.get_soc(0)
    else:
        return None
        
###############################################################################固件升级

#"""下载更新请求"""
#def update_request() -> Optional[bytes]:
#    write_data(UPDATE_REQUEST_H, UPDATE_REQUEST_L)
#    start_time = time.time()
#    while True:
#        response =process_received_data()
#        if response:
#            display_data = response[6:-3].decode(errors="ignore")
#            print(f"从机响应: {display_data}")
#            return display_data
#        else:
#            if time.time() - start_time > 3:
#                print("读取超时")
#                buffer.clear() 
#                return None
#
#"""查询最大通讯长度"""
#def read_max_com_len() -> Optional[bytes]:
#    write_data(MAX_COM_LEN_H, MAX_COM_LEN_L)
#    start_time = time.time()
#    while True:
#        response =process_received_data()
#        if response:
#            display_data = response[6:-3].decode(errors="ignore")
#            print(f"从机响应: {display_data}")
#            return display_data
#        else:
#            if time.time() - start_time > 3:
#                print("读取超时")
#                buffer.clear() 
#                return None
#
#"""下载文件的信息"""
#def download_massage() -> Optional[bytes]:
#    write_data(DL_MESSAGE_H, DL_MESSAGE_L, file_data)#文件信息来源从哪获取？
#    start_time = time.time()
#    while True:
#        response =process_received_data()
#        if response:
#            display_data = response[6:-3].decode(errors="ignore")
#            print(f"从机响应: {display_data}")
#            return display_data
#        else:
#            if time.time() - start_time > 3:
#                print("读取超时")
#                buffer.clear() 
#                return None
#
#"""查询设备状态"""
#def read_device_status() -> Optional[bytes]:
#    write_data(READ_STATUS_H, READ_STATUS_L)
#    start_time = time.time()
#    while True:
#        response =process_received_data()
#        if response:
#            display_data = response[6:-3].decode(errors="ignore")
#            print(f"从机响应: {display_data}")
#            return display_data
#        else:
#            if time.time() - start_time > 3:
#                print("读取超时")
#                buffer.clear() 
#                return None
#        
#"""发送页校验码"""
#def write_page_check() -> Optional[bytes]:
#    write_data(PAGE_CHECK_H, PAGE_CHECK_L, page_check_data)
#    start_time = time.time()
#    while True:
#        response =process_received_data()
#        if response:
#            display_data = response[6:-3].decode(errors="ignore")
#            print(f"从机响应: {display_data}")
#            return display_data
#        else:
#            if time.time() - start_time > 3:
#                print("读取超时")
#                buffer.clear() 
#                return None          
#        
#"""发送页数据"""
#def write_page_check() -> Optional[bytes]:
#    write_data(PAGE_SEND_H, PAGE_SEND_L, page_send_data)
#    start_time = time.time()
#    while True:
#        response =process_received_data()
#        if response:
#            display_data = response[6:-3].decode(errors="ignore")
#            print(f"从机响应: {display_data}")
#            return display_data
#        else:
#            if time.time() - start_time > 3:
#                print("读取超时")
#                buffer.clear() 
#                return None
     
###############################################################################读取传感器信息

"""读取外设连接情况"""
def read_peripheral() -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(READ_PERIPH_H, READ_PERIPH_L)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3]
#            for x in display_data:
#                print(f"{x:02X}", end=' ')
#            print("\n")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None

"""单次操作外设"""         
def single_operate_sensor(op_struct: bytes) -> Optional[bytes]:     
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程            
    write_data(SINGLE_OP_H, SINGLE_OP_L, op_struct)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3]
#            for x in display_data:
#                print(f"{x:02X}", end=' ')
#            print("\n")
            return display_data
        else:
            if time.time() - start_time > 2:  
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None  

#P端口初始化释放     
def P_port_init(port:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x0F, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    response = single_operate_sensor(servo_str)
    if response:
        return 0
    else:
        return None
              
"""从机模式转换"""         
def mode_change(send_data: str) -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程    
    write_data(MODE_CHANGE_H, MODE_CHANGE_L, send_data)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3]
#            for x in display_data:
#                print(f"{x:02X}", end=' ')
#            print("\n")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear() 
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None
        
"""智能模式发送周期"""         
def mode_change(send_data: str) -> Optional[bytes]:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程    
    write_data(SEND_CYCLE_H, SEND_CYCLE_L, send_data)
    start_time = time.time()
    while True:
        response =process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3]
#            for x in display_data:
#                print(f"{x:02X}", end=' ')
#            print("\n")
            return display_data
        else:
            if time.time() - start_time > 3:
                print("读取超时")
                buffer.clear()
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁 
                return None
                
def shut_down():
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    write_data(0XFF, 0XFE)
    serial_lock.release()  #释放线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
    time.sleep(0.5)
    
def shut_down_state() -> bool:
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    response =process_received_data()
    if response:
        receive_data = response[4:-3]
        if receive_data[0]==0XFF and receive_data[1]==0XFE:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            return True
        else:
            buffer.clear()
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            return False
    else:
        serial_lock.release()  #释放线程锁
        fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
        return False
        
def buf_clear():
    buffer.clear()

"""H2-RCU初始化"""
def smartpi_init():
    
    if is_lock_locked(serial_lock):
        serial_lock.release()  #释放线程锁
    
    fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程
    uart3_init()
    fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
    P_port_init(1)
    P_port_init(2)
    P_port_init(3)
    P_port_init(4)
    P_port_init(5)
    P_port_init(6)
    servo.set_init(1)
    servo.set_init(2)
    servo.set_init(3)
    servo.set_init(4)
    servo.set_init(5)
    servo.set_init(6)
    motor.set_motor(1,0)
    motor.set_motor(2,0)
    motor.set_motor(3,0)
    motor.set_motor(4,0)
    motor.set_motor(5,0)
    motor.set_motor(6,0)
    servo.reset_encode(1)
    servo.reset_encode(2)
    servo.reset_encode(3)
    servo.reset_encode(4)
    servo.reset_encode(5)
    servo.reset_encode(6)
    motor.reset_motor_encoder(1)
    motor.reset_motor_encoder(2)
    motor.reset_motor_encoder(3)
    motor.reset_motor_encoder(4)
    motor.reset_motor_encoder(5)
    motor.reset_motor_encoder(6)
    time.sleep(0.1)
    gui.init()
    serial_lock.release()     
    time.sleep(0.1)   
            