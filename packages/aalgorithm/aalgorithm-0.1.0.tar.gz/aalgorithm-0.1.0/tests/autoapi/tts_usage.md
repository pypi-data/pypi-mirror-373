# TTS 语音合成工具使用指南 https://github.com/coqui-ai/TTS

本文档简要介绍了 TTS 工具的主要功能及其使用方法，包含文本转语音、多说话人语音合成和语音转换。可用于文本朗读、配音、语音合成等多种场景。

已经在本机的 TTS 这个 Conda 环境中安装了相关依赖。运行相关 cli 需要先激活虚拟环境。

## 1. 文本转语音（Text-to-Speech, TTS）

**功能描述**  
将输入的文本内容转换为自然语音音频文件。支持多种语言和模型，适合文本朗读、语音合成等应用。

**输入**  
- 文本内容（如：`Hello world!`）

**预期输出**  
- 音频文件路径（如：`output.wav`）

**命令示例**
```bash
tts --text "Hello world!" --out_path output.wav
```
