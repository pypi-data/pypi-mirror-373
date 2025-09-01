# coding=utf-8
import time
from typing import List, Optional
from smartpi import base_driver


#以速度移动x秒：dir:方向forward、backward、turnright、turnleft；speed:0~100；second:x秒
def run_second(dir:bytes,speed:bytes,second:bytes) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x11, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0xBE]
    
    if dir=="forward":
        move_str[4]=0x01
    elif dir=="backward":
        move_str[4]=0x02
    elif dir=="turnright":
        move_str[4]=0x03
    elif dir=="turnleft":
        move_str[4]=0x04
            
    move_str[6]=speed
    move_str[8]=second      
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#以速度移动x度：dir:方向forward、backward、turnright、turnleft：speed:0~100：angle:65535
def run_angle(dir:bytes,speed:bytes,angle:int) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x12, 0x71, 0x00, 0x71, 0x00, 0x81, 0x00, 0x00, 0xBE]
    
    if dir=="forward":
        move_str[4]=0x01
    elif dir=="backward":
        move_str[4]=0x02
    elif dir=="turnright":
        move_str[4]=0x03
    elif dir=="turnleft":
        move_str[4]=0x04
        
    move_str[6]=speed
    move_str[8]=angle//256
    move_str[9]=angle%256      
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#以速度移动：dir:方向forward、backward、turnright、turnleft；speed:0~100；
def run(dir:bytes,speed:bytes) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x13, 0x71, 0x00, 0x71, 0x00, 0xBE]
    
    if dir=="forward":
        move_str[4]=0x01
    elif dir=="backward":
        move_str[4]=0x02
    elif dir=="turnright":
        move_str[4]=0x03
    elif dir=="turnleft":
        move_str[4]=0x04
        
    move_str[6]=speed      
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#设置左右轮速度移动x秒：Lspeed:-100~100；Rspeed:-100~100；second:1~255
def run_speed_second(Lspeed:int,Rspeed:int,second:bytes) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x14, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0xBE]
    
    if Lspeed>100:
        m_par=100
    elif Lspeed>=0 and Lspeed<=100:
        m_par=Lspeed        
    elif Lspeed<-100:
        m_par=156
    elif Lspeed<=0 and Lspeed>=-100:
        m_par=256+Lspeed
        
    move_str[6]=m_par
        
    if Rspeed>100:
        m_par=100
    elif Rspeed>=0 and Rspeed<=100:
        m_par=Rspeed        
    elif Rspeed<-100:
        m_par=156
    elif Rspeed<=0 and Rspeed>=-100:
        m_par=256+Rspeed
        
    move_str[4]=m_par
    
    move_str[8]=second
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#设置左右轮速度移动：Lspeed:-100~100；Rspeed:-100~100；
def run_speed(Lspeed:int,Rspeed:int) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x15, 0x71, 0x00, 0x71, 0x00, 0xBE]
    
    if Lspeed>100:
        m_par=100
    elif Lspeed>=0 and Lspeed<=100:
        m_par=Lspeed        
    elif Lspeed<-100:
        m_par=156
    elif Lspeed<=0 and Lspeed>=-100:
        m_par=256+Lspeed
        
    move_str[6]=m_par
        
    if Rspeed>100:
        m_par=100
    elif Rspeed>=0 and Rspeed<=100:
        m_par=Rspeed        
    elif Rspeed<-100:
        m_par=156
    elif Rspeed<=0 and Rspeed>=-100:
        m_par=256+Rspeed
        
    move_str[4]=m_par
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#设置左右轮功率移动：Lpower:0~100；Rpower:0~100；
def run_power(Lpower:bytes,Rpower:bytes) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x17, 0x71, 0x00, 0x71, 0x00, 0xBE]
        
    move_str[4]=Rpower       
    move_str[6]=Lpower
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#设置最大功率：M1:0~100；M2:0~100；M3:0~100；M4:0~100；M5:0~100；M6:0~100；
def set_maxpower(M1:bytes,M2:bytes,M3:bytes,M4:bytes,M5:bytes,M6:bytes) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x18, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0xBE]
        
    move_str[4]=M1       
    move_str[6]=M2
    move_str[8]=M3       
    move_str[10]=M4
    move_str[12]=M5       
    move_str[14]=M6
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#马达停止
def stop() -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x0A, 0xBE]   
             
    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0
        
#设置左右轮方向：Lmotor:1~6；Rmotor:1~6；state: no_reversal、all_reversal、left_reversal、right_reversal
def set_move_init(Lmotor:bytes,Rmotor:bytes,state:bytes) -> Optional[bytes]:
    move_str=[0xA0, 0x01, 0x19, 0x71, 0x00, 0x71, 0x00, 0x71, 0x00, 0xBE]
       
    if state=="no_reversal":
        move_str[4]=0x01
    elif state=="all_reversal":
        move_str[4]=0x02
    elif state=="left_reversal":
        move_str[4]=0x03
    elif state=="right_reversal":
        move_str[4]=0x04  
        
    move_str[6]=Rmotor
    move_str[8]=Lmotor          

    response = base_driver.single_operate_sensor(move_str)        
    if response == None:
        return None
    else:
        return 0        
        
        