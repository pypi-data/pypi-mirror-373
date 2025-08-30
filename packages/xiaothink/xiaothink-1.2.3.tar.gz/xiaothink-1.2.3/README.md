# Xiaothink Python 模块使用文档

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
Xiaothink 是一个以自然语言处理（NLP）为核心的AI研究组织，致力于在少数据、低算力下训练出先进的端侧模型。Xiaothink Python 模块是我们提供的核心工具包，涵盖了文本问答、图文问答、图像压缩、情感分类等多种功能。以下是详细的使用指南和代码示例。

## 目录
1. [安装](#安装)
2. [本地对话模型](#本地对话模型)
3. [图像特征提取与多模态对话](#图像特征提取与多模态对话)
4. [图像压缩转特征技术 (img_zip)](#图像压缩转特征技术-img_zip)
5. [情感分类工具](#情感分类工具)
6. [更新日志](#更新日志)

---

## 安装

首先，您需要通过 pip 安装 Xiaothink 模块：

```bash
pip install xiaothink
```

---

## 注：由于业务范围调整，2025年7月17日后，小思框架将暂停所有WebAI服务，转向端侧AI模型领域研究，本代码库也同步删除相关接口。

---

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

The [NOTICE](NOTICE) file contains additional attribution information for the proprietary technologies included in this module.

---

## 本地纯文本对话模型

对于本地加载的对话模型，根据模型类型的不同，应调用相应的函数来进行对话。

### 单轮对话（即将在未来版本被移除）

适用于单轮对话场景。

### 示例代码

```python
import xiaothink.llm.inference.test_formal as tf

model = tf.QianyanModel(
    ckpt_dir=r'path/to/your/t6_model',
    MT='t6_beta_dense',
    vocab=r'path/to/your/vocab'# vocab文件在模型储存库中已给出
)

while True:
    inp = input('【问】：')
    if inp == '[CLEAN]':
        print('【清空上下文】\n\n')
        model.clean_his()
        continue
    re = model.chat_SingleTurn(inp, temp=0.32)  # 使用 chat_SingleTurn 进行单轮对话
    print('\n【答】：', re, '\n')
```

### 多轮对话

适用于多轮对话场景。

### 示例代码

```python
import xiaothink.llm.inference.test_formal as tf

model = tf.QianyanModel(
    ckpt_dir=r'path/to/your/t6_model',
    MT='t6_beta_dense',
    vocab=r'path/to/your/vocab'# vocab文件在模型储存库中已给出
)

while True:
    inp = input('【问】：')
    if inp == '[CLEAN]':
        print('【清空上下文】\n\n')
        model.clean_his()
        continue
    re = model.chat(inp, temp=0.32)  # 使用 chat 进行多轮对话
    print('\n【答】：', re, '\n')
```

### 文本续写

适用于更灵活的文本续写场景

### 示例代码

```python
import xiaothink.llm.inference.test as test

MT = 't6_beta_dense'
m, d = test.load(
    ckpt_dir=r'path/to/your/t6_model',
    MT='t6_beta_dense',
    vocab=r'path/to/your/vocab'# vocab文件在模型储存库中已给出
)

inp='你好！'
belle_chat = '{"conversations": [{"role": "user", "content": {inp}}, {"role": "assistant", "content": "'.replace('{inp}', inp)    # t6系列中经过指令微调的模型支持的instruct格式
inp_m = belle_chat

ret = test.generate_texts_loop(m, d, inp_m,    
                               num_generate=100,
                               every=lambda a: print(a, end='', flush=True),
                               temperature=0.32,
                               pass_char=['▩'])    #▩是t6系列模型的<unk>标识
```

**重要提示**：对于本地模型，建议调用 `model.chat` 函数进行多轮对话，未进行指令微调的预训练模型建议调用 `test.generate_texts_loop` 函数。** 单轮对话的 `model.chat_SingleTurn` 函数即将在未来版本被移除 **

---

## 图像特征提取与多模态对话

### 双视觉方案

在1.2.0版本中，我们引入了创新的双视觉方案：
1. **图像压缩转特征(img_zip)**：将图像转为文本token插入在对话的任何位置
2. **原生视觉编码器**：将最新的一张图片传入原生视觉模型的视觉编码器（标准做法）

这种方案实现了：
- 基于原生视觉编码器对最新单图进行细节分析
- 基于img_zip技术对上下文中多图的理解能力
- 大幅降低算力资源需求

### 视觉模型使用规范

对于支持视觉的模型，无论是否有图像输入，都应使用以下代码：

```python
from xiaothink.llm.inference.test_formal import QianyanModel

if __name__ == '__main__':
    model = QianyanModel(
        ckpt_dir=r'path/to/your/vision_model',
        MT='t6_standard_vision',  # 注意模型类型为视觉模型
        vocab=r'path/to/your/vocab.txt',
        imgzip_model_path='path/to/img_zip/model.keras'  # 指定img_zip模型路径
    )

    temp = 0.28  # 温度参数
    
    while True:
        inp = input('【问】：')
        if inp == '[CLEAN]':
            print('【清空上下文】\n\n')
            model.clean_his()
            continue
        # 使用chat_vision进行对话
        ret = model.chat_vision(inp, temp=temp, pre_text='', pass_start_char=[])
        print('\n【答】：', ret, '\n')
```

**重要提示**：
- 视觉模型必须使用 `chat_vision` 方法，不能使用 `chat`（仅适用于纯文本模型）
- 必须提前准备好与视觉模型匹配的img_zip图像压缩编码器模型
- 不匹配的模型会导致模型无法理解编码后的token含义

### 图像处理接口

新增两种图像处理接口：

1. **img2ms**（适用于非原生视觉模型）：
   ```python
   description = model.img2ms('path/to/image.jpg', temp=0.28)
   print(description)
   ```

2. **img2ms_vision**（适用于原生视觉模型）：
   ```python
   description = model.img2ms_vision('path/to/image.jpg', temp=0.28, max_shape=224)
   print(description)
   ```

### 图像引用语法

在对话中，使用以下语法引用图像：
```python
<img>图像路径或URL</img>请你描述这张图片
```

模型将自动解析图像路径并提取特征，然后根据图像内容进行回答。

**注意事项**：
1. 图像路径需使用绝对路径以确保正确解析
2. 原生视觉模型只支持分析最近的一张图像
3. img_zip技术支持在上下文中引用多张图像

---

## 图像压缩转特征技术 (img_zip)

`img_zip` 模块提供了先进的图像和视频压缩/解压功能，基于深度学习的特征提取技术。以下是详细的使用方法：

### 1. 命令行交互模式

```bash
python -m xiaothink.llm.img_zip.img_zip
```

运行后会进入交互式命令行界面：

```
===== img_zip 图像视频压缩工具 =====
请输入.keras模型路径: path/to/your/imgzip_model.keras
模型加载完成!

请选择功能:
1. 压缩图像
2. 解压图像
3. 压缩视频
4. 解压视频
5. 图像转数组并保存
6. 从数组加载图像
0. 退出

请选择 (0-6): 
```

### 2. Python 代码调用

```python
from xiaothink.llm.img_zip import ImgZip

# 初始化实例
img_zip = ImgZip(model_path='path/to/your/imgzip_model.keras')

# 压缩图像
compressed_path = img_zip.compress_image(
    img_path='input.jpg',
    patch=True,  # 是否使用分块处理
    save_path='compressed_img'  # 保存路径前缀
)
# 生成两个文件: compressed_img.npy 和 compressed_img.shape

# 解压图像
img_zip.decompress_image(
    compressed_input='compressed_img',  # 压缩文件前缀
    patch=True,  # 是否使用分块处理
    save_path='decompressed.jpg'  # 输出路径
)

# 压缩视频
compressed_paths, metadata_path = img_zip.compress_video(
    video_path='input.mp4',
    output_dir='compressed_video',  # 输出目录
    patch=True  # 是否使用分块处理
)

# 解压视频
img_zip.decompress_video(
    compressed_dir='compressed_video',  # 压缩文件目录
    output_path='decompressed.mp4'  # 输出路径
)

# 图像转数组并保存
img_array = img_zip.image_to_array('input.jpg')
img_zip.save_image_array(img_array, 'image_array.npy')

# 从数组加载图像
loaded_array = img_zip.load_image_array('image_array.npy')
img = img_zip.array_to_image(loaded_array)
img.save('restored.jpg')
```

### 3. 关键功能说明

1. **压缩图像** (`compress_image`)
   - `patch=True`: 将大图切分为80x80块分别处理
   - 输出两个文件: `.npy` (特征向量) 和 `.shape` (原始尺寸信息)

2. **解压图像** (`decompress_image`)
   - 需要`.npy`和`.shape`两个文件
   - 自动恢复原始尺寸

3. **视频处理** (`compress_video`/`decompress_video`)
   - 自动提取视频帧并批量处理
   - 保留原始视频的帧率、分辨率信息
   - 使用临时目录处理中间文件

4. **图像数组转换**
   - `image_to_array`: 将图像转为归一化的float32数组
   - `array_to_image`: 将数组转回图像

#### 4. 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `model_path` | str | img_zip模型路径 (.keras文件) |
| `patch` | bool | 是否使用分块处理 (默认为True) |
| `save_path` | str | 输出文件路径前缀 |
| `img_path` | str | 输入图像路径 |
| `video_path` | str | 输入视频路径 |
| `output_dir` | str | 输出目录路径 |
| `output_path` | str | 输出文件路径 |

#### 5. 处理流程特点

1. **分块处理**:
   - 大图自动分割为80x80块
   - 每块独立编码为特征向量
   - 保留原始尺寸信息

2. **视频处理**:
   - 自动提取帧并批量处理
   - 保留原始视频参数 (fps, 分辨率)
   - 使用临时目录处理中间文件

3. **进度显示**:
   - 所有操作都带详细进度条
   - 显示当前处理步骤和剩余时间

4. **错误处理**:
   - 完善的异常捕获机制
   - 详细的错误信息提示

#### 6. 使用建议

1. 对于大于80x80的图像，推荐使用分块处理 (`patch=True`)
2. 视频处理需要足够磁盘空间存放临时帧文件
3. 确保输入模型与处理任务匹配
4. 使用绝对路径避免文件定位问题

此模块为Xiaothink视觉模型（尤其是非原生的模型）的核心组件，基于高效的图像特征表示和压缩，可以经过微调让任何纯文本AI模型都拥有基础的视觉能力。

---

## 情感分类工具

情感分类工具基于已加载的对话模型，提供文本情感倾向分析功能，可快速判断输入文本的情感类别（如积极、消极、中性等）。

### 功能说明
- 该工具是基于小思框架（Xiaothink T6系列等）模型的定制化接口
- 基于小思框架语言模型实现情感分类，无需额外加载分类模型
- 支持输入超长文本并返回情感分析结果
- 建议使用单论对话增强模型，例如：Xiaothink-T6-0.15B-ST

### 使用示例

```python
from xiaothink.llm.inference.test_formal import *
from xiaothink.llm.tools.classify import *

if __name__ == '__main__':
    # 初始化基础对话模型
    model = QianyanModel(
        ckpt_dir=r'path/to/your/t6_model',  # 模型权重目录  建议使用_ST版模型
        MT='t6_standard',  # 模型类型（需与权重匹配）
        vocab=r'path/to/your/vocab.txt',  # 词汇表路径
        use_patch=0  # 不使用分块处理（纯文本模型）
    )
    
    # 初始化情感分类模型（依赖基础对话模型）
    cmodel = ClassifyModel(model)
    
    # 循环输入文本进行情感分类
    while True:
        inp = input('输入文本：')
        res = cmodel.emotion(inp)  # 调用情感分类接口
        print(res)  # 输出情感分析结果
```

### 注意事项
1. 情感分类模型依赖已初始化的`QianyanModel`，需确保基础模型加载成功
2. 推荐使用经过指令微调的模型（如`t6_standard`），非微调模型可能影响分类精度
4. 输出结果格式为：{'积极': 0.6667, '消极': 0.1667, '中性': 0.1667}


---
小思框架系列模型名称、其对应MT（模型架构版本）以及form（模型prompt传入格式）一览：
| 模型名称（按发布时间）              | mt 参数           | form 参数   |
|-----------------------|------------------|-------------|
| Xiaothink-T6-0.08B       | mt='t6_beta_dense'| form=1      |
| Xiaothink-T6-0.15B       | mt='t6_standard' | form=1      |
| Xiaothink-T6-0.02B       | mt='t6_fast'     | form=1      |
| Xiaothink-T6-0.5B        | mt='t6_large'    | form=1      |
| Xiaothink-T6-0.5B-pretrain| mt='t6_large'    | form='pretrain' |

---

## 更新日志
### 版本 1.2.3 (2025-08-30)
- **新增功能**：
  - 添加了Xiaothink-T6-0.02B系列模型（MT='t6_fast'）
  - 添加了Xiaothink-T6-0.5B系列模型（MT='t6_large'）
  - 在model.chat方法中添加了form='pretrain'的支持，t6系列指令微调的模型应使用form=1，预训练模型应使用form='pretrain'

### 版本 1.2.2 (2025-08-18)
- **新增功能**：
  - 新增情感分类工具，通过`ClassifyModel`实现文本情感倾向分析
  - 新增`xiaothink.llm.tools.classify`模块，支持基于基础对话模型的情感分类
  - 提供`cmodel.emotion(inp)`接口，实时返回文本情感结果

### 版本 1.2.1 (2025-08-16)
- **新增模型**：
  - 添加了Xiaothink-T6-0.15B系列模型（MT='t6_standard'）


### 版本 1.2.0 (2025-08-08)
- **突破性创新**：
  - 添加对原生视觉模型的支持，采用创新的双视觉方案
  - 图像压缩转特征token(img_zip) + 原生视觉编码器双路处理
  - 既保留多图上下文理解能力，又实现单图细节分析

- **新增接口**：
  - `model.chat_vision`：视觉模型专用对话接口
  - `model.img2ms`：非原生视觉模型图像描述接口
  - `model.img2ms_vision`：原生视觉模型图像描述接口（支持max_shape参数）
  
- **模块扩展**：
  - 新增 `xiaothink.llm.img_zip.img_zip` 命令行工具
  - 支持图像和视频的压缩与解压
  - 提供丰富的参数调节压缩质量

- **使用规范**：
  - 视觉模型必须使用 `chat_vision` 方法
  - 必须使用匹配的img_zip编码器模型
  - 图像路径需使用绝对路径

### 版本 1.1.0 (2025-08-02)
- **新增功能**：
  - 添加`img2ms`和`ms2img`接口，实现图像的高压缩率有损压缩
  - 支持将图像转换为AI可读的特征tokens
  - 扩展对话模型支持多模态输入（图像+文本）
  - test_formal中，默认支持将多模态AI生成的特征tokens转为图像并保存至系统临时文件夹。
  
- **技术升级**：
  - 基于小思框架自研的img_zip技术
  - 支持80x80x3图像块的智能压缩
  - 当输出为96个特征值时，结合.7z算法可实现10%超高压缩率
  
- **使用方式**：
  - 在对话中使用`<img>{image_path}</img>`标签插入图像
  - 初始化模型时需指定img_zip模型路径
  - 支持多模态对话（图像描述、图像问答等场景）


---

以上就是 Xiaothink Python 模块的主要功能及使用方法。

如有任何疑问或建议，请随时联系我们：xiaothink@foxmail.com。