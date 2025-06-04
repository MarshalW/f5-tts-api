# F5-TTS api

在官方 [Dockerfile](https://github.com/SWivid/F5-TTS/blob/main/Dockerfile) 基础上：

- 增加了简单的 Restful API
- 默认的参考音频和文本

默认配置方式， `docker-compose.yaml`：

```yaml
services:
  f5-tts:
    build: . 
    container_name: f5-tts-server
    ports:
      - "7760:7760"
    environment:
      - F5_TTS_SERVER_PORT=7760
    volumes:
      - f5-tts:/root/.cache/huggingface/hub/
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
volumes:
  f5-tts:
    driver: local
```

构建和运行：

```bash
docker compose build
docker compose up -d
```

文本生成克隆音频：

```bash
curl -o test.wav -X POST "http://monkey:7760/convert/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "李在明还强调，要警惕社会充满厌恶情绪，进而出现分裂对抗。"}'
```

问题：

- 一般多音字情况，模型会自动识别，比如 `下午去趟银行，行么？`
- 如需要自定义读音，见 [中文如何进行更精细的控制，如多音字、连读等](https://github.com/SWivid/F5-TTS/issues/193)
- 数字都会读成英文，需要在使用前做预处理，比如
  - 原文： `1984年12月1日，是一个不平凡的日子。`
  - 转为： `一九八四年十二月一日，是一个不平凡的日子。`