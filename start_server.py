'''
请在运行前进行如下配置：
1.在MozartsTouch文件夹内设定config.yaml
2.确保电脑自身配置足够运行
'''

import uvicorn

if __name__ == '__main__':
    uvicorn.run("backend_app:app", host="0.0.0.0", port=3001, reload=True)