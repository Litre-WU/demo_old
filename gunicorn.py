#vim: set fileencoding:utf-8
import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing


# chdir = '/app/'  # 加载应用程序之前将chdir目录指定到指定目录

proc_name = 'demo'  # 进程名

bind = '0.0.0.0:52'  # 绑定ip和端口号

backlog = 512  # 监听队列

timeout = 120  # 超时

# worker_class = 'gevent' # 默认的是sync模式
worker_class = 'uvicorn.workers.UvicornWorker'  # 使用uvicorn模式

# workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
# workers = multiprocessing.cpu_count() * 2 + 1  # 进程数
workers = 4  # 进程数

threads = 4  # 指定每个进程开启的线程数

daemon = True  # 守护进程

reload = True  # 自动加载

worker_connections = 2000  # 设置最大并发量

loglevel = 'info'  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置

# accesslog = "/app/logs/demo_access.log"  # 访问日志文件, "-" 表示标准输出

# errorlog = "/app/logs/demo_err.log"  # 错误日志文件, "-" 表示标准输出

"""
其每个选项的含义如下：
h          remote address
l          '-'
u          currently '-', may be user name in future releases
t          date of the request
r          status line (e.g. ``GET / HTTP/1.1``)
s          status
b          response length or '-'
f          referer
a          user agent
T          request time in seconds
D          request time in microseconds
L          request time in decimal seconds
p          process ID
"""
