import socket
import json
import sys

# 连接对象（模块级单例）
_connection = None

def init(host="127.0.0.1", port=65167):
    """初始化GUI连接"""
    global _connection
    if _connection is None:
        _connection = socket.create_connection((host, port))
        _send({"type": "clear"})

def _send(cmd):
    """发送命令到服务器"""
    if _connection is None and "pytest" not in sys.modules:  # 允许测试环境不初始化
        raise ConnectionError("GUI not initialized. Call gui.init() first.")
    if _connection:
        _connection.sendall((json.dumps(cmd) + "\n").encode())

def show_text(x, y, text, color="black", size=16):
    _send({"type": "text", "x": x, "y": y, "text": text, "color": color, "size": size})

def print(text):  # 使用print作为函数名，因为调用时使用gui.print()
    _send({"type": "print", "text": text})

def println(text):
    _send({"type": "println", "text": text})

def show_image(x, y, path, width, height):
    _send({"type": "image", "x": x, "y": y, "path": path, "width": width, "height": height})

def draw_line(x1, y1, x2, y2, color="black", width=1):
    _send({"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": color, "width": width})

def fill_rect(x, y, w, h, color="black"):
    _send({"type": "fill_rect", "x": x, "y": y, "w": w, "h": h, "color": color})
    
def draw_rect(x, y, w, h, width, color="black"):
    _send({"type": "draw_rect", "x": x, "y": y, "w": w, "h": h, "width": width, "color": color})

def fill_circle(cx, cy, r, color="black"):
    _send({"type": "fill_circle", "cx": cx, "cy": cy, "r": r, "color": color})

def draw_circle(cx, cy, r, width, color="black"):
    _send({"type": "draw_circle", "cx": cx, "cy": cy, "r": r, "width": width, "color": color})

def clear():
    _send({"type": "clear"})

def close():
    """关闭GUI连接"""
    global _connection
    if _connection:
        _connection.close()
        _connection = None

# 注册程序退出时自动关闭连接
import atexit
atexit.register(close)