# coding=utf-8
import time,fcntl,serial,threading
from typing import List, Optional
from smartpi import base_driver

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
        
# 创建全局线程锁
serial_lock = threading.RLock()

#循迹卡单通道阈值比较后的布尔值读取 port:连接P端口；chn:检测通道1~7；正常返回：通道布尔值; 读取错误：None
def get_chn_data(port:bytes, chn:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x18, 0x01, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=chn
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        return response[4]

#循迹卡设置各通道颜色 port:连接P端口；color1~color7:7个通道彩灯的颜色1~7(红、绿、蓝、黄、紫、青、白)
def set_chn_color(port:bytes, color1:bytes, color2:bytes, color3:bytes, color4:bytes, color5:bytes, color6:bytes, color7:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x19, 0x01, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=color1
    trace_str[6]=color2
    trace_str[8]=color3
    trace_str[10]=color4
    trace_str[12]=color5
    trace_str[14]=color6
    trace_str[16]=color7
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        return response[4]
        
#循迹卡设置全部颜色 port:连接P端口；color:全部彩灯的颜色1~7(红、绿、蓝、黄、紫、青、白)
def set_color(port:bytes, color:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x20, 0x01, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=color
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        return response[4]

#循迹卡单通道光值读取 port:连接P端口；chn:检测通道；正常返回：通道光值数据; 读取错误：None  
def get_analog(port:bytes, chn:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x21, 0x01, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=20+chn
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        return response[4]

#循迹卡判断是否组合图形 port:连接P端口；state:判断图形组合 1:TT 2:TL 3:TR 4:TM 5:L2 6:L1 7:L 8:M 9:R 10:R1 11:R2
#正常返回：True/False; 读取错误：None
def get_line_state(port:bytes, state:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x22, 0x01, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=state
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        return response[4]
        
#循迹卡自动设置灰度阈值 port:连接P端口；second:秒数 
def set_threshold(port:bytes, second:int) -> Optional[bytes]:
    trace_str=[0xA0, 0x23, 0x01, 0x81, 0x00, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=second//256
    trace_str[5]=second%256   
    
    serial_lock.acquire()  #获取线程锁
    fcntl.flock(ser.fileno(), fcntl.LOCK_EX)  # 进程锁，阻塞其他进程            
    base_driver.write_data(0X01, 0X02, trace_str)
    start_time = time.time()
    
    while True:
        response =base_driver.process_received_data()
        if response:
            serial_lock.release()  #释放线程锁
            fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
            display_data = response[6:-3]
            return display_data
        else:
            if time.time() - start_time > second+2:  
                print("读取超时")
                base_driver.buf_clear()
                serial_lock.release()  #释放线程锁
                fcntl.flock(ser.fileno(), fcntl.LOCK_UN)  # 释放进程锁
                return None 
        