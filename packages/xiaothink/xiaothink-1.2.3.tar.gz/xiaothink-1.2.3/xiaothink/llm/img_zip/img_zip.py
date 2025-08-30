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
import numpy as np
from PIL import Image
import os
import tqdm
import cv2
import tempfile
import shutil
import json
from tqdm import tqdm

class ImgZip:
    """图像和视频压缩解压处理类，带详细进度条显示"""
    
    def __init__(self, model_path):
        """初始化ImgZip实例"""
        self.model_path = model_path
        self.autoencoder, self.encoder, self.decoder = self._load_and_split_model()
        # 确定编码器输出向量的维度
        test_input = np.random.rand(1, 80, 80, 3).astype(np.float32)
        self.vector_dim = self.encoder.predict(test_input, verbose=0).shape[1]
    
    def _load_and_split_model(self):
        """加载自编码器模型并拆分编码器和解码器"""
        try:
            print("正在加载模型...")
            autoencoder = tf.keras.models.load_model(self.model_path)
            encoder = autoencoder.get_layer('encoder')
            decoder = autoencoder.get_layer('decoder')
            print("模型加载完成")
            return autoencoder, encoder, decoder
        except Exception as e:
            raise RuntimeError(f"模型加载失败: {str(e)}")
    
    # 图像数组转换与保存
    def image_to_array(self, img_path, image_size=(80, 80)):
        """将图像转换为数组"""
        try:
            img = Image.open(img_path).resize(image_size).convert('RGB')
            return np.array(img).astype(np.float32) / 255.0
        except Exception as e:
            raise IOError(f"图像转换为数组失败: {str(e)}")
    
    def array_to_image(self, img_array):
        """将数组转换为图像"""
        try:
            img_array = (img_array * 255).clip(0, 255).astype(np.uint8)
            return Image.fromarray(img_array)
        except Exception as e:
            raise ValueError(f"数组转换为图像失败: {str(e)}")
    
    def save_image_array(self, array, save_path):
        """将图像数组保存为文件"""
        try:
            np.save(save_path, array)
            return True
        except Exception as e:
            raise IOError(f"保存图像数组失败: {str(e)}")
    
    def load_image_array(self, array_path):
        """从文件加载图像数组"""
        try:
            return np.load(array_path)
        except Exception as e:
            raise IOError(f"加载图像数组失败: {str(e)}")
    
    # 图像压缩与解压
    def compress_image(self, img_path, patch=True, save_path=None):
        """压缩图像"""
        result = {}
        
        if patch:
            # 分块处理模式
            img = Image.open(img_path)
            w, h = img.size
            cols = (w + 79) // 80
            rows = (h + 79) // 80
            
            # 保存形状信息
            result['shape'] = (w, h, cols, rows)
            result['vectors'] = []
            
            # 创建足够大的画布
            canvas = Image.new('RGB', (cols * 80, rows * 80))
            canvas.paste(img, (0, 0))
            
            # 分块处理带进度条
            total_blocks = rows * cols
            with tqdm(total=total_blocks, desc="图像分块编码", unit="块") as pbar:
                for y in range(rows):
                    for x in range(cols):
                        # 裁剪出 80x80 的块
                        block = canvas.crop((x * 80, y * 80, (x + 1) * 80, (y + 1) * 80))
                        block_array = np.array(block).astype(np.float32) / 255.0
                        
                        # 编码
                        vector = self.encoder.predict(np.expand_dims(block_array, axis=0), verbose=0)[0]
                        result['vectors'].append(vector.astype(np.int16))
                        pbar.update(1)
        else:
            # 单块处理模式
            img = Image.open(img_path).resize((80, 80)).convert('RGB')
            img_array = np.array(img).astype(np.float32) / 255.0
            vector = self.encoder.predict(np.expand_dims(img_array, axis=0), verbose=0)[0]
            result['vector'] = vector.astype(np.int16)
            result['shape'] = (80, 80)
        
        # 保存压缩结果
        if save_path:
            # 分离形状信息和向量数据
            shape_path = save_path + ".shape"
            with open(shape_path, 'w') as f:
                json.dump(result['shape'], f)
            
            # 保存向量数据
            if patch:
                vectors = np.array(result['vectors'])
                np.save(save_path, vectors)
            else:
                np.save(save_path, result['vector'])
            return save_path
        else:
            return result
    
    def decompress_image(self, compressed_input, patch=True, save_path=None):
        """解压图像"""
        # 加载压缩数据
        if isinstance(compressed_input, str) and os.path.exists(compressed_input + ".npy"):
            # 从文件加载
            data = {}
            # 加载形状信息
            shape_path = compressed_input + ".shape"
            with open(shape_path, 'r') as f:
                data['shape'] = json.load(f)
            
            # 加载向量数据
            vector_data = np.load(compressed_input + ".npy")
            if patch:
                data['vectors'] = vector_data
            else:
                data['vector'] = vector_data
        else:
            # 使用内存中的数据
            data = compressed_input
        
        if patch:
            # 提取原始尺寸信息
            w, h, cols, rows = data['shape']
            vectors = data['vectors']
            
            if len(vectors) != rows * cols:
                raise ValueError(f"压缩数据中的块数量与尺寸信息不匹配: {len(vectors)} != {rows * cols}")
            
            # 创建空白画布
            canvas = Image.new('RGB', (cols * 80, rows * 80))
            
            # 分块解码带进度条
            total_blocks = len(vectors)
            with tqdm(total=total_blocks, desc="图像分块解码", unit="块") as pbar:
                for idx, vector in enumerate(vectors):
                    # 计算当前块的位置
                    row = idx // cols
                    col = idx % cols
                    
                    # 解码单个块
                    decoded = self.decoder.predict(np.expand_dims(vector, axis=0), verbose=0)[0]
                    decoded = (decoded * 255).clip(0, 255).astype(np.uint8)
                    block_img = Image.fromarray(decoded)
                    
                    # 将块粘贴到画布上
                    canvas.paste(block_img, (col * 80, row * 80))
                    pbar.update(1)
            
            # 裁剪回原始尺寸
            img = canvas.crop((0, 0, w, h))
        else:
            # 单块处理模式
            vector = data['vector']
            decoded = self.decoder.predict(np.expand_dims(vector, axis=0), verbose=0)[0]
            decoded = (decoded * 255).clip(0, 255).astype(np.uint8)
            img = Image.fromarray(decoded)
        
        # 保存解压结果
        if save_path:
            img.save(save_path)
        
        return img
    
    # 视频处理函数
    def _extract_frames(self, video_path, temp_dir=None):
        """从视频中提取帧，带进度条"""
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()
        
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_paths = []
        frame_count = 0
        
        # 提取帧带进度条
        with tqdm(total=total_frames, desc="提取视频帧", unit="帧") as pbar:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 转换为RGB格式(OpenCV默认是BGR)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_img = Image.fromarray(frame_rgb)
                
                # 保存帧
                frame_path = os.path.join(temp_dir, f"frame_{frame_count:06d}.jpg")
                frame_img.save(frame_path)
                frame_paths.append(frame_path)
                
                frame_count += 1
                pbar.update(1)
        
        cap.release()
        return frame_paths, (fps, width, height), temp_dir
    
    def _frames_to_video(self, frame_paths, output_path, fps, width, height):
        """将帧组合成视频，带进度条"""
        # 定义编码器和创建VideoWriter对象
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        # 组合帧带进度条
        with tqdm(total=len(frame_paths), desc="合成视频帧", unit="帧") as pbar:
            for frame_path in frame_paths:
                # 读取图像并转换为BGR格式
                frame = cv2.imread(frame_path)
                # 确保图像尺寸正确
                frame = cv2.resize(frame, (width, height))
                out.write(frame)
                pbar.update(1)
        
        out.release()
    
    def compress_video(self, video_path, output_dir, patch=True):
        """压缩视频，带详细进度条"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("开始视频压缩流程...")
        
        # 提取帧
        print("步骤1/3: 提取视频帧")
        frame_paths, (fps, width, height), temp_dir = self._extract_frames(video_path)
        frame_count = len(frame_paths)
        print(f"成功提取 {frame_count} 帧")
        
        # 保存视频元数据
        metadata = {
            "fps": fps,
            "width": width,
            "height": height,
            "frame_count": frame_count,
            "patch": patch
        }
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        # 压缩每一帧
        print("步骤2/3: 压缩视频帧")
        compressed_paths = []
        for i, frame_path in enumerate(tqdm(frame_paths, desc="压缩帧", unit="帧")):
            compressed_path = os.path.join(output_dir, f"frame_{i:06d}")
            self.compress_image(frame_path, patch=patch, save_path=compressed_path)
            compressed_paths.append(compressed_path)
        
        # 清理临时文件
        print("步骤3/3: 清理临时文件")
        with tqdm(total=len(frame_paths), desc="清理文件", unit="个") as pbar:
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
                pbar.update(1)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        print(f"视频压缩完成，共处理 {frame_count} 帧")
        return compressed_paths, metadata_path
    
    def decompress_video(self, compressed_dir, output_path):
        """解压视频，带详细进度条"""
        print("开始视频解压流程...")
        
        # 读取元数据
        metadata_path = os.path.join(compressed_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"找不到元数据文件: {metadata_path}")
            
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        fps = float(metadata['fps'])
        width = int(metadata['width'])
        height = int(metadata['height'])
        frame_count = int(metadata['frame_count'])
        patch = metadata['patch']
        
        print(f"视频信息: 分辨率 {width}x{height}, 帧率 {fps:.2f}, 共 {frame_count} 帧")
        
        # 创建临时目录保存解压的帧
        temp_dir = tempfile.mkdtemp()
        frame_paths = []
        
        # 解压每一帧
        print("步骤1/2: 解压视频帧")
        for i in tqdm(range(frame_count), desc="解压帧", unit="帧"):
            compressed_path = os.path.join(compressed_dir, f"frame_{i:06d}")
            if not os.path.exists(compressed_path + ".npy"):
                raise FileNotFoundError(f"找不到压缩帧文件: {compressed_path}")
                
            frame_path = os.path.join(temp_dir, f"frame_{i:06d}.jpg")
            self.decompress_image(compressed_path, patch=patch, save_path=frame_path)
            frame_paths.append(frame_path)
        
        # 将帧组合成视频
        print("步骤2/2: 合成视频")
        self._frames_to_video(frame_paths, output_path, fps, width, height)
        
        # 清理临时文件
        print("清理临时文件...")
        with tqdm(total=len(frame_paths), desc="清理文件", unit="个") as pbar:
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
                pbar.update(1)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)
        
        print(f"视频解压完成，已保存到 {output_path}")


def interactive_mode():
    """交互模式，允许用户通过命令行使用库功能"""
    print("===== img_zip 图像视频压缩工具 =====")
    model_path = input("请输入.keras模型路径: ")
    
    try:
        img_zip = ImgZip(model_path)
        print("模型加载完成!")
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        return
    
    while True:
        print("\n请选择功能:")
        print("1. 压缩图像")
        print("2. 解压图像")
        print("3. 压缩视频")
        print("4. 解压视频")
        print("5. 图像转数组并保存")
        print("6. 从数组加载图像")
        print("0. 退出")
        
        choice = input("请选择 (0-6): ")
        
        if choice == '0':
            print("感谢使用，再见!")
            break
        
        elif choice == '1':
            img_path = input("请输入图像路径: ")
            if not os.path.exists(img_path):
                print("错误: 图像文件不存在")
                continue
                
            use_patch = input("使用分块处理? (y/n): ").lower() == 'y'
            save_path = input("请输入保存压缩结果的路径前缀: ")
            
            try:
                img_zip.compress_image(img_path, patch=use_patch, save_path=save_path)
                print(f"成功: 图像已压缩并保存到 {save_path}.npy 和 {save_path}.shape")
            except Exception as e:
                print(f"失败: {str(e)}")
        
        elif choice == '2':
            compressed_path = input("请输入压缩文件路径前缀: ")
            if not os.path.exists(compressed_path + ".npy"):
                print("错误: 压缩文件不存在")
                continue
                
            use_patch = input("使用分块处理? (y/n): ").lower() == 'y'
            save_path = input("请输入保存解压结果的路径: ")
            
            try:
                img_zip.decompress_image(compressed_path, patch=use_patch, save_path=save_path)
                print(f"成功: 图像已解压并保存到 {save_path}")
            except Exception as e:
                print(f"失败: {str(e)}")
        
        elif choice == '3':
            video_path = input("请输入视频路径: ")
            if not os.path.exists(video_path):
                print("错误: 视频文件不存在")
                continue
                
            output_dir = input("请输入保存压缩结果的目录: ")
            use_patch = input("使用分块处理? (y/n): ").lower() == 'y'
            
            try:
                _, _ = img_zip.compress_video(video_path, output_dir, patch=use_patch)
                print(f"成功: 视频已压缩并保存到 {output_dir}")
            except Exception as e:
                print(f"失败: {str(e)}")
        
        elif choice == '4':
            compressed_dir = input("请输入压缩帧所在目录: ")
            if not os.path.exists(compressed_dir):
                print("错误: 压缩目录不存在")
                continue
                
            output_path = input("请输入保存解压视频的路径: ")
            
            try:
                img_zip.decompress_video(compressed_dir, output_path)
                print(f"成功: 视频已解压并保存到 {output_path}")
            except Exception as e:
                print(f"失败: {str(e)}")
        
        elif choice == '5':
            img_path = input("请输入图像路径: ")
            if not os.path.exists(img_path):
                print("错误: 图像文件不存在")
                continue
                
            save_path = input("请输入保存数组的路径 (.npy): ")
            
            try:
                img_array = img_zip.image_to_array(img_path)
                img_zip.save_image_array(img_array, save_path)
                print(f"成功: 图像已转换为数组并保存到 {save_path}")
            except Exception as e:
                print(f"失败: {str(e)}")
        
        elif choice == '6':
            array_path = input("请输入数组文件路径 (.npy): ")
            if not os.path.exists(array_path):
                print("错误: 数组文件不存在")
                continue
                
            save_path = input("请输入保存图像的路径: ")
            
            try:
                img_array = img_zip.load_image_array(array_path)
                img = img_zip.array_to_image(img_array)
                img.save(save_path)
                print(f"成功: 数组已转换为图像并保存到 {save_path}")
            except Exception as e:
                print(f"失败: {str(e)}")
        
        else:
            print("无效的选择，请重试")


if __name__ == "__main__":
    interactive_mode()
