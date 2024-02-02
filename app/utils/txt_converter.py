from openai import OpenAI
from pathlib import Path
import httpx

app_path = Path(__file__).resolve().parent.parent # app_path为项目根目录（`/app`）

class TxtConverter:
    def txt_converter(self,content):
        client = OpenAI(
            base_url="https://oneapi.xty.app/v1", 
            api_key="sk-uqaulFmTlu24Onqd70A687FaC4A44dEd8dD2Cf33D85f9e76",
            http_client=httpx.Client(
                base_url="https://oneapi.xty.app/v1",
                follow_redirects=True,
            ),
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Convert in less than 200 characters this image caption to a very concise musical description with musical terms, as if you wanted to describe a musical ambiance, stricly in English"},
                {"role": "user", "content": content}
            ]
        )
        converted_result = completion.choices[0].message.content
        print("converted result:"+converted_result.encode('gbk', errors='replace').decode('gbk'))
        return converted_result
    
if __name__=="__main__":   
    content = "the image shows a bright star in the center of a galaxy"
    txt_con = TxtConverter()
    converted_result = txt_con.txt_converter(content)
    print(converted_result)