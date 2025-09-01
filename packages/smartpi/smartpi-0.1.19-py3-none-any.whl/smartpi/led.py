# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


#彩灯控制 port:连接P端口；command:0:关灯；1:红；2:绿；3:蓝；4:黄；5:紫；6:青；7:白；  正常返回：0; 读取错误：-1  
def set_color(port:bytes,command:bytes) -> Optional[bytes]:
    color_lamp_str=[0xA0, 0x05, 0x00, 0xBE]
    color_lamp_str[0]=0XA0+port
    color_lamp_str[2]=command
    response = base_driver.single_operate_sensor(color_lamp_str)
    if response == None:
        return None
    else:
        return 0
        