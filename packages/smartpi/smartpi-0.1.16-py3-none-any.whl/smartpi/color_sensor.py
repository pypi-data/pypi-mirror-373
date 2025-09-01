# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver

#颜色读取  正常返回值：1-红色；2-绿色；3-蓝色；4-黄色；5-黑色；6-白色；  读取错误：-1  
def get_value(port:bytes) -> Optional[bytes]:
    color_str=[0xA0, 0x04, 0x00, 0xBE]
    color_str[0]=0XA0+port
    color_str[2]=1
    response = base_driver.single_operate_sensor(color_str)        
    if response == None:
        return None
    else:
        return response[4]
        
        