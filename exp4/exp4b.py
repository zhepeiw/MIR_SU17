import numpy as np
import tensorflow as tf
import h5py
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

# Functions for initializing neural nets parameters
def init_weight_variable(shape):
	initial = tf.truncated_normal(shape, stddev=0.1, dtype=tf.float32)
	return tf.Variable(initial)

def init_bias_variable(shape):
	initial = tf.constant(0.1, shape=shape, dtype=tf.float32)
	return tf.Variable(initial)

# wrapper function for training
def train_wrapper(X_train, y_train, step_fn, error_fn, \
	num_epochs=10, print_freq=1, batch_size=1000):
	num_training_vec = X_train.shape[0]
	train_err_list = []
	# benchmark
	t_start = time.time()
	for epoch in range(num_epochs):
		for i in range(0, num_training_vec, batch_size):
			batch_end_point = min(i + batch_size, num_training_vec)
			train_batch_data = X_train[i : batch_end_point]
			train_batch_label = y_train[i : batch_end_point]
			step_fn.run(feed_dict={x: train_batch_data, y_: train_batch_label})
		if (epoch + 1) % print_freq == 0:
			train_err = error_fn.eval(feed_dict={x: X_train, y_: y_train})
			train_err_list.append(train_err)     
			print("-- epoch: %d, training error %g"%(epoch + 1, train_err))

	t_end = time.time()
	print('--Time elapsed for training: {t:.2f} \
			seconds'.format(t = t_end - t_start))


print('==> Experiment 4b')
filepath = '/pylon2/ci560sp/haunter/exp2_d15_1s_2.mat'
print('==> Loading data from {}...'.format(filepath))
# benchmark
t_start = time.time()

# reading data
f = h5py.File(filepath)
X_train = np.array(f.get('trainingFeatures'))
y_train = np.array(f.get('trainingLabels'))
X_val = np.array(f.get('validationFeatures'))
y_val = np.array(f.get('validationLabels'))

t_end = time.time()
print('--Time elapsed for loading data: {t:.2f} \
		seconds'.format(t = t_end - t_start))
del f

print('-- Training portion is: {}'.format(training_portion))
print('-- Number of training samples: {}'.format(X_train.shape[0]))
print('-- Number of validation samples: {}'.format(X_val.shape[0]))

# Neural-network model set-up
num_training_vec, total_features = X_train.shape
num_freq = 169
num_frames = int(total_features / num_freq)
num_classes = int(max(y_train.max(), y_val.max()) + 1)
ae1_size, ae2_size = 800, 500

batch_size = 1000
num_epochs = 10
print_freq = 1

# Transform labels into on-hot encoding form
y_train_OHEnc = tf.one_hot(y_train.copy(), num_classes)
y_val_OHEnc = tf.one_hot(y_val.copy(), num_classes)

# Set-up input and output label
x = tf.placeholder(tf.float32, [None, total_features])
h1 = tf.placeholder(tf.float32, [None, total_features]) # decoder output for layer 1
a1 = tf.placeholder(tf.float32, [None, ae1_size]) # autoencoder output for layer 1
h2 = tf.placeholder(tf.float32, [None, ae1_size]) # decoder output for layer 2
a2 = tf.placeholder(tf.float32, [None, ae2_size])
y_ = tf.placeholder(tf.float32, [None, num_classes])

# first autoencoder: x -> a1 -> x
W_ae1 = init_weight_variable([total_features, ae1_size])
b_ae1 = init_bias_variable([ae1_size])
a1 = tf.nn.relu(tf.matmul(x, W_ae1) + b_ae1)
W_ad1 = init_bias_variable([ae1_size, total_features])
b_ad1 = init_bias_variable([total_features])
h1 = tf.nn.relu(tf.matmul(a1, W_ad1 + b_ad1))
# change this!!
error_ae1 = tf.reduce_mean(
		tf.nn.softmax_cross_entropy_with_logits(labels=x, logits=h1))
train_step1 = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(error_ae1)

# second autoencoder: a1 -> a2 -> a1
W_ae2 = init_weight_variable([ae1_size, ae2_size])
b_ae2 = init_bias_variable([ae2_size])
a2 = tf.nn.relu(tf.matmul(a1, W_ae2) + b_ae2)
W_ad2 = init_bias_variable([ae2_size, ae1_size])
b_ad2 = init_bias_variable([ae1_size])
h2 = tf.nn.relu(tf.matmul(a2, W_ad2 + b_ad2))
# change this!!
error_ae2 = tf.reduce_mean(
		tf.nn.softmax_cross_entropy_with_logits(labels=a1, logits=h2))
train_step2 = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(error_ae2)

# softmax layer: a2 -> y_sm
W_sm = init_weight_variable([ae2_size, num_classes])
b_sm = init_bias_variable([num_classes])
y_sm = tf.matmul(a2, W_sm) + b_sm
# evaluations
cross_entropy = tf.reduce_mean(
		tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y_sm))

train_step = tf.train.AdamOptimizer(learning_rate=1e-4).minimize(cross_entropy)
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# session
sess = tf.InteractiveSession()
sess.run(tf.global_variables_initializer())

y_train = sess.run(y_train_OHEnc)[:, 0, :]
y_val = sess.run(y_val_OHEnc)[:, 0, :]

train_acc_list = []
val_acc_list = []
train_err_list = []
val_err_list = []

# benchmark
t_start = time.time()
for epoch in range(num_epochs):
	for i in range(0, num_training_vec, batch_size):
		batch_end_point = min(i + batch_size, num_training_vec)
		train_batch_data = X_train[i : batch_end_point]
		train_batch_label = y_train[i : batch_end_point]
		train_step.run(feed_dict={x: train_batch_data, y_: train_batch_label})
	if (epoch + 1) % print_freq == 0:
		train_acc = accuracy.eval(feed_dict={x:X_train, y_: y_train})
		train_acc_list.append(train_acc)
		val_acc = accuracy.eval(feed_dict={x: X_val, y_: y_val})
		val_acc_list.append(val_acc)
		train_err = cross_entropy.eval(feed_dict={x: X_train, y_: y_train})
		train_err_list.append(train_err)
		val_err = cross_entropy.eval(feed_dict={x: X_val, y_: y_val})
		val_err_list.append(val_err)      
		print("-- epoch: %d, training error %g"%(epoch + 1, train_err))

t_end = time.time()
print('--Time elapsed for training: {t:.2f} \
		seconds'.format(t = t_end - t_start))

# Reports
print('-- Training accuracy: {:.4f}'.format(train_acc_list[-1]))
print('-- Validation accuracy: {:.4f}'.format(val_acc_list[-1]))
print('-- Training error: {:.4E}'.format(train_err_list[-1]))
print('-- Validation error: {:.4E}'.format(val_err_list[-1]))

print('==> Generating error plot...')
x_list = range(0, print_freq * len(train_acc_list), print_freq)
train_err_plot, = plt.plot(x_list, train_err_list, 'b.')
val_err_plot, = plt.plot(x_list, val_err_list, '.', color='gold')
plt.xlabel('Number of epochs')
plt.ylabel('Cross-Entropy Error')
plt.title('Fraction {}: Error vs Number of Epochs with Filter Size of {} x {}'.format(training_portion, filter_row, filter_col))
plt.legend((train_err_plot, val_err_plot), ('training', 'validation'), loc='best')
plt.savefig('exp2k_f{}_{}x{}.png'.format(training_portion, filter_row, filter_col), format='png')
plt.close()

print('==> Done.')
