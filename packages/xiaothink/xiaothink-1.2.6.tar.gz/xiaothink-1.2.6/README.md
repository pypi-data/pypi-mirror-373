# Xiaothink Python Module Usage Documentation

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
Xiaothink is an AI research organization focused on Natural Language Processing (NLP), dedicated to training advanced on-device models with limited data and computing resources. The Xiaothink Python module is our core toolkit, offering functionalities such as text-based Q&A, visual Q&A, image compression, sentiment classification, and more. Below is a detailed usage guide with code examples.

## Table of Contents
1. [Installation](#installation)
2. [Local Dialogue Model](#local-dialogue-model)
3. [Image Feature Extraction and Multimodal Dialogue](#image-feature-extraction-and-multimodal-dialogue)
4. [Image Compression to Feature Technology (img_zip)](#image-compression-to-feature-technology-img_zip)
5. [Sentiment Classification Tool](#sentiment-classification-tool)
6. [Changelog](#changelog)

---

## Installation

First, install the Xiaothink module via pip:

```bash
pip install xiaothink
```

---

## Note: Due to business scope adjustments, after July 17, 2025, the Xiaothink framework will suspend all WebAI services and shift focus to on-device AI model research. This code repository will also remove related interfaces accordingly.

---

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

The [NOTICE](NOTICE) file contains additional attribution information for the proprietary technologies included in this module.

---

## Local Text-Only Dialogue Model

For locally loaded dialogue models, the corresponding function should be called based on the model type.

### Single-Turn Dialogue (To be removed in a future version)

Suitable for single-turn dialogue scenarios.

### Example Code

```python
import xiaothink.llm.inference.test_formal as tf

model = tf.QianyanModel(
    ckpt_dir=r'path/to/your/t6_model',
    MT='t6_beta_dense',
    vocab=r'path/to/your/vocab' # The vocab file is provided in the model repository
)

while True:
    inp = input('[Question]:')
    if inp == '[CLEAN]':
        print('[Clear Context]\n\n')
        model.clean_his()
        continue
    re = model.chat_SingleTurn(inp, temp=0.32)  # Use chat_SingleTurn for single-turn dialogue
    print('\n[Answer]:', re, '\n')
```

### Multi-Turn Dialogue

Suitable for multi-turn dialogue scenarios.

### Example Code

```python
import xiaothink.llm.inference.test_formal as tf

model = tf.QianyanModel(
    ckpt_dir=r'path/to/your/t6_model',
    MT='t6_beta_dense',
    vocab=r'path/to/your/vocab' # The vocab file is provided in the model repository
)

while True:
    inp = input('[Question]:')
    if inp == '[CLEAN]':
        print('[Clear Context]\n\n')
        model.clean_his()
        continue
    re = model.chat(inp, temp=0.32)  # Use chat for multi-turn dialogue
    print('\n[Answer]:', re, '\n')
```

### Text Completion

Suitable for more flexible text completion scenarios.

### Example Code

```python
import xiaothink.llm.inference.test as test

MT = 't6_beta_dense'
m, d = test.load(
    ckpt_dir=r'path/to/your/t6_model',
    MT='t6_beta_dense',
    vocab=r'path/to/your/vocab' # The vocab file is provided in the model repository
)

inp='Hello!'
belle_chat = '{"conversations": [{"role": "user", "content": {inp}}, {"role": "assistant", "content": "'.replace('{inp}', inp)    # The instruct format supported by instruction-tuned models in the T6 series
inp_m = belle_chat

ret = test.generate_texts_loop(m, d, inp_m,
                               num_generate=100,
                               every=lambda a: print(a, end='', flush=True),
                               temperature=0.32,
                               pass_char=[b'\xE2\x96\xA9'.decode()])    # b'\xE2\x96\xA9' is the <unk> identifier for T6 series models
```

**Important Note**: For local models, it is recommended to use the `model.chat` function for multi-turn dialogue. Pre-trained models without instruction tuning should use the `test.generate_texts_loop` function. **The single-turn dialogue function `model.chat_SingleTurn` will be removed in a future version.**

---

## Image Feature Extraction and Multimodal Dialogue

### Dual-Vision Solution

Version 1.2.0 introduces an innovative dual-vision solution:
1. **Image Compression to Feature (img_zip)**: Converts images into text tokens that can be inserted anywhere in the dialogue.
2. **Native Visual Encoder**: The latest image is passed to the native visual encoder of the vision model (standard practice).

This solution achieves:
- Detailed analysis of the latest single image via the native visual encoder.
- Understanding of multiple images in the context via img_zip technology.
- Significantly reduced computational resource requirements.

### Vision Model Usage Specification

For vision-enabled models, use the following code regardless of whether there is image input:

```python
from xiaothink.llm.inference.test_formal import QianyanModel

if __name__ == '__main__':
    model = QianyanModel(
        ckpt_dir=r'path/to/your/vision_model',
        MT='t6_standard_vision',  # Note: The model type is a vision model
        vocab=r'path/to/your/vocab.txt',
        imgzip_model_path='path/to/img_zip/model.keras'  # Specify the img_zip model path
    )

    temp = 0.28  # Temperature parameter

    while True:
        inp = input('[Question]:')
        if inp == '[CLEAN]':
            print('[Clear Context]\n\n')
            model.clean_his()
            continue
        # Use chat_vision for dialogue
        ret = model.chat_vision(inp, temp=temp, pre_text='', pass_start_char=[])
        print('\n[Answer]:', ret, '\n')
```

**Important Notes**:
- Vision models must use the `chat_vision` method; do not use `chat` (which is only for text-only models).
- The img_zip image compression encoder model must be prepared in advance and must match the vision model.
- Mismatched models will prevent the model from understanding the encoded tokens.

### Image Processing Interfaces

Two new image processing interfaces are added:

1. **img2ms** (For non-native vision models):
   ```python
   description = model.img2ms('path/to/image.jpg', temp=0.28)
   print(description)
   ```

2. **img2ms_vision** (For native vision models):
   ```python
   description = model.img2ms_vision('path/to/image.jpg', temp=0.28, max_shape=224)
   print(description)
   ```

### Image Reference Syntax

Use the following syntax to reference images in dialogue:
```python
<img>Image path or URL</img> Please describe this image.
```

The model will automatically parse the image path, extract features, and answer based on the image content.

**Notes**:
1. Use absolute paths for image paths to ensure correct parsing.
2. Native vision models only support analyzing the most recent single image.
3. img_zip technology supports referencing multiple images in the context.

---

## Image Compression to Feature Technology (img_zip)

The `img_zip` module provides advanced image and video compression/decompression functionalities based on deep learning feature extraction. Below is the detailed usage:

### 1. Command-Line Interactive Mode

```bash
python -m xiaothink.llm.img_zip.img_zip
```

After running, you will enter an interactive command-line interface:

```
===== img_zip Image/Video Compression Tool =====
Please enter the .keras model path: path/to/your/imgzip_model.keras
Model loaded successfully!

Please select a function:
1. Compress Image
2. Decompress Image
3. Compress Video
4. Decompress Video
0. Exit

Please choose (0-4):
```

### 2. Python Code Invocation

```python
from xiaothink.llm.img_zip.img_zip import ImgZip

# Initialize instance
img_zip = ImgZip(model_path='path/to/your/imgzip_model.keras')

# Compress Image
compressed_path = img_zip.compress_image(
    img_path='input.jpg',
    patch=True,  # Whether to use patch processing
    save_path='compressed_img'  # Save path prefix
    ability=0.02, # New in 1.2.5: Set custom compression rate to 0.02 (when ability is 0, it means not using custom compression rate). The algorithm calculates and compresses to a size close to the target (theoretical calculation may differ from actual size).
)

# Two files are generated: compressed_img.npy and compressed_img.shape

# Decompress Image
img_zip.decompress_image(
    compressed_input='compressed_img',  # Compressed file prefix
    patch=True,  # Whether to use patch processing
    save_path='decompressed.jpg'  # Output path
)

# Compress Video
compressed_paths, metadata_path = img_zip.compress_video(
    video_path='input.mp4',
    output_dir='compressed_video',  # Output directory
    patch=True  # Whether to use patch processing
)

# Decompress Video
img_zip.decompress_video(
    compressed_dir='compressed_video',  # Compressed file directory
    output_path='decompressed.mp4'  # Output path
)

# Convert image to array and save
img_array = img_zip.image_to_array('input.jpg')
img_zip.save_image_array(img_array, 'image_array.npy')

# Load image from array
loaded_array = img_zip.load_image_array('image_array.npy')
img = img_zip.array_to_image(loaded_array)
img.save('restored.jpg')
```

### 3. Key Function Descriptions

1. **Compress Image** (`compress_image`)
   - `patch=True`: Splits large images into 80x80 patches for separate processing.
   - Outputs two files: `.npy` (feature vectors) and `.shape` (original dimension information).

2. **Decompress Image** (`decompress_image`)
   - Requires both `.npy` and `.shape` files.
   - Automatically restores original dimensions.

3. **Video Processing** (`compress_video`/`decompress_video`)
   - Automatically extracts video frames and processes them in batches.
   - Preserves original video parameters (frame rate, resolution).
   - Uses temporary directories for intermediate files.

#### 4. Parameter Descriptions

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_path` | str | Path to the img_zip model (.keras file) |
| `patch` | bool | Whether to use patch processing (default: True) |
| `save_path` | str | Output file path prefix |
| `img_path` | str | Input image path |
| `video_path` | str | Input video path |
| `output_dir` | str | Output directory path |
| `output_path` | str | Output file path |

#### 5. Processing Flow Characteristics

1. **Patch Processing**:
   - Large images are automatically split into 80x80 patches.
   - Each patch is independently encoded into feature vectors.
   - Original dimension information is preserved.

2. **Video Processing**:
   - Frames are automatically extracted and processed in batches.
   - Original video parameters (fps, resolution) are preserved.
   - Temporary directories are used for intermediate files.

3. **Progress Display**:
   - All operations include detailed progress bars.
   - Current processing step and remaining time are displayed.

4. **Error Handling**:
   - Comprehensive exception catching mechanism.
   - Detailed error message prompts.

#### 6. Usage Recommendations

1. For images larger than 80x80, use patch processing (`patch=True`).
2. Video processing requires sufficient disk space for temporary frame files.
3. Ensure the input model matches the processing task.
4. Use absolute paths to avoid file location issues.

This module is a core component of Xiaothink vision models (especially non-native ones), based on efficient image feature representation and compression. It can be fine-tuned to give any text-only AI model basic visual capabilities.

---

## Sentiment Classification Tool

The sentiment classification tool, based on a loaded dialogue model, provides text sentiment analysis functionality, quickly determining the sentiment category (e.g., positive, negative, neutral) of input text.

### Function Description
- This tool is a customized interface based on the Xiaothink framework (e.g., Xiaothink T6 series) models.
- Sentiment classification is implemented using the Xiaothink framework language model without needing to load an additional classification model.
- Supports input of very long texts and returns sentiment analysis results.
- It is recommended to use single-turn dialogue enhanced models, such as Xiaothink-T6-0.15B-ST.

### Usage Example

```python
from xiaothink.llm.inference.test_formal import *
from xiaothink.llm.tools.classify import *

if __name__ == '__main__':
    # Initialize the base dialogue model
    model = QianyanModel(
        ckpt_dir=r'path/to/your/t6_model',  # Model weights directory. It is recommended to use the _ST version model.
        MT='t6_standard',  # Model type (must match the weights)
        vocab=r'path/to/your/vocab.txt',  # Vocabulary path
        use_patch=0  # Do not use patch processing (text-only model)
    )

    # Initialize the sentiment classification model (depends on the base dialogue model)
    cmodel = ClassifyModel(model)

    # Loop for inputting text for sentiment classification
    while True:
        inp = input('Input text:')
        res = cmodel.emotion(inp)  # Call the sentiment classification interface
        print(res)  # Output the sentiment analysis result
```

### Notes
1. The sentiment classification model depends on an initialized `QianyanModel`; ensure the base model loads successfully.
2. It is recommended to use instruction-tuned models (e.g., `t6_standard`); non-tuned models may affect classification accuracy.
4. The output result format is: {'Positive': 0.6667, 'Negative': 0.1667, 'Neutral': 0.1667}

---
Overview of Xiaothink framework series model names, their corresponding MT (model architecture version), and form (model prompt input format):
| Model Name (by release date)      | mt Parameter        | form Parameter |
|-----------------------------------|---------------------|----------------|
| Xiaothink-T6-0.08B                | mt='t6_beta_dense'  | form=1         |
| Xiaothink-T6-0.15B                | mt='t6_standard'    | form=1         |
| Xiaothink-T6-0.02B                | mt='t6_fast'        | form=1         |
| Xiaothink-T6-0.5B                 | mt='t6_large'       | form=1         |
| Xiaothink-T6-0.5B-pretrain        | mt='t6_large'       | form='pretrain' |
Note: This series of models only supports Chinese!

---

## Changelog
### Version 1.2.6 (2025-09-02)
- **Updated Interface**:
  - Added "Custom Compression Rate" feature to the ImgZIP command-line interface, supporting compression rates other than the model's native rate (achieved by calculating and scaling the original image).

### Version 1.2.4 (2025-08-30)
- **Updated Interface**:
  - Updated the import method for ImgZIP-related interfaces in the documentation to: `from xiaothink.llm.img_zip.img_zip import ImgZip`

### Version 1.2.3 (2025-08-30)
- **New Features**:
  - Added Xiaothink-T6-0.02B series models (MT='t6_fast').
  - Added Xiaothink-T6-0.5B series models (MT='t6_large').
  - Added support for `form='pretrain'` in the `model.chat` method. T6 series instruction-tuned models should use `form=1`, while pre-trained models should use `form='pretrain'`.

### Version 1.2.2 (2025-08-18)
- **New Features**:
  - Added a sentiment classification tool, implementing text sentiment analysis via `ClassifyModel`.
  - Added the `xiaothink.llm.tools.classify` module, supporting sentiment classification based on the base dialogue model.
  - Provided the `cmodel.emotion(inp)` interface for real-time text sentiment results.

### Version 1.2.1 (2025-08-16)
- **New Models**:
  - Added Xiaothink-T6-0.15B series models (MT='t6_standard').

### Version 1.2.0 (2025-08-08)
- **Breakthrough Innovation**:
  - Added support for native vision models using an innovative dual-vision solution.
  - Dual-path processing: Image compression to feature tokens (img_zip) + native visual encoder.
  - Retains multi-image context understanding while enabling detailed single-image analysis.

- **New Interfaces**:
  - `model.chat_vision`: Dedicated dialogue interface for vision models.
  - `model.img2ms`: Image description interface for non-native vision models.
  - `model.img2ms_vision`: Image description interface for native vision models (supports max_shape parameter).

- **Module Expansion**:
  - Added `xiaothink.llm.img_zip.img_zip` command-line tool.
  - Supports compression and decompression of images and videos.
  - Provides rich parameters to adjust compression quality.

- **Usage Specifications**:
  - Vision models must use the `chat_vision` method.
  - A matching img_zip encoder model must be used.
  - Image paths must be absolute paths.

### Version 1.1.0 (2025-08-02)
- **New Features**:
  - Added `img2ms` and `ms2img` interfaces for high compression rate lossy image compression.
  - Supports converting images into AI-readable feature tokens.
  - Extended dialogue models to support multimodal input (image + text).
  - In `test_formal`, support is added by default for converting multimodal AI-generated feature tokens into images and saving them to the system temporary folder.

- **Technical Upgrade**:
  - Based on Xiaothink's self-developed img_zip technology.
  - Supports intelligent compression of 80x80x3 image patches.
  - When outputting 96 feature values, combined with the .7z algorithm, an ultra-high compression rate of 10% can be achieved.

- **Usage**:
  - Use the `<img>{image_path}</img>` tag to insert images in dialogue.
  - The img_zip model path must be specified when initializing the model.
  - Supports multimodal dialogue (image description, visual Q&A, etc.).

---

The above covers the main functionalities and usage methods of the Xiaothink Python module.

For any questions or suggestions, please contact us at: xiaothink@foxmail.com.