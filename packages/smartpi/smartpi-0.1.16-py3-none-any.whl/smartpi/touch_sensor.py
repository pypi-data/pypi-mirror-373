# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver

#触碰传感器 port:连接P端口  正常返回：1、0; 读取错误：-1  
def get_value(port:bytes) -> Optional[bytes]:
    read_sw_str=[0xA0, 0x03, 0x01, 0xBE]
    read_sw_str[0]=0XA0+port   
    response = base_driver.single_operate_sensor(read_sw_str)
    if response == None:
        return None
    else:
        return response[4]
        