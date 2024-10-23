from abc import ABC, abstractmethod
import io
from typing import Union

class AbstractSingletonMeta(type, ABC):
    '''
    单例模式抽象基类元类，保证音乐生成类只有一个实例
    '''
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    

class MusicGenerator(metaclass=AbstractSingletonMeta):
    '''
    音乐生成模型抽象基类，增加模型类时需要继承此类并实现generate方法
    '''
    @property
    @abstractmethod
    def model_name(self):
        pass
    
    @abstractmethod
    def generate(self, text: str, music_duration: int) -> Union[io.BytesIO, str]:
        """
        根据传入文本和音乐时长生成音乐

        Parameters:
            text (str): 音乐生成的提示文本
            music_duration (int): 音乐的时长，单位为秒

        Returns:
            io.BytesIO: 包含生成音乐的字节流对象
        """
        pass

