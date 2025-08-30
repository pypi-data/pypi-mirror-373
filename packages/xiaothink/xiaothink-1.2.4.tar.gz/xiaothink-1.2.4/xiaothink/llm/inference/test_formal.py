# -*- coding: utf-8 -*-
# Copyright 2025 Shi Jingqi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import xiaothink.llm.inference.test as test
import xiaothink.llm.inference.test_vision as test_vision
#form
import tempfile

def gen_tempfn():
    # 创建一个临时图片文件名（.png格式）
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_filename = temp_file.name
        print(f"临时图片文件名: {temp_filename}")
        
import re
from xiaothink.llm.inference.vision_api import *

from PIL import Image
import tempfile
import os

import os
import difflib
import matplotlib.pyplot as plt
from tqdm import tqdm

plt.rcParams['font.family'] = 'SimHei'


def compress_image_to_160(img_path):
    """
    按比例压缩图片至最大尺寸160×160×3以内，并返回临时文件路径
    
    参数:
        img_path: 原始图片文件路径
        
    返回:
        压缩后图片的临时文件路径
    """
    # 打开原始图片
    with Image.open(img_path) as img:
        # 确保图片是RGB模式（3通道）
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # 转换为RGB模式，透明部分用白色填充
            background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
            background.paste(img, img.split()[-1])
            img = background.convert("RGB")
        elif img.mode != 'RGB':
            img = img.convert("RGB")
        
        # 获取原始尺寸
        original_width, original_height = img.size
        
        # 计算压缩比例（保持宽高比）
        max_size = 160
        if original_width > max_size or original_height > max_size:
            # 计算宽度和高度的缩放比例
            width_ratio = max_size / original_width
            height_ratio = max_size / original_height
            
            # 取较小的比例以确保缩放后尺寸不超过最大值
            scale_ratio = min(width_ratio, height_ratio)
            
            # 计算新尺寸
            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)
            
            # 按新尺寸缩放图片
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_path = temp_file.name
        temp_file.close()
        
        # 保存压缩后的图片
        img.save(temp_path, 'JPEG', quality=90)
        
        return temp_path

# 使用示例：
# compressed_path = compress_image_to_160("input_image.jpg")
# print(f"压缩后的图片临时路径: {compressed_path}")

def to_vector(img_path, vocab, n_min, n_max, use_patch=True):
    """测试压缩和解压流程"""
    # 压缩
    #img_path=compress_image_to_160(img_path)
    compressed = image_to_compressed(encoder, img_path, vocab, n_min, n_max, patch=use_patch)
    #print(f"压缩后的特征长度: {len(compressed)} 字符")
    #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
    return (compressed)
def to_img(vec, vocab, n_min, n_max, use_patch=True):
    """测试压缩和解压流程"""
    # 压缩
    compressed = compressed_to_image(decoder, vec, vocab, n_min, n_max, patch=use_patch)
    #print(f"压缩后的特征长度: {len(compressed)} 字符")
    #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
    fn=gen_tempfn()
    (compressed).save(fn)
    return fn


vocab, n_min, n_max, vocab_size = None, None, None, None
autoencoder, encoder, decoder = None, None, None

def replace_img(text,v_path,use_patch=1, imgzip_model_path=None):
    global autoencoder, encoder, decoder, vocab, n_min, n_max, vocab_size
    # 检查文本中是否包含完整的<img>标签
    if not '<img>' in text or not '</img>' in text:
        return text
    
    # 加载模型（如果尚未加载）
    global autoencoder, encoder, decoder, vocab
    if autoencoder is None:
        
        autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model(imgzip_model_path))

    if vocab is None:
        vocab, n_min, n_max, vocab_size = load_vocab(v_path)
        
    # 正则表达式匹配<img>标签及其内容
    # 匹配模式：<img>任意字符（非贪婪模式）</img>
    pattern = r'<img>(.*?)</img>'
    
    # 定义替换函数：在路径后添加'666'
    def add_suffix(match):
        global autoencoder, encoder, decoder, vocab, n_min, n_max, vocab_size
        path = match.group(1)
        return f'<img>{to_vector(path, vocab, n_min, n_max, use_patch=use_patch)}</img>'
    
    # 执行替换
    modified_text = re.sub(pattern, add_suffix, text)
    
    return modified_text

def create_black_image(max_shape):
    """创建全黑图片"""
    return np.zeros((max_shape, max_shape, 3), dtype=np.float32)
    
Img_path=None
def replace_img_vision(text,v_path,use_patch=1, max_shape=128, imgzip_model_path=None):
    global autoencoder, encoder, decoder, vocab, n_min, n_max, vocab_size, Img_path
    # 检查文本中是否包含完整的<img>标签
    if not '<img>' in text or not '</img>' in text:
        return text, create_black_image(max_shape)
    
    # 加载模型（如果尚未加载）
    global autoencoder, encoder, decoder, vocab
    if autoencoder is None:
        
        autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model(imgzip_model_path))

    if vocab is None:
        vocab, n_min, n_max, vocab_size = load_vocab(v_path)
        
    # 正则表达式匹配<img>标签及其内容
    # 匹配模式：<img>任意字符（非贪婪模式）</img>
    pattern = r'<img>(.*?)</img>'
    
    # 定义替换函数
    def add_suffix(match):
        global autoencoder, encoder, decoder, vocab, n_min, n_max, vocab_size, Img_path
        path = match.group(1)
        vecres=to_vector(path, vocab, n_min, n_max, use_patch=use_patch)
        Img_path=path
        
        
        return f'<img>{vecres}</img><img/>'
    
    # 执行替换
    modified_text = re.sub(pattern, add_suffix, text)
    
    return modified_text, test_vision.load_image(Img_path, max_shape)

def replace_vec(text,v_path,use_patch=1,imgzip_model_path=None):
    # 检查文本中是否包含完整的<img>标签
    if not '<img>' in text or not '</img>' in text:
        return text
    
    # 加载模型（如果尚未加载）
    global autoencoder, encoder, decoder, vocab
    if autoencoder is None:
        
        autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model(imgzip_model_path))
    if vocab is None:
        vocab, n_min, n_max, vocab_size = load_vocab(v_path)
        
    # 正则表达式匹配<img>标签及其内容
    # 匹配模式：<img>任意字符（非贪婪模式）</img>
    pattern = r'<img>(.*?)</img>'
    
    # 定义替换函数：在路径后添加'666'
    def add_suffix(match):
        path = match.group(1)
        return f'<img>{to_img(path, vocab, n_min, n_max, use_patch=use_patch)}</img>'
    
    # 执行替换
    modified_text = re.sub(pattern, add_suffix, text)
    
    return modified_text




class QianyanModel:
    def __init__(self,ckpt_dir=r'E:\小思框架\论文\ganskchat\ckpt_test_t6_tiny_img2ms',
               MT='t6_tiny',
                 vocab=r'E:\小思框架\论文\ganskchat\vocab_lx3.txt',
                 use_patch=0,
                 imgzip_model_path=None):
        self.model,self.d=test.load(ckpt_dir=ckpt_dir, model_type=MT,
                                    vocab=vocab,
                                    )
        self.v_path=vocab
        self.use_patch=use_patch
        self.his=''
        self.imgzip_model_path=imgzip_model_path
        
    #moe lyric:0.72
    def chat_SingleTurn(self,t,temp=0.8,maxlen=1200,form=1,ontime=True,loop=True,stop=None):#0.85
        t=replace_img(t,self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)
        self.model.reset_states()
        if form==0:
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   ]
        elif form==1:
            inp='{"conversations": [{"role": "user", "content": {inp}}, {"role": "assistant", "content": "'.replace('{inp}',t)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            
            return '-1: form error'
        if stop:
            stopc.append(stop)
        funct=None
        if ontime:
            funct=lambda a:print(a,end='',flush=True)
        if loop:
            inf=test.generate_texts_untilstr_loop
        else:
            inf=test.generate_texts_untilstr
            
        #print(funct)
        ret=inf(self.model, self.d, inp,num_generate=maxlen,
                                 every=funct,
                                 temperature=temp,#0.8
                                stop_c=stopc
                                    #q=[0.6,0.4]
                                    )
        self.model.reset_states()
        return replace_vec(ret,self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)#ret

    def add_his(self,q,a,form=1):#0.85
        q=replace_img(q.replace('\n','\\n'),self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)
        a=replace_img(a.replace('\n','\\n'),self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)
        self.model.reset_states()
        if form==0:
            if self.his!='':
                self.his+='\\nHuman: '+text+'\\nAssistant:'
            else:
               self.his+='Human: '+text+'\\nAssistant:'
            #print('his',self.his)
            t=self.his
            
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   '\\nHuman:',
                   ]
        elif form==1:
            if self.his!='':
                self.his+=', {"role": "user", "content": "{inp}"}'.replace('{inp}',q)
      
            else:
                self.his='{"role": "user", "content": "{inp}"}'.replace('{inp}',q)


            inp='{"conversations": [{his}, {"role": "assistant", "content": "'.replace('{his}',self.his)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            return '-1: form error'

        ret=a
        if form==0:
            self.his+=ret
        elif form==1:
            self.his+=', {"role": "assistant", "content": "{inp}"}'.replace('{inp}',ret)
      
        return replace_vec(ret,self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)
    
    def chat(self,text,temp=0.68,max_len=2048,form=1,ontime=True,
             loop=True,pre_text='',repetition_penalty=1.2,pass_start_char=[]):
        self.model.reset_states()
        text=replace_img(text.replace('\n','\\n'),self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)
        #print(text)
        if form==0:
            if self.his!='':
                self.his+='\\nHuman: '+text+'\\nAssistant:'
            else:
               self.his+='Human: '+text+'\\nAssistant:'
            #print('his',self.his)
            t=self.his
            
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   '\\nHuman:',
                   ]
        elif form==1:
            if self.his!='':
                self.his+=', {"role": "user", "content": "{inp}"}'.replace('{inp}',text)
      
            else:
                self.his='{"role": "user", "content": "{inp}"}'.replace('{inp}',text)

            #print(self.his)
            inp='{"conversations": [{his}, {"role": "assistant", "content": "'.replace('{his}',self.his)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        elif form=='pretrain':
            if self.his!='':
                self.his+='\n{inp} '.replace('{inp}',text)
      
            else:
                self.his='{inp} '.replace('{inp}',text)

            #print(self.his)
            inp='{"text": "<s>{his}'.replace('{his}',self.his)
            stopc=[
                    '</s>',
                    '"}',
                ]
        else:
            print('Err')
            return '-1: form error'
        funct=None
        if ontime:
            funct=lambda a:print(a,end='',flush=True)
            print('\n【实时输出】')
        #print(inp)
        if loop:
            inf=test.generate_texts_untilstr_loop
        else:
            inf=test.generate_texts_untilstr
        ret=pre_text+inf(self.model, self.d, inp+pre_text,num_generate=max_len,
                                 every=funct,
                                 temperature=temp,#0.8
                                stop_c=stopc,
                        repetition_penalty=repetition_penalty,
                         pass_start_char=pass_start_char
                                    #q=[0.6,0.4]
                                    )
        if form==0:
            self.his+=ret
        elif form==1:
            self.his+=', {"role": "assistant", "content": "{inp}"}'.replace('{inp}',ret)
        elif form=='pretrain':
            self.his+='{inp}'.replace('{inp}',ret)
        return replace_vec(ret,self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)#ret

    def chat_(self,text,temp=0.68,max_len=2048,form=1,ontime=True,
             loop=True,pre_text='',repetition_penalty=1.2):
        text=text.replace('\n','\\n')
        self.model.reset_states()
        if form==0:
            if self.his!='':
                self.his+='\\nHuman: '+text+'\\nAssistant:'
            else:
               self.his+='Human: '+text+'\\nAssistant:'
            #print('his',self.his)
            t=self.his
            
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   '\\nHuman:',
                   ]
        elif form==1:
            if self.his!='':
                self.his+=', {"role": "user", "content": "{inp}"}'.replace('{inp}',text)
      
            else:
                self.his='{"role": "user", "content": "{inp}"}'.replace('{inp}',text)

            #print(self.his)
            inp='{"conversations": [{his}, {"role": "assistant", "content": "'.replace('{his}',self.his)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            return '-1: form error'
        funct=None
        if ontime:
            funct=lambda a:print(a,end='',flush=True)
            print('\n【实时输出】')
        #print(funct)
        if loop:
            inf=test.generate_texts_untilstr_loop
        else:
            inf=test.generate_texts_untilstr
        ret=pre_text+inf(self.model, self.d, inp+pre_text,num_generate=max_len,
                                 every=funct,
                                 temperature=temp,#0.8
                                stop_c=stopc,
                        repetition_penalty=repetition_penalty
                                    #q=[0.6,0.4]
                                    )
        if form==0:
            self.his+=ret
        elif form==1:
            self.his+=', {"role": "assistant", "content": "{inp}"}'.replace('{inp}',ret)
      
        return ret
    
    def clean_his(self):
        self.his=''

    def write(self,t,temp=0.85,max_len=150,form=0,ontime=True,onfunc=None):#0.62

        self.model.reset_states()
        if ontime:
            funct=onfunc#lambda a:print(a,end='',flush=True)

        #print(funct)
        ret=test.generate_texts_loop(self.model, self.d, t,num_generate=max_len,
                                 every=funct,
                                 temperature=temp,#0.8
                                    #q=[0.6,0.4]
                                    )
        return ret

    def img2ms(self, img_path, temp=0.28, pre_text='', pass_start_char=[], ontime=False, max_len=128):
        self.clean_his()
        self.model.reset_states()
        ret=self.chat('<img>'+img_path+'</img>请你描述图片内容', repetition_penalty=1.0, temp=temp, pre_text=pre_text, pass_start_char=pass_start_char, ontime=ontime, max_len=max_len)
        self.clean_his()
        self.model.reset_states()
        return ret





    def chat_vision(self,text,temp=0.68,max_len=2048,form=1,ontime=True,
             loop=True,pre_text='',repetition_penalty=1.2,pass_start_char=[],
                    max_shape=224):
        self.model.reset_states()
        text,image=replace_img_vision(text.replace('\n','\\n'),self.v_path,self.use_patch,max_shape=max_shape,imgzip_model_path=self.imgzip_model_path)
        #print(text,image)
        if not loop:
            print('Vision 模型只支持loop生成模式')
        if form==0:
            if self.his!='':
                self.his+='\\nHuman: '+text+'\\nAssistant:'
            else:
               self.his+='Human: '+text+'\\nAssistant:'
            #print('his',self.his)
            t=self.his
            
            inp=f'{{"instruction": "{t}", "input": "", "output": "'
            stopc=['"}\r\n',
                   '"}\n\r',
                   '"}\n',
                   '", "input"',
                   '", "i',
                   '"}',
                   '\\nHuman:',
                   ]
        elif form==1:
            if self.his!='':
                self.his+=', {"role": "user", "content": "{inp}"}'.replace('{inp}',text)
      
            else:
                self.his='{"role": "user", "content": "{inp}"}'.replace('{inp}',text)

            #print(self.his)
            inp='{"conversations": [{his}, {"role": "assistant", "content": "'.replace('{his}',self.his)
            stopc=[
                    '"}]}',
                    '"}',
                ]
        else:
            print('Err')
            return '-1: form error'
        funct=None
        if ontime:
            funct=lambda a:print(a,end='',flush=True)
            print('\n【实时输出】')
        #print(funct)
        #if loop:
        inf=test_vision.generate_texts_untilstr_loop

        ret=pre_text+inf(self.model, self.d, inp+pre_text,num_generate=max_len,
                                 every=funct,
                                 temperature=temp,#0.8
                                stop_c=stopc,
                        repetition_penalty=repetition_penalty,
                         pass_start_char=pass_start_char,
                         image=np.array([image]),
                                    #q=[0.6,0.4]
                                    )
        if form==0:
            self.his+=ret
        elif form==1:
            self.his+=', {"role": "assistant", "content": "{inp}"}'.replace('{inp}',ret)
      
        return replace_vec(ret,self.v_path,self.use_patch,imgzip_model_path=self.imgzip_model_path)#ret

    def img2ms_vision(self, img_path, max_shape=256, temp=0.24, pre_text='', pass_start_char=[], ontime=True):
        self.model.reset_states()
        self.clean_his()
        ret=self.chat_vision('<img>'+img_path+'</img>请你描述图片内容', max_shape=max_shape, temp=temp, pre_text=pre_text, pass_start_char=pass_start_char, ontime=ontime)
        self.clean_his()
        self.model.reset_states()
        return ret


    
 
