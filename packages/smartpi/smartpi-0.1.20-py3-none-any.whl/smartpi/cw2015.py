#!/usr/bin/env python3
import os
import sys
import fcntl
import time

# I2C设备文件路径
I2C_DEV_PATH = "/dev/i2c-2"  # 根据实际情况修改总线号

# I2C从设备地址
CW2015_ADDR = 0x62  # 7位地址

# I2C通信常量
I2C_SLAVE = 0x0703
I2C_SMBUS = 0x0720  # SMBus传输

# SMBus命令结构
class i2c_smbus_ioctl_data:
    def __init__(self, read_write, command, size, data):
        self.read_write = read_write  # 0 = write, 1 = read
        self.command = command        # 寄存器地址
        self.size = size              # 数据大小
        self.data = data              # 数据指针

# 寄存器地址定义
VERSION = 0x00
VCELL_H = 0x02
VCELL_L = 0x03
SOC_B = 0x04
SOC = 0x05
RRT_H = 0x06
RRT_L = 0x07
CONFIG = 0x08
MOOD = 0x0A

class I2CDevice:
    """通过设备文件直接访问I2C设备"""
    def __init__(self, device_path, device_addr):
        """
        初始化I2C设备
        :param device_path: I2C设备文件路径 (例如 "/dev/i2c-2")
        :param device_addr: I2C从设备地址 (7位地址)
        """
        self.device_path = device_path
        self.device_addr = device_addr
        self.fd = None
        
        try:
            # 打开设备文件
            self.fd = os.open(device_path, os.O_RDWR)
            # 设置从设备地址
            fcntl.ioctl(self.fd, I2C_SLAVE, device_addr)
            #print(f"成功打开 {device_path} 并设置地址 0x{device_addr:02X}")
        except Exception as e:
            print(f"打开I2C设备失败: {e}")
            if self.fd:
                os.close(self.fd)
            sys.exit(1)
    
    def __del__(self):
        """关闭设备文件"""
        if self.fd:
            os.close(self.fd)
    
    def write_byte(self, reg_addr, value):
        """
        向寄存器写入一个字节
        :param reg_addr: 寄存器地址
        :param value: 要写入的值
        :return: 成功返回True，失败返回False
        """
        try:
            # 构造写入数据：寄存器地址 + 值
            data = bytes([reg_addr, value])
            os.write(self.fd, data)
            return True
        except Exception as e:
            print(f"写入寄存器0x{reg_addr:02X}失败: {e}")
            return False
    
    def read_byte(self, reg_addr):
        """
        从寄存器读取一个字节
        :param reg_addr: 寄存器地址
        :return: 读取到的字节值，失败返回0
        """
        try:
            # 先写入寄存器地址
            os.write(self.fd, bytes([reg_addr]))
            # 然后读取一个字节
            value = os.read(self.fd, 1)
            return value[0] if value else 0
        except Exception as e:
            print(f"读取寄存器0x{reg_addr:02X}失败: {e}")
            return 0
    
    def read_word(self, reg_addr):
        """
        从寄存器读取两个字节（先高字节后低字节）
        :param reg_addr: 寄存器地址（高字节寄存器）
        :return: (高字节 << 8) | 低字节
        """
        try:
            # 先写入寄存器地址
            os.write(self.fd, bytes([reg_addr]))
            # 读取两个字节
            data = os.read(self.fd, 2)
            if len(data) == 2:
                return (data[0] << 8) | data[1]
            else:
                return 0
        except Exception as e:
            print(f"读取寄存器0x{reg_addr:02X}失败: {e}")
            return 0

class CW2015:
    """CW2015电池监测芯片驱动"""
    def __init__(self, i2c_dev_path=I2C_DEV_PATH, i2c_addr=CW2015_ADDR):
        """
        初始化CW2015
        :param i2c_dev_path: I2C设备路径
        :param i2c_addr: I2C地址
        """
        self.device = I2CDevice(i2c_dev_path, i2c_addr)
    
    def init(self):
        """初始化芯片配置"""
        # 写入配置
        if not self.device.write_byte(CONFIG, 0x50):
            print("配置寄存器写入失败")
            return False
        if not self.device.write_byte(MOOD, 0x00):
            print("模式寄存器写入失败")
            return False
        
        time.sleep(0.05)  # 50ms延时
        #print("CW2015初始化完成")
        return True
    
    def get_id(self):
        """获取芯片ID"""
        return self.device.read_byte(VERSION)
    
    def get_voltage(self):
        """读取电池电压(mV)"""
        # 读取电压高字节寄存器
        vh = self.device.read_byte(VCELL_H)
        # 读取电压低字节寄存器
        vl = self.device.read_byte(VCELL_L)
        
        # 组合14位ADC值
        adc_value = ((vh & 0x3F) << 8) | vl
        # 转换为电压值 (305μV/LSB)
        voltage = adc_value * 305 / 1000
        return int(voltage)
    
    def get_soc(self, mode=0):
        """读取电池剩余电量"""
        if mode == 0:
            return self.device.read_byte(SOC_B)  # 百分比整数
        else:
            return self.device.read_byte(SOC)     # 高精度值
    
    def get_remaining_time(self):
        """获取剩余工作时间(分钟)"""
        # 读取时间高字节寄存器
        rh = self.device.read_byte(RRT_H)
        # 读取时间低字节寄存器
        rl = self.device.read_byte(RRT_L)
        
        # 提取剩余时间（13位）
        remaining_time = ((rh & 0x1F) << 8) | rl
        return remaining_time
    
    def get_alert_status(self):
        """获取告警状态"""
        rh = self.device.read_byte(RRT_H)
        return (rh >> 7) & 0x01

