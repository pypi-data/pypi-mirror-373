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

import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Dense, Reshape, Conv2D, 
    Conv2DTranspose, LeakyReLU, Flatten,
    BatchNormalization, UpSampling2D
)
import numpy as np
from PIL import Image
import os
import tqdm

# 导入num2str模块
import os
import json
import numpy as np

def load_vocab(vocab_file='vocab_lx3.txt', n_min=-500, n_max=500):
    """加载词汇表"""
    if 1:
        with open(vocab_file, 'r', encoding='utf-8') as f:
            vocab_list = eval(f.read())[1:]
            return vocab_list, n_min, n_max, len(vocab_list)

def compress_vector__(vector, vocab_list):
    """压缩向量到字符串 - 基于位置分组"""
    L = len(vector)
    vocab_size = len(vocab_list)
    group_size = vocab_size // L
    
    # 计算每组的值范围
    half_group = group_size // 2
    n_min_i = -half_group
    n_max_i = half_group - 1 if group_size % 2 == 0 else half_group
    #print(n_min_i, n_max_i)
    
    compressed_chars = []
    for i, val in enumerate(vector):
        # 获取当前位置对应的字符组
        start_idx = i * group_size
        end_idx = start_idx + group_size
        group_chars = vocab_list[start_idx:end_idx]
        
        # 截断值到当前组范围
        clipped = np.clip(val, n_min_i, n_max_i)
        # 映射到字符
        idx_in_group = int(clipped - n_min_i)
        compressed_chars.append(group_chars[idx_in_group])
    
    return ''.join(compressed_chars)

def decompress_vector__(text, vocab_list, L=None):
    """从字符串解压回向量 - 基于位置分组"""
    if L == None:
        L=len(text)
    vocab_size = len(vocab_list)
    group_size = vocab_size // L
    
    # 计算每组的值范围
    half_group = group_size // 2
    n_min_i = -half_group
    n_max_i = half_group - 1 if group_size % 2 == 0 else half_group
    
    vector = []
    for i, char in enumerate(text):
        # 获取当前位置对应的字符组
        start_idx = i * group_size
        end_idx = start_idx + group_size
        group_chars = vocab_list[start_idx:end_idx]
        
        # 找到字符在组内的索引
        idx_in_group = group_chars.index(char)
        # 还原数值
        val = idx_in_group + n_min_i
        vector.append(val)
    
    return vector

def compress(text, vocab_list, n_min=-500, n_max=500):
    """压缩文本（基于位置分组）"""
    numbers = [int(x) for x in text.split(',')]
    L = len(numbers)
    return compress_vector__(np.array(numbers), vocab_list)

def decompress(compressed_text, vocab_list, n_min=-500, n_max=500, L=None):
    """解压文本（基于位置分组）"""
    if 0:#L is None:
        raise ValueError("必须提供原始序列长度L")
    
    vector = decompress_vector__(compressed_text, vocab_list, L)
    return ','.join([f"{v:.0f}" for v in vector])

if __name__ == "__main__":
    try:
        # 加载词汇表
        vocab_list, n_min, n_max, vocab_size = load_vocab()
        print(f"加载词汇表长度：{len(vocab_list)}")
        print(f"值范围：{n_min} ~ {n_max}")
        
        # 压缩测试
        test_input = "5,-5,-1,-1,2,-11,5,-2,-37,1,-4,2,2,-2,-47,-1,-1,-2,6,-1,-5,-1,6,-7,1,1,1,-1,-6,-2,1,-2,3,0,3,-1,-1,-2,-6,-7,-3,-7,11,1,1,-0,-1,1,-1,-3,7,3,2,1,-4,4,-5,2,5,-5,2,1,-3,1,-8,-1,5,1,10,-4,-5,5,1,5,11,-1,-1,2,-0,9,1,56,3,-0,1,-1,-1,2,-22,5,11,-7,-31,-3,-1,-5"
        numbers = [int(x) for x in test_input.split(',')]
        L = len(numbers)
        
        compressed = compress(test_input, vocab_list, n_min, n_max)
        print(f"压缩结果：{compressed}")
        print(f"压缩后长度：{len(compressed)} 字符")
        
        # 解压测试
        decompressed = decompress(compressed, vocab_list, n_min, n_max, L=L)
        print(f"解压结果：{decompressed}")
        
        # 验证一致性
        group_size = vocab_size // L
        half_group = group_size // 2
        n_min_i = -half_group
        n_max_i = half_group - 1 if group_size % 2 == 0 else half_group
        
        expected = [str(np.clip(int(x), n_min_i, n_max_i)) for x in test_input.split(',')]
        assert decompressed.split(',') == expected, "解压结果与原始输入不一致"
        print("测试通过！")
    except Exception as e:
        print(f"发生错误：{str(e)}")




#----------------------------------------------------


# 数据预处理函数
def load_and_preprocess_images(image_dir, image_size=(80, 80)):
    """加载并预处理图像数据集"""
    images = []
    err = 0
    for filename in tqdm.tqdm(os.listdir(image_dir)):
        img_path = os.path.join(image_dir, filename)
        try:
            img = Image.open(img_path).resize(image_size).convert('RGB')
        except Exception as e:
            err += 1
            print(f'Error ({err}): {str(e)} - {img_path}')
            continue
        
        img_array = np.array(img).flatten() / 255.0
        if img_array.size != image_size[0] * image_size[1] * 3:
            err += 1
            print(f'尺寸错误 ({err}): {img_path}')
            continue
        images.append(img_array.astype(np.float32))
    
    return np.array(images)



# 图像处理工具函数
def image_to_vector(encoder, img_path):
    """将图像编码为特征向量"""
    img = Image.open(img_path).resize((80, 80)).convert('RGB')
    img_array = np.array(img).astype(np.float32) / 255.0
    return encoder.predict(img_array.reshape(1, 80, 80, 3))[0]

def vector_to_image(decoder, vector):
    """将特征向量解码为图像"""
    decoded = decoder.predict(np.expand_dims(vector, axis=0))[0]
    decoded = (decoded * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(decoded)

def load_model(encoder_path='encoder.h5', decoder_path='decoder.h5'):
    """加载预训练模型"""
    encoder = tf.keras.models.load_model(encoder_path)
    decoder = tf.keras.models.load_model(decoder_path)
    return encoder, decoder

def compress_vector(vector, vocab):
    """压缩特征向量到字符串"""
    # 将向量转换为逗号分隔的字符串
    vector_str = ",".join([f"{v:.0f}" for v in vector])
    return compress(vector_str, vocab)

def decompress_vector(text, vocab):
    """从字符串解压回向量"""
    # 先用num2str解压
    vector_str = decompress(text, vocab)
    # 再转换为向量
    return np.array([float(x) for x in vector_str.split(",")], dtype=np.float32)

def split_autoencoder(model):
    """
    将自编码器模型拆分为autoencoder、encoder和decoder三个独立模型
    """
    encoder = model.get_layer('encoder')
    decoder = model.get_layer('decoder')
    return model, encoder, decoder

def image_to_compressed(encoder, img_path, vocab, n_min, n_max, patch=True):
    """将图像编码为压缩字符串，支持分块处理"""
    if patch:
        # 分块处理模式
        img = Image.open(img_path)
        w, h = img.size
        # 计算分块数量
        cols = (w + 79) // 80
        rows = (h + 79) // 80
        
        # 创建足够大的画布
        canvas = Image.new('RGB', (cols * 80, rows * 80))
        canvas.paste(img, (0, 0))
        
        blocks = []
        for y in range(rows):
            for x in range(cols):
                # 裁剪出 80x80 的块
                block = canvas.crop((x * 80, y * 80, (x + 1) * 80, (y + 1) * 80))
                block_array = np.array(block).astype(np.float32) / 255.0
                
                # 编码并压缩
                vector = encoder.predict(np.expand_dims(block_array, axis=0), verbose=0)[0]
                compressed = ','.join([str(int(i)) for i in vector])
                blocks.append(compress((compressed), vocab, n_min, n_max))
        
        # 添加尺寸信息作为前缀
        return f"{w},{h}|" + "|".join(blocks ) 
    else:
        # 单块处理模式
        img = Image.open(img_path).resize((80, 80)).convert('RGB')
        img_array = np.array(img).astype(np.float32) / 255.0
        vector = encoder.predict(np.expand_dims(img_array, axis=0), verbose=0)[0]
        return compress_vector(vector, vocab)

def compressed_to_image(decoder, compressed_str, vocab, n_min, n_max, patch=True):
    """从压缩字符串解码为图像，支持分块处理"""
    # 先解压整个字符串
    raw_str = compressed_str
    
    if patch:
        # 提取原始尺寸信息
        parts = [decompress(i, vocab, n_min, n_max) for i in raw_str.split('|')[1:]]
        w, h = map(int, raw_str.split('|')[0].split(','))
        block_strs = parts
        
        # 计算分块数量
        cols = (w + 79) // 80
        rows = (h + 79) // 80
        
        if len(block_strs) != rows * cols:
            raise ValueError(f"压缩字符串中的块数量与尺寸信息不匹配: {len(block_strs)} != {rows * cols}")
        
        # 创建空白画布
        canvas = Image.new('RGB', (cols * 80, rows * 80))
        
        for idx, block_str in enumerate(block_strs):
            # 计算当前块的位置
            row = idx // cols
            col = idx % cols
            
            # 解码单个块
            vector = [int(i) for i in (block_str).split(',')]
            decoded = decoder.predict(np.expand_dims(vector, axis=0), verbose=0)[0]
            decoded = (decoded * 255).clip(0, 255).astype(np.uint8)
            block_img = Image.fromarray(decoded)
            
            # 将块粘贴到画布上
            canvas.paste(block_img, (col * 80, row * 80))
        
        # 裁剪回原始尺寸
        return canvas.crop((0, 0, w, h))
    else:
        # 单块处理模式
        vector = decompress_vector(raw_str, vocab)
        decoded = decoder.predict(np.expand_dims(vector, axis=0),verbose=0)[0]
        decoded = (decoded * 255).clip(0, 255).astype(np.uint8)
        return Image.fromarray(decoded)

#

if __name__ == '__main__' and 0:
    autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model('best_pro2_96c.keras'))

    def test_compression(img_path, use_patch=True):
        """测试压缩和解压流程"""
        # 压缩
        compressed = image_to_compressed(encoder, img_path, patch=use_patch)
        print(f"压缩后的特征长度: {len(compressed)} 字符")
        print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
        with open('compressed.txt','w',encoding='utf-8') as f:
            f.write(compressed)
        
        # 解压
        reconstructed = compressed_to_image(decoder, compressed, patch=use_patch)
        reconstructed.save("reconstructed.jpg")
        print("图片已重建并保存为 reconstructed.jpg")
    
    while True:
        img_path = input('请输入图片路径: ')
        use_patch = input('使用分块处理? (y/n): ').lower() == 'y'
        test_compression(img_path, use_patch)

if __name__ == '__main__' and 0:
    autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model('best_pro2_96c.keras'))

    def test_compression(img_path, use_patch=True):
        """测试压缩和解压流程"""
        # 压缩
        compressed = image_to_compressed(encoder, img_path, patch=use_patch)
        print(f"压缩后的特征长度: {len(compressed)} 字符")
        print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
        with open('compressed.txt','w',encoding='utf-8') as f:
            f.write(compressed)
        
        # 解压
        reconstructed = compressed_to_image(decoder, compressed, patch=use_patch)
        reconstructed.save("reconstructed.jpg")
        print("图片已重建并保存为 reconstructed.jpg")
    
    while True:
        img_path = input('请输入图片路径: ')
        use_patch = input('使用分块处理? (y/n): ').lower() == 'y'
        test_compression(img_path, use_patch)
elif 0:
    autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model('best_pro2_96c.keras'))

    temp='''{"conversations": [{"role": "user", "content": "{inp}"}, {"role": "assistant", "content": "{out}"}]}'''
    def to_vector(img_path, use_patch=True):
        """测试压缩和解压流程"""
        # 压缩
        compressed = image_to_compressed(encoder, img_path, patch=use_patch)
        #print(f"压缩后的特征长度: {len(compressed)} 字符")
        #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
        return (compressed)
            
    import os
    for i in tqdm.tqdm(os.listdir('./images_sjk_2_ms')):
        try:
            filepath='./images_sjk_2_ms/'+i
            ms='.'.join(i.split('.')[:-1])
            vec=to_vector(filepath, use_patch=False)
            with open('aidata/best_pro2_96c__img2ms.txt','a',encoding='utf-8') as f:
                f.write(temp.replace('{inp}','<img>'+vec+'</img>请你描述图片内容').replace('{out}',ms))
            with open('aidata/best_pro2_96c__ms2img.txt','a',encoding='utf-8') as f:
                f.write(temp.replace('{out}','<img>'+vec+'</img>').replace('{inp}','请你生成图片：'+ms))
        except Exception as ee:
            print('Error',ee)
            
            
elif 0:
    autoencoder, encoder, decoder = split_autoencoder(tf.keras.models.load_model('moti/best_pro2_96c.keras'))

    def to_vector(img_path, use_patch=True):
        """测试压缩和解压流程"""
        # 压缩
        compressed = image_to_compressed(encoder, img_path, patch=use_patch)
        #print(f"压缩后的特征长度: {len(compressed)} 字符")
        #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
        return (compressed)
    def to_img(vec, use_patch=True):
        """测试压缩和解压流程"""
        # 压缩
        compressed = compressed_to_image(decoder, vec, patch=use_patch)
        #print(f"压缩后的特征长度: {len(compressed)} 字符")
        #print(f"压缩后的内容: {compressed[:100]}...")  # 只打印前100个字符
        return (compressed)
    while 1:
        vec=eval(input('vec:'))
        img = to_img(vec, use_patch=input('use_patch?').lower()=='y')
        img.save("reconstructed.jpg")
        print("图片已重建并保存为 reconstructed.jpg")
    
    
        
        
    while 1:
        filepath=input('img:')
        vec=to_vector(filepath, use_patch=input('use_patch?').lower()=='y')
        print(vec)
    
    
        
