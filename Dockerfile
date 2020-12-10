# 基于镜像基础
 FROM python:3.8.6
 
 # 设置时区
 ENV TZ Asia/Shanghai
 
 # 设置代码文件夹工作目录 /app
 WORKDIR /demo

 # 复制当前代码文件到容器中 /app
 ADD . /demo

 # 安装所需的包
 RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

 # Run app.py when the container launches
 # CMD ["python", "run.py"]
 # CMD ["uvicorn","main:app","--host","0.0.0.0","--port","52","--workers","4"]
 
 CMD ["gunicorn", "main:app", "-c","gunicorn.py"]
 
