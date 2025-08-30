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
import time
import numpy as np
import os
import time
try:from build_model import *
except ImportError:
    from xiaothink.llm.inference.build_model import *

from tensorflow.keras.layers import Input, Embedding, GRU, Dense, Dropout  
from tensorflow.keras.models import Model  
from tensorflow.keras.layers import Multiply,Attention
from tensorflow.keras.layers import Bidirectional
from tensorflow.keras.layers import LayerNormalization
from tensorflow.keras.layers import Add,MultiHeadAttention
import gc
def ct():
    gc.collect()
#tf.config.run_functions_eagerly(True)

from tensorflow.keras.layers import Embedding, GRU, Dropout, Dense, AdditiveAttention, LayerNormalization


#------------------------------------------------------
dic={1:[int(256*4*2*0.7),int(1024*4*2*0.7),512],
         2:[int(1024*2*1),int(1024*4*2),128],
     2.2:[int(1024*2*1),int(1024*4*2),128],
     3:[int(512),int(1024),128],
     0.1:[128,256,32],
     0.2:[1024,int(1024*5.5),128],
     0.01:[512,int(1024*2.5),128],
     0.02:[int(1024*1),int(1024*4*2.75),128],
     0.022:[int(1024*9),int(1024*4*1.2),128],
     0.023:[int(1024*16),int(1024*4*0.55),128],
     0.024:[int(1024*16),int(1024*4*0.6),64],
     0.025:[int(1024*16),int(1024*4*0.6),64],
     0.0252:[int(1024*16),int(1024*4*0.6),64],
     0.0253:[int(1024*16),int(1024*4*0.6),64],
     0.0254:[int(1024*5),int(1024*2),64],
     0.0255:[int(1024*5),int(1024*2),64],
     0.0256:[int(100),int(200),128],
     0.02562:[int(1024*3),int(1024*3),128],
     0.02563:[int(1024*4),int(1024*2),128],
     0.025632:[int(512),int(500),32],
     10:[int(100),int(128),128],
     10.1:[int(128),int(128),64],
     20.1:[int(1024*24),int(1028*12),64],
     20.2:[int(1024*24),int(1028*6),64],
     #20.3:[int(1024*18),int(1024*5),64],
20.3:[int(1024),int(1024),64],
20.32:[int(2048*2),int(1024*6),256],
20.33:[int(2048*2),int(1024),256],
20.35:[int(2048*2),int(1024),256],
20.36:[int(2048*2),int(1024*2.5),128],
20.40:[int(2048*2),int(1024*2.5),128],
20.41:[int(2048*2),int(1024*2.5),128],
20.412:[int(2048*2),int(1024*2.5),128],
20.4121:[int(2048*20),int(1024*0.7),512],#5_3707_1849参数
20.412666:[int(1024),int(2048*2.6),1024],
20.4126662:[int(1024),int(2048),1024],
20.4126663:[int(4096),int(4096*1.5),256],
20.42:[int(2048*20),int(1024*0.7),512],#5_3707_1849参数
30.1:[int(2048*2),{'rnn_units':int(1024*6),'embed_q':0.7,'train_deep_layer':True,'train_main':True},512],#wd_q:0.15
30.11:[int(2048),{'rnn_units':int(1024),'embed_q':0.7,'train_deep_layer':True,'train_main':True},512],#512
30.011:[int(7000),{'rnn_units':int(512),'embed_q':0.6,'train_deep_layer':True,'train_main':True},128],
30.0112:[int(2048),{'rnn_units':int(512),'embed_q':0.6,'train_deep_layer':True,'train_main':True},128],
30.2:[int(2048),{'rnn_units':int(1024),'embed_q':0.6,'train_deep_layer':True,'train_main':True},128],
40.1:[int(1300),{'rnn_units':int(1300),'embed_q':0.7,'num_heads':12,'ff_dim':2048,},128],
40.2:[int(1024),{'num_heads':16,'ff_dim':2048},128],
40.22:[int(256),{'num_heads':8,'ff_dim':1024},128],
40.23:[int(256),{'rnn_units':int(1300),'embed_q':0.7,},128],
41.23:[int(64),{'rnn_units':int(2048),'embed_q':0.7,},128],
40.231:[int(1024),{'rnn_units':int(2048),'embed_q':0.6,}, 128],#512],#推理时需要500M内存
40.23101:[int(512),{'rnn_units':int(512), 'embed_q':0.4,}, 512],
40.23102:[int(512),{'rnn_units':int(512), 'embed_q':0.4,'router_units':256,'n_layer':1,}, 128],
40.23103:[int(512),{'rnn_units':int(512), 'embed_q':0.4,'router_units':256,'n_layer':1,'maxlen':600,}, 128],
40.23104:[int(512),{'rnn_units':int(512), 'embed_q':0.4,'router_units':200,'n_layer':1,'maxlen':200,}, 128],

40.231041:[int(256),{'rnn_units':int(256), 'embed_q':0.4,'router_units':128,'n_layer':1,'maxlen':140,'trans_layers':4}, 128],
40.231042:[int(1024),{'rnn_units':int(1024), 'embed_q':0.4,'router_units':256,'n_layer':1,'maxlen':600,'trans_layers':12}, 128],

40.2310421:[int(512),{'rnn_units':int(1024), 'embed_q':0.4,'router_units':256,'n_layer':1,'maxlen':160,'trans_layers':12}, 128],

40.3:[int(1024),{'rnn_units':int(1024), 'embed_q':0.4,'router_units':256,'n_layer':1,'maxlen':160,'trans_layers':5,'dff_factor':4}, 128],

40.31:[int(512),{'rnn_units':int(512), 'embed_q':0.4,'router_units':256,'n_layer':1,
            'maxlen':130,'trans_layers':5,'dff_factor':4,'trans_window':130}, 512],#1200#512

40.3101:[int(128),{'rnn_units':int(128), 'embed_q':0.4,'router_units':64,'n_layer':1,
            'maxlen':130,'trans_layers':3,'dff_factor':2,'trans_window':100}, 128],#1200#512
40.31666:[int(512),{'rnn_units':int(512), 'embed_q':0.4,'router_units':256,'n_layer':1,
            'maxlen':130,'trans_layers':5,'dff_factor':4,'trans_window':100}, 1200],#1200#512


1.001:[int(512),int(64),128],
40.23101001:[int(512),{'rnn_units':int(64), 'embed_q':0.4,}, 128],

40.4:[int(512),{'rnn_units':int(512), 'embed_q':0.4,'router_units':128,'n_layer':1,
            'maxlen':130,'trans_layers':4,'dff_factor':1,'trans_window':64,'num_moes':4,'momoe_router_units':128,}, 512],#1200#512

#40.32:[int(1024),{'rnn_units':int(256), 'embed_q':0.4,'router_units':256,'n_layer':1,
#            'maxlen':130,'trans_layers':32,'dff_factor':1,'trans_window':100}, 800],#1200 #512

40.32:[int(800),{'rnn_units':int(800), 'embed_q':0.4,'router_units':256,'n_layer':1,
            'maxlen':130,'trans_layers':22,'dff_factor':4,'trans_window':130,
            'num_heads':12,
            }, 400],#800


40.321:[int(256),{'rnn_units':int(128), 'embed_q':0.4,'router_units':64,'n_layer':1,
            'maxlen':130,'trans_layers':6,'dff_factor':2,'trans_window':130,
            'num_heads':6,
            }, 1600],#800

40.3301:[int(512),{'rnn_units':int(256), 'embed_q':0.4,'router_units':64,'n_layer':1,
            'maxlen':180,'trans_layers':16,'dff_factor':6,'trans_window':180,
            'num_heads':12,
            }, 512],#800
40.3302:[int(256),{'rnn_units':int(80), 'embed_q':0.4,'router_units':64,'n_layer':1,
            'maxlen':80,'trans_layers':6,'dff_factor':2,'trans_window':80,
            'num_heads':6,
            }, 512],#800
40.3303:[int(1200),{'rnn_units':int(128), 'embed_q':0.4,'router_units':128,'n_layer':1,
            'maxlen':130,'trans_layers':5,'dff_factor':2,'trans_window':130,
            'num_heads':6,
            }, 512],#800

40.33032:[int(160),{'rnn_units':int(64), 'embed_q':0.4,'router_units':22,'n_layer':1,
            'maxlen':90,'trans_layers':2,'dff_factor':1,'trans_window':90,
            'num_heads':3,
            }, 256],




0.444:[int(1200),{'rnn_units':int(128), 'embed_q':0.4,'router_units':128,'n_layer':1,
            'maxlen':130,'trans_layers':5,'dff_factor':2,'trans_window':130,
            'num_heads':6,
            }, 512],
0.666:[int(1200),int(1024),512],
1.001:[int(1200),int(3400),512],

0.4442:[int(1200),{'rnn_units':int(128), 'embed_q':0.4,'router_units':128,'n_layer':1,
            'maxlen':130,'trans_layers':5,'dff_factor':2,'trans_window':130,
            'num_heads':6,
            }, 2048],
0.6662:[int(1200),int(1024),2048],
1.0012:[int(1200),int(3400),2048],

50.0:[int(512),int(256),128],



't5':[int(1500),{'rnn_units':int(140), 'embed_q':0.4,'router_units':128,'n_layer':1,
            'maxlen':130,'trans_layers':2,'dff_factor':2,'trans_window':130,
            'num_heads':5,


            }, 256],

't5_reason':[int(1024),{'rnn_units':int(256), 'embed_q':0.4,'router_units':128,'n_layer':1,
            'maxlen':130,'trans_layers':34,'dff_factor':2,'trans_window':130,
            'num_heads':12,

            }, 256],

't5_mini':[int(512),{'rnn_units':int(80), 'embed_q':0.4,'router_units':80,'n_layer':1,
            'maxlen':130,'trans_layers':5,'dff_factor':2,'trans_window':130,
            'num_heads':7,
            }, 512],



't6_beta_dense':[int(512),{'rnn_units':int(1400), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':23,'dff_factor':1,'num_heads':8,'trans_window':200,#130,
                                            'all_maxlen':4096}, 
                            512],#2048],#220],

't6_bigger':[int(1024),{'rnn_units':int(4096), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':23,'dff_factor':2,'num_heads':8,'trans_window':130,
                                            'all_maxlen':4096}, 
                            220],

't6_beta_big':[int(512),{'rnn_units':int(4096), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':37,'dff_factor':2,'num_heads':8,'trans_window':130,
                                            'all_maxlen':4096}, 
                            220],

# embed_dim 必须是 num_heads 的整数倍


't6_mini2':[int(360),{'rnn_units':int(2400), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':37,'dff_factor':2,'num_heads':6,'trans_window':130,#130,
                                            'all_maxlen':2048}, 
                            512],#2048],#220],

't6_tiny':[int(240),{'rnn_units':int(1400), 'n_layer':1,'embed_q':0.4,'router_units':64,
                                            'trans_layers':39,'dff_factor':2,'num_heads':4,'trans_window':140,#130,
                                            'all_maxlen':2048}, 
                            256],#2048],#220],

't6_deep':[int(360),{'rnn_units':int(1200), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':73,'dff_factor':2,'num_heads':4,'trans_window':130,
                                            'all_maxlen':1024}, 
                            512],
't6_tiny_vision':[int(240),{'rnn_units':int(1400), 'n_layer':1,'embed_q':0.4,'router_units':64,
                                            'trans_layers':39,'dff_factor':2,'num_heads':4,'trans_window':140,#130,
                                            'all_maxlen':2048}, 
                            256],#2048],#220],

't6_standard_vision':[int(440),{'rnn_units':int(1600), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':31,'dff_factor':2,'num_heads':4,'trans_window':160,#130,
                                            'all_maxlen':2048}, 
                            512],#2048],#220],

't6_standard':[int(512),{'rnn_units':int(1100), 'n_layer':1,'embed_q':0.4,'router_units':128,
                                            'trans_layers':33,'dff_factor':4,'num_heads':8,
                                            'trans_window':140,#130,
                                            'all_maxlen':2048,
}, 
                            512],

't6_fast':[int(256),{'rnn_units':int(600), 'n_layer':1,'embed_q':0.4,'router_units':64,
                                            'trans_layers':17,'dff_factor':2,'num_heads':4,
                                            'trans_window':140,#130,
                                            'all_maxlen':2048,
}, 
                            512],

't6_large':[int(920),{'rnn_units':int(1200), 'n_layer':1,'embed_q':0.4,'router_units':512,
                                            'trans_layers':41,'dff_factor':2,'num_heads':4,
                                            'trans_window':130,#130,
                                            'all_maxlen':2048,
}, 
                            512],


     
}



manual_LR=True
# [Embedding ,(num_layer, num_heads, dff, maximum_position_encoding)]
LR=0.0001#0.000325#0.00005#0.000001#0.001#0.000001#0.0002#0.00085#0.000045#0.000001#0.0018#0.0015#0.00085#0.000001

lr_change=4000#400#6
LR_c1=0.0004#0.0006


lr_change2=7000#4700#2601#200
LR_c2=0.0001#0.0004

#0.0000001#0.000001#0.0015#0.0015# 0.008
LR_ontime=0.000001

MEMORY_SIZE =  128  # 指定记忆条数上限
MEMORY_SHAPE = 128  # 单条记忆长度
MEMORY_FILE_PATH = "memory_bank_0256_128_rf.npy"  # 设定记忆数据存储文件路径
FILL_VALUE = 0.0  # 用于填充的值
#---------------------------------------------------
import tensorflow as tf
from tensorflow.keras import layers




ms=0
def load(ckpt_dir=r'E:\小思框架\论文\ganskchat\ckpt_novel_en',
         vocab=r'E:\小思框架\论文\ganskchat\vocab_lx3.txt',
         BATCH_SIZE = 1,
         model_type=3,
         print_out=True,
         ):
    global dic, ms
    with open(vocab,'r',encoding='utf-8') as f:
        vocab=eval(f.read())
    char2idx = {u:i for i, u in enumerate(vocab)}
    idx2char = np.array(vocab)
    
    # 词集的长度
    vocab_size = len(vocab)
    '''
    dic={1:[int(256*4*2*0.7),int(1024*4*2*0.7),512],
         2:[int(1024*2*1),int(1024*4*2),128],
         2.2:[int(1024*2*1),int(1024*4*2),128],
         3:[int(512),int(1024),128],
         2.3:[int(1024*2*1),int(1024*3),128],
         0.1:[128,256,32],
         0.2:[1024,int(1024*5.5),128],
         0.01:[512,int(1024*2.5),128],
         0.02:[int(1024*1),int(1024*4*2.75),128],
         0.022:[int(1024*9),int(1024*4*1.2),128],
         0.023:[int(1024*16),int(1024*4*0.55),128],
         0.024:[int(1024*16),int(1024*4*0.6),64],
         0.025:[int(1024*16),int(1024*4*0.6),64],
         0.0252:[int(1024*16),int(1024*4*0.6),64],
         0.0253:[int(1024*16),int(1024*4*0.6),64],
         0.0254:[int(1024*5),int(1024*2),64],#int(1024*2.414),64],
         0.0255:[int(1024*5),int(1024*2),64],
         }
    '''

    seq_length=dic[model_type][2]
    
    # 嵌入的维度
    embedding_dim = dic[model_type][0]

    # RNN 的单元数量
    rnn_units = dic[model_type][1]
    window= dic[model_type][2]
    
    checkpoint_dir=ckpt_dir

    checkpoint_path = tf.train.latest_checkpoint(checkpoint_dir)



    # 假设 build_model 是一个定义并返回模型的函数
    model = build_model(vocab_size, embedding_dim, rnn_units, batch_size=BATCH_SIZE,
                        mt=model_type,window=window)
    try:
        if print_out:model.summary()
    except:
        ms=1
        if print_out:print('Model Summary Error')
    
    if print_out:print(checkpoint_path)
    # 直接加载权重到模型中
    model.load_weights(checkpoint_path)
    
    return model,[char2idx,idx2char]





# 评估步骤（用学习过的模型生成文本）
#@tf.function
def generate_texts_old(model,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 0.6,
                  every=None,#每写一个字执行的函数
                  pass_char=[],
                  ):
  t1=time.time()
  char2idx,idx2char=vocabdata[0],vocabdata[1]
  
  # 将起始字符串转换为数字（向量化）
  input_eval = tf.convert_to_tensor([int(char2idx.get(s, char2idx['▩'])) for s in start_string], dtype=tf.int32)
  input_eval = tf.expand_dims(input_eval, 0)

  # 空字符串用于存储结果
  text_generated = []

  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
  #print(input_eval.shape)

  # 这里批大小为 1
  try:model.reset_states()
  except:print('model rest error')
  #cnt=0
  f=1
  for i in range(num_generate):
      
      predictions = model.predict(input_eval,verbose=0)#model(input_eval)#model.predict(input_eval,verbose=0)
      # 删除批次的维度
      predictions = tf.squeeze(predictions, 0)

      # 用分类分布预测模型返回的字符
      predictions = predictions / temperature
      predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
      while idx2char[predicted_id] in pass_char:
                predictions = model.predict(input_eval,verbose=0)#model(input_eval)#model.predict(input_eval,verbose=0)
                # 删除批次的维度
                predictions = tf.squeeze(predictions, 0)

                # 用分类分布预测模型返回的字符
                predictions = predictions / temperature
                predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()



      input_eval = tf.expand_dims([predicted_id], 0)
      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])
      
      
      '''
      cnt+=1
      if time.time()-t1>1 and f:
          print(time.time()-t1,cnt)
          f=0
      '''
          
      '''
      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])
      '''
  del model,vocabdata
  ct()
  return ''.join(text_generated)#(start_string + ''.join(text_generated))
def generate_texts(model,
                  vocabdata,
                  start_string,
                  num_generate=512,
                  temperature=0.6,
                  every=None,
                  pass_char=[],
                  repetition_penalty=1.0):
    char2idx, idx2char = vocabdata[0], vocabdata[1]
    
    # 处理初始输入（包含历史惩罚）
    init_tokens = [char2idx.get(c, char2idx['▩']) for c in start_string]
    input_eval = tf.expand_dims(init_tokens, 0)  # 形状 [1, seq_len]
    
    text_generated = []
    all_generated = init_tokens.copy()  # 包含输入和生成的全部token

    try:
        model.reset_states()
    except:
        pass

    for _ in range(num_generate):
        # 获取模型预测（三维张量 [batch, seq_len, vocab]）
        predictions = model(input_eval, training=False)
        
        # 提取最后一个位置的logits（二维 [batch, vocab]）
        if len(predictions.shape) == 3:
            last_logits = predictions[:, -1, :]  # 形状 [1, vocab_size]
        else:
            last_logits = predictions  # 兼容非序列输出
        
        # 转换为numpy数组处理
        logits = last_logits.numpy().copy()[0]  # 降维到一维 [vocab_size]

        # 应用重复惩罚（包含初始输入）
        if repetition_penalty != 1.0:
            for token in set(all_generated):
                if 0 <= token < len(logits):
                    logits[token] /= repetition_penalty

        # 应用温度参数
        scaled_logits = logits / temperature

        # 采样过程
        while True:
            # 转换为概率分布
            probs = tf.nn.softmax(scaled_logits).numpy()
            
            # 排除需要跳过的字符
            valid_indices = [i for i, c in enumerate(idx2char) if c not in pass_char]
            if not valid_indices:
                raise ValueError("所有候选字符都被过滤")
            
            # 重新标准化概率
            filtered_probs = probs[valid_indices] / probs[valid_indices].sum()
            
            # 采样
            chosen = np.random.choice(valid_indices, p=filtered_probs)
            
            # 检查字符有效性
            if idx2char[chosen] not in pass_char:
                predicted_id = chosen
                break
            
            # 如果仍采样到非法字符，降低该字符概率
            scaled_logits[chosen] = -float('inf')

        # 更新状态
        all_generated.append(predicted_id)
        input_eval = tf.expand_dims([predicted_id], 0)  # 新输入形状 [1, 1]
        
        # 记录输出
        char = idx2char[predicted_id]
        text_generated.append(char)
        if every:
            every(char)

    return ''.join(text_generated)
generate_texts_rp=generate_texts

def generate_texts_passchar2(model, vocabdata, start_string, num_generate=512, temperature=0.6, every=None, pass_char=[]):
    char2idx, idx2char = vocabdata[0], vocabdata[1]
    
    # 转换起始字符串并初始化输入
    input_eval = [char2idx.get(s, char2idx['▩']) for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
    
    text_generated = []
    
    # 重置模型状态（如果支持）
    if hasattr(model, 'reset_states'):
        model.reset_states()
    
    for _ in range(num_generate):
        # 获取模型预测结果
        predictions = model.predict(input_eval, verbose=0)  # 形状应为 [1, seq_len, vocab_size]
        
        # 提取最后一个时间步的logits
        last_step_logits = predictions[0, -1, :]  # 形状变为 [vocab_size]
        
        # 过滤pass_char字符
        pass_indices = [char2idx.get(c, -1) for c in pass_char]
        pass_indices = [idx for idx in pass_indices if 0 <= idx < len(last_step_logits)]
        if pass_indices:
            last_step_logits = last_step_logits#.numpy()
            last_step_logits[pass_indices] = -1e9
            last_step_logits = tf.convert_to_tensor(last_step_logits)
        
        # 应用温度采样
        scaled_logits = last_step_logits / temperature
        
        # 注意这里输入的logits形状已经是 [vocab_size]，需要添加batch维度
        predicted_id = tf.random.categorical([scaled_logits], 1)[0, 0].numpy()  # 形状变为 [1,1]

        
        # 更新输入并保存结果
        input_eval = tf.expand_dims([predicted_id], 0)
        text_generated.append(idx2char[predicted_id])
        if every:
            every(idx2char[predicted_id])
    
    return start_string + ''.join(text_generated)


def generate_texts_f2(model,
                   vocabdata,
                   start_string,
                   num_generate=512,
                   temperature=0.6,
                   every=None,
                   pass_char=[]):
    char2idx, idx2char = vocabdata[0], vocabdata[1]
    default_char = char2idx['▩']
    
    # 预处理pass_char为索引列表
    pass_indices = [char2idx[c] for c in pass_char if c in char2idx]
    
    # 初始化输入序列
    input_eval = tf.convert_to_tensor(
        [char2idx.get(s, default_char) for s in start_string],
        dtype=tf.int32
    )[tf.newaxis, ...]  # 更高效的维度扩展方式

    text_generated = []

    # 优化状态重置逻辑
    if hasattr(model, 'reset_states'):
        model.reset_states()
    
    # 预分配TensorArray提升性能
    # ta = tf.TensorArray(dtype=tf.int32, size=num_generate)
    
    for _ in range(num_generate):
        # 直接调用模型替代predict方法
        predictions = model(input_eval)[0, -1]  # 直接获取最后一个时间步的输出
        
        # 应用温度调节和字符过滤
        if temperature > 0:
            scaled_logits = predictions / temperature
            # 使用掩码技术一次性过滤非法字符
            if pass_indices:
                scaled_logits = tf.tensor_scatter_nd_update(
                    scaled_logits,
                    indices=tf.reshape(pass_indices, (-1, 1)),
                    updates=tf.fill((len(pass_indices),), -float('inf'))
                )
            predicted_id = tf.random.categorical(
                tf.expand_dims(scaled_logits, 0), 1
            )[0, 0].numpy()
        else:
            # 温度=0时优化路径
            scaled_logits = predictions
            if pass_indices:
                scaled_logits = tf.tensor_scatter_nd_update(
                    scaled_logits,
                    indices=tf.reshape(pass_indices, (-1, 1)),
                    updates=tf.fill((len(pass_indices),), -float('inf'))
                )
            predicted_id = tf.argmax(scaled_logits, axis=-1).numpy()

        # 更新输入序列
        input_eval = tf.expand_dims([predicted_id], 0)
        
        # 处理生成字符
        generated_char = idx2char[predicted_id]
        text_generated.append(generated_char)
        if every:
            every(generated_char)

    return ''.join(text_generated)


def generate_texts_untilstr(model,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 0.6,
                  every=None,#每写一个字执行的函数
                  stop_c='\n问：',
                  ):
  #print('every',every)
  char2idx,idx2char=vocabdata[0],vocabdata[1]
  
  # 将起始字符串转换为数字（向量化）
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # 空字符串用于存储结果
  text_generated = []

  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
  #print(input_eval.shape)

  # 这里批大小为 1
  try:model.reset_states()
  except:print('model rest error')
  for i in range(num_generate):
      
      predictions = model.predict(input_eval,verbose=0)#model(input_eval)#model.predict(input_eval,verbose=0)
      # 删除批次的维度
      predictions = tf.squeeze(predictions, 0)

      # 用分类分布预测模型返回的字符
      predictions = predictions / temperature
      predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      if 1:#not idx2char[predicted_id] in ['，','。']:
          input_eval = tf.expand_dims([predicted_id], 0)
          text_generated.append(idx2char[predicted_id])
          if every!= None:every(idx2char[predicted_id])
      if type(stop_c)==str:
          if stop_c in ''.join(text_generated):
              return ''.join(text_generated)[:-len(stop_c)]
      elif type(stop_c)==list:
          for ii in stop_c:
              if ii in ''.join(text_generated):
                  return ''.join(text_generated)[:-len(ii)]
      '''
      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])
      '''
  del model,vocabdata
  ct()
  return ''.join(text_generated)#(start_string + ''.join(text_generated))


'''
def generate_texts_batch(model,
                         vocabdata,
                         start_strings,
                         num_generate = 512,
                         temperature = 0.6,
                         every=None,
                         batch_size=1):
    char2idx, idx2char = vocabdata[0], vocabdata[1]

    # 将所有起始字符串转换为数字（向量化）
    input_evals = [[char2idx[s] for s in start_str] for start_str in start_strings]
    input_evals = tf.keras.preprocessing.sequence.pad_sequences(input_evals, maxlen=num_generate, padding='pre')
    input_evals = tf.expand_dims(input_evals, axis=1)

    # 初始化存储结果的列表
    text_generated = [[] for _ in start_strings]

    model.reset_states()
    for i in range(num_generate):
        # 对整个批次进行预测
        predictions = model.predict(input_evals[:, :i, :], verbose=0)

        # 平滑分布并抽样
        predictions /= temperature
        predicted_ids = tf.random.categorical(predictions, num_samples=1)
        predicted_ids = tf.squeeze(predicted_ids, axis=-1).numpy()

        # 更新每个起始字符串对应的生成序列
        for j in range(len(start_strings)):
            text_generated[j].append(idx2char[predicted_ids[j]])

            if every is not None and (i % batch_size == 0 or i == num_generate - 1):
                every(idx2char[predicted_ids[j]], start_strings[j])

        # 将预测字符添加到下一轮输入
        input_evals = tf.concat([input_evals[:, i:i+1], tf.expand_dims(predicted_ids, axis=1)], axis=1)

    return [start_str + ''.join(text_seq) for start_str, text_seq in zip(start_strings, text_generated)]
'''


def generate_texts_faster(model, vocabdata, start_string,
                          num_generate=512, temperature=0.6,
                          every=None, utf=False, rest=True):
    char2idx, idx2char = vocabdata
    input_eval = tf.convert_to_tensor([int(char2idx.get(s, char2idx['▩'])) for s in start_string], dtype=tf.int32)
    input_eval = tf.expand_dims(input_eval, 0)

    # 预分配内存以提升效率
    text_generated = np.empty(num_generate, dtype=np.int32)

    if rest:model.reset_states()

    for i in range(num_generate):
        # 获取预测
        predictions = model.predict(input_eval, verbose=0)
        predictions = tf.squeeze(predictions, 0)

        # 用分类分布预测模型返回的字符
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

        # 更新input_eval 和 text_generated
        input_eval = tf.expand_dims([predicted_id], 0)
        text_generated[i] = predicted_id

        # 如果需要，执行外部函数
        if every is not None:
            every(idx2char[predicted_id])

    # 转换为字符串并拼接起始字符串
    return ''.join(idx2char[text_generated.tolist()])



def generate_texts_np(model,
                   vocabdata,
                   start_string,
                   num_generate=512,
                   top_n=1,  # 选取概率最高的前n个字符
                   every=None):  # 每写一个字执行的函数
    char2idx, idx2char = vocabdata[0], vocabdata[1]

    # 将起始字符串转换为数字（向量化）
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)

    # 空字符串用于存储结果
    text_generated = []

    # 这里批大小为 1
    #model.reset_states()
    for i in range(num_generate):
        predictions = model.predict(input_eval, verbose=0)
        # 删除批次的维度
        predictions = tf.squeeze(predictions, 0)

        # 找到概率最高的前n个预测
        top_n_probs, top_n_indices = tf.nn.top_k(predictions, k=top_n)
        # 从最高的n个预测中随机选择一个
        predicted_id = np.random.choice(top_n_indices.numpy()[0])

        # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
        input_eval = tf.expand_dims([predicted_id], 0)

        text_generated.append(idx2char[predicted_id])
        if every is not None:
            every(idx2char[predicted_id])

    return start_string + ''.join(text_generated)


# 评估步骤（用学习过的模型生成文本）
@tf.function
def generate_texts_fast_core(model,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 1.0,
                  every=None,#每写一个字执行的函数
                  ):
  char2idx,idx2char=vocabdata[0],vocabdata[1]
  
  # 将起始字符串转换为数字（向量化）
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)
  #print('ie',input_eval)
  # 空字符串用于存储结果
  text_generated = []

  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
  

  # 这里批大小为 1
  model.reset_states()
  for i in range(num_generate):
      
      predictions = model(input_eval)
      # 删除批次的维度
      try:
          predictions = tf.squeeze(predictions, 0)

          # 用分类分布预测模型返回的字符
          '''
          predictions = predictions / temperature
          predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
            '''
          predicted_id = tf.random.categorical(predictions / temperature, num_samples=1)[0, 0]
      except tf.python.framework.errors_impl.InvalidArgumentError:
          predictions = tf.expand_dims(predictions, axis=0) 
          predicted_id = tf.random.categorical(predictions / temperature, num_samples=1)[0, 0]

      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])

  del model, vocabdata
  return text_generated


def generate_texts_fast(model,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature =1.0,
                  every=None,#每写一个字执行的函数
                  ret_ori=True):
    li=generate_texts_fast_core(model=model,
                   vocabdata= vocabdata,
                  start_string=start_string,
                  num_generate = num_generate ,
                  temperature = temperature,
                  every=every,
                  )
    str_=''
    for i in li:
        str_+=i.numpy().decode('utf-8')
    del model, vocabdata
    if ret_ori:return (start_string + str_)
    else:return str_

def generate_texts_add(model,
                       model2,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 0.6,
                  every=None,#每写一个字执行的函数
                       q=[0.5,0.5],
                  ):
  q1,q2=q
  char2idx,idx2char=vocabdata[0],vocabdata[1]
  
  # 将起始字符串转换为数字（向量化）
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # 空字符串用于存储结果
  text_generated = []

  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
  #print(input_eval.shape)

  # 这里批大小为 1
  #model.reset_states()
  for i in range(num_generate):
      
      predictions = model(input_eval)*q1+model2(input_eval)*q2#model.predict(input_eval,verbose=0)
      # 删除批次的维度
      predictions = tf.squeeze(predictions, 0)

      # 用分类分布预测模型返回的字符
      predictions = predictions / temperature
      predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      if 1:#not idx2char[predicted_id] in ['，','。']:
          input_eval = tf.expand_dims([predicted_id], 0)
          text_generated.append(idx2char[predicted_id])
          if every!= None:every(idx2char[predicted_id])
      '''
      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])
      '''
  del model,vocabdata
  ct()
  return ''.join(text_generated)#(start_string + ''.join(text_generated))


def generate_texts_mask(model,
                       model2,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 0.6,
                  every=None,#每写一个字执行的函数
                       #q=[0.5,0.5],
                  ):
  #q1,q2=q
  char2idx,idx2char=vocabdata[0],vocabdata[1]
  
  # 将起始字符串转换为数字（向量化）
  input_eval = [char2idx[s] for s in start_string]
  input_eval = tf.expand_dims(input_eval, 0)

  # 空字符串用于存储结果
  text_generated = []

  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
  #print(input_eval.shape)

  # 这里批大小为 1
  #model.reset_states()
  for i in range(num_generate):
      mean=np.mean((model2(input_eval)))
      predictions = (model(input_eval))#model.predict(input_eval,verbose=0)
      predictions2=predictions
      
      # 创建一个布尔数组，其中matrix中的元素大于threshold的位置为True，否则为False
      bool_mask = predictions2 > mean*0.

      # 使用布尔数组对matrix进行索引，并将True位置的值设为1，False位置的值设为0
      booln = np.where(bool_mask, 1, 0)

      predictions+=mean*booln
      #print(predictions)

      
      # 删除批次的维度
      predictions = tf.squeeze(predictions, 0)

      # 用分类分布预测模型返回的字符
      predictions = predictions / temperature
      predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

      if 1:#not idx2char[predicted_id] in ['，','。']:
          input_eval = tf.expand_dims([predicted_id], 0)
          text_generated.append(idx2char[predicted_id])
          if every!= None:every(idx2char[predicted_id])
      '''
      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])
      '''
  del model,vocabdata
  ct()
  return ''.join(text_generated)#(start_string + ''.join(text_generated))
def fill(inp,n,pad_char=' ',cut=False):
    if len(inp)>=n:
        if not cut:return inp
        else:
            return inp[-n:]
    elif len(inp)<n:
        return pad_char*(n-len(inp))+inp

def generate_texts_loop(m, d, inp_m, num_generate=100,
                             every=lambda a:print(a,end='',flush=True),
                             temperature=0.7,#0.5#0.8
                       window=128,
                       pass_char=['▩']
                             ):
    out=''
    for i in range(num_generate):
          out+=generate_texts(m, d, (inp_m+out)[-window:],num_generate=1,
                             every=every,
                             temperature=temperature,#0.5#0.8
                             pass_char=pass_char
                       #      utf=False,
                               #q=[0.6,0.4]
                       #     rest=False,
                                )
    return out

##
##def generate_texts_untilstr_loop(model,
##                   vocabdata,
##                  start_string,
##                  num_generate = 512,
##                  temperature = 0.6,
##                  every=None,#每写一个字执行的函数
##                  stop_c='\n问：',
##                  window=128,
##                  pass_char=[],
##                  repetition_penalty=1.2,
##                                 
##                  ):
##  #print('every',every)
##  char2idx,idx2char=vocabdata[0],vocabdata[1]
##  
##  # 将起始字符串转换为数字（向量化）
##  # 将起始字符串转换为数字（向量化）
##  input_eval = tf.convert_to_tensor([int(char2idx.get(s, char2idx['▩'])) for s in start_string], dtype=tf.int32)
##  input_eval = tf.expand_dims(input_eval, 0)
##
##  # 空字符串用于存储结果
##  text_generated = list(start_string)#[]
##  ou=[]
##  # 低温度会生成更可预测的文本
##  # 较高温度会生成更令人惊讶的文本
##  # 可以通过试验以找到最好的设定
##  #print(input_eval.shape)
##
##  # 这里批大小为 1
##  try:model.reset_states()
##  except:print('model rest error')
##  for i in range(num_generate):
##      
##
##      g=generate_texts_rp(model, vocabdata, ''.join(text_generated)[-window:],num_generate=1,
##                             every=every,
##                             temperature=temperature,#0.5#0.8
##                            pass_char=pass_char,
##                          repetition_penalty=repetition_penalty
##                                )
##      if 1:#not idx2char[predicted_id] in ['，','。']:
##          
##          text_generated.append(g)
##          ou.append(g)
##        
##      #if every!= None:every(idx2char[predicted_id])
##      if type(stop_c)==str:
##          if stop_c in ''.join(ou):
##              return ''.join(ou)[:-len(stop_c)]
##      elif type(stop_c)==list:
##          for ii in stop_c:
##              if ii in ''.join(ou):
##                  return ''.join(ou)[:-len(ii)]
##      '''
##      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
##      input_eval = tf.expand_dims([predicted_id], 0)
##
##      text_generated.append(idx2char[predicted_id])
##      if every!= None:every(idx2char[predicted_id])
##      '''
##  del model,vocabdata
##  ct()
##  return ''.join(ou)#(start_string + ''.join(text_generated))

def generate_texts_untilstr_loop(model,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 0.6,
                  every=None,  # 每写一个字执行的函数
                  stop_c='\n问：',
                  window=128,
                  pass_char=[],
                  repetition_penalty=1.2,
                  pass_start_char=[],  # 禁止作为第一个字符的列表
                                 image=None,
                  ):
    char2idx, idx2char = vocabdata[0], vocabdata[1]
    
    # 将起始字符串转换为数字（向量化）
    input_eval = tf.convert_to_tensor(
        [int(char2idx.get(s, char2idx['▩'])) for s in start_string],
        dtype=tf.int32
    )
    input_eval = tf.expand_dims(input_eval, 0)

    text_generated = list(start_string)
    ou = []
    
    try:
        model.reset_states()
    except:
        print('model reset error')
    
    for i in range(num_generate):
        # 生成单个字符
        g = generate_texts(
            model, vocabdata, ''.join(text_generated)[-window:],
            num_generate=1,
            #every=every,
            temperature=temperature,
            pass_char=pass_char,
            repetition_penalty=repetition_penalty,
        )
        
        # === 新增 pass_start_char 逻辑 ===
        # 如果是第一个生成的字符且在禁止列表中，则重新生成
        if i == 0 and pass_start_char:
            retry_count = 0
            # 最大重试次数防止无限循环
            while g in pass_start_char and retry_count < 10:
                g = generate_texts(
                    model, vocabdata, ''.join(text_generated)[-window:],
                    num_generate=1,
                    #every=every,
                    temperature=temperature,
                    pass_char=pass_char,
                    repetition_penalty=repetition_penalty,
                )
                retry_count += 1
        if every:every(g)
        # 添加生成的字符
        text_generated.append(g)
        ou.append(g)
        
        # 检查停止条件
        if isinstance(stop_c, str) and stop_c in ''.join(ou):
            return ''.join(ou)[:-len(stop_c)]
        elif isinstance(stop_c, list):
            for stop_str in stop_c:
                if stop_str in ''.join(ou):
                    return ''.join(ou)[:-len(stop_str)]
    
    # 清理资源
    del model, vocabdata
    ct()  # 假设这是清理函数
    return ''.join(ou)



def generate_texts_untilstr_loop_add(model1,model2,
                   vocabdata,
                  start_string,
                  num_generate = 512,
                  temperature = 0.6,
                  every=None,#每写一个字执行的函数
                  stop_c='\n问：',
                  window=128,
                  pass_char=[],
                  q=[0.4,0.6]
                  ):
  #print('every',every)
  char2idx,idx2char=vocabdata[0],vocabdata[1]
  
  # 将起始字符串转换为数字（向量化）
  # 将起始字符串转换为数字（向量化）
  input_eval = tf.convert_to_tensor([int(char2idx.get(s, char2idx['▩'])) for s in start_string], dtype=tf.int32)
  input_eval = tf.expand_dims(input_eval, 0)

  # 空字符串用于存储结果
  text_generated = list(start_string)#[]
  ou=[]
  # 低温度会生成更可预测的文本
  # 较高温度会生成更令人惊讶的文本
  # 可以通过试验以找到最好的设定
  #print(input_eval.shape)

  # 这里批大小为 1
  try:model.reset_states()
  except:print('model rest error')
  for i in range(num_generate):
      

      g=generate_texts_add(model1,model2, vocabdata, ''.join(text_generated)[-window:],num_generate=1,
                             every=every,
                             temperature=temperature,#0.5#0.8
                       #      utf=False,
                               #q=[0.6,0.4]
                       #     rest=False,
                       q=q
                                )
      if 1:#not idx2char[predicted_id] in ['，','。']:
          
          text_generated.append(g)
          ou.append(g)
        
      #if every!= None:every(idx2char[predicted_id])
      if type(stop_c)==str:
          if stop_c in ''.join(ou):
              return ''.join(ou)[:-len(stop_c)]
      elif type(stop_c)==list:
          for ii in stop_c:
              if ii in ''.join(ou):
                  return ''.join(ou)[:-len(ii)]
      '''
      # 把预测字符和前面的隐藏状态一起传递给模型作为下一个输入
      input_eval = tf.expand_dims([predicted_id], 0)

      text_generated.append(idx2char[predicted_id])
      if every!= None:every(idx2char[predicted_id])
      '''
  del model1,model2,vocabdata
  ct()
  return ''.join(ou)#(start_string + ''.join(text_generated))


