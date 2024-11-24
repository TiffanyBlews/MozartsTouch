from pathlib import Path
import torch
import torchvision
import json
import os
import random 
import numpy as np
import argparse
import decord

# from einops import rearrange
from torchvision import transforms
from tqdm import tqdm
from PIL import Image
from decord import VideoReader, cpu
from transformers import BlipProcessor, BlipForConditionalGeneration

module_path = Path(__file__).resolve().parent.parent  # module_path为模块根目录（`/MozartsTouch`）

decord.bridge.set_bridge('torch')

class PreProcessVideos:
    def __init__(
            self, 
            video_path,
            random_start_frame = False,
            clip_frame_data = False,
            max_frames = 30,
            beam_amount = 7,
            prompt_amount = 25,
            min_prompt_length = 15,
            max_prompt_length = 30,
        ):

        # Paramaters for parsing videos
        self.prompt_amount = prompt_amount
        self.video_path = video_path
        self.random_start_frame = random_start_frame
        self.clip_frame_data = clip_frame_data
        self.max_frames = max_frames
        self.vid_types = (".mp4", ".avi", ".mov", ".webm", ".flv", ".mjpeg")

        # Parameters for BLIP2
        self.processor = None
        self.blip_model = None
        self.beam_amount = beam_amount
        self.min_length = min_prompt_length
        self.max_length = max_prompt_length

        # Helper parameters
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # self.save_dir = save_dir

        # Config parameters
        # self.config_name = config_name
        # self.config_save_name = config_save_name

    # Base dict to hold all the data.
    # {base_config}
    # def build_base_config(self):
    #     return {
    #         "name": self.config_name,
    #         "data": []
    #     }

    # Video dict for individual videos.
    # {base_config: data -> [{video_path, num_frames, data}]}
    # def build_video_config(self, video_path: str, num_frames: int):
    #     return {
    #         "video_path": video_path,
    #         "num_frames": num_frames,
    #         "data": []
    #     }

    # Dict for video frames and prompts / captions.
    # Gets the frame index, then gets a caption for the that frame and stores it.
    # {base_config: data -> [{name, num_frames, data: {frame_index, prompt}}]}
    def build_video_data(self, frame_index: int, prompt: str):
        return {
            "frame_index": frame_index,
            "prompt": prompt
        }

    # Load BLIP for processing
    def load_blip(self, model_name = "blip-image-captioning-base"):
        print("Loading BLIP...")

        processor = BlipProcessor.from_pretrained(module_path / "model" / f"{model_name}_processor")
        model = BlipForConditionalGeneration.from_pretrained(
            module_path / "model" / f"{model_name}_model", torch_dtype=torch.float16
        ).to(self.device)

        self.processor = processor
        self.blip_model = model

    # Process the frames to get the length and image.
    # The limit parameter ensures we don't get near the max frame length.
    def video_processor(
            self, 
            video_reader: VideoReader, 
            num_frames: int, 
            random_start_frame=True,
            frame_num=0
        ):

        frame_number = (
            random.randrange(0, int(num_frames)) if random_start_frame else frame_num
            )
        # print("getting frame: ", frame_number)
        frame = video_reader[frame_number].permute(2,0,1)
        # print("getting image...")
        image = transforms.ToPILImage()(frame).convert("RGB")
        return frame_number, image

    def get_frame_range(self, derterministic):
        return range(self.prompt_amount) if self.random_start_frame else derterministic

    def process_blip(self, image: Image):
        inputs = self.processor(images=image, return_tensors="pt").to(self.device, torch.float16)
        generated_ids = self.blip_model.generate(
                **inputs, 
                num_beams=self.beam_amount, 
                min_length=self.min_length, 
                max_length=self.max_length
            )
        generated_text = self.processor.batch_decode(
            generated_ids, 
            skip_special_tokens=True)[0].strip()
        
        return generated_text
    
    # def get_out_paths(self, prompt, frame_number):
    #     out_name= f"{prompt}_{str(frame_number)}"
    #     save_path = f"{self.save_dir}/{self.config_save_name}"
    #     save_filepath = f"{save_path}/{out_name}.mp4"

    #     return out_name, save_path, save_filepath

    # def save_train_config(self, config: dict):
    #     os.makedirs(self.save_dir, exist_ok=True)

    #     save_json = json.dumps(config, indent=4)
    #     save_dir = f"{self.save_dir}/{self.config_save_name}"
        
    #     with open(f"{save_dir}.json", 'w') as f:
    #         f.write(save_json)

    def save_video(self, save_path, save_filepath, frames):
        os.makedirs(save_path, exist_ok=True)
        torchvision.io.write_video(save_filepath, frames, fps=30)

    # Main loop for processing all videos.
    def process_video(self):
        self.load_blip()
        video_path = self.video_path
        video_frame_list = []

        if not os.path.exists(video_path):
            raise ValueError(f"{video_path} does not exist.")

        try:
            video_reader = VideoReader(video_path, ctx=cpu(0))
            video_len = len(video_reader)
            frame_step = abs(video_len // self.prompt_amount)
            derterministic_range = range(1, abs(video_len - 1), frame_step) if frame_step else range(video_len)
        except:
            print(f"Error loading {video_path}. Video may be unsupported or corrupt.")
            return

        try:
            num_frames = int(len(video_reader))
            # video_config = self.build_video_config(video_path, num_frames)

            for i in tqdm(
                    self.get_frame_range(derterministic_range), 
                    desc=f"Processing {os.path.basename(video_path)}"
                ):

                frame_number, image = self.video_processor(
                    video_reader, 
                    num_frames, 
                    self.random_start_frame,
                    frame_num=i
                )

                prompt = self.process_blip(image)
                video_data = self.build_video_data(frame_number, prompt)
                video_frame_list.append(video_data)

        except Exception as e:
            print(e)
            return

        # print(f"Done. Saving train config to {self.save_dir}.")
        # self.save_train_config(config)
        return str(video_frame_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # parser.add_argument('--config_name', help="The name of the configuration.", type=str, default='My Config')
    # parser.add_argument('--config_save_name', help="The name of the config file that's saved.", type=str, default='my_config')
    parser.add_argument('--video_path', help="The directory where your videos are located.", type=str, default='/root/Mozart-Diancai/Video-BLIP2-Preprocessor/videos')
    # parser.add_argument(
    #     '--random_start_frame', 
    #     help="Use random start frame when processing videos. Good for long videos where frames have different scenes and meanings.", 
    #     action='store_true', 
    #     default=False
    # )
    parser.add_argument(
        '--clip_frame_data', 
        help="Save the frames as video clips to HDD/SDD. Videos clips are saved in the same folder as your json directory.", 
        action='store_true', 
        default=False
    )
    parser.add_argument('--max_frames', help="Maximum frames for clips when --clip_frame_data is enabled.", type=int, default=60)
    parser.add_argument('--beam_amount', help="Amount for BLIP beam search.", type=int, default=7)
    parser.add_argument('--prompt_amount', help="The amount of prompts per video that is processed.", type=int, default=25)
    parser.add_argument('--min_prompt_length', help="Minimum words required in prompt.", type=int, default=15)
    parser.add_argument('--max_prompt_length', help="Maximum words required in prompt.", type=int, default=30)
    # parser.add_argument('--save_dir', help="The directory to save the config to.", type=str, default=f"{os.getcwd()}/train_data")

    args = parser.parse_args()

    
    #processor = PreProcessVideos(**vars(args))
    #processor.process_videos()
    
    #json_file_path = 'Video-BLIP2-Preprocessor/train_data/my_videos.json'
    #content = process_video_description(json_file_path)
    #txt_con = TxtConverter()
    #converted_result = txt_con.txt_converter(content)