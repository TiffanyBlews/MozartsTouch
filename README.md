# Mozart's Touch: Multi-Modal Music Generation with Pre-Trained Models
[![arXiv](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)](https://arxiv.org/abs/2405.02801) [![GitHub Stars](https://img.shields.io/github/stars/TiffanyBlews/MozartsTouch?style=social)](https://github.com/TiffanyBlews/MozartsTouch) [![githubio](https://img.shields.io/badge/GitHub.io-Demo_Page-blue?logo=Github&style=flat-square)](https://tiffanyblews.github.io/MozartsTouch-demo/)

This is the official implementation of [Mozart's Touch: A Lightweight Multi-modal Music Generation Framework Based on Pre-Trained Large Models](https://arxiv.org/abs/2405.02801)

![](logo.png)

![](architecture.png)

## Package Description
This repository is structured as follows:
```
Diancai-Backend
├─MozartsTouch/: source code for the implementation of Mozart's Touch
│  ├─model/: pre-trained models
│  ├─static/: static source for test purpose
│  ├─utils/: source code for the modules
│  ├─download_model.py: download pre-trained model to ./model/
│  ├─config.yaml: configurations such as LLM model URLs, API keys
│  └─main.py: Main program of Mozart's Touch
│ outputs/: directory to store generation result music
├─backend_app.py: program for backend web application of Mozart's Touch
└─start_server.py: start the backend server of Mozart's Touch
```
## Setup
1. Before running, please configure [config.yaml](MozartsTouch/config.yaml). 
2. Install dependencies using `pip install -r requirements.txt`.
3. Run [download_model.py](MozartsTouch/download_model.py) to download model parameters needed.
4. Use [MozartsTouch.img_to_music_generate()](MozartsTouch/main.py) to generate music.

To test codes without importing large models, set `TEST_MODE` to `True` in [config.yaml](MozartsTouch/config.yaml).

## Usage


## Running as a Command Line Tool
With the setup complete, you can now run the following command to generate music:
```bash
python main.py
```
or debug with no model imported:
```bash
python main.py --test_mode
```

## Running as a Web Backend Server

1. Install dependencies using `pip install -r requirements_for_server.txt`.
2. Configure port number and other parameters in[start_server.py](/app/start_server.py).
3. Run `python start_server.py`.
4. Access http://localhost:3001/docs#/ to view the backend documentation and test the APIs.

The related frontend project is at https://github.com/ScientificW/MozartFrontEndConnect


## TO-DO List
- ~~增加用户输入提示词功能~~
- 删除API中的mode
- ~~更新到最新的代码，将 `Video-BLIP2` 整合到我们的项目中。~~
- 将评估代码整合进来
- ~~Use `argparse` to set and pass config~~
- ~~MusicGen部分重构策略模式~~
- ~~Use API instead of loading models manually~~
- ~~Add support for other models as an alternative e.g. LLaMa.~~
### 远期任务
- 尝试Florence-2等最新模型
- 优化音乐生成部分MusicGen模型的代码（主要需求：优化生成效率）



