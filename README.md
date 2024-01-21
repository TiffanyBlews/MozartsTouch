# Diancai-Backend
“点彩成乐”大创项目后端工程（开发中）

由于使用fastapi，在本地运行后可以直接访问`http://0.0.0.0:3000/docs#/`或者 `http://局域网IP:3000/docs#/`查看文档并测试接口
单独的API文档见[API.md](API.md)

![](logo.png)

项目logo（仮）

## TO-DO List
- 完善音乐生成部分MusicGen模型的代码
- 尝试将lora模型附加至clip模型中（或使用GPT接口）将生成的描述画面的文本改为描述音乐的文本
- 将https://github.com/jina-ai/clip-as-service 调试整合到`image_processing.py`
- 优化与前端的通信
