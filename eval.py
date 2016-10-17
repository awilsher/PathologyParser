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
from collections import Counter

# "evaluate" the trained RNN model by computing softmax activations for "true" or "false" for each sequence of characters in the first 400 characters on the input (i.e. first 400 chars of an individual pathology report)
# i.e. score each sequence with a probability that it is, or is not, a test name
# then, take every sequence with a score above a threshold, find the longest common substrings, and print out the top X - the hypothesis is that one of these will be the test name
# this is simply a trial approach - I don't actually think this works any better than simple partial regex matching on each line
# however, I think it would definitely be worth exploring the RNN approach by scoring report sequences with some kind of metric trained on an "authoritative" input source - infectious diseases dictionary/encyclopaedia, textbooks, etc. 
# the approach would be similar - we (humans) can identify that a particular sequence of characters is a report names not because we've seen that exact sequence before (we might not have), but because we have previously learned that some of the individual subsequences are important (from our work/education/textbooks/etc)
# very interesting problem to explore!

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('eval_dir', '/tmp/healthhack_eval',
                           """Directory where to write event logs.""")
tf.app.flags.DEFINE_string('eval_data', 'test',
                           """Either 'test' or 'train_eval'.""")
tf.app.flags.DEFINE_string('checkpoint_dir', '/tmp/healthhacktrain',
                           """Directory where to read model checkpoints.""")
tf.app.flags.DEFINE_integer('eval_interval_secs', 60 * 5,
                            """How often to run the eval.""")
tf.app.flags.DEFINE_integer('num_examples', 100,
                            """Number of examples to run.""")
tf.app.flags.DEFINE_boolean('run_once', False,
                         """Whether to run eval only once.""")
                         
tf.app.flags.DEFINE_boolean('use_fp16', False,
                            """Train the model using fp16.""")


# rebuild dict
lines = []
i = 0
char_indices = []
with open('tests.csv') as f:
    for line in f:
        lines.append(line)
        for char in line:
            if char not in char_indices:
                char_indices.append(char)

unique_chars = 57
# create tensor from dataframe
input = tf.placeholder(tf.float32,(1,1,unique_chars))

# Parameters
batch_size = 1
n_steps = 1
n_input = unique_chars
n_output = 2
num_layers = 1;
n_hidden = 128


# Define weights
weights = {
    'out': tf.Variable(tf.random_normal([n_hidden, n_output]),name="weights")
}
biases = {
    'out': tf.Variable(tf.random_normal([n_output]),name="biases")
}

state_placeholder = tf.placeholder(tf.float32, shape=((num_layers, 2, 1, n_hidden)))
outputs, states = model.RNN(input, weights, biases, num_layers, n_input, n_hidden, batch_size, n_steps, state_placeholder)        
predictions = tf.nn.softmax(tf.squeeze(outputs, squeeze_dims=[0]))

saver = tf.train.Saver([weights['out'],biases['out']])

def lcs(S,T):
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    lcs_set = set()
                    longest = c
                    lcs_set.add(S[i-c+1:i+1])
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])

    return lcs_set

with tf.Session() as sess:
    ckpt = tf.train.get_checkpoint_state(FLAGS.checkpoint_dir)
    if ckpt and ckpt.model_checkpoint_path:
      # Restores from checkpoint
      saver.restore(sess, ckpt.model_checkpoint_path)
      # Assuming model_checkpoint_path looks something like:
      #   /my-favorite-path/cifar10_train/model.ckpt-0,
      # extract global_step from it.
      global_step = ckpt.model_checkpoint_path.split('/')[-1].split('-')[-1]
    else:
      print('No checkpoint file found')
      sys.exit()
    # Start the queue runners.
    coord = tf.train.Coordinator()
    sess.run(tf.initialize_all_variables())
    state = np.zeros((num_layers, 2, batch_size, n_hidden))
    
    char_buffer = []
    with open('syp.stripped.csv.small') as f:
        for line in f:
            subsequences = []
            found = 0
            for char_buffer in [line[i:i+30] for i in range(75, len(line)) if i < 390]:
                buffer = [char_indices.index(c.upper()) if c.upper() in char_indices else unique_chars - 2 for c in char_buffer]
                # create a queue of 1 * 1 sequences
                char_scores = []
                for i in range(30):
                    if i < len(buffer):
                        one_hot = np.zeros((1,1,unique_chars))
                        one_hot[0,0,buffer[i]] = 1
                        pred, state = sess.run([predictions, states],feed_dict={state_placeholder:state,input:one_hot})
                        char_scores.append(pred[0][1])

                if np.mean(char_scores) > 0.5:
                    found += 1
                    #print("".join(char_buffer))
                    subsequences.append(char_buffer)
            longest_common_substrings = []
            for i in range(len(subsequences)):
                for j in range(len(subsequences)):
                    if i != j:
                        lcs1 = lcs(subsequences[i], subsequences[j])
                        if len(lcs1) > 0:
                            el = lcs1.pop()
                            if len(el) > 5:
                                longest_common_substrings.append(el)
            counter = Counter(longest_common_substrings)
            top20 = counter.most_common(20)
            idx = 0
            max = [0,""]
            b = False
            match = None
            # for line in lines:
                # if b:
                    # break
            for item in top20:
                print(item[0])
