## 上传图片以进行音乐生成
请求 URL：`http://127.0.0.1:8000/upload`

请求方法：`POST`

上传表单内容：
- `file`：图片文件，Content-Type: `image/*`。
- `mode`：指定生成模型，可选值为`0`（测试用）、`1`（Mubert模型）、`2`（Riffusion模型）。

返回结果：
- `prompt`：图片转文字结果。
- `result`：生成的音频文件经过Base64编码后的结果。

## 上传图片链接以进行音乐生成
请求 URL：`http://127.0.0.1:8000/upload-url`

请求方法：`POST`

上传表单内容：
- `url`：图片链接，字符串。
- `mode`：指定生成模型，可选值为`0`（测试用）、`1`（Mubert模型）、`2`（Riffusion模型）。

返回结果：
- `prompt`：图片转文字结果。
- `result`：生成的音频文件经过Base64编码后的结果。