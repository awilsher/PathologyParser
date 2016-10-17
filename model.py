import tensorflow as tf
import numpy as np
import random
import os, sys

def RNN(x, weights, biases, num_layers, n_input, n_hidden, batch_size, n_steps, state_placeholder):

    l = tf.unpack(state_placeholder, axis=0)
    state = tuple([tf.nn.rnn_cell.LSTMStateTuple(l[idx][0], l[idx][1]) for idx in range(num_layers)])
        
    lstm = tf.nn.rnn_cell.LSTMCell(n_hidden, forget_bias=1.0, state_is_tuple=True,cell_clip=5)
    dropout = tf.nn.rnn_cell.DropoutWrapper(lstm,output_keep_prob=0.5)  
    lstm_stack = tf.nn.rnn_cell.MultiRNNCell([dropout] * num_layers,state_is_tuple=True) 
    # reshape x to a list of n_steps tensors batch_size * vocab
    x = tf.transpose(x, [1, 0, 2])
    # Reshaping to (n_steps*batch_size, n_input)
    x = tf.reshape(x, [-1, n_input])
    # Split to get a list of 'n_steps' tensors of shape (batch_size, n_input)   
    x = tf.split(0, n_steps, x)

    outputs, states = tf.nn.rnn(lstm_stack, x, dtype=tf.float32, initial_state=state, sequence_length=[n_steps] * batch_size)
    weighted_outputs = []
    for output in outputs:
        weighted_outputs.append(tf.matmul(output, weights['out']) + biases['out']) 
    return weighted_outputs, states
            
def train(input_batch, output_batch, batch_size,sequence_length, dictionary):

    n_input = len(dictionary)
    n_output = 2
    
    # Parameters
    learning_rate = 0.002
    training_iters = 10000000
    display_step = 100
    num_layers = 1;
    save_step = 1000
    n_hidden = 128
    
    # # Define weights
    weights = {
        'out': tf.Variable(tf.random_normal([n_hidden, n_output]),name="weights")
    }
    biases = {
        'out': tf.Variable(tf.random_normal([n_output]),name="biases")
    }
    
    # Training operations
    with tf.variable_scope('train') as scope:
        # model_outputs is a list of batch_size * vocab tensors, i.e. the output for each batch at every time step through the sequence
        model_outputs, states = RNN(input_batch, weights, biases, num_layers, n_input, n_hidden, batch_size, sequence_length, tf.zeros((num_layers, 2, batch_size, n_hidden)))
        # softmax function expects a 2D tensor, so iterate across model_outputs and collect the cross_entropy_loss at every timestep
        # note every output (i.e. y[i]) for a sequence is the same - S->Y->P->H = 1 because SYPH was picked up from the test list, whereas O->T->H->E->R = 0 as this was not present
        softmax_losses = []
        for output in model_outputs:
            actual = tf.slice(output_batch, [0,0,0], [-1, 2,-1])
            step_loss = tf.nn.softmax_cross_entropy_with_logits(output, tf.squeeze(actual, [2]))
            softmax_losses.append(step_loss)
        softmax_losses = tf.convert_to_tensor(softmax_losses)
        # optimize the average loss across every timestep in the batch
        total_batch_and_sequence_loss = tf.reduce_mean(softmax_losses)
        # Define loss and optimizer    
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(total_batch_and_sequence_loss)
        
    # Initializing the variables
    init = tf.initialize_all_variables()
    
    saver = tf.train.Saver(tf.all_variables())
    summary_op = tf.merge_all_summaries()
    
    print("Launching graph...")
   
    # Launch the graph
    with tf.Session() as sess:    
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        sess.run(init)
                
        # Keep training until reach max iterations
        step = 1
        while step < training_iters:
            sys.stdout.write((str(step) + ", "))
            sys.stdout.flush()
                       
            # Calculate batch loss & run optimization op (backprop) 
                            
            _, loss = sess.run([optimizer,total_batch_and_sequence_loss])
            
            if step % save_step == 0 or (step + 1) * batch_size == training_iters:
                checkpoint_path = os.path.join("/tmp/healthhacktrain", 'model.ckpt')
                saver.save(sess, checkpoint_path, global_step=step)
                summary_writer = tf.train.SummaryWriter("/tmp/healthhacktrain", sess.graph)
                summary_str = sess.run(summary_op)
                summary_writer.add_summary(summary_str, step)
            
            if step % display_step == 0:

                print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
                     "{:.6f}".format(loss)) 
                
            step += 1
        print("Optimization Finished!")
        coord.request_stop()
        coord.join(threads)
