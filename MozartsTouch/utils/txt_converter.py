from openai import OpenAI
from pathlib import Path
import httpx
import configparser

from sympy import content

app_path = Path(__file__).resolve().parent.parent  # 项目根目录（`/app`）

class TxtConverter:
    def __init__(self):
        self.api_key = self.load_api_key()

    def load_api_key(self):
        config = configparser.ConfigParser()
        config_file = app_path / 'api_key.ini'
        config.read(config_file)

        api_key = "sk-uqaulFmTlu24Onqd70A687FaC4A44dEd8dD2Cf33D85f9e76"

        if not api_key:
            # 如果没有找到API密钥，可以要求用户手动输入或引发异常
            api_key = input("Enter your OpenAI API key: ")

            # 将新的API密钥保存到配置文件中
            config['OpenAI']['API_KEY'] = api_key
            with open(config_file, 'w') as configfile:
                config.write(configfile)

        return api_key

    def process_video_description(self, json_string):
        client = OpenAI(
            base_url="https://api.xty.app/v1", 
            api_key=self.api_key,
            http_client=httpx.Client(
                base_url="https://api.xty.app/v1",
                follow_redirects=True,
            ),
        )

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are about to process a sequence of captions, each corresponding to a distinct frame sampled from a video. Your task is to convert these captions into a cohesive, well-structured paragraph. \
                                            This paragraph should describe the video in a fluid, engaging manner and follows these guidelines: avoiding semantic repetition to the greatest extent, and giving a description in less than 200 characters."},
                {"role": "user", "content": json_string}
            ]
        )
        result = completion.choices[0].message.content
        print(result)
        #print("result: " + result.encode('gbk', errors='replace').decode('gbk'))

        return result # 返回生成结果

    def txt_converter(self, content, addtxt):
        # Step 1. Filtered Prompt
        final_txt = ""
        result_list = content.split(", ")
        it = 0
        for rel in result_list:
            # print(rel)
            it += 1        
            if it == 3 : continue # list[3] 表示图片来源，可丢弃
            if it == 2 : # list[2] 表示图片创作者，一般都是瞎猜的，可丢弃
                rel = rel.split(" by")[0]  
            final_txt += rel + ", "
        
        content = final_txt[:-2]
        if addtxt != None:
            content = content + addtxt #在这里加入附加文本然后一起丢进llm跑
        print("filtered_prompt result:"+content.encode('gbk', errors='replace').decode('gbk'))

        # Step 2. Converted Prompt
        client = OpenAI(
            base_url="https://oneapi.xty.app/v1",
            api_key=self.api_key,
            http_client=httpx.Client(
                base_url="https://oneapi.xty.app/v1",
                follow_redirects=True,
            ),
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Convert in less than 200 characters this image caption to a very concise musical description with musical terms, so that it can be used as a prompt to generate music through AI model, stricly in English. You need to speculate the mood of the given image caption and add it to the music description. You also need to specify a music genre in the description such as pop, hip hop, funk, electronic, jazz, rock, metal, soul, R&B etc."},
                {"role": "user", "content": "a city with a tower and a castle in the background, a detailed matte painting, art nouveau, epic cinematic painting, kingslanding"},
                {"role": "assistant", "content": "A grand orchestral arrangement with thunderous percussion, epic brass fanfares, and soaring strings, creating a cinematic atmosphere fit for a heroic battle."},
                {"role": "user", "content": "a group of people sitting on a beach next to a body of water, tourist destination, hawaii"},
                {"role": "assistant", "content": "Pop dance track with catchy melodies, tropical percussion, and upbeat rhythms, perfect for the beach."},
                {"role": "user", "content": content}
            ]
        )
        converted_result = completion.choices[0].message.content
        print("converted result: " + converted_result.encode('gbk', errors='replace').decode('gbk'))
        return converted_result
    
    def video_txt_converter(self, content, addtxt):
        
        client = OpenAI(
            base_url="https://oneapi.xty.app/v1",
            api_key=self.api_key,
            http_client=httpx.Client(
                base_url="https://oneapi.xty.app/v1",
                follow_redirects=True,
            ),
        )

        if addtxt != None:
            content = content + addtxt #在这里加入附加文本然后一起丢进llm跑
            
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "Convert in less than 200 characters this video caption to a very concise musical description with musical terms, so that it can be used as a prompt to generate music through AI model, stricly in English. \
                                               You need to speculate the mood of the given video caption and add it to the music description. \
                                               You also need to specify a music genre in the description such as pop, hip hop, funk, electronic, jazz, rock, metal, soul, R&B etc."},
                {"role": "user", "content": "Two men playing cellos in a room with a piano and a grand glass window backdrop."},
                {"role": "assistant", "content": "Classical chamber music piece featuring cello duet, intricate piano accompaniment, emotive melodies set in an elegant setting, showcasing intricate melodies and emotional depth, the rich harmonies blend seamlessly in an elegant and refined setting, creating a symphonic masterpiece."},
                {"role": "user", "content": "A man with guitar in hand, captivates a large audience on stage at a concert. The crowd watches in awe as the performer delivers a stellar musical performance."},
                {"role": "assistant", "content": "Rock concert with dynamic guitar riffs, precise drumming, and powerful vocals, creating a captivating and electrifying atmosphere, uniting the audience in excitement and musical euphoria."},
                {"role": "user", "content": content}
            ]
        )
        converted_result = completion.choices[0].message.content
        print("converted result: " + converted_result.encode('gbk', errors='replace').decode('gbk'))
        return converted_result

if __name__ == "__main__":
    
    # content = "a wreath hanging from a rope, an album cover inspired, land art, japanese shibari with flowers, hanging from a tree,the empress’ hanging"
    content = input()
    txt_con = TxtConverter()
    converted_result = txt_con.txt_converter(content)
    # print(converted_result)
