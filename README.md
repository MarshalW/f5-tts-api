# F5-TTS 定制 Dockerfile

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

文本生成克隆音频：

```bash
curl -o test.wav -X POST "http://monkey:7760/convert/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "李在明还强调，要警惕社会充满厌恶情绪，进而出现分裂对抗。"}'
```