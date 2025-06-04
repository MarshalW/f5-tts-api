FROM ghcr.io/swivid/f5-tts:main

# 创建必要的目录结构
RUN mkdir -p /reference /app

# 复制参考音频和文本文件
COPY ./data/ref.wav /reference/ref.wav
COPY ./data/ref.txt /reference/ref.txt

# 复制服务器脚本
COPY ./src/server.py /app/server.py

# 设置容器入口点
ENTRYPOINT ["python", "/app/server.py"]