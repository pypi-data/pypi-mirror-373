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
from tensorflow.keras import layers
import numpy as np
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

#---------------------------------

LR=0.00005

import tensorflow as tf
from tensorflow.keras.layers  import Layer, Dense, Embedding



import tensorflow as tf
from tensorflow.keras import layers

    
def send_matrices_to_server(matrix1, matrix2):
    tf.compat.v1.enable_eager_execution()
    #time1 = time.time()
    return tf.linalg.matmul(matrix1, matrix2)


class CustomGRUCell(tf.keras.layers.Layer):
    def __init__(self, units, recurrent_initializer='glorot_uniform', **kwargs):
        super(CustomGRUCell, self).__init__(**kwargs)
        self.units = units
        self.state_size = units
        self.recurrent_initializer = recurrent_initializer

    def build(self, input_shape):
        self.kernel = self.add_weight(
            shape=(input_shape[-1], 3 * self.units),
            initializer='glorot_uniform',
            name='kernel'
        )
        self.recurrent_kernel = self.add_weight(
            shape=(self.units, 3 * self.units),
            initializer=self.recurrent_initializer,
            name='recurrent_kernel'
        )
        self.bias = self.add_weight(
            shape=(3 * self.units,),
            initializer='zeros',
            name='bias'
        )

    def call(self, inputs, states):
        h_tm1 = states[0]  # previous memory state
        combined_inputs = tf.concat([inputs, h_tm1], axis=-1)

        # Perform the linear transformation and split into three parts
        z_r_h = (
            send_matrices_to_server(inputs, self.kernel) +
            send_matrices_to_server(h_tm1, self.recurrent_kernel) +
            self.bias
        )
        z, r, h_hat = tf.split(z_r_h, num_or_size_splits=3, axis=1)

        # Apply activations
        z = tf.sigmoid(z)
        r = tf.sigmoid(r)
        h_hat = tf.tanh(r * h_hat + (1 - r) * h_tm1)

        # Update hidden state
        h_t = (1 - z) * h_hat + z * h_tm1

        return h_t, [h_t]

    
class CustomGRU(tf.keras.layers.RNN):
    def __init__(self, units, return_sequences=False, stateful=False, recurrent_initializer='glorot_uniform', name=None, trainable=True, **kwargs):
        cell = CustomGRUCell(units, recurrent_initializer=recurrent_initializer, **kwargs)
        super(CustomGRU, self).__init__(
            cell,
            return_sequences=return_sequences,
            stateful=stateful,
            name=name,
            trainable=trainable,
            **kwargs
        )

class CLModel_41_1(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, his_q=0.75, use_matt=True, att_q=0.4, att_units=None, n_char=3, wd_q=1.0, nh=8, train_deep_layer=True, train_main=True, num_chargru_layer=8, embed_q=0.5, **kwargs):
        super(CLModel_41_1, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window
        self.units = units
        self.n = n  # Number of stacked GRU layers
        self.his_q = his_q
        self.use_matt = use_matt
        self.att_q = att_q
        self.att_units = att_units
        self.n_char = n_char
        self.wd_q = wd_q
        self.nh = nh
        self.train_deep_layer = train_deep_layer
        self.train_main = train_main
        self.num_chargru_layer = num_chargru_layer
        self.embed_q = embed_q

        self.next_token_predictor = layers.Dense(vocab_size, trainable=True)
        self.styler = layers.Dense(vocab_size, trainable=True)
        self.dropout = tf.keras.layers.Dropout(0.1)
        self.embedding = layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim)

        # Stacked GRU layers
        self.context_encoders = [
            GRU(units, return_sequences=True, stateful=False, recurrent_initializer='glorot_uniform', name=f'gru_{i}', trainable=True) for i in range(n)
        ]

        self.lnl = layers.LayerNormalization(epsilon=1e-6)
        self.lnl0 = layers.LayerNormalization(epsilon=1e-6)
        self.lnl1 = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, training=None, use_teacher_forcing=True):
        # 嵌入层
        embedded_inputs = inputs#self.embedding(inputs)
        embedded_inputs = self.lnl0(embedded_inputs)
        embedded_inputs = self.dropout(embedded_inputs, training=training)

        # 使用GRU进行序列编码
        sequence = embedded_inputs
        for gru_layer in self.context_encoders:
            sequence = gru_layer(sequence, training=training)
            sequence = self.lnl(sequence)


        return sequence

    def get_config(self):
        config = super(CLModel_40_1, self).get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "n": self.n,
            "his_q": self.his_q,
            "use_matt": self.use_matt,
            "att_q": self.att_q,
            "att_units": self.att_units,
            "n_char": self.n_char,
            "wd_q": self.wd_q,
            "nh": self.nh,
            "train_deep_layer": self.train_deep_layer,
            "train_main": self.train_main,
            "num_chargru_layer": self.num_chargru_layer,
            "embed_q": self.embed_q
        })
        return config


class CLModel_40_1_01(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, his_q=0.75, use_matt=True, att_q=0.4, att_units=None, n_char=3, wd_q=1.0, nh=8, train_deep_layer=True, train_main=True, num_chargru_layer=8, embed_q=0.5, **kwargs):
        super(CLModel_40_1_01, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window
        self.units = units
        self.n = n  # Number of stacked GRU layers
        self.his_q = his_q
        self.use_matt = use_matt
        self.att_q = att_q
        self.att_units = att_units
        self.n_char = n_char
        self.wd_q = wd_q
        self.nh = nh
        self.train_deep_layer = train_deep_layer
        self.train_main = train_main
        self.num_chargru_layer = num_chargru_layer
        self.embed_q = embed_q

        self.next_token_predictor = layers.Dense(vocab_size, trainable=True)
        self.styler = layers.Dense(vocab_size, trainable=True)
        self.dropout = tf.keras.layers.Dropout(0.1)
        #self.embedding = layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim)

        # Stacked GRU layers
        self.context_encoders = [
            CustomGRU(units, return_sequences=True, stateful=False, recurrent_initializer='glorot_uniform', name=f'gru_{i}', trainable=True) for i in range(n)
        ]

        self.lnl = layers.LayerNormalization(epsilon=1e-6)
        self.lnl0 = layers.LayerNormalization(epsilon=1e-6)
        self.lnl1 = layers.LayerNormalization(epsilon=1e-6)
        self.f_d=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh', trainable=train_main)
        self.f_d_0=tf.keras.layers.Dense(units=self.vocab_size,trainable=train_main)
        self.f_d2=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh', trainable=train_main)

        
        #self.memory= GRUMemoryLayer(input_dim=units, memory_size=units, key_dim=units // 2)


    def call(self, inputs, training=None, use_teacher_forcing=True):
        # 嵌入层
        
        input_shape = tf.shape(inputs)  
        input_dim = input_shape[-1]  
        embedded_inputs = self.f_d(inputs)
        embedded_inputs=self.lnl0(embedded_inputs)
        embedded_inputs = self.f_d2(embedded_inputs)*self.embed_q+embedded_inputs*(1-self.embed_q)
        embedded_inputs=self.lnl1(embedded_inputs)
        
        embedded_inputs = self.dropout(embedded_inputs, training=training)
        
        # 使用GRU进行序列编码
        sequence = inputs#(embedded_inputs)
        for gru_layer in self.context_encoders:
            sequence = gru_layer(sequence, training=training)
            sequence = self.lnl(sequence)


        return sequence

    def get_config(self):
        config = super(CLModel_40_1, self).get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "n": self.n,
            "his_q": self.his_q,
            "use_matt": self.use_matt,
            "att_q": self.att_q,
            "att_units": self.att_units,
            "n_char": self.n_char,
            "wd_q": self.wd_q,
            "nh": self.nh,
            "train_deep_layer": self.train_deep_layer,
            "train_main": self.train_main,
            "num_chargru_layer": self.num_chargru_layer,
            "embed_q": self.embed_q
        })
        return config
    
'''
class TokenAndPositionEmbedding_41_01(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding_41_01, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.lstm = layers.LSTM(units=embed_dim, return_sequences=True)
        self.bn = layers.BatchNormalization()

    def call(self, x):
        x = self.token_emb(x)
        residual = x  # 残差连接
        x = self.lstm(x)
        x = self.bn(x)
        x += residual  # 添加残差
        return x   





class TokenAndPositionEmbedding_41_01(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding_41_01, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.lstm1 = layers.GRU(units=embed_dim, return_sequences=True)
        self.dropout1 = layers.Dropout(0.5)
        self.dense = layers.Dense(embed_dim, activation='relu')
        self.bn = layers.BatchNormalization()
        
        # 添加LAuReL模块，这里简化为一个小型网络，实际应用中可以根据需要调整
        self.lau_rel = tf.keras.Sequential([
            layers.Dense(embed_dim // 4, activation='relu'),  # 减少参数量
            layers.Dense(embed_dim)                          # 输出维度与残差一致
        ])

    def call(self, x, training=False):
        x = self.token_emb(x)
        residual = x  # 残差连接
        
        x = self.lstm1(x)
        x = self.dropout1(x, training=training)
        
        x = self.dense(x)
        x = self.bn(x, training=training)
        
        # LAuReL: 在残差连接之前通过一个小网络处理residual
        residual = self.lau_rel(residual)
        
        x += residual  # 添加残差，经过了LAuReL处理
        return x


'''



# 定义MoE模型
class MoEModel_40_2(tf.keras.Model):
    def __init__(self, experts, vocab_size, **kwargs):
        super(MoEModel_40_2, self).__init__(**kwargs)
        self.experts = experts
        #self.router = router
        self.router_outputs=None
        self.rout_dense=layers.Dense(1, activation='softmax')
        self.next_token_predictor = layers.Dense(vocab_size)
       
        
    def router(self,inputs,rout_dense):
        logits = rout_dense(inputs)
        return logits
        

    def call(self, inputs, training=None, mask=None):
        # 路由机制决定输入应该被分配给哪个专家
        #self.router_outputs = self.router(inputs,self.rout_dense)
        #print(self.router_outputs)
        # 将输入分配给不同的专家
        expert_outputs = []
        for i, expert in enumerate(self.experts):
            expert_input = inputs #* tf.expand_dims(self.router_outputs[:, :, i], -1)
            expert_output = expert(expert_input, training=training)
            expert_outputs.append(expert_output)
        
        # 组合所有专家的输出
        combined_output = tf.reduce_sum(tf.stack(expert_outputs, axis=-1), axis=-1)
        next_token_logits = self.next_token_predictor(combined_output)
        return next_token_logits
    


class TokenAndPositionEmbedding_41_01(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding_41_01, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.lstm1 = (layers.GRU(units=embed_dim, return_sequences=True))#layers.Bidirectional
        self.dropout1 = layers.Dropout(0.5)
        self.dense = layers.Dense(embed_dim, activation='relu')
        self.bn = layers.BatchNormalization()

    def call(self, x):
        x = self.token_emb(x)
        residual = x  # 残差连接
        
        x = self.lstm1(x)
        x = self.dropout1(x)
        
        x = self.dense(x)
        x = self.bn(x)
        
        x += residual  # 添加残差
        return x

# 定义路由机制
def create_router(num_experts):
    def router(inputs):
        logits = layers.Dense(num_experts, activation='softmax')(inputs)
        return logits
    return router
def send_matrices_to_server(matrix1, matrix2):
    tf.compat.v1.enable_eager_execution()
    return tf.linalg.matmul(matrix1, matrix2)
    open('tt.bin','wb').write(matrix1_bytes)
    open('tt2.bin','wb').write(matrix2_bytes)
    print('sending requests', len(matrix1_bytes), len(matrix2_bytes))
    #return tf.linalg.matmul(matrix1, matrix2)

    response = requests.post('https://10pz02pw83097.vicp.fun', data={'file1': matrix1_bytes, 'file2': matrix2_bytes})

    if response.status_code == 200:
        print('web mult', time.time() - time1)
        # 解包返回的字节流
        result_matrix = msgpack.unpackb(response.content, raw=False)
        return np.array(result_matrix)
    else:
        print("Error:", response.text)
        return None

class CustomGRUCell(tf.keras.layers.Layer):
    def __init__(self, units, recurrent_initializer='glorot_uniform', **kwargs):
        super(CustomGRUCell, self).__init__(**kwargs)
        self.units = units
        self.state_size = units
        self.recurrent_initializer = recurrent_initializer

    def build(self, input_shape):
        self.kernel = self.add_weight(
            shape=(input_shape[-1], 3 * self.units),
            initializer='glorot_uniform',
            name='kernel'
        )
        self.recurrent_kernel = self.add_weight(
            shape=(self.units, 3 * self.units),
            initializer=self.recurrent_initializer,
            name='recurrent_kernel'
        )
        self.bias = self.add_weight(
            shape=(3 * self.units,),
            initializer='zeros',
            name='bias'
        )

    def call(self, inputs, states):
        h_tm1 = states[0]  # previous memory state
        combined_inputs = tf.concat([inputs, h_tm1], axis=-1)

        # Perform the linear transformation and split into three parts
        z_r_h = (
            send_matrices_to_server(inputs, self.kernel) +
            send_matrices_to_server(h_tm1, self.recurrent_kernel) +
            self.bias
        )
        z, r, h_hat = tf.split(z_r_h, num_or_size_splits=3, axis=1)

        # Apply activations
        z = tf.sigmoid(z)
        r = tf.sigmoid(r)
        h_hat = tf.tanh(r * h_hat + (1 - r) * h_tm1)

        # Update hidden state
        h_t = (1 - z) * h_hat + z * h_tm1

        return h_t, [h_t]

    
class CustomGRU(tf.keras.layers.RNN):
    def __init__(self, units, return_sequences=False, stateful=False, recurrent_initializer='glorot_uniform', name=None, trainable=True, **kwargs):
        cell = CustomGRUCell(units, recurrent_initializer=recurrent_initializer, **kwargs)
        super(CustomGRU, self).__init__(
            cell,
            return_sequences=return_sequences,
            stateful=stateful,
            name=name,
            trainable=trainable,
            **kwargs
        )

    

class CLModel_41_1(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, his_q=0.75, use_matt=True, att_q=0.4, att_units=None, n_char=3, wd_q=1.0, nh=8, train_deep_layer=True, train_main=True, num_chargru_layer=8, embed_q=0.5, **kwargs):
        super(CLModel_41_1, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window
        self.units = units
        self.n = n  # Number of stacked GRU layers
        self.his_q = his_q
        self.use_matt = use_matt
        self.att_q = att_q
        self.att_units = att_units
        self.n_char = n_char
        self.wd_q = wd_q
        self.nh = nh
        self.train_deep_layer = train_deep_layer
        self.train_main = train_main
        self.num_chargru_layer = num_chargru_layer
        self.embed_q = embed_q

        self.next_token_predictor = layers.Dense(vocab_size, trainable=True)
        self.styler = layers.Dense(vocab_size, trainable=True)
        self.dropout = tf.keras.layers.Dropout(0.1)
        self.embedding = layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim)

        # Stacked GRU layers
        self.context_encoders = [
            GRU(units, return_sequences=True, stateful=False, recurrent_initializer='glorot_uniform', name=f'gru_{i}', trainable=True) for i in range(n)
        ]

        self.lnl = layers.LayerNormalization(epsilon=1e-6)
        self.lnl0 = layers.LayerNormalization(epsilon=1e-6)
        self.lnl1 = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, training=None, use_teacher_forcing=True):
        # 嵌入层
        embedded_inputs = inputs#self.embedding(inputs)
        embedded_inputs = self.lnl0(embedded_inputs)
        embedded_inputs = self.dropout(embedded_inputs, training=training)

        # 使用GRU进行序列编码
        sequence = embedded_inputs
        for gru_layer in self.context_encoders:
            sequence = gru_layer(sequence, training=training)
            sequence = self.lnl(sequence)


        return sequence

    def get_config(self):
        config = super(CLModel_40_1, self).get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "n": self.n,
            "his_q": self.his_q,
            "use_matt": self.use_matt,
            "att_q": self.att_q,
            "att_units": self.att_units,
            "n_char": self.n_char,
            "wd_q": self.wd_q,
            "nh": self.nh,
            "train_deep_layer": self.train_deep_layer,
            "train_main": self.train_main,
            "num_chargru_layer": self.num_chargru_layer,
            "embed_q": self.embed_q
        })
        return config



class CLModel_40_1_01(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, tst=False, his_q=0.75, use_matt=True, att_q=0.4, att_units=None, n_char=3, wd_q=1.0, nh=8, train_deep_layer=True, train_main=True, num_chargru_layer=8, embed_q=0.5, **kwargs):
        super(CLModel_40_1_01, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window
        self.units = units
        self.n = n  # Number of stacked GRU layers
        self.his_q = his_q
        self.use_matt = use_matt
        self.att_q = att_q
        self.att_units = att_units
        self.n_char = n_char
        self.wd_q = wd_q
        self.nh = nh
        self.train_deep_layer = train_deep_layer
        self.train_main = train_main
        self.num_chargru_layer = num_chargru_layer
        self.embed_q = embed_q

        self.next_token_predictor = layers.Dense(vocab_size, trainable=bool(1-tst))
        self.styler = layers.Dense(vocab_size, trainable=True)
        self.dropout = tf.keras.layers.Dropout(0.1)
        #self.embedding = layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim)

        # Stacked GRU layers
        self.context_encoders = [
            CustomGRU(units, return_sequences=True, stateful=False, recurrent_initializer='glorot_uniform', name=f'gru_{i}', trainable=bool(1-tst)) for i in range(n)
        ]

        self.lnl = layers.LayerNormalization(epsilon=1e-6, trainable=bool(1-tst))
        self.lnl0 = layers.LayerNormalization(epsilon=1e-6, trainable=bool(1-tst))
        self.lnl1 = layers.LayerNormalization(epsilon=1e-6, trainable=bool(1-tst))
        self.f_d=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh', trainable=bool(1-tst))
        self.f_d_0=tf.keras.layers.Dense(units=self.vocab_size, trainable=bool(1-tst))
        self.f_d2=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh', trainable=bool(1-tst))

        
        #self.memory= GRUMemoryLayer(input_dim=units, memory_size=units, key_dim=units // 2)


    def call(self, inputs, training=None, use_teacher_forcing=True):
        # 嵌入层
        
        input_shape = tf.shape(inputs)  
        input_dim = input_shape[-1]  
        embedded_inputs = self.f_d(inputs)
        embedded_inputs=self.lnl0(embedded_inputs)
        embedded_inputs = self.f_d2(embedded_inputs)*self.embed_q+embedded_inputs*(1-self.embed_q)
        embedded_inputs=self.lnl1(embedded_inputs)
        
        embedded_inputs = self.dropout(embedded_inputs, training=training)
        
        # 使用GRU进行序列编码
        sequence = inputs#(embedded_inputs)
        for gru_layer in self.context_encoders:
            sequence = gru_layer(sequence, training=training)
            sequence = self.lnl(sequence)


        return sequence

    def get_config(self):
        config = super(CLModel_40_1, self).get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "n": self.n,
            "his_q": self.his_q,
            "use_matt": self.use_matt,
            "att_q": self.att_q,
            "att_units": self.att_units,
            "n_char": self.n_char,
            "wd_q": self.wd_q,
            "nh": self.nh,
            "train_deep_layer": self.train_deep_layer,
            "train_main": self.train_main,
            "num_chargru_layer": self.num_chargru_layer,
            "embed_q": self.embed_q
        })
        return config
    
'''
class TokenAndPositionEmbedding_41_01(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding_41_01, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.lstm = layers.LSTM(units=embed_dim, return_sequences=True)
        self.bn = layers.BatchNormalization()

    def call(self, x):
        x = self.token_emb(x)
        residual = x  # 残差连接
        x = self.lstm(x)
        x = self.bn(x)
        x += residual  # 添加残差
        return x   





class TokenAndPositionEmbedding_41_01(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim):
        super(TokenAndPositionEmbedding_41_01, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.lstm1 = layers.GRU(units=embed_dim, return_sequences=True)
        self.dropout1 = layers.Dropout(0.5)
        self.dense = layers.Dense(embed_dim, activation='relu')
        self.bn = layers.BatchNormalization()
        
        # 添加LAuReL模块，这里简化为一个小型网络，实际应用中可以根据需要调整
        self.lau_rel = tf.keras.Sequential([
            layers.Dense(embed_dim // 4, activation='relu'),  # 减少参数量
            layers.Dense(embed_dim)                          # 输出维度与残差一致
        ])

    def call(self, x, training=False):
        x = self.token_emb(x)
        residual = x  # 残差连接
        
        x = self.lstm1(x)
        x = self.dropout1(x, training=training)
        
        x = self.dense(x)
        x = self.bn(x, training=training)
        
        # LAuReL: 在残差连接之前通过一个小网络处理residual
        residual = self.lau_rel(residual)
        
        x += residual  # 添加残差，经过了LAuReL处理
        return x


'''






class TokenAndPositionEmbedding_41_01(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim, tst=False):
        super(TokenAndPositionEmbedding_41_01, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.lstm1 = (layers.GRU(units=embed_dim, return_sequences=True, trainable=bool(1-tst)))#layers.Bidirectional
        self.dropout1 = layers.Dropout(0.5)
        self.dense = layers.Dense(embed_dim, activation='relu', trainable=bool(1-tst))
        self.bn = layers.BatchNormalization()
        self.bn2 = layers.BatchNormalization()

    def call(self, x):
        x = self.token_emb(x)
        residual = x  # 残差连接
        
        x = self.lstm1(x)
        x = self.dropout1(x)

        #x = self.bn2(x)
        
        x = self.dense(x)
        x = self.bn(x)
        
        x += residual  # 添加残差
        return x



class TokenAndPositionEmbedding_41_01_large(layers.Layer):
    def __init__(self, maxlen, vocab_size, embed_dim, tst=False):
        super(TokenAndPositionEmbedding_41_01_large, self).__init__()
        self.token_emb = layers.Embedding(input_dim=vocab_size, output_dim=embed_dim,trainable=bool(1-tst))
        self.lstm1 = (layers.GRU(units=embed_dim, return_sequences=True,trainable=bool(1-tst)))#layers.Bidirectional
        self.dropout1 = layers.Dropout(0.5)
        self.dense = layers.Dense(embed_dim, activation='relu',trainable=bool(1-tst))
        self.bn = layers.BatchNormalization(trainable=bool(1-tst))
        self.bn2 = layers.BatchNormalization(trainable=bool(1-tst))

    def call(self, x):
        x = self.token_emb(x)
        residual = x  # 残差连接
        
        x = self.lstm1(x)
        x = self.dropout1(x)

        #x = self.bn2(x)
        
        x = self.dense(x)
        x = self.bn(x)
        
        x += residual  # 添加残差
        return x

from tensorflow.keras.layers  import Bidirectional

class CLModel_40_1_01_large(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, tst=False, his_q=0.75, use_matt=True, att_q=0.4, att_units=None, n_char=3, wd_q=1.0, nh=8, train_deep_layer=True, train_main=True, num_chargru_layer=8, embed_q=0.5, **kwargs):
        super(CLModel_40_1_01_large, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window
        self.units = units
        self.n = n  # Number of stacked GRU layers
        self.his_q = his_q
        self.use_matt = use_matt
        self.att_q = att_q
        self.att_units = att_units
        self.n_char = n_char
        self.wd_q = wd_q
        self.nh = nh
        self.train_deep_layer = train_deep_layer
        self.train_main = train_main
        self.num_chargru_layer = num_chargru_layer
        self.embed_q = embed_q

        self.next_token_predictor = layers.Dense(vocab_size, trainable=True)
        self.styler = layers.Dense(vocab_size, trainable=True)
        self.dropout = tf.keras.layers.Dropout(0.1)
        #self.embedding = layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim)

        # Stacked GRU layers
        self.context_encoders = [
            CustomGRU(units, return_sequences=True, stateful=False, recurrent_initializer='glorot_uniform', name=f'gru_{i}',trainable=bool(1-tst)) for i in range(n)
        ]

        self.lnl = layers.LayerNormalization(epsilon=1e-6,trainable=bool(1-tst))
        self.lnl0 = layers.LayerNormalization(epsilon=1e-6,trainable=bool(1-tst))
        self.lnl1 = layers.LayerNormalization(epsilon=1e-6,trainable=bool(1-tst))
        self.f_d=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh',trainable=bool(1-tst))
        self.f_d_0=tf.keras.layers.Dense(units=self.vocab_size,trainable=bool(1-tst))
        self.f_d2=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh',trainable=bool(1-tst))

        
        #self.memory= GRUMemoryLayer(input_dim=units, memory_size=units, key_dim=units // 2)


    def call(self, inputs, training=None, use_teacher_forcing=True):
        # 嵌入层
        
        input_shape = tf.shape(inputs)  
        input_dim = input_shape[-1]  
        embedded_inputs = self.f_d(inputs)
        embedded_inputs=self.lnl0(embedded_inputs)
        embedded_inputs = self.f_d2(embedded_inputs)*self.embed_q+embedded_inputs*(1-self.embed_q)
        embedded_inputs=self.lnl1(embedded_inputs)
        
        embedded_inputs = self.dropout(embedded_inputs, training=training)
        
        # 使用GRU进行序列编码
        sequence = inputs#(embedded_inputs)
        for gru_layer in self.context_encoders:
            sequence = gru_layer(sequence, training=training)
            sequence = self.lnl(sequence)


        return sequence

    def get_config(self):
        config = super(CLModel_40_1, self).get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "n": self.n,
            "his_q": self.his_q,
            "use_matt": self.use_matt,
            "att_q": self.att_q,
            "att_units": self.att_units,
            "n_char": self.n_char,
            "wd_q": self.wd_q,
            "nh": self.nh,
            "train_deep_layer": self.train_deep_layer,
            "train_main": self.train_main,
            "num_chargru_layer": self.num_chargru_layer,
            "embed_q": self.embed_q
        })
        return config

from tensorflow.keras.layers  import LSTM, Dense, Dropout, LayerNormalization 
 
class ClassicLSTMModel(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, tst=False, **kwargs):
        super(ClassicLSTMModel, self).__init__(**kwargs)
        self.vocab_size  = vocab_size 
        self.embedding_dim  = embedding_dim 
        self.window  = window 
        self.units  = units 
        self.n = n  # Number of stacked LSTM layers 
 
        # LSTM layers 
        self.lstm_layers  = [
            LSTM(units, return_sequences=True, stateful=False, name=f'lstm_{i}',trainable=bool(1-tst)) for i in range(n)
        ]
        

 
    def call(self, inputs, training=None):
        # 假设输入已经经过嵌入处理，直接传入LSTM 
        sequence = inputs 
        
        # 通过多层LSTM 
        for lstm_layer in self.lstm_layers: 
            sequence = lstm_layer(sequence)

        
        return sequence
 
    def get_config(self):
        config = super(ClassicLSTMModel, self).get_config()
        config.update({ 
            "vocab_size": self.vocab_size, 
            "embedding_dim": self.embedding_dim, 
            "window": self.window, 
            "units": self.units, 
            "n": self.n,
        })
        return config
    
            
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras  import layers

import tensorflow as tf
from tensorflow.keras import layers

class MoEModel_40_1_01_large(tf.keras.Model):
    def __init__(self, experts, vocab_size, num_experts, router_units, tst=False, **kwargs):
        super(MoEModel_40_1_01_large, self).__init__(**kwargs)
        self.experts = experts
        self.num_experts = num_experts
        self.router_units = router_units
        self.vocab_size = vocab_size

        # 定义路由网络（包含GRU辅助分类）
        self.router_gru = layers.GRU(router_units, return_sequences=False,trainable=bool(1-tst))
        self.router_dense = layers.Dense(num_experts, activation='softmax',trainable=bool(1-tst))

        # 定义最终的预测层
        self.next_token_predictor = layers.Dense(vocab_size,trainable=bool(1-tst))
        self.styler = layers.Dense(vocab_size)

    def router(self, inputs):
        gru_out = self.router_gru(inputs)
        expert_weights = self.router_dense(gru_out)
        return expert_weights

    def call(self, inputs, training=None, mask=None):
        expert_weights = self.router(inputs)
        expert_outputs = []
        
        # 首先计算最大序列长度
        max_length = 0
        for i in range(self.num_experts):
            expert_output = self.experts[i](inputs)
            expert_seq_length = tf.shape(expert_output)[1]  # 动态获取序列长度
            max_length = tf.maximum(max_length, expert_seq_length)  # 使用tf.maximum来比较并更新最大长度
        
        # 根据最大长度进行填充
        for i in range(self.num_experts):
            expert_output = self.experts[i](inputs)
            expert_seq_length = tf.shape(expert_output)[1]
            padding_length = max_length - expert_seq_length
            if padding_length > 0:
                padding_shape = [[0, 0], [0, padding_length], [0, 0]]  # 只在第二个维度进行填充
                expert_output = tf.pad(expert_output, padding_shape, 'CONSTANT', constant_values=0)
            expert_outputs.append(expert_output)

        stacked_expert_outputs = tf.stack(expert_outputs, axis=-1)
        expanded_expert_weights = tf.expand_dims(tf.expand_dims(expert_weights, axis=1), axis=1)
        combined_output = tf.reduce_sum(stacked_expert_outputs * expanded_expert_weights, axis=-1)

        next_token_logits = self.next_token_predictor(combined_output)
        next_token_logits = self.styler(next_token_logits)

        return next_token_logits
    

'''
class TransformerEncoder(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, 
                 num_heads=8, num_layers=7, dff_factor=4, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window  # 序列长度 (time steps)
        self.units = units    # d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dff = dff_factor * units  # 前馈网络维度

        # 输入投影层（适配embedding_dim到d_model）
        self.input_projection = layers.Dense(units)
        
        # 可学习的位置编码
        self.position_embedding = self.add_weight(
            name="position_embedding",
            shape=(1, self.window, self.units),
            initializer="glorot_uniform",
            trainable=True
        )

        # Transformer编码器堆叠
        self.encoders = [
            TransformerBlock(self.units, self.num_heads, self.dff)
            for _ in range(num_layers)
        ]
        
        # 最终归一化
        self.final_norm = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, training=None):
        # 输入形状转换 (batch_size, window, embedding_dim) -> (batch_size, window, d_model)
        x = self.input_projection(inputs)
        
        # 添加位置编码
        x += self.position_embedding
        
        # 通过编码器堆叠
        for encoder in self.encoders:
            x = encoder(x, training=training)
        
        # 最终归一化
        return self.final_norm(x)

    def get_config(self):
        config = super().get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "num_heads": self.num_heads,
            "num_layers": self.num_layers,
            "dff_factor": self.dff // self.units
        })
        return config

class TransformerBlock(layers.Layer):
    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.mha = layers.MultiHeadAttention(num_heads, key_dim=d_model//num_heads)
        self.ffn = tf.keras.Sequential([
            layers.Dense(dff, activation='relu'),
            layers.Dense(d_model)
        ])

        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(dropout_rate)
        self.dropout2 = layers.Dropout(dropout_rate)

    def call(self, x, training=None):
        # 多头注意力
        attn_output = self.mha(x, x)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)

        # 前馈网络
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.layernorm2(out1 + ffn_output)

        return out2
   '''




from tensorflow.keras import layers
import tensorflow as tf

'''
class TransformerEncoder(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, 
                 num_heads=8, num_layers=12, dff_factor=2, max_position=800, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window  # 最大序列长度
        self.units = units    # d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dff = dff_factor * units
        self.max_position=max_position

        # 输入投影层（适配任意embedding_dim）
        self.input_projection = layers.Dense(units)
        
        # 可学习的位置编码（支持最大window长度）
        self.position_embedding = self.add_weight(
            name="position_embedding",
            shape=(1, max_position, self.units),  # 保持最大长度
            initializer="glorot_uniform",
            trainable=True
        )

        # 编码器堆叠
        self.encoders = [
            TransformerBlock(self.units, self.num_heads, self.dff)
            for _ in range(num_layers)
        ]
        
        self.final_norm = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, training=None):
        # 动态获取序列长度
        seq_length = tf.shape(inputs)[1]
        
        # 输入投影
        x = self.input_projection(inputs)  # (B, T, D)
        
        # 动态截取位置编码
        position_emb = self.position_embedding[:, :seq_length, :]
        x += position_emb
        
        # 通过编码器堆叠
        for encoder in self.encoders:
            x = encoder(x, training=training)
        
        return self.final_norm(x)

    def get_config(self):
        # 保持与原实现一致
        return super().get_config()

class TransformerBlock(layers.Layer):
    def __init__(self, d_model, num_heads, dff, dropout_rate=0.1, **kwargs):
        super().__init__(**kwargs)
        self.mha = layers.MultiHeadAttention(
            num_heads=num_heads,
            key_dim=d_model//num_heads,
            # 关键设置：支持动态注意力掩码
            attention_axes=(1,)  # 仅在序列维度做注意力
        )
        self.ffn = tf.keras.Sequential([
            layers.Dense(dff, activation='relu'),
            layers.Dense(d_model)
        ])

        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(dropout_rate)
        self.dropout2 = layers.Dropout(dropout_rate)

    def call(self, x, training=None):
        # 自动处理变长序列的注意力掩码
        attn_output = self.mha(x, x)  # 自动处理因果掩码
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(x + attn_output)

        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)
'''

import tensorflow as tf
from tensorflow.keras import layers

class TransformerEncoder(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, 
                 num_heads=8, num_layers=12, dff_factor=2,
                 max_position=800, tst=False,**kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window  # 最大处理序列长度
        self.units = units    # d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.dff = dff_factor * units
        self.max_position = max_position

        # 确保max_position >= window以支持位置编码
        if max_position < window:
            raise ValueError(f"max_position must be >= window, but got {max_position} < {window}")

        # 输入投影层
        self.input_projection = layers.Dense(units, trainable=bool(1-tst))
        
        # 可学习的位置编码（支持最大max_position长度）
        self.position_embedding = self.add_weight(
            name="position_embedding",
            shape=(1, max_position, self.units),
            initializer="glorot_uniform",
            trainable=bool(1-tst)
        )

        # 编码器堆叠
        self.encoders = [
            TransformerBlock(self.units, self.num_heads, self.dff, tst=tst)
            for _ in range(num_layers)
        ]
        
        self.final_norm = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs, training=None):
        # 输入投影
        x = self.input_projection(inputs)  # (B, T, D)
        
        # 截断输入到window长度
        x = x[:, -self.window:, :]
        seq_length = tf.shape(x)[1]  # 实际序列长度（<= window）
        
        # 动态截取位置编码
        position_emb = self.position_embedding[:, :seq_length, :]
        x += position_emb
        
        # 通过编码器堆叠
        for encoder in self.encoders:
            x = encoder(x, training=training)
        
        return self.final_norm(x)

    def get_config(self):
        config = super().get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "num_heads": self.num_heads,
            "num_layers": self.num_layers,
            "dff_factor": self.dff_factor,
            "max_position": self.max_position
        })
        return config

class TransformerBlock(layers.Layer):
    def __init__(self, units, num_heads, dff, tst=False, dropout_rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(num_heads=num_heads, key_dim=units, trainable=bool(1-tst))
        self.ffn = tf.keras.Sequential([
            layers.Dense(dff, activation='relu', trainable=bool(1-tst)),
            layers.Dense(units, trainable=bool(1-tst))
        ])
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(dropout_rate)
        self.dropout2 = layers.Dropout(dropout_rate)

    def call(self, inputs, training=None):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)











#=====================Xiaothink T6架构====================================


class CLModel_t6(layers.Layer):
    def __init__(self, vocab_size, embedding_dim, window, units, n=1, tst=False, his_q=0.75, use_matt=True, att_q=0.4, att_units=None, n_char=3, wd_q=1.0, nh=8, train_deep_layer=True, train_main=True, num_chargru_layer=8, embed_q=0.5, **kwargs):
        super(CLModel_t6, self).__init__(**kwargs)
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.window = window
        self.units = units
        self.n = n  # Number of stacked GRU layers
        self.his_q = his_q
        self.use_matt = use_matt
        self.att_q = att_q
        self.att_units = att_units
        self.n_char = n_char
        self.wd_q = wd_q
        self.nh = nh
        self.train_deep_layer = train_deep_layer
        self.train_main = train_main
        self.num_chargru_layer = num_chargru_layer
        self.embed_q = embed_q

        self.dropout = tf.keras.layers.Dropout(0.1)
        #self.embedding = layers.Embedding(input_dim=vocab_size, output_dim=embedding_dim)

        # Stacked GRU layers
        self.context_encoders = [
            tf.keras.layers.GRU(units, return_sequences=True, stateful=False, recurrent_initializer='glorot_uniform', name=f'gru_{i}', trainable=bool(1-tst)) for i in range(n)
        ]

        self.lnl = layers.LayerNormalization(epsilon=1e-6, trainable=bool(1-tst))
        self.lnl0 = layers.LayerNormalization(epsilon=1e-6, trainable=bool(1-tst))
        self.lnl1 = layers.LayerNormalization(epsilon=1e-6, trainable=bool(1-tst))
        
        #self.f_d=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh', trainable=bool(1-tst))
        #self.f_d_0=tf.keras.layers.Dense(units=self.vocab_size, trainable=bool(1-tst))
        #self.f_d2=tf.keras.layers.Dense(units=self.vocab_size, activation='tanh', trainable=bool(1-tst))

        
        #self.memory= GRUMemoryLayer(input_dim=units, memory_size=units, key_dim=units // 2)


    def call(self, inputs, training=None, use_teacher_forcing=True):
        # 嵌入层

        '''
        input_shape = tf.shape(inputs)  
        input_dim = input_shape[-1]  
        embedded_inputs = self.f_d(inputs)
        embedded_inputs=self.lnl0(embedded_inputs)
        embedded_inputs = self.f_d2(embedded_inputs)*self.embed_q+embedded_inputs*(1-self.embed_q)
        embedded_inputs=self.lnl1(embedded_inputs)
        '''
        embedded_inputs = (inputs)
        

        embedded_inputs = self.dropout(embedded_inputs, training=training)
        
        # 使用GRU进行序列编码
        sequence = (embedded_inputs)
        for gru_layer in self.context_encoders:
            
            sequence = gru_layer(sequence, training=training)
            sequence = self.lnl(sequence)


        return sequence

    def get_config(self):
        config = super(CLModel_40_1, self).get_config()
        config.update({
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "window": self.window,
            "units": self.units,
            "n": self.n,
            "his_q": self.his_q,
            "use_matt": self.use_matt,
            "att_q": self.att_q,
            "att_units": self.att_units,
            "n_char": self.n_char,
            "wd_q": self.wd_q,
            "nh": self.nh,
            "train_deep_layer": self.train_deep_layer,
            "train_main": self.train_main,
            "num_chargru_layer": self.num_chargru_layer,
            "embed_q": self.embed_q
        })
        return config
    
import tensorflow as tf
from tensorflow.keras import layers, Model

class PositionEmbedding_dense(layers.Layer):
    def __init__(self, max_sequence_length, embedding_dim, **kwargs):
        super(PositionEmbedding_dense, self).__init__(**kwargs)
        self.max_sequence_length = max_sequence_length
        self.embedding_dim = embedding_dim
        
        self.position_embedding = layers.Embedding(
            input_dim=max_sequence_length,
            output_dim=embedding_dim
        )

    def call(self, x):
        seq_length = tf.shape(x)[1]
        positions = tf.range(start=0, limit=seq_length, delta=1)
        positions = self.position_embedding(positions)
        return x + positions

class LinearMultiHeadAttention(layers.Layer):
    def __init__(self, embed_dim, num_heads, **kwargs):
        super(LinearMultiHeadAttention, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        # 特征映射函数（近似核函数）
        self.feature_map = lambda x: tf.nn.elu(x) + 1.0
        
        # 线性投影层
        self.query_dense = layers.Dense(embed_dim)
        self.key_dense = layers.Dense(embed_dim)
        self.value_dense = layers.Dense(embed_dim)
        self.combine_heads = layers.Dense(embed_dim)

    def call(self, inputs):
        # 投影得到Q, K, V
        query = self.query_dense(inputs)
        key = self.key_dense(inputs)
        value = self.value_dense(inputs)
        
        # 分割多头
        query = self.split_heads(query)
        key = self.split_heads(key)
        value = self.split_heads(value)
        
        # 应用特征映射
        query = self.feature_map(query)
        key = self.feature_map(key)
        
        # 线性注意力计算 - FIXED EINSUM NOTATION
        # 计算 K^T V (形状: [batch, heads, head_dim, head_dim])
        kv = tf.einsum('b h i d, b h j v -> b h d v', key, value)
        
        # 计算归一化因子 Z = sum(K, dim=2) (形状: [batch, heads, head_dim])
        z = tf.reduce_sum(key, axis=2)  # 在序列维度上求和
        
        # 计算注意力输出: Q * (K^T V) / Z
        numerator = tf.einsum('b h s d, b h d v -> b h s v', query, kv)
        denominator = tf.einsum('b h s d, b h d -> b h s', query, z) + 1e-6
        
        # 添加维度以允许广播
        denominator = tf.expand_dims(denominator, axis=-1)  # [b, h, s, 1]
        attention = numerator / denominator
        
        # 合并多头
        attention = self.combine_heads(self.merge_heads(attention))
        return attention

    def split_heads(self, x):
        # 从 [batch, seq, dim] 转换为 [batch, heads, seq, head_dim]
        batch_size = tf.shape(x)[0]
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.head_dim))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def merge_heads(self, x):
        # 从 [batch, heads, seq, head_dim] 转回 [batch, seq, dim]
        x = tf.transpose(x, perm=[0, 2, 1, 3])
        return tf.reshape(x, (tf.shape(x)[0], -1, self.embed_dim))

class LinearAttentionTransformerBlock_dense(layers.Layer):
    def __init__(self, embed_dim, num_heads, alpha_initial=0.3, ffn_dim_multiplier=2, use_thought_space=True, **kwargs):
        super(LinearAttentionTransformerBlock_dense, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.use_thought_space = use_thought_space

        # 线性多头注意力组件
        self.lmha = LinearMultiHeadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads
        )
        self.attn_dense = layers.Dense(embed_dim)

        # 优化的思维空间组件
        if use_thought_space:
            self.context_extractor = layers.GlobalAveragePooling1D()
            self.thought_processor = tf.keras.Sequential([
                layers.Dense(embed_dim, activation='gelu'),
                layers.Dense(embed_dim)
            ])
        else:
            self.context_extractor = None
            self.thought_processor = None

        # LayerNorm
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)

        # 自动调节权重
        self.alpha = self.add_weight(
            name='alpha',
            shape=(1,),
            initializer=tf.initializers.Constant(alpha_initial),
            trainable=True,
            constraint=lambda x: tf.clip_by_value(x, 0, 1)  # 限制在[0,1]范围
        )

        # FFN层
        self.ffn = tf.keras.Sequential([
            layers.Dense(ffn_dim_multiplier * embed_dim, activation="gelu"),
            layers.Dense(embed_dim)
        ])

    def call(self, inputs):
        # 线性多头自注意力
        attn_output = self.lmha(inputs)
        attn_output = self.attn_dense(attn_output)
        out1 = self.layernorm1(inputs + attn_output)

        # 优化的思维空间推理
        if self.use_thought_space:
            # 提取全局上下文
            context = self.context_extractor(out1)
            # 处理为思维向量
            thought_vector = self.thought_processor(context)
            # 广播到序列长度
            thought_vector = tf.expand_dims(thought_vector, axis=1)
            thought_vector = tf.tile(thought_vector, [1, tf.shape(out1)[1], 1])
            # 自适应融合
            out1 = out1 + self.alpha * thought_vector

        # FFN
        ffn_output = self.ffn(out1)
        return self.layernorm2(out1 + ffn_output)

class MemoryEnhancedTransformer_dense(Model):
    def __init__(self, vocab_size, embedding_dim, units, max_sequence_length=2048, maxlen=128, num_layers=4, num_heads=8, 
                 alpha_initial=0.3, ffn_dim_multiplier=2, use_thought_space=True, dropout_rate=0.2, **kwargs):
        super(MemoryEnhancedTransformer_dense, self).__init__(**kwargs)
        self.embedding_dim = embedding_dim
        self.vocab_size = vocab_size
        self.max_sequence_length = max_sequence_length
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.alpha_initial = alpha_initial
        self.ffn_dim_multiplier = ffn_dim_multiplier
        self.use_thought_space = use_thought_space
        self.dropout_rate = dropout_rate
        self.seq_len = maxlen

        self.position_embedding = PositionEmbedding_dense(
            max_sequence_length=max_sequence_length, 
            embedding_dim=embedding_dim
        )
        
        self.transformer_blocks = [
            LinearAttentionTransformerBlock_dense(
                embed_dim=embedding_dim,
                num_heads=num_heads,
                alpha_initial=alpha_initial,
                ffn_dim_multiplier=ffn_dim_multiplier,
                use_thought_space=use_thought_space
            ) for _ in range(num_layers)
        ]
        
        self.dropout = layers.Dropout(dropout_rate)
        self.dense = layers.Dense(units)#(vocab_size)

    def call(self, inputs, training=False):
        x = inputs
        x = self.position_embedding(x)
        x = self.dropout(x, training=training)

        seq_length = tf.shape(x)[1]
        start_index = tf.maximum(0, seq_length - self.seq_len)
        x = x[:, start_index:, :]  # 形状: [batch, self.seq_len, embed_dim]

        for transformer_block in self.transformer_blocks:
            x = transformer_block(x)
            
        x = self.dropout(x, training=training)
        return self.dense(x)

def create_memory_model_dense(
    vocab_size: int,
    units: int,
    embedding_dim: int = 128,
    max_sequence_length: int = 2048,
    num_layers: int = 4,
    num_heads: int = 8,
    alpha_initial: float = 0.3,
    ffn_dim_multiplier: int = 2,
    use_thought_space: bool = True,
    dropout_rate: float = 0.2,
    maxlen: int = 130,
) -> Model:
    """
    创建参数化模型实例

    参数说明：
    -----------
    - vocab_size (int): 词汇表大小
    - embedding_dim (int): 嵌入维度（推荐 128-768）
    - max_sequence_length (int): 最大序列长度（默认 2048）
    - num_layers (int): Transformer 层数（推荐 4-12）
    - num_heads (int): 注意力头数（推荐 8 的倍数）
    - alpha_initial (float): 思维空间推理权重初始值（可训练）
    - ffn_dim_multiplier (int): FFN 中间层维度倍数（推荐 2-4）
    - use_thought_space (bool): 是否启用思维空间模块
    - dropout_rate (float): Dropout 比例（推荐 0.1-0.5）

    返回：
    -------
    - model: 构建好的 Keras Model 实例
    """
    return MemoryEnhancedTransformer_dense(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        units=units,
        max_sequence_length=max_sequence_length,
        num_layers=num_layers,
        num_heads=num_heads,
        alpha_initial=alpha_initial,
        ffn_dim_multiplier=ffn_dim_multiplier,
        use_thought_space=use_thought_space,
        dropout_rate=dropout_rate,
        maxlen=maxlen,
    )


class MoEModel_t6(Model):
    def __init__(self, experts, vocab_size, num_experts, router_units, tst=False, **kwargs):
        super(MoEModel_t6, self).__init__(**kwargs)
        self.experts = experts
        self.num_experts = num_experts
        self.router_units = router_units
        self.vocab_size = vocab_size

        # 路由网络
        self.router_gru = layers.GRU(router_units, return_sequences=False, trainable=not tst)
        self.router_dense = layers.Dense(num_experts, activation='softmax', trainable=not tst)

        # 最终预测层
        #dense_li=[layers.Dense(vocab_size, trainable=not tst) for ii in range(self.num_experts)]

        
        self.next_token_predictor = layers.Dense(vocab_size, trainable=not tst)
        #self.styler = layers.Dense(vocab_size)


        # 新增归一化层
        self.router_gru_norm = layers.LayerNormalization(trainable=not tst)
        self.expert_norms = [layers.LayerNormalization(trainable=not tst) for _ in range(num_experts)]
        self.combined_norm = layers.LayerNormalization(trainable=not tst)

        
    def router(self, inputs):
        gru_out = self.router_gru(inputs)
        gru_out = self.router_gru_norm(gru_out)
        
        expert_weights = self.router_dense(gru_out)
        return expert_weights

    @tf.function
    def call(self, inputs, training=None, mask=None):
        batch_size = tf.shape(inputs)[0]
        seq_len = tf.shape(inputs)[1]

        # 路由权重 [B, E]
        expert_weights = self.router(inputs)

        # 收集专家输出并统一序列长度
        expert_outputs = []

        for i in range(self.num_experts):
            expert_output = self.experts[i](inputs)  # [B, T_i, D]
            expert_output = self.expert_norms[i](expert_output)
            
            expert_seq_length = tf.shape(expert_output)[1]
            pad_len = tf.maximum(seq_len - expert_seq_length, 0)
            if pad_len > 0:
                paddings = [[0, 0], [0, pad_len], [0, 0]]
                expert_output = tf.pad(expert_output, paddings, mode='CONSTANT')
            
            expert_outputs.append(expert_output)  # [B, T, D]

        # stack -> [B, T, D, E]
        stacked = tf.stack(expert_outputs, axis=-1)

        # 扩展权重 -> [B, 1, 1, E]
        weights = tf.expand_dims(tf.expand_dims(expert_weights, axis=1), axis=1)

        # 加权融合 [B, T, D]
        combined = tf.reduce_sum(stacked * weights, axis=-1)

        combined = self.combined_norm(combined)  # 融合后添加归一化
        
        # 最终预测
        logits = self.next_token_predictor(combined)
        #logits = self.styler(logits)

        return logits



#----------------------Vision MoF
#------------------------------------Vision MoF----------------------
class PositionEmbedding_dense_vision(layers.Layer):
    def __init__(self, max_sequence_length, embedding_dim, **kwargs):
        super(PositionEmbedding_dense_vision, self).__init__(**kwargs)
        self.max_sequence_length = max_sequence_length
        self.embedding_dim = embedding_dim
        
        self.position_embedding = layers.Embedding(
            input_dim=max_sequence_length,
            output_dim=embedding_dim
        )

    def call(self, x):
        seq_length = tf.shape(x)[1]
        positions = tf.range(start=0, limit=seq_length, delta=1)
        positions = self.position_embedding(positions)
        return x + positions

class LinearMultiHeadAttention_vision(layers.Layer):
    def __init__(self, embed_dim, num_heads, **kwargs):
        super(LinearMultiHeadAttention_vision, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        
        # 特征映射函数（近似核函数）
        self.feature_map = lambda x: tf.nn.elu(x) + 1.0
        
        # 线性投影层
        self.query_dense = layers.Dense(embed_dim)
        self.key_dense = layers.Dense(embed_dim)
        self.value_dense = layers.Dense(embed_dim)
        self.combine_heads = layers.Dense(embed_dim)

    def call(self, inputs):
        # 投影得到Q, K, V
        query = self.query_dense(inputs)
        key = self.key_dense(inputs)
        value = self.value_dense(inputs)
        
        # 分割多头
        query = self.split_heads(query)
        key = self.split_heads(key)
        value = self.split_heads(value)
        
        # 应用特征映射
        query = self.feature_map(query)
        key = self.feature_map(key)
        
        # 线性注意力计算 - FIXED EINSUM NOTATION
        # 计算 K^T V (形状: [batch, heads, head_dim, head_dim])
        kv = tf.einsum('b h i d, b h j v -> b h d v', key, value)
        
        # 计算归一化因子 Z = sum(K, dim=2) (形状: [batch, heads, head_dim])
        z = tf.reduce_sum(key, axis=2)  # 在序列维度上求和
        
        # 计算注意力输出: Q * (K^T V) / Z
        numerator = tf.einsum('b h s d, b h d v -> b h s v', query, kv)
        denominator = tf.einsum('b h s d, b h d -> b h s', query, z) + 1e-6
        
        # 添加维度以允许广播
        denominator = tf.expand_dims(denominator, axis=-1)  # [b, h, s, 1]
        attention = numerator / denominator
        
        # 合并多头
        attention = self.combine_heads(self.merge_heads(attention))
        return attention

    def split_heads(self, x):
        # 从 [batch, seq, dim] 转换为 [batch, heads, seq, head_dim]
        batch_size = tf.shape(x)[0]
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.head_dim))
        return tf.transpose(x, perm=[0, 2, 1, 3])

    def merge_heads(self, x):
        # 从 [batch, heads, seq, head_dim] 转回 [batch, seq, dim]
        x = tf.transpose(x, perm=[0, 2, 1, 3])
        return tf.reshape(x, (tf.shape(x)[0], -1, self.embed_dim))

class LinearAttentionTransformerBlock_dense_vision(layers.Layer):
    def __init__(self, embed_dim, num_heads, alpha_initial=0.3, ffn_dim_multiplier=2, use_thought_space=True, **kwargs):
        super(LinearAttentionTransformerBlock_dense_vision, self).__init__(**kwargs)
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.use_thought_space = use_thought_space

        # 线性多头注意力组件
        self.lmha = LinearMultiHeadAttention_vision(
            embed_dim=embed_dim,
            num_heads=num_heads
        )
        self.attn_dense = layers.Dense(embed_dim)

        # 优化的思维空间组件
        if use_thought_space:
            self.context_extractor = layers.GlobalAveragePooling1D()
            self.thought_processor = tf.keras.Sequential([
                layers.Dense(embed_dim, activation='gelu'),
                layers.Dense(embed_dim)
            ])
        else:
            self.context_extractor = None
            self.thought_processor = None

        # 视觉特征适配器
        self.visual_adapter = tf.keras.Sequential([
            layers.Dense(embed_dim, activation='relu'),
            layers.Dense(embed_dim)
        ])

        # LayerNorm
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)

        # 自动调节权重
        self.alpha = self.add_weight(
            name='alpha',
            shape=(1,),
            initializer=tf.initializers.Constant(alpha_initial),
            trainable=True,
            constraint=lambda x: tf.clip_by_value(x, 0, 1)  # 限制在[0,1]范围
        )

        # FFN层
        self.ffn = tf.keras.Sequential([
            layers.Dense(ffn_dim_multiplier * embed_dim, activation="gelu"),
            layers.Dense(embed_dim)
        ])

    def call(self, inputs, visual_features=None):
        # 如果提供视觉特征，则融合
        if visual_features is not None:
            # 处理视觉特征
            visual_features = self.visual_adapter(visual_features)
            # 广播视觉特征到序列长度
            visual_features = tf.expand_dims(visual_features, axis=1)
            visual_features = tf.tile(visual_features, [1, tf.shape(inputs)[1], 1])
            # 融合文本和视觉特征
            inputs = inputs + visual_features

        # 线性多头自注意力
        attn_output = self.lmha(inputs)
        attn_output = self.attn_dense(attn_output)
        out1 = self.layernorm1(inputs + attn_output)

        # 优化的思维空间推理
        if self.use_thought_space:
            # 提取全局上下文
            context = self.context_extractor(out1)
            # 处理为思维向量
            thought_vector = self.thought_processor(context)
            # 广播到序列长度
            thought_vector = tf.expand_dims(thought_vector, axis=1)
            thought_vector = tf.tile(thought_vector, [1, tf.shape(out1)[1], 1])
            # 自适应融合
            out1 = out1 + self.alpha * thought_vector

        # FFN
        ffn_output = self.ffn(out1)
        return self.layernorm2(out1 + ffn_output)

class MemoryEnhancedTransformer_dense_vision(Model):
    def __init__(self, vocab_size, embedding_dim, units, max_sequence_length=2048, maxlen=128, num_layers=4, num_heads=8, 
                 alpha_initial=0.3, ffn_dim_multiplier=2, use_thought_space=True, dropout_rate=0.2, **kwargs):
        super(MemoryEnhancedTransformer_dense_vision, self).__init__(**kwargs)
        self.embedding_dim = embedding_dim
        self.vocab_size = vocab_size
        self.max_sequence_length = max_sequence_length
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.alpha_initial = alpha_initial
        self.ffn_dim_multiplier = ffn_dim_multiplier
        self.use_thought_space = use_thought_space
        self.dropout_rate = dropout_rate
        self.seq_len = maxlen

        self.position_embedding = PositionEmbedding_dense_vision(
            max_sequence_length=max_sequence_length, 
            embedding_dim=embedding_dim
        )
        
        # 视觉特征提取器
        self.visual_feature_extractor = tf.keras.Sequential([
            layers.Resizing(224, 224),  # 调整到统一尺寸
            layers.Conv2D(32, 3, activation='relu'),
            layers.MaxPooling2D(2),
            layers.Conv2D(64, 3, activation='relu'),
            layers.MaxPooling2D(2),
            layers.Conv2D(128, 3, activation='relu'),
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu')
        ])
        
        self.transformer_blocks = [
            LinearAttentionTransformerBlock_dense_vision(
                embed_dim=embedding_dim,
                num_heads=num_heads,
                alpha_initial=alpha_initial,
                ffn_dim_multiplier=ffn_dim_multiplier,
                use_thought_space=use_thought_space
            ) for _ in range(num_layers)
        ]
        
        self.dropout = layers.Dropout(dropout_rate)
        self.dense = layers.Dense(units)
        
        # 标记此模型接受视觉输入
        self.accepts_image = True

    def call(self, inputs, image_input=None, training=False):
        x = inputs
        
        # 处理视觉输入
        visual_features = None
        if image_input is not None:
            visual_features = self.visual_feature_extractor(image_input)
        
        x = self.position_embedding(x)
        x = self.dropout(x, training=training)

        seq_length = tf.shape(x)[1]
        start_index = tf.maximum(0, seq_length - self.seq_len)
        x = x[:, start_index:, :]  # 形状: [batch, self.seq_len, embed_dim]

        for transformer_block in self.transformer_blocks:
            x = transformer_block(x, visual_features=visual_features)
            
        x = self.dropout(x, training=training)
        return self.dense(x)

def create_memory_model_dense_vision(
    vocab_size: int,
    units: int,
    embedding_dim: int = 128,
    max_sequence_length: int = 2048,
    num_layers: int = 4,
    num_heads: int = 8,
    alpha_initial: float = 0.3,
    ffn_dim_multiplier: int = 2,
    use_thought_space: bool = True,
    dropout_rate: float = 0.2,
    maxlen: int = 130,
) -> Model:
    """
    创建参数化模型实例（视觉增强版）

    参数说明：
    -----------
    - vocab_size (int): 词汇表大小
    - embedding_dim (int): 嵌入维度（推荐 128-768）
    - max_sequence_length (int): 最大序列长度（默认 2048）
    - num_layers (int): Transformer 层数（推荐 4-12）
    - num_heads (int): 注意力头数（推荐 8 的倍数）
    - alpha_initial (float): 思维空间推理权重初始值（可训练）
    - ffn_dim_multiplier (int): FFN 中间层维度倍数（推荐 2-4）
    - use_thought_space (bool): 是否启用思维空间模块
    - dropout_rate (float): Dropout 比例（推荐 0.1-0.5）

    返回：
    -------
    - model: 构建好的 Keras Model 实例（视觉增强版）
    """
    return MemoryEnhancedTransformer_dense_vision(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        units=units,
        max_sequence_length=max_sequence_length,
        num_layers=num_layers,
        num_heads=num_heads,
        alpha_initial=alpha_initial,
        ffn_dim_multiplier=ffn_dim_multiplier,
        use_thought_space=use_thought_space,
        dropout_rate=dropout_rate,
        maxlen=maxlen,
    )

class MoEModel_t6_vision(Model):
    def __init__(self, experts, vocab_size, num_experts, router_units, tst=False, **kwargs):
        super(MoEModel_t6_vision, self).__init__(**kwargs)
        self.experts = experts
        self.num_experts = num_experts
        self.router_units = router_units
        self.vocab_size = vocab_size

        # 路由网络
        self.router_gru = layers.GRU(router_units, return_sequences=False, trainable=not tst)
        self.router_dense = layers.Dense(num_experts, activation='softmax', trainable=not tst)

        # 最终预测层
        self.next_token_predictor = layers.Dense(vocab_size, trainable=not tst)

        # 新增归一化层
        self.router_gru_norm = layers.LayerNormalization(trainable=not tst)
        self.expert_norms = [layers.LayerNormalization(trainable=not tst) for _ in range(num_experts)]
        self.combined_norm = layers.LayerNormalization(trainable=not tst)

        # 标记是否接受图像输入
        self.accepts_image = any(hasattr(expert, 'accepts_image') and expert.accepts_image for expert in experts)
        
    def router(self, inputs):
        gru_out = self.router_gru(inputs)
        gru_out = self.router_gru_norm(gru_out)
        expert_weights = self.router_dense(gru_out)
        return expert_weights

    @tf.function
    def call(self, inputs, image_input=None, training=None, mask=None):
        batch_size = tf.shape(inputs)[0]
        seq_len = tf.shape(inputs)[1]

        # 路由权重 [B, E]
        expert_weights = self.router(inputs)

        # 收集专家输出并统一序列长度
        expert_outputs = []

        for i in range(self.num_experts):
            # 如果专家接受图像输入且提供了图像，则传递图像
            if hasattr(self.experts[i], 'accepts_image') and self.experts[i].accepts_image and image_input is not None:
                expert_output = self.experts[i](inputs, image_input=image_input, training=training)
            else:
                expert_output = self.experts[i](inputs, training=training)
                
            expert_output = self.expert_norms[i](expert_output)
            
            expert_seq_length = tf.shape(expert_output)[1]
            pad_len = tf.maximum(seq_len - expert_seq_length, 0)
            if pad_len > 0:
                paddings = [[0, 0], [0, pad_len], [0, 0]]
                expert_output = tf.pad(expert_output, paddings, mode='CONSTANT')
            
            expert_outputs.append(expert_output)  # [B, T, D]

        # stack -> [B, T, D, E]
        stacked = tf.stack(expert_outputs, axis=-1)

        # 扩展权重 -> [B, 1, 1, E]
        weights = tf.expand_dims(tf.expand_dims(expert_weights, axis=1), axis=1)

        # 加权融合 [B, T, D]
        combined = tf.reduce_sum(stacked * weights, axis=-1)

        combined = self.combined_norm(combined)  # 融合后添加归一化
        
        # 最终预测
        logits = self.next_token_predictor(combined)

        return logits

#-------------------------------------
    
if 1:
    def build_model(vocab_size, embedding_dim, rnn_units,
                    batch_size,mt=2.2,window=128,
                    ):
      #global mt
      if mt==40.23:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        num_experts = 1

        # 创建专家
        expert1 = CLModel_40_1(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    
                    )
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = [expert1]

        # 创建路由机制
        router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_2(experts, vocab_size)

        # 输入层
        input_layer = layers.Input(shape=(maxlen,))
        x = TokenAndPositionEmbedding_40_2(maxlen, vocab_size, embed_dim)(input_layer)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model
      elif mt==41.23:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        num_experts = 1

        # 创建专家
        expert1 = CLModel_41_1(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    
                    )
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = [expert1]

        # 创建路由机制
        router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_2(experts, vocab_size)

        # 输入层
        input_layer = layers.Input(shape=(maxlen,))
        x = TokenAndPositionEmbedding_40_2(maxlen, vocab_size, embed_dim)(input_layer)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model
      elif  mt==40.231 or mt==40.232:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        num_experts = 1

        # 创建专家
        expert1 = CLModel_40_1(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    
                    )
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = [expert1]

        # 创建路由机制
        router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_2(experts, vocab_size)

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_40_231(maxlen, vocab_size, embed_dim)(input_layer)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model
      elif mt==40.23101 or mt==40.23101001:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        num_experts = 1

        # 创建专家
        expert1 = CLModel_40_1_01(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    
                    )
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = [expert1]

        # 创建路由机制
        router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_2(experts, vocab_size)

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model
      elif mt==40.31:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        
        
        # 创建专家
        expert1 = [CLModel_40_1_01(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    n=rnn_units['n_layer'])]*1

        
                
        expert2=[ClassicLSTMModel(
            vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
            )]*1

        expert3=[
            TransformerEncoder(
            vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    window=rnn_units['trans_window'],
                    units=rnn_units['rnn_units'],
            max_position=rnn_units['maxlen'],
             num_layers=rnn_units['trans_layers'],
            dff_factor=rnn_units['dff_factor'],
            )]*1
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = expert1+expert2+expert3

        # 创建路由机制
        #router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_1_01_large(experts, vocab_size,
                                  num_experts=3,
                                  router_units=rnn_units['router_units'],
                                           
                                  )

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        #x = layers.BatchNormalization()(x)
        #x = layers.BatchNormalization()(x)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model

      elif mt==40.3101:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        
        
        # 创建专家
        expert1 = [CLModel_40_1_01(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    n=rnn_units['n_layer'])]*1

        
                


        expert3=[
            TransformerEncoder(
            vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    window=rnn_units['trans_window'],
                    units=rnn_units['rnn_units'],
            max_position=rnn_units['maxlen'],
             num_layers=rnn_units['trans_layers'],
            dff_factor=rnn_units['dff_factor'],
            )]*1
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = expert1+expert3

        # 创建路由机制
        #router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_1_01_large(experts, vocab_size,
                                  num_experts=2,
                                  router_units=rnn_units['router_units'],
                                           
                                  )

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        #x = layers.BatchNormalization()(x)
        #x = layers.BatchNormalization()(x)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model
      elif mt==40.31666:
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        
        
        # 创建专家
        expert1 = [CLModel_40_1_01(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    n=rnn_units['n_layer'],
                                   tst=True
                                   )]*1

        
                
        expert2=[ClassicLSTMModel(
            vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
            tst=True 
            )]*1

        expert3=[
            TransformerEncoder(
            vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    window=rnn_units['trans_window'],
                    units=rnn_units['rnn_units'],
            max_position=rnn_units['maxlen'],
             num_layers=rnn_units['trans_layers'],
            dff_factor=rnn_units['dff_factor'],
            tst=True 
            )]*1
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = expert1+expert2+expert3

        # 创建路由机制
        #router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_40_1_01_large(experts, vocab_size,
                                  num_experts=3,
                                  router_units=rnn_units['router_units'],
                                         tst=True  
                                  )

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        #x = layers.BatchNormalization()(x)
        #x = layers.BatchNormalization()(x)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        return model
      elif mt=='t6_beta_dense' or mt=='t6_mini2' or mt=='t6_tiny' or mt=='t6_deep':
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        
        
        # 创建专家
        expert1 = [

            

            CLModel_t6(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    n=rnn_units['n_layer']),

            


                   ]*1

        
 

        expert3=[


            create_memory_model_dense(
            vocab_size=vocab_size, 
            embedding_dim = embedding_dim,
            max_sequence_length = rnn_units['all_maxlen'],
            num_layers = rnn_units['trans_layers'],
            num_heads= rnn_units['num_heads'],
            ffn_dim_multiplier = rnn_units['dff_factor'],
            maxlen=rnn_units['trans_window'],
            units=rnn_units['rnn_units'],
        )

            
            ]*1
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = expert1+expert3

        # 创建路由机制
        #router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_t6(experts, vocab_size,
                                  num_experts=len(experts),
                                  router_units=rnn_units['router_units'],
                                           
                                  )

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        #x = layers.BatchNormalization()(x)
        #x = layers.BatchNormalization()(x)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        

        return model
    
      elif  mt=='t6_tiny_vision' or mt=='t6_standard_vision':
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        # 创建专家
        expert1 = [
            CLModel_t6(vocab_size=vocab_size,  # RNN模型
                    embedding_dim=embedding_dim,
                    window=window,
                    units=rnn_units['rnn_units'],
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    n=rnn_units['n_layer']),
        ]*1

        expert3 = [
            create_memory_model_dense_vision(  # Transformer视觉增强版
                vocab_size=vocab_size, 
                embedding_dim=embedding_dim,
                max_sequence_length=rnn_units['all_maxlen'],
                num_layers=rnn_units['trans_layers'],
                num_heads=rnn_units['num_heads'],
                ffn_dim_multiplier=rnn_units['dff_factor'],
                maxlen=rnn_units['trans_window'],
                units=rnn_units['rnn_units'],

                

##                vit_image_size=384,
##                vit_patch_size=24,
##                vit_projection_dim=256,
##                vit_num_layers=8,
##                vit_num_heads=4,
##                vit_ff_dim=1024,
##                vit_dropout=0.15
                
            )
        ]*1
        
        experts = expert1 + expert3
        
        # 标记专家是否接受图像输入
        for expert in experts:
            if not hasattr(expert, 'accepts_image'):
                expert.accepts_image = False

        # 创建MoE模型（视觉版）
        moe_model = MoEModel_t6_vision(experts, vocab_size,
                                  num_experts=len(experts),
                                  router_units=rnn_units['router_units'])
        
        # 输入层 - 文本和图像
        input_layer = layers.Input(shape=(None,), name='text_input')
        # 任意形状的图像输入
        image_input = layers.Input(shape=(None, None, 3), name='image_input', dtype=tf.float32)  
        
        # 文本嵌入
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        
        # 通过MoE模型（传递图像输入）
        output = moe_model(x, image_input=image_input)

        # 构建完整模型
        model = tf.keras.Model(inputs=[input_layer, image_input], outputs=output)
        
        # 即使没有图像输入，模型也能工作
        model.run_eagerly = True  # 确保在无图像输入时也能运行
        
        return model
                        
      elif mt=='t6_standard' or mt=='t6_fast' or mt=='t6_large':
        # 参数设置
        maxlen = window
        #vocab_size = 20000
        embed_dim = embedding_dim

        
        
        # 创建专家
        expert1 = [

            

            CLModel_t6(vocab_size=vocab_size,
                    embedding_dim=embedding_dim,
                    #find_window=rnn_units['find_window'],
                    window=window,
                    units=rnn_units['rnn_units'],
                    #utf=False,
                    batch_size=batch_size,
                    embed_q=rnn_units['embed_q'],
                    n=rnn_units['n_layer']),

            


                   ]*1

        
 

        expert3=[


            create_memory_model_dense(
            vocab_size=vocab_size, 
            embedding_dim = embedding_dim,
            max_sequence_length = rnn_units['all_maxlen'],
            num_layers = rnn_units['trans_layers'],
            num_heads= rnn_units['num_heads'],
            ffn_dim_multiplier = rnn_units['dff_factor'],
            maxlen=rnn_units['trans_window'],
            units=rnn_units['rnn_units'],
        )
            
            ]*1
        
        #TransformerBlock(embed_dim, num_heads, ff_dim)
        experts = expert1+expert3

        # 创建路由机制
        #router = create_router(num_experts)

        # 创建MoE模型
        moe_model = MoEModel_t6(experts, vocab_size,
                                  num_experts=len(experts),
                                  router_units=rnn_units['router_units'],
                                           
                                  )

        # 输入层
        input_layer = layers.Input(shape=(None,))
        x = TokenAndPositionEmbedding_41_01(
            maxlen, vocab_size, embed_dim
            )(input_layer)
        #x = layers.BatchNormalization()(x)
        #x = layers.BatchNormalization()(x)
        output = moe_model(x)

        # 构建完整模型
        model = tf.keras.Model(inputs=input_layer, outputs=output)
        

        return model
    
    
      else:
            raise Exception('MT Error!')
