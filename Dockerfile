# 基于镜像基础
 FROM python:3.8.5

 # 设置代码文件夹工作目录 /app
 WORKDIR /app

 # 复制当前代码文件到容器中 /app
 ADD . /app

 # 安装所需的包
 RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple/

 # Run app.py when the container launches
 # CMD ["python", "run.py"]
 CMD ["python","-m","uvicorn","main:app","--workers","4"]
 # CMD ["python","-m","gunicorn", "main:app", "-c","gunicorn.py"]