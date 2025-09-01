# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


#小舵机控制 port:连接P端口；angle:角度0~270；
def steer_angle(port:bytes,angle:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x0E, 0x01, 0x71, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    servo_str[4]=angle
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0
        
#小舵机延时控制 port:连接P端口；angle:角度0~270；second:1~256
def steer_angle_delay(port:bytes,angle:bytes,second:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x10, 0x01, 0x81, 0x00, 0x00, 0x81, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    servo_str[4]=angle//256
    servo_str[5]=angle%256
    servo_str[7]=second
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0
        
#BE-9528数字舵机以速度转至角度 port:连接P端口；angle:角度(0~360)；speed:速度(0~100)；
def set_angle_speed(port:bytes,angle:bytes,speed:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x0D, 0x01, 0x81, 0x00, 0x00, 0x81, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    servo_str[4]=angle//256
    servo_str[5]=angle%256
    servo_str[7]=speed
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0
        
#数字舵机转动到角度延时时间 port:连接P端口；angle:角度(0~360)；ms:延时时间(0~65535)；
def set_angle_ms(port:bytes,angle:bytes,ms:int) -> Optional[bytes]:
    servo_str=[0xA0, 0x11, 0x01, 0x81, 0x00, 0x00, 0x81, 0x00, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    servo_str[4]=angle//256
    servo_str[5]=angle%256
    servo_str[7]=ms//256
    servo_str[8]=ms%256
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0

#数字舵机复位 port:连接P端口；
def set_init(port:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x12, 0x01, 0xBE]
    servo_str[0]=0XA0+port
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0
        
#获取数字舵机角度 port:连接P端口；
def get_angle(port:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x13, 0x01, 0xBE]
    servo_str[0]=0XA0+port
    response = base_driver.single_operate_sensor(servo_str)       
    if response == None:
        return None
    else:
        angle_data=response[4:-1]
        angle_num=int.from_bytes(angle_data, byteorder='big', signed=True)
        return angle_num
        
#数字舵机速度转动 port:连接P端口；
def set_speed(port:bytes,speed:int) -> Optional[bytes]:
    servo_str=[0xA0, 0x14, 0x01, 0x71, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    if speed>100:
        m_par=100
    elif speed>=0 and speed<=100:
        m_par=speed        
    elif speed<-100:
        m_par=156
    elif speed<=0 and speed>=-100:
        m_par=256+speed
        
    servo_str[4]=m_par
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0      
        
#数字舵机编码转动 port:连接P端口；code:编码(0~65535)；speed:速度(-100~100)；
def set_code_speed(port:bytes,code:int,speed:int) -> Optional[bytes]:
    servo_str=[0xA0, 0x15, 0x01, 0x81, 0x00, 0x00, 0x71, 0x00, 0xBE]
    servo_str[0]=0XA0+port
    
    servo_str[4]=code//256
    servo_str[5]=code%256
    
    if speed>100:
        m_par=100
    elif speed>=0 and speed<=100:
        m_par=speed        
    elif speed<-100:
        m_par=156
    elif speed<=0 and speed>=-100:
        m_par=256+speed      
    servo_str[7]=m_par

    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0  

#数字舵机编码值清零 port:连接P端口；
def reset_encode(port:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x16, 0x01, 0xBE]
    servo_str[0]=0XA0+port
    response = base_driver.single_operate_sensor(servo_str)
    if response == None:
        return None
    else:
        return 0
        
#获取数字舵机编码值 port:连接P端口；
def get_encoder(port:bytes) -> Optional[bytes]:
    servo_str=[0xA0, 0x17, 0x01, 0xBE]
    servo_str[0]=0XA0+port
    response = base_driver.single_operate_sensor(servo_str)        
    if response == None:
        return None
    else:
        code_data=response[4:-1]
        code_num=int.from_bytes(code_data, byteorder='big', signed=True)
        return code_num




