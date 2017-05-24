import numpy as np
import tensorflow as tf
import h5py
from sklearn.preprocessing import OneHotEncoder
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

startTime = time.time()

print('==> Experiment 1g')

def loadData(filepath):

	print('==> Loading data from {}'.format(filepath))
	f = h5py.File(filepath)
	X_train = np.array(f.get('trainingFeatures'))
	y_train = np.array(f.get('trainingLabels'))
	X_test = np.array(f.get('validationFeatures'))
	y_test = np.array(f.get('validationLabels'))
	del f
	print('==> Data sizes:',X_train.shape, y_train.shape, X_test.shape, y_test.shape)

	# Transform labels into on-hot encoding form
	enc = OneHotEncoder()
	y_train = enc.fit_transform(y_train.copy()).astype(int).toarray()
	y_test = enc.fit_transform(y_test.copy()).astype(int).toarray()

	return [X_train, y_train, X_test, y_test]

# Neural-network model set-up
# Functions for initializing neural nets parameters
def init_weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1, dtype=tf.float64)
  return tf.Variable(initial)

def init_bias_variable(shape):
  initial = tf.constant(0.1, shape=shape, dtype=tf.float64)
  return tf.Variable(initial)


def runNeuralNet(num_features, hidden_layer_size, X_train, y_train, X_test, y_test):

	'''
		NN config parameters
	'''

	num_classes = y_test.shape[1]
	
	print('==> Creating Neural net with %d features, %d hidden units, and %d classes'%(num_features, hidden_layer_size, num_classes))

	# Set-up NN layers
	x = tf.placeholder(tf.float64, [None, num_features])
	W1 = init_weight_variable([num_features, hidden_layer_size])
	b1 = init_bias_variable([hidden_layer_size])

	# Hidden layer activation function: ReLU
	h1 = tf.nn.relu(tf.matmul(x, W1) + b1)

	W2 = init_weight_variable([hidden_layer_size, num_classes])
	b2 = init_bias_variable([num_classes])

	# Softmax layer (Output), dtype = float64
	y = tf.matmul(h1, W2) + b2

	# NN desired value (labels)
	y_ = tf.placeholder(tf.float64, [None, num_classes])

	# Loss function
	cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
	train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

	sess = tf.InteractiveSession()

	correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
	accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float64))
	sess.run(tf.global_variables_initializer())


	'''
		Training config
	'''
	numTrainingVec = len(X_train)
	batchSize = 1000
	numEpochs = 10
	print_freq = 5

	train_accuracies = []
	test_accuracies = []
	train_costs = []
	test_costs = []

	print('Training with %d samples, a batch size of %d, for %d epochs'%(numTrainingVec, batchSize, numEpochs))


	for epoch in range(numEpochs):

		epochStart = time.time()
		for i in range(0,numTrainingVec,batchSize):

			# Batch Data
			batchEndPoint = min(i+batchSize, numTrainingVec)
			trainBatchData = X_train[i:batchEndPoint]
			trainBatchLabel = y_train[i:batchEndPoint]

			train_step.run(feed_dict={x: trainBatchData, y_: trainBatchLabel})

		epochEnd = time.time()

		# calculate the accuracies and costs at this epoch
		train_accuracy = accuracy.eval(feed_dict={x:X_train, y_: y_train})
		test_accuracy = accuracy.eval(feed_dict={x: X_test, y_: y_test})
		train_cost = cross_entropy.eval(feed_dict={x:X_train, y_: y_train})
		test_cost = cross_entropy.eval(feed_dict={x: X_test, y_: y_test})
		# update the lists
		train_accuracies += [train_accuracy]
		test_accuracies += [test_accuracy]
		train_costs += [train_cost]
		test_costs += [test_cost]
		# Print accuracy

		if (epoch + 1) % print_freq == 0:

			print("epoch: %d, time: %g, t acc, v acc, t cost, v cost: %g, %g, %g, %g"%(epoch+1, epochEnd - epochStart, train_accuracy, test_accuracy, train_cost, test_cost))

	# Validation
	train_accuracy = accuracy.eval(feed_dict={x:X_train, y_: y_train})
	test_accuracy = accuracy.eval(feed_dict={x: X_test, y_: y_test})
	train_cost = cross_entropy.eval(feed_dict={x:X_train, y_: y_train})
	test_cost = cross_entropy.eval(feed_dict={x:X_test, y_: y_test})
	print("test accuracy %g"%(test_accuracy))
	return [train_accuracies, test_accuracies, train_costs, test_costs]


''' 
our main
'''
[X_train, y_train, X_test, y_test] = loadData('taylorswift_smallDataset_71_7.mat')

[train_accuracies, test_accuracies, train_costs, test_costs] = runNeuralNet(121, 100, X_train, y_train, X_test, y_test)


endTime = time.time()
print("Experiment took: %g"%(endTime - startTime))

'''
Printing results
'''
print("--------------------------")
print("Summary Of Results")
print("Training Accuracies: %s"%str(train_accuracies))
print("Testing Accuracies: %s"%str(test_accuracies))
print("--------------------------")


'''
Plotting results
'''
numEpochs = len(train_accuracies)
epochNumbers = range(numEpochs)
matplotlib.rcParams.update({'font.size': 8})

fig = plt.figure()
accPlot = fig.add_subplot(211)

accPlot.plot(epochNumbers, train_accuracies, label="Training", marker="o", markersize="3", ls="None")
accPlot.plot(epochNumbers, test_accuracies, label="Validation", marker="o", markersize="3", ls="None")
accPlot.set_xlabel("Epoch Number")
accPlot.set_ylabel("Accuracy")
accPlot.legend(loc="upper left", frameon=False)
accPlot.set_title("Accuracy vs. Epoch")

errPlot = fig.add_subplot(212)
errPlot.plot(epochNumbers, train_costs, label="Training", marker="o", markersize="3", ls="None")
errPlot.plot(epochNumbers, test_costs, label="Validation", marker="o", markersize="3", ls="None")
errPlot.set_xlabel("Epoch Number")
errPlot.set_ylabel("Cross-Entropy Error")
errPlot.legend(loc="lower left", frameon=False)
errPlot.set_title("Cross-Entropy Error vs. Epoch Number")

fig.tight_layout()
fig.savefig('exp1g_ErrorAndEpoch.png')



'''
Summary Of Results
Training Accuracies: [0.027586206896551724, 0.041379310344827586, 0.055172413793103448, 0.055172413793103448, 0.055172413793103448, 0.048275862068965517, 0.048275862068965517, 0.062068965517241378, 0.062068965517241378, 0.068965517241379309, 0.07586206896551724, 0.068965517241379309, 0.082758620689655171, 0.082758620689655171, 0.082758620689655171, 0.089655172413793102, 0.10344827586206896, 0.11724137931034483, 0.11724137931034483, 0.12413793103448276, 0.12413793103448276, 0.12413793103448276, 0.12413793103448276, 0.12413793103448276, 0.1310344827586207, 0.14482758620689656, 0.14482758620689656, 0.14482758620689656, 0.14482758620689656, 0.14482758620689656, 0.13793103448275862, 0.14482758620689656, 0.15862068965517243, 0.15172413793103448, 0.15172413793103448, 0.15862068965517243, 0.15862068965517243, 0.16551724137931034, 0.17241379310344829, 0.17241379310344829, 0.17241379310344829, 0.1793103448275862, 0.17241379310344829, 0.1793103448275862, 0.17241379310344829, 0.18620689655172415, 0.19310344827586207, 0.20689655172413793, 0.20689655172413793, 0.20689655172413793, 0.21379310344827587, 0.21379310344827587, 0.21379310344827587, 0.20689655172413793, 0.20689655172413793, 0.20689655172413793, 0.20689655172413793, 0.20689655172413793, 0.20689655172413793, 0.20689655172413793, 0.21379310344827587, 0.21379310344827587, 0.21379310344827587, 0.21379310344827587, 0.22068965517241379, 0.22068965517241379, 0.22758620689655173, 0.22758620689655173, 0.23448275862068965, 0.23448275862068965, 0.23448275862068965, 0.23448275862068965, 0.23448275862068965, 0.23448275862068965, 0.22758620689655173, 0.22758620689655173, 0.22758620689655173, 0.22758620689655173, 0.22758620689655173, 0.22758620689655173, 0.22758620689655173, 0.23448275862068965, 0.23448275862068965, 0.22758620689655173, 0.23448275862068965, 0.23448275862068965, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.2413793103448276, 0.24827586206896551, 0.24827586206896551, 0.24827586206896551, 0.25517241379310346, 0.25517241379310346, 0.2620689655172414, 0.26896551724137929, 0.26896551724137929, 0.26896551724137929, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.27586206896551724, 0.28275862068965518, 0.28275862068965518, 0.28275862068965518, 0.28275862068965518, 0.28965517241379313, 0.28965517241379313, 0.28965517241379313, 0.28965517241379313, 0.28965517241379313, 0.28965517241379313, 0.28965517241379313, 0.28965517241379313, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.30344827586206896, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.29655172413793102, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.30344827586206896, 0.31724137931034485, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.32413793103448274, 0.33103448275862069, 0.33103448275862069, 0.33793103448275863, 0.34482758620689657, 0.34482758620689657, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.34482758620689657, 0.34482758620689657, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35172413793103446, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.35862068965517241, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.3724137931034483, 0.3724137931034483, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.36551724137931035, 0.3724137931034483, 0.3724137931034483, 0.3724137931034483, 0.3724137931034483, 0.3724137931034483, 0.3724137931034483, 0.3724137931034483, 0.37931034482758619, 0.38620689655172413, 0.38620689655172413, 0.38620689655172413, 0.38620689655172413, 0.39310344827586208, 0.39310344827586208, 0.39310344827586208, 0.39310344827586208, 0.39310344827586208, 0.39310344827586208, 0.39310344827586208, 0.39310344827586208, 0.40000000000000002, 0.40000000000000002, 0.40000000000000002, 0.40000000000000002, 0.40000000000000002, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.40689655172413791, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.41379310344827586, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.4206896551724138, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.42758620689655175, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.43448275862068964, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758, 0.44137931034482758]
Testing Accuracies: [0.030239502895752897, 0.037725225225225228, 0.051168355855855857, 0.05255590411840412, 0.056979971042471045, 0.060237693050193053, 0.066778273809523808, 0.076953627734877739, 0.086219031531531529, 0.092352397039897047, 0.096640725546975545, 0.10025036196911197, 0.10364382239382239, 0.10651443854568854, 0.1093850546975547, 0.11255228442728443, 0.11541284588159588, 0.11812258687258688, 0.12128981660231661, 0.12454251126126126, 0.12787564350064351, 0.13084680662805662, 0.13413972007722008, 0.13747285231660231, 0.14085625804375804, 0.14381736647361648, 0.14745213963963963, 0.15052384974259975, 0.15370113416988418, 0.15655666827541828, 0.15937701093951093, 0.16218227155727155, 0.1647009732947233, 0.16750120656370657, 0.1699495254182754, 0.1729257158944659, 0.17532376126126126, 0.17787765444015444, 0.18058236808236808, 0.18325189028314029, 0.18570523648648649, 0.1884602236164736, 0.19110963642213641, 0.19351773648648649, 0.19599119208494209, 0.19842945624195624, 0.20074203667953669, 0.20302948037323038, 0.205402388996139, 0.20743846525096524, 0.2094544321106821, 0.21156591859716858, 0.21363215894465895, 0.21592462998713, 0.21795065154440155, 0.22012246621621623, 0.22228925353925355, 0.22401866151866151, 0.22583856177606176, 0.22800534909909909, 0.23001126126126126, 0.23168034105534105, 0.23337958494208494, 0.23507882882882883, 0.23682331885456886, 0.23844715250965251, 0.24023688867438867, 0.24201657014157013, 0.24396718146718147, 0.24559101512226511, 0.24716960263835264, 0.24848676801801803, 0.25, 0.25141268500643499, 0.25288067084942084, 0.2542883285070785, 0.25581161518661516, 0.25759632400257398, 0.25907436454311455, 0.26059262387387389, 0.26173383204633205, 0.26316662644787647, 0.26441843629343631, 0.26571046492921491, 0.26691702863577865, 0.26826938545688545, 0.26954130469755472, 0.27055180180180183, 0.2716025176962677, 0.27285432754182753, 0.27396034427284427, 0.27494570463320461, 0.27628297940797941, 0.27748451576576577, 0.27854025900900903, 0.27957589285714285, 0.28052606177606176, 0.28153153153153154, 0.28253197393822393, 0.28344695141570142, 0.28457307754182753, 0.28552324646074645, 0.28638795045045046, 0.28742358429858428, 0.28851954633204635, 0.28958031692406694, 0.29047518500643499, 0.29118906853281851, 0.29222470238095238, 0.29322514478764478, 0.29423061454311455, 0.29514056467181465, 0.29609073359073357, 0.29703084781209782, 0.29778495012870015, 0.29860943532818535, 0.29931326415701415, 0.30010255791505791, 0.3009572072072072, 0.30173141891891891, 0.30251568532818535, 0.30329995173745172, 0.30386804214929214, 0.30464728120978118, 0.30536619208494209, 0.3061404037966538, 0.30674368564993565, 0.30743745978120979, 0.3080960424710425, 0.30884511743886744, 0.30947856338481339, 0.31007179054054052, 0.31074545527670527, 0.31146436615186618, 0.31215311293436293, 0.31283683236808235, 0.31338481338481339, 0.31400317728442728, 0.31460645913770913, 0.31513433075933078, 0.31570242117117114, 0.31639619530244528, 0.31704472329472327, 0.31782898970398971, 0.3185076817889318, 0.31929697554697556, 0.3200209137709138, 0.32073479729729731, 0.32132802445302444, 0.32197655244530243, 0.32261502574002576, 0.32317808880308879, 0.32390202702702703, 0.32450530888030887, 0.32519908301158301, 0.32564148970398971, 0.3262900176962677, 0.32683297136422135, 0.32741614382239381, 0.32802948037323038, 0.32873833655083656, 0.32945222007722008, 0.33002533783783783, 0.33060851029601029, 0.33106599903474904, 0.33159387065637064, 0.33224239864864863, 0.33295628217503215, 0.33367016570141572, 0.33409246299871298, 0.33463541666666669, 0.33527891731016729, 0.33591236325611323, 0.33656089124839123, 0.33711389961389959, 0.33768199002574001, 0.33825510778635781, 0.33866735038610041, 0.33913992117117114, 0.33973817567567566, 0.34030123873873874, 0.34082408301158301, 0.34139217342342343, 0.34199042792792794, 0.34241775257400259, 0.34290037805662804, 0.34337797619047616, 0.343865629021879, 0.34429295366795365, 0.3448509893822394, 0.34509732947232946, 0.34568552927927926, 0.34609274453024452, 0.34663067084942084, 0.34718870656370654, 0.34765625, 0.34820925836550837, 0.34862150096525096, 0.34901866151866151, 0.34951636904761907, 0.3498733108108108, 0.3502855534105534, 0.35082347972972971, 0.35114523005148007, 0.35165801962676962, 0.35211048101673104, 0.35257299710424711, 0.35299529440154442, 0.35334720881595882, 0.35363879504504503, 0.35398065476190477, 0.35430743243243246, 0.35462918275418276, 0.35495596042471045, 0.35530787483912485, 0.35573017213642216, 0.35609716859716861, 0.35651443854568854, 0.35684121621621623, 0.35722832207207206, 0.35761040057915056, 0.35793215090090091, 0.35835947554697556, 0.35872647200772201, 0.35907335907335908, 0.35954090250965248, 0.35989784427284427, 0.36024975868725867, 0.36061172779922779, 0.36101391570141572, 0.36148648648648651, 0.36182331885456886, 0.3621500965250965, 0.36244168275418276, 0.36277851512226511, 0.36311032014157013, 0.36350245334620335, 0.36375382078507079, 0.36405546171171171, 0.36425655566280568, 0.36452803249678251, 0.36488497425997424, 0.36514136904761907, 0.36545809202059204, 0.36577481499356501, 0.36606137387387389, 0.36633285070785071, 0.36671995656370654, 0.36698640604890603, 0.36726291023166024, 0.36764498873873874, 0.36799187580437581, 0.36838400900900903, 0.368700731981982, 0.3690526463963964, 0.36931406853281851, 0.36954029922779924, 0.36987210424710426, 0.37020390926640928, 0.37054576898326896, 0.37076697232947231, 0.3710334218146718, 0.3712998712998713, 0.37157134813384812, 0.37178249678249681, 0.37213441119691121, 0.37246118886743884, 0.37259189993564995, 0.37284829472329473, 0.37312982625482627, 0.37332589285714285, 0.37350185006435005, 0.37376829954954954, 0.37403474903474904, 0.37425595238095238, 0.37452240186615188, 0.37474360521235522, 0.37491453507078509, 0.37524634009009011, 0.37543235199485198, 0.37564852799227799, 0.37580940315315314, 0.37608590733590735, 0.37630208333333331, 0.37649814993564995, 0.37671432593307591, 0.37706624034749037, 0.3772170608108108, 0.37743323680823682, 0.37753378378378377, 0.37780023326898327, 0.37804154601029599, 0.37827783140283139, 0.37847389800514802, 0.37869007400257398, 0.37894144144144143, 0.37918778153153154, 0.3792883285070785, 0.3794944498069498, 0.37965029761904762, 0.37980614543114544, 0.37996199324324326, 0.38022341537966536, 0.38036920849420852, 0.38058538449163448, 0.38078145109395112, 0.38084177927927926, 0.3810629826254826, 0.38119872104247104, 0.38144003378378377, 0.38156069015444016, 0.38171653796653798, 0.38193774131274133, 0.38221927284427282, 0.38233992921492921, 0.38250080437580436, 0.38273206241956242, 0.38286780083655081, 0.38302867599742602, 0.38326998873873874, 0.38344091859716861, 0.38363195785070786, 0.38392857142857145, 0.38410955598455598, 0.38430562258687256, 0.38451677123552125, 0.38465250965250963, 0.38484857625482627, 0.38501447876447875, 0.38519546332046334, 0.38540158462033464, 0.38554235038610041, 0.38567808880308879, 0.38584399131274133, 0.38605513996138996, 0.38623109716859716, 0.38638191763191765, 0.3865729568854569, 0.38678913288288286, 0.38699022683397682, 0.38720640283140284, 0.38738738738738737, 0.38748793436293438, 0.38762870012870015, 0.38776946589446587, 0.38800575128700127, 0.38819176319176318, 0.38834258365508367, 0.38851351351351349, 0.38869449806949807, 0.38885034588159589, 0.38897100225225223, 0.38912182271557272, 0.38926258848133849, 0.38946368243243246, 0.38960444819819817, 0.38978543275418276, 0.38996641731016729, 0.39007701898326896, 0.39023286679536678, 0.39044401544401547, 0.39052445302445304, 0.39069538288288286, 0.39085625804375806, 0.39105735199485198, 0.39117800836550837, 0.39133385617760619, 0.39145953989703991, 0.39157014157014158, 0.39161538770913773, 0.39173101673101673, 0.39189189189189189, 0.39206282175032175, 0.39223877895752896, 0.3923141891891892, 0.39246500965250963, 0.39259572072072074, 0.39268118564993565, 0.39276665057915056, 0.39294260778635781, 0.39308337355212353, 0.39318392052767054, 0.39333976833976836, 0.39354588963963966, 0.39361124517374518, 0.39372184684684686, 0.39381736647361648, 0.3939430501930502, 0.39407376126126126, 0.39416425353925355, 0.3943251287001287, 0.3944709218146718, 0.39452119530244528, 0.39456644144144143, 0.39464185167310167, 0.39475245334620335, 0.39489824646074645, 0.39500382078507079, 0.39513453185328185, 0.39527027027027029, 0.39539092664092662, 0.39540600868725867, 0.39546633687258687, 0.39556185649935649, 0.39558699324324326, 0.39568754021879021, 0.39579814189189189, 0.39583333333333331, 0.39601934523809523, 0.39624557593307591, 0.39640645109395112, 0.39652208011583012, 0.39665279118404118, 0.39681869369369371, 0.3969544321106821, 0.39709017052767054, 0.39715552606177607, 0.39720579954954954, 0.3973063465250965, 0.39746722168597171, 0.39747224903474904, 0.39762306949806953, 0.39766831563706562, 0.39781913610038611, 0.39799006595881598, 0.3980554214929215, 0.3981459137709138, 0.39827662483912485, 0.39838219916344919, 0.39848777348777348, 0.3986134572072072, 0.3987592503217503, 0.39877433236808235, 0.39886482464607464, 0.39894526222651222, 0.39913127413127414, 0.39917652027027029, 0.39928712194337196, 0.39935247747747749, 0.39945805180180183, 0.39952340733590735, 0.39960384491634493, 0.39968428249678251, 0.39974963803088803, 0.39977980212355213, 0.39985018500643499, 0.39991051319176318, 0.39995575933075933, 0.40004625160875162, 0.40017696267696268, 0.40029761904761907, 0.40041324806949807, 0.40050374034749037, 0.40051379504504503, 0.40062942406692409, 0.40067467020592018, 0.40076013513513514, 0.400830518018018, 0.40096625643500644, 0.4010366393178893, 0.40112210424710426, 0.40125281531531531, 0.40130308880308879, 0.40139358108108109, 0.40142877252252251, 0.40153434684684686, 0.40163992117117114, 0.4017857142857143, 0.40183096042471045, 0.40190134330759331, 0.4019616714929215, 0.40207227316602318, 0.40224823037323038, 0.4022834218146718, 0.40236385939510938, 0.40239905083655081, 0.40249457046332049, 0.40255992599742602, 0.40261019948519949, 0.40268058236808235, 0.40271074646074645, 0.40280626608751607, 0.40281129343629346, 0.40296211389961389, 0.40306768822393824, 0.40315818050193047, 0.40322856338481339, 0.40330900096525096, 0.40338441119691121, 0.40346987612612611, 0.40358550514800517, 0.40372124356499356, 0.40370113416988418, 0.40375140765765766, 0.40379162644787647, 0.40391731016731014, 0.40399774774774777, 0.40410332207207206, 0.40416867760617758, 0.40424911518661516, 0.4043245254182754, 0.40436474420849422, 0.40446026383526384, 0.40448540057915056, 0.40454572876447875, 0.40457086550836552, 0.40467643983268986, 0.40480715090090091, 0.40481720559845558, 0.40485239703989706, 0.40495294401544402, 0.40508868243243246, 0.40514398326898327, 0.4051490106177606, 0.40519425675675674, 0.40524955759330761, 0.40531491312741313, 0.40535513191763189, 0.40538529601029599, 0.40542551480051481, 0.40548081563706562, 0.40555119851994853, 0.40563163610038611, 0.40565677284427282, 0.40574726512226511, 0.40586289414414417, 0.40598857786357784, 0.40602879665379665, 0.4060740427927928, 0.40611928893178895, 0.40620475386100385, 0.40623491795366795, 0.40630027348777348, 0.40633546492921491, 0.40638573841698844, 0.40644103925353925, 0.40653153153153154, 0.4066019144144144, 0.40668737934362936, 0.40676781692406694, 0.40680300836550837, 0.40693371943371942, 0.40701918436293438, 0.40710967664092662, 0.40716497747747749, 0.40721525096525096, 0.40725044240669239, 0.4073509893822394, 0.40739623552123549, 0.40748672779922779, 0.40762246621621623, 0.40766268500643499, 0.4077330678893179, 0.40783864221364219, 0.40786377895752896, 0.40791405244530243, 0.40803973616473616, 0.40815033783783783, 0.40821569337194336, 0.4082609395109395, 0.40840170527670527, 0.40838662323037322, 0.40847208815958819, 0.40855755308880309, 0.40860279922779924, 0.40866815476190477, 0.40871842824967825, 0.40873853764478763, 0.40880892052767054, 0.40880389317889315, 0.40885416666666669, 0.40895471364221364, 0.40901001447876451, 0.40907034266409265, 0.40904017857142855, 0.40908542471042469, 0.40912564350064351, 0.40916083494208494, 0.40916586229086227, 0.40920608108108109, 0.40923624517374518, 0.40929657335907338, 0.40934684684684686, 0.40943733912483915, 0.40949263996138996, 0.40954794079794082, 0.4096283783783784, 0.40973898005148007, 0.40978422619047616, 0.40981941763191765, 0.40990488256113256, 0.40993504665379665, 0.41002051158301156, 0.41008586711711714, 0.41009089446589447, 0.41010597651222652, 0.41016127734877733, 0.41021155083655081, 0.41025176962676962, 0.41030707046332049, 0.41034728925353925, 0.41038248069498068, 0.41040761743886744, 0.41047297297297297, 0.41051821911196912, 0.41059362934362936, 0.41063887548262551, 0.41072434041184042, 0.41073942245817247, 0.41079472329472327, 0.41087516087516085, 0.41092543436293438, 0.41095057110682109, 0.41096565315315314, 0.41106620012870015, 0.41111647361647363, 0.41116674710424711, 0.41119691119691121, 0.41123210263835264, 0.41130248552123549, 0.41131254021879021, 0.41141308719433717, 0.41146838803088803, 0.41153877091377089, 0.41164434523809523, 0.41164434523809523, 0.41170970077220076, 0.41177002895752896, 0.41185046653796653, 0.41187057593307591, 0.41197615025740025, 0.4120213963963964, 0.4120515604890605, 0.41210686132561131, 0.4121671895109395, 0.41218729890604888, 0.41226773648648651, 0.41229790057915056, 0.41231800997425999, 0.41238839285714285, 0.41242861164736166, 0.4125191039253539, 0.41256435006435005, 0.41262467824967825, 0.41264981499356501, 0.41271517052767054, 0.41275036196911197, 0.41276544401544402, 0.41286599099099097, 0.41291123712998712, 0.41286599099099097, 0.41287604568854569, 0.41295145592020593, 0.41300675675675674, 0.41302183880308879, 0.41308216698841699, 0.4131223857786358, 0.41314249517374518, 0.41318271396396394, 0.41322293275418276, 0.41325309684684686, 0.41330337033462033, 0.41332347972972971, 0.41338380791505791, 0.41345921814671815, 0.41344916344916344, 0.4134743001930502, 0.41349440958815958, 0.41354971042471045, 0.41358992921492921, 0.41361506595881598, 0.41364020270270269, 0.41367539414414417, 0.41372064028314026, 0.41379605051480051, 0.4138865427927928, 0.41392676158301156, 0.41397703507078509, 0.41400719916344919, 0.41404741795366795, 0.41410774613899615, 0.41418315637065639, 0.41419321106821105, 0.41424348455598453, 0.41424851190476192, 0.41430381274131273, 0.41437419562419564, 0.41440435971685974, 0.41442446911196912, 0.41448982464607464, 0.41449485199485198, 0.41455518018018017, 0.41455518018018017, 0.41453004343629346, 0.4145602075289575, 0.41458031692406694, 0.41460042631917632, 0.41466075450450451, 0.41464567245817247, 0.41466075450450451, 0.41468589124839123, 0.41475627413127414, 0.41478643822393824, 0.41483671171171171, 0.41483671171171171, 0.41488698519948519, 0.41491212194337196, 0.41494228603603606, 0.41492720398970401, 0.41492217664092662, 0.41501266891891891, 0.41500764157014158, 0.41501769626769625, 0.41503780566280568, 0.41504283301158301, 0.41505288770913773, 0.41510316119691121, 0.41515846203346202, 0.41517354407979407, 0.41515343468468469, 0.41518862612612611, 0.41521879021879021, 0.41520370817245816, 0.41526403635778636, 0.41525900900900903, 0.41526906370656369, 0.41529922779922779, 0.4153394465894466, 0.41541485682110685, 0.41540480212355213, 0.41544502091377089, 0.41548021235521237, 0.41546010296010294, 0.4155154037966538, 0.4156058960746461, 0.41563606016731014, 0.41565114221364219, 0.41565616956241958, 0.41570141570141572, 0.41571649774774777, 0.41572655244530243, 0.41579693532818535, 0.41583212676962678, 0.41590250965250963, 0.41593770109395112, 0.41596283783783783, 0.41594272844272845, 0.41596786518661516, 0.4159578104890605, 0.41599802927927926, 0.4160734395109395, 0.41611868564993565, 0.41612874034749037, 0.41617901383526384, 0.41623431467181465, 0.41618906853281851, 0.41616895913770913, 0.41623934202059204, 0.41628458815958819, 0.41629967020592018, 0.41629967020592018, 0.4163097249034749, 0.416339888996139, 0.41637508043758042, 0.41636502574002576, 0.41641529922779924, 0.41641027187902185, 0.41643540862290862, 0.41646054536679539, 0.41647562741312744, 0.41652590090090091, 0.41657114703989706, 0.41660633848133849, 0.41668174871299873, 0.41670688545688545, 0.41673704954954954, 0.41674710424710426, 0.41676218629343631, 0.41677726833976836, 0.41680240508365507, 0.41683256917631917, 0.41687278796653798, 0.41692306145431146, 0.41693814350064351, 0.41693311615186618, 0.41696830759330761, 0.41699847168597171, 0.41704874517374518, 0.41706382722007723, 0.41709399131274133, 0.41715431949806953, 0.41719453828828829, 0.41722972972972971, 0.41726492117117114, 0.41726994851994853, 0.41733027670527673, 0.41734535875160877, 0.4174107142857143, 0.41747606981981983, 0.41751126126126126]
'''







