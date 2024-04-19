# Diancai-Backend
“点彩成乐”大创项目后端工程（开发中）

由于使用fastapi，在本地运行后可以直接访问`http://localhost:3000/docs#/`或者 `http://局域网IP:3000/docs#/`查看文档并测试接口
单独的API文档见[API.md](API.md)

![](logo.png)

项目logo（仮）


## 运行
0. 运行前请首先配置api_key（参见群内信息，或者使用其他OpenAI的API）。
1. 配置环境：`pip install -r requirements.txt`。
2.进入项目主目录：`cd app`
3. 运行 [start_server.py](/app/start_server.py) 即可：`python start_server.py`。

修改`main.py`中的`music_gen_model_name`可以切换small和medium模型

**注意：** 不要运行[main.py](/app/main.py)，会造成一些奇怪的错误！

## 测试模式
将`main.py`中的`test_mode`设置为True时后端会不导入大模型，可以用于测试


## TO-DO List
- 增加用户输入提示词功能
- 删除API中的mode
- 优化音乐生成部分MusicGen模型的代码（主要需求：优化生成效率）
- ~~将https://github.com/jina-ai/clip-as-service 调试整合到`image_processing.py`~~
- 部署视频配乐的功能，尝试将 `Video-Llama` 或者 `Video-BLIP2` 整合到我们的项目中。




