%% use the data with 121 features
addpath('./exp2a_helpers');
load('../taylorswift_out/data_pca.mat');
X_train = trainingFeatures';
y_train = trainingLabels';
disp(['-- Number of training samples ', int2str(size(X_train, 1))]);

%% perform PCA on horizontal and vertical features
disp(['==> PCA on frequency...']);
[~, S_freq] = PCA(X_train);
k_freq = variance_analysis(diag(S_freq) .^ 2, 0.99);
disp(['Number of desired components for frequency (column) vectors is ', int2str(k_freq)]);

mult_factor = 16;
disp(['PCA on temporal...']);
X_train_sub = X_train(1: mult_factor, :);
for col = 1 : size(X_train_sub, 2)
	row_start = randi(size(X_train, 1) - mult_factor + 1);
	X_train_sub(:, col) = X_train(row_start : row_start + mult_factor - 1, col);
end
[~, S_temp] = PCA(X_train_sub');

k_temp = variance_analysis(diag(S_temp) .^ 2, 0.99);
disp(['Number of desired components for row (temporal) vectors is ', int2str(k_temp)]);

freq_fig = figure;
var_freq = diag(S_freq) .^ 2;
var_freq = var_freq / sum(var_freq);
stem(var_freq(1 : 20));
axis([1 20 0 1.1 * var_freq(2)]);
title('Column PCA: Relative Variance of Top 20 Eigenvalue');
saveas(freq_fig, 'col_pca.png');
temp_fig = figure;
var_temp = diag(S_temp) .^ 2;
var_temp = var_temp / sum(var_temp);
stem(var_temp(1 : 10));
axis([1 10 0 1.1 * var_temp(2)]);
title('Row PCA: Relative Variance of Top 10 Eigenvalue');
saveas(temp_fig, 'row_pca.png');