from openai import OpenAI
from pathlib import Path
import httpx
import yaml
from loguru import logger


module_path = Path(__file__).resolve().parent.parent  # module_path为模块根目录（`/MozartsTouch`）
with open(module_path / 'config.yaml', 'r', encoding='utf8') as file:
    config = yaml.safe_load(file)

class TxtConverter:
    def __init__(self):
        # assert config['LLM_MODEL_CONFIG']['PLATFORM_TYPE']
        if config['USE_LLM']:
            self.use_llm = True
            self.model = config['DEFAULT_LLM_MODEL']
            self.api_url = config['LLM_MODEL_CONFIG']['API_BASE_URL']
            self.api_key = config['LLM_MODEL_CONFIG']['API_KEY']
            
            if not self.api_key:
                # 如果没有找到API密钥，可以要求用户手动输入或引发异常
                api_key = input("Enter your OpenAI API key: ")

                # 将新的API密钥保存到配置文件中
                config['LLM_MODEL_CONFIG']['API_KEY'] = api_key
                with open(module_path / 'config.yaml', 'w') as file:
                    yaml.dump(config, file)

            self.client = OpenAI(
                base_url=self.api_url, 
                api_key=self.api_key,
                http_client=httpx.Client(
                    base_url=self.api_url,
                    follow_redirects=True,
                ),
            )

        else:
            self.use_llm = False

    def process_video_description(self, json_string):
        if not self.use_llm:
            return json_string
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are about to process a sequence of captions, each corresponding to a distinct frame sampled from a video. Your task is to convert these captions into a cohesive, well-structured paragraph. \
                                            This paragraph should describe the video in a fluid, engaging manner and follows these guidelines: avoiding semantic repetition to the greatest extent, and giving a description in less than 200 characters."},
                {"role": "user", "content": json_string}
            ]
        )
        result = completion.choices[0].message.content
        logger.info(result)

        return result # 返回生成结果

    def txt_converter(self, content, addtxt = None):
        # # Step 1. Filtered Prompt
        # final_txt = ""
        # result_list = content.split(", ")
        # it = 0
        # for rel in result_list:
        #     # print(rel)
        #     it += 1        
        #     if it == 3 : continue # list[3] 表示图片来源，可丢弃
        #     if it == 2 : # list[2] 表示图片创作者，一般都是瞎猜的，可丢弃
        #         rel = rel.split(" by")[0]  
        #     final_txt += rel + ", "
        
        # content = final_txt[:-2]
        if addtxt:
            content = content + addtxt #在这里加入附加文本然后一起丢进llm跑
        # logger.info("filtered_prompt result:"+content.encode('utf8', errors='replace').decode('utf8'))

        if not self.use_llm:
            return content

        # Step 2. Converted Prompt
        completion = self.client.chat.completions.create(
            model=self.model,
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
        logger.info("converted result: " + converted_result.encode('utf8', errors='replace').decode('utf8'))
        return converted_result
    
    def video_txt_converter(self, content, addtxt = None):
        if addtxt:
            content = content + addtxt #在这里加入附加文本然后一起丢进llm跑

        if not self.use_llm:
            return content
        
        completion = self.client.chat.completions.create(
            model=self.model,
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
        logger.info("converted result: " + converted_result.encode('utf8', errors='replace').decode('utf8'))
        return converted_result

if __name__ == "__main__":
    
    # content = "a wreath hanging from a rope, an album cover inspired, land art, japanese shibari with flowers, hanging from a tree,the empress’ hanging"
    content = input()
    txt_con = TxtConverter()
    converted_result = txt_con.txt_converter(content)
