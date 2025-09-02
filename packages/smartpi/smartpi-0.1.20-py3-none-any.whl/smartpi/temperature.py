# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


#温度读取 port:连接P端口；正常返回：温度数据; 读取错误：-1
def get_value(port:bytes) -> Optional[bytes]:
    temp_str=[0XA0, 0X0C, 0X01, 0X71, 0X00, 0XBE]
    temp_str[0]=0XA0+port
    temp_str[4]=0 
    response = base_driver.single_operate_sensor(temp_str)
    if response == None:
        return None
    else:
        return response[4]
        