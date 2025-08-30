"""
UDP广播监听模块 - listengb
使用方式: 
  import listengb
  
  def my_callback(time, address, message):
      # 处理接收到的消息
      pass
      
  listengb.listengb(callback=my_callback)  # 开始监听
  
  # 当需要停止时
  listengb.stop_listening()
"""

from .core import listengb, stop_listening

__version__ = "0.1.0"
__author__ = "Your Name"
__all__ = ['listengb', 'stop_listening']