# Diancai-Backend
“点彩成乐”大创项目后端工程（开发中）

由于使用fastapi，在本地运行后可以直接访问`http://localhost:3000/docs#/`或者 `http://局域网IP:3000/docs#/`查看文档并测试接口
单独的API文档见[API.md](API.md)

![](logo.png)

项目logo（仮）


## 运行
运行前请首先配置api_key（参见群内信息）

直接运行[start_server.py](`python app/start_server.py`)，不要运行[main.py](/app/main.py)！

目前默认音频生成模型为Musicgen-small


## TO-DO List
- 优化音乐生成部分MusicGen模型的代码（主要需求：优化生成效率）
- ~~将https://github.com/jina-ai/clip-as-service 调试整合到`image_processing.py`~~
- 部署视频配乐的功能，尝试将 `Video-Llama` 或者 `Video-BLIP2` 项目与我们的项目整合。




