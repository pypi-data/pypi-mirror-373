import socket
import datetime
import threading
import time

# 全局变量，用于控制监听线程
_listening = False
_listen_thread = None
_sock = None

def listengb(callback=None, port=10130):
    """
    开始监听UDP广播消息
    
    参数:
        callback: 回调函数，用于处理接收到的消息，必须提供
        port: 监听端口，默认为10130
    """
    global _listening, _listen_thread, _sock
    
    if callback is None:
        raise ValueError("必须提供回调函数")
    
    if _listening:
        print("已经在监听中")
        return
    
    # 创建UDP socket
    _sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    # 绑定到所有接口的指定端口
    _sock.bind(('0.0.0.0', port))
    
    # 设置非阻塞模式
    _sock.setblocking(False)
    
    # 启动监听线程
    _listening = True
    _listen_thread = threading.Thread(target=_listen_loop, args=(callback,))
    _listen_thread.daemon = True
    _listen_thread.start()
    
    print(f"开始监听UDP广播，端口: {port}")

def stop_listening():
    """停止监听UDP广播"""
    global _listening, _sock
    
    if not _listening:
        print("当前没有在监听")
        return
    
    _listening = False
    
    if _sock:
        try:
            # 发送一个空数据包到本地以唤醒阻塞的recvfrom
            _sock.sendto(b'', ('127.0.0.1', _sock.getsockname()[1]))
        except:
            pass
        
        try:
            _sock.close()
        except:
            pass
    
    print("监听已停止")

def _listen_loop(callback):
    """监听循环"""
    global _listening, _sock
    
    while _listening:
        try:
            # 接收数据和地址
            data, addr = _sock.recvfrom(1024)  # 缓冲区大小为1024字节
            
            # 获取当前时间
            receive_time = datetime.datetime.now()
            
            # 解码消息
            try:
                message = data.decode('utf-8')
            except UnicodeDecodeError:
                message = str(data)  # 如果无法解码为UTF-8，则使用原始字节表示
            
            # 调用回调函数处理消息
            callback(receive_time, addr, message)
            
        except socket.error:
            # 非阻塞socket在没有数据时会抛出异常，这是正常的
            time.sleep(0.1)  # 短暂休眠以减少CPU使用率
        except Exception as e:
            print(f"接收消息时出错: {e}")
            # 继续监听，不退出循环
            time.sleep(1)
    
    # 清理资源
    if _sock:
        try:
            _sock.close()
        except:
            pass