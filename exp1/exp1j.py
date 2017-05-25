import numpy as np
import tensorflow as tf
import h5py
from sklearn.preprocessing import OneHotEncoder
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time

startTime = time.time()

print('==> Experiment 1j')

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
	numEpochs = 500
	print_freq = 5

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
		
		# Print accuracy
		if (epoch + 1) % print_freq == 0:
			train_accuracy = accuracy.eval(feed_dict={x:X_train, y_: y_train})
			test_accuracy = accuracy.eval(feed_dict={x: X_test, y_: y_test})
			train_cost = cross_entropy.eval(feed_dict={x:X_train, y_: y_train})
			test_cost = cross_entropy.eval(feed_dict={x: X_test, y_: y_test})
			print("epoch: %d, time: %g, t acc, v acc, t cost, v cost: %g, %g, %g, %g"%(epoch+1, epochEnd - epochStart, train_accuracy, test_accuracy, train_cost, test_cost))

	# Validation
	train_accuracy = accuracy.eval(feed_dict={x:X_train, y_: y_train})
	test_accuracy = accuracy.eval(feed_dict={x: X_test, y_: y_test})
	train_cost = cross_entropy.eval(feed_dict={x:X_train, y_: y_train})
	test_cost = cross_entropy.eval(feed_dict={x:X_test, y_: y_test})
	print("test accuracy %g"%(test_accuracy))
	return [train_accuracy, test_accuracy, train_cost, test_cost]


''' 
our main
'''

print("==> Starting Downsampling Tests for exp1c")
# set the rates we want to test at
files = ['bigk.r.i.t._smallDataset_71_7.mat', 'chromeo_smallDataset_44_7.mat', 'deathcabforcutie_smallDataset_87_7.mat', 'foofighters_smallDataset_87_7.mat', 'kanyewest_smallDataset_92_7.mat', 'maroon5_smallDataset_66_7.mat', 'onedirection_smallDataset_60_7.mat', 'taylorswift_smallDataset_71_7.mat', 't.i_smallDataset_154_7.mat', 'tompetty_smallDataset_193_7.mat']
numSongs = [71, 44, 87, 87, 92, 66, 60, 71, 154, 193] # track the number of songs for each file

trainingAccuracies = []
testAccuracies = []
trainingCosts = []
testCosts = []

for curFileName in files:
	print("==> Test with Filename %s"%(curFileName))
	startOfLoop = time.time()

	[X_train, y_train, X_test, y_test] = loadData(curFileName)
	# run with this set of data
	[trainingAccuracy, testAccuracy, trainingCost, testCost] = runNeuralNet(121, 100, X_train, y_train, X_test, y_test)
	# track the final accuracies
	trainingAccuracies += [trainingAccuracy]
	testAccuracies += [testAccuracy]
	trainingCosts += [trainingCost]
	testCosts += [testCost]

	# time how long this run took
	endOfLoop = time.time()
	print("Test with file %s took: %g"%(curFileName, endOfLoop - startOfLoop))

endTime = time.time()
print("Whole experiment Took: %g"%(endTime - startTime))

'''
Printing results
'''
print("--------------------------")
print("Summary Of Results")
print("--------------------------")
print("Filenames: %s"%str(files))
print("Training Accuracies: %s"%str(trainingAccuracies))
print("Test Accuracies: %s"%str(testAccuracies))
print("Training Costs: %s"%str(trainingCosts))
print("Test Costs: %s"%str(testCosts))

'''
Plotting results
'''

trainingError = map(lambda x: 1.0 - x, trainingAccuracies)
validationError = map(lambda x: 1.0 - x, testAccuracies)

matplotlib.rcParams.update({'font.size': 8})

fig = plt.figure()
accPlot = fig.add_subplot(211)

accPlot.plot(numSongs, trainingAccuracies, label="Training accuracy", marker="o", ls="None")
accPlot.plot(numSongs, testAccuracies, label="Validation accuracy", marker="o", ls="None")
accPlot.set_xlabel("Number of songs")
accPlot.set_ylabel("Accuracy")
accPlot.legend(loc="upper left", frameon=False)
accPlot.set_title("Accuracy vs. Number of Songs")

errPlot = fig.add_subplot(212)
errPlot.plot(numSongs, trainingError, label="Training", marker="o", ls="None")
errPlot.plot(numSongs, validationError, label="Validation", marker="o", ls="None")
errPlot.set_xlabel("Number of songs")
errPlot.set_ylabel("One-hot error")
errPlot.legend(loc="upper left", frameon=False)
errPlot.set_title("Error vs. Number of Songs")

fig.tight_layout()
fig.savefig('exp1c_AcurracyAndError.png')

'''
--------------------------
Summary Of Results
--------------------------

'''


