import gc
import pandas as pd
import random
import numpy as np
import Parse1 as parser
from sklearn.decomposition import PCA
from sklearn import preprocessing
import matplotlib.pyplot as plt
import pylab
import sys
from collections import defaultdict
import string
import tensorflow as tf
import model

# train a recurrent neural network
# each input is a sequence of characters 
# our "true" inputs are test names (each sequence in the input file must have the same length - this was already preprocessed determined by taking the longest sequence, then padding any shorter sequences with spaces)
# these "true" inputs are labeled "true" (1)
# the "false" inputs need to be anything other than test names, labeled "false" (0)
# at the moment we are using the original report CSV as our source for "false" inputs but this is not correct as this will also slurp in legitimate test names!
# maybe "true" inputs should be any sequences from the report CSV that fuzzy match a certain % of characters from the test name?

rows = []
i = 0
char_indices = []
sequence_length = 0
with open('tests.csv') as f:
    for line in f:
        sequence_length = len(line)
        rows.append([] * len(line))
        for char in line:
            if char not in char_indices:
                char_indices.append(char)
            rows[i].append(char_indices.index(char))
        i += 1

df = pd.DataFrame(rows)
df.iloc[:,-1] = 1 
df.fillna(value=0,inplace=True)
original = df.copy()

rows = []
i = 0
with open('syp.stripped.csv.small') as f:
    buffer = []
    for line in f:
        for char in line:
            if char not in char_indices:
                char_indices.append(char)
            if len(buffer) == sequence_length:
                rows.append([char_indices.index(c) for c in buffer])
                buffer = buffer[1:len(buffer) - 1]
            buffer.append(char)

for row in rows:
    row.append(0)
    
df = df.append(pd.DataFrame(rows),ignore_index=True)
df = df.append([original] * 5,ignore_index=True)
df.fillna(value=0,inplace=True)
unique_chars = len(char_indices) 
batch_size = 100

# create tensor from dataframe
input = tf.convert_to_tensor(df.values, dtype=tf.float32)

# create a queue of 1 * sequence_length sequences
input = tf.train.input_producer(input)
# dequeue a sequence, slice and apply one-hot encoding
input = input.dequeue()
input = tf.reshape(input, [1,-1])

# copy the sequence and offset by 1 to create an input/output pair
inputs = tf.slice(input, [0,0], [-1, sequence_length-1], name="inputs")
outputs = tf.slice(input, [0,sequence_length - 2], [-1, 1], name="outputs")

inputs = tf.cast(inputs, tf.int32)
outputs = tf.cast(outputs, tf.int32)
# apply one-hot encoding
inputs = tf.one_hot(inputs, unique_chars)
outputs = tf.one_hot(outputs, 2)
outputs = tf.reshape(outputs,[-1,1])   
outputs = tf.cast(outputs,tf.float32)

# create a batch of batch_size * sequence_length * unique_chars
input_batch, output_batch = tf.train.batch([inputs, outputs], batch_size)

model.train(tf.squeeze(input_batch), output_batch, batch_size,sequence_length -1, char_indices)
