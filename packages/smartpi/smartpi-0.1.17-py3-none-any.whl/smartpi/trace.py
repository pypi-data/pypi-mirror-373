# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver

#循迹卡单通道光值读取 port:连接P端口；正常返回：通道光值数据; 读取错误：None  
def get_analog(port:bytes, chn:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x21, 0x01, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=20+chn
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        trace_data=response[4:-1]
        trace_num=int.from_bytes(trace_data, byteorder='big', signed=True)
        return response[4]
        
#循迹卡设置全部颜色 port:连接P端口；正常返回：通道光值数据; 读取错误：None  
def set_color(port:bytes, color:bytes) -> Optional[bytes]:
    trace_str=[0xA0, 0x20, 0x01, 0x71, 0x00, 0xBE]
    trace_str[0]=0XA0+port
    trace_str[4]=color
    response = base_driver.single_operate_sensor(trace_str)       
    if response == None:
        return None
    else:
        return response[4]

        
        