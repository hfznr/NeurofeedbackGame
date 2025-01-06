import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt
import wfdb
import matplotlib.pyplot as plt
import os

import seaborn as sns

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance

class EMGFeatureExtractor:
    def __init__(self, sampling_frequency):
        self.sampling_frequency = sampling_frequency
        self.raw_data = None
        self.filtered_data = None
        self.windows = None
        self.graphs_dir = 'graphs'

    def load_data(self, data):
        self.raw_data = np.array(data)  # Convert to numpy arra
        return self.raw_data

    def filter_data(self, bandpass_filter, notch_filter):
        self.filtered_data = np.array([
            bandpass_filter(notch_filter(channel))
            for channel in self.raw_data.T
        ]).T
        print(f"Filtered data shape: {self.filtered_data.shape}")

    def create_windows(self, window_size=100, overlap=50):
        step = window_size - overlap
        num_windows = (self.filtered_data.shape[0] - window_size) // step + 1
        self.windows = np.array([
            self.filtered_data[i:i + window_size, :]
            for i in range(0, num_windows * step, step)
        ])
        print(f"Created {self.windows.shape[0]} windows of shape {self.windows.shape[1:]}")

    def plot_first_window(self,filename='feature_extraction_first_window_channel_1.png'):
        if self.windows is None:
            print("Windows not created yet!")
            return
        output_path = os.path.join(self.graphs_dir, filename)
        plt.figure(figsize=(12, 6))
        plt.plot(self.windows[0, :, 0])  # First window, first channel
        plt.title("First Window - Channel 1")
        plt.xlabel("Sample")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_path)
        
        plt.show()
        
        
    def zero_crossing(self, window, threshold=0.005):
        crossings = np.diff(np.sign(window)) != 0
        above_threshold = np.abs(window[1:]) > threshold
        return np.sum(crossings & above_threshold)

    def waveform_length(self, window):
        return np.sum(np.abs(np.diff(window)))

    def difference_absolute_std(self, window):
        return np.std(np.abs(np.diff(window)))

    # Feature: Integral Absolute Value
    def integral_absolute_value(self, window):
        return np.sum(np.abs(window))

    # Feature: Log Detector
    def log_detector(self, window):
        return np.exp(np.mean(np.log(np.abs(window) + 1e-8)))  # Add epsilon to avoid log(0)

    # Feature: Mean Absolute Value
    def mean_absolute_value(self, window):
        return np.mean(np.abs(window))

    # Feature: Root Mean Square
    def root_mean_square(self, window):
        return np.sqrt(np.mean(window ** 2))

    # Feature: Absolute Temporal Moment
    def absolute_temporal_moment(self, window):
        return np.mean(window ** 2)

    # Feature: Variance
    def variance(self, window):
        return np.var(window)

    # Feature: V-Order (example with V=3)
    def v_order(self, window, v=3):
        return np.mean(np.abs(window) ** v)

    # Feature: Mean Frequency
    def mean_frequency(self, window):
        fft = np.fft.rfft(window)
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(window), 1 / self.sampling_frequency)
        return np.sum(freqs * magnitudes) / np.sum(magnitudes)

    # Feature: Maximum Amplitude
    def maximum_amplitude(self, window):
        return np.max(np.abs(window))

    # Feature: Peak Frequency
    def peak_frequency(self, window):
        fft = np.fft.rfft(window)
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(window), 1 / self.sampling_frequency)
        return freqs[np.argmax(magnitudes)]

    # Feature: Mean Power
    def mean_power(self, window):
        return np.mean(window ** 2)

    # Feature: Total Power
    def total_power(self, window):
        return np.sum(window ** 2)

    # Feature: Variance of Central Frequency
    def variance_of_central_frequency(self, window):
        fft = np.fft.rfft(window)
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(window), 1 / self.sampling_frequency)
        mean_freq = self.mean_frequency(window)
        return np.sum(magnitudes * (freqs - mean_freq) ** 2) / np.sum(magnitudes)

    # Compute features for all windows and channels
    def extract_features(self):
        if self.windows is None:
            print("Windows not created yet!")
            return None

        num_windows, window_size, num_channels = self.windows.shape
        num_features = 16  # Total number of features implemented
        feature_matrix = np.zeros((num_windows, num_channels, num_features))

        for i in range(num_windows):
            for ch in range(num_channels):
                window = self.windows[i, :, ch]
                feature_matrix[i, ch, 0] = self.zero_crossing(window)
                feature_matrix[i, ch, 1] = self.waveform_length(window)
                feature_matrix[i, ch, 2] = self.difference_absolute_std(window)
                feature_matrix[i, ch, 3] = self.integral_absolute_value(window)
                feature_matrix[i, ch, 4] = self.log_detector(window)
                feature_matrix[i, ch, 5] = self.mean_absolute_value(window)
                feature_matrix[i, ch, 6] = self.root_mean_square(window)
                feature_matrix[i, ch, 7] = self.absolute_temporal_moment(window)
                feature_matrix[i, ch, 8] = self.variance(window)
                feature_matrix[i, ch, 9] = self.v_order(window)
                feature_matrix[i, ch, 10] = self.mean_frequency(window)
                feature_matrix[i, ch, 11] = self.maximum_amplitude(window)
                feature_matrix[i, ch, 12] = self.peak_frequency(window)
                feature_matrix[i, ch, 13] = self.mean_power(window)
                feature_matrix[i, ch, 14] = self.total_power(window)
                feature_matrix[i, ch, 15] = self.variance_of_central_frequency(window)

        print("Feature extraction complete.")
        return feature_matrix
    
    def compute_average_correlation(self, feature_matrix):
        """
        Compute the average correlation matrix across all windows.
        
        Args:
            feature_matrix: numpy array of shape (num_windows, num_channels, num_features)
        Returns:
            avg_correlation_matrix: numpy array representing the average correlation matrix
        """
        num_windows, num_channels, num_features = feature_matrix.shape
        correlation_matrices = []

        # Compute correlation for each window
        for i in range(num_windows):
            # Flatten features across channels for the current window
            flattened_features = feature_matrix[i, :, :].reshape(-1, num_features)
            df = pd.DataFrame(flattened_features, columns=[f"Feature_{j}" for j in range(num_features)])
            correlation = df.corr()
            correlation_matrices.append(correlation)

        # Average the correlation matrices
        avg_correlation_matrix = np.abs(np.mean(correlation_matrices, axis=0))
        return avg_correlation_matrix

    def plot_correlation_matrix(self, correlation_matrix, feature_names=None, filename='correlation_matrix.png'):
        """
        Plot the correlation matrix using Seaborn's heatmap.
        
        Args:
            correlation_matrix: numpy array representing the correlation matrix
            feature_names: list of feature names for labeling the heatmap
        """
        plt.figure(figsize=(10, 8))
        output_path = os.path.join(self.graphs_dir, filename)
        
        sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm",
                    xticklabels=feature_names, yticklabels=feature_names)
        plt.title("Average Feature Correlation Matrix")
        plt.tight_layout()
         
        plt.savefig(output_path)
        #plt.show()
        
        
    def remove_highly_correlated_features(self, correlation_matrix, threshold=0.9):
        """
        Remove features with correlation higher than the specified threshold.
        """
        # Find highly correlated features
        to_remove = set()
        for i in range(len(correlation_matrix.columns)):
            for j in range(i + 1, len(correlation_matrix.columns)):
                if abs(correlation_matrix.iloc[i, j]) > threshold:
                    to_remove.add(correlation_matrix.columns[j])

        # Drop redundant features
        reduced_correlation_matrix = correlation_matrix.drop(columns=to_remove, index=to_remove)
        print(f"Removed {len(to_remove)} features. Retained {len(reduced_correlation_matrix.columns)} features.")
        return reduced_correlation_matrix, to_remove
    
    def evaluate_feature_importance(self, feature_matrix, labels,filename='feature_importance.png'):
        """
        Evaluate feature importance using SVC with RBF kernel and permutation importance.
        """
        num_windows, num_channels, num_features = feature_matrix.shape

        # Scale features and compute importance per channel
        feature_importances = np.zeros((num_channels, num_features))

        for ch in range(num_channels):
            print(f"Evaluating channel {ch + 1}/{num_channels}...")

            # Extract features for the current channel
            X = feature_matrix[:, ch, :]
            y = labels

            # Scale the features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Split data into train/test
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

            # Train the SVC model
            model = SVC(kernel="rbf")
            model.fit(X_train, y_train)

            # Compute permutation importance
            result = permutation_importance(model, X_test, y_test, scoring="accuracy", n_repeats=10, random_state=42)
            feature_importances[ch, :] = result.importances_mean

        # Calculate mean importance across all channels
        mean_importance = np.abs(np.mean(feature_importances, axis=0))

        # Select the top 4 features
        top_4_indices = np.abs(np.argsort(mean_importance)[-4:][::-1])
        top_4_features = [(idx, mean_importance[idx]) for idx in top_4_indices]

        print("Top 4 features and their importance values:")
        for idx, importance in top_4_features:
            print(f"Feature {idx}: {importance:.4f}")

        # Plot histogram of feature importances
        self.plot_feature_importance(mean_importance,filename)

        return top_4_indices, mean_importance

    def plot_feature_importance(self, feature_importances,filename='feature_importance.png'):
        """
        Plot the feature importance values as a histogram.
        """
        plt.figure(figsize=(12, 6))
        output_path = os.path.join(self.graphs_dir, filename)
        sns.barplot(x=np.arange(len(feature_importances)), y=feature_importances)
        plt.title("Feature Importance Values")
        plt.xlabel("Feature Index")
        plt.ylabel("Mean Importance")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_path)
        #plt.show()