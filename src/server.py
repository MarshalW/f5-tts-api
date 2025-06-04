from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from importlib.resources import files
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import soundfile as sf
from io import BytesIO
import logging

# 创建FastAPI应用实例
app = FastAPI()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在应用启动时初始化TTS模型


@app.on_event("startup")
async def load_model():
    global f5tts
    try:
        from f5_tts.api import F5TTS
        logger.info("正在加载TTS模型...")
        f5tts = F5TTS()
        logger.info("✅ TTS模型加载完成")
    except ImportError:
        logger.error("❌ 无法导入f5_tts模块")
        raise RuntimeError("TTS模块加载失败")
    except Exception as e:
        logger.error(f"❌ 模型初始化失败: {str(e)}")
        raise RuntimeError(f"模型初始化失败: {e}")

# 设置完全无限制的 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许携带凭证（如 cookies）
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET, POST, PUT 等）
    allow_headers=["*"],  # 允许所有 HTTP 头部
)

# 定义路由和处理函数


@app.get("/hello")
def say_hello():
    return {"say": "hello"}

# 核心转换接口


@app.post("/convert/tts")
async def convert_tts(text_data: dict):
    # 验证输入数据
    if "text" not in text_data:
        raise HTTPException(status_code=400, detail="缺少'text'字段")

    text = text_data["text"]
    if not isinstance(text, str) or len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="无效的文本输入")

    logger.info(f"收到TTS请求，文本长度: {len(text)}字符")

    # 定义文件路径
    file_path = '/reference/ref.txt'

    try:
        # 获取参考音频的绝对路径
        ref_audio_path = str(files("f5_tts").joinpath("/reference/ref.wav"))

        # 以UTF-8编码打开文件并读取内容
        with open(file_path, 'r', encoding='utf-8') as file:
            ref_text = file.read()

        # 执行TTS转换
        wav, sr, _ = f5tts.infer(
            ref_file=ref_audio_path,
            ref_text=ref_text,
            gen_text=text,
            seed=None     # 随机种子
        )

        # 将numpy数组转换为WAV字节流
        wav_buffer = BytesIO()
        sf.write(wav_buffer, wav, sr, format='WAV')
        wav_buffer.seek(0)

        logger.info(f"✅ TTS转换成功，生成音频时长: {len(wav)/sr:.2f}秒")

        # 返回音频流响应
        return StreamingResponse(
            content=wav_buffer,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=tts_output.wav"}
        )

    except Exception as e:
        logger.error(f"❌ TTS处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS处理失败: {str(e)}")


# 启动应用的命令
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("F5_TTS_SERVER_PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)
