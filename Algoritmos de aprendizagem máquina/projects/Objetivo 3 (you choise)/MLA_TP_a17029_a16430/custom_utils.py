from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score)
import tensorflow as tf
from sklearn.base import BaseEstimator, TransformerMixin
import os
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator, ScalarFormatter
import datetime


class CustomUtils():
    """
    Custom class with some static utils methods.
    """
    
    def __init__(self) -> None:
        """
        Initialize an empty constructor.
        """
        pass
    
    
    @staticmethod
    def evaluate_preds(y_true, y_preds):
        """
        Perform evaluation comparison on y_true labels vs. y_pred labels.

        Parameters:
        -----------
        y_true : array-like
            True labels.

        y_preds : array-like
            Predicted labels.

        Returns:
        -----------
        metric_dict : dict
            Dictionary containing evaluation metrics (accuracy, precision, recall, f1).
        """
        
        accuracy = accuracy_score(y_true, y_preds)
        precision = precision_score(y_true, y_preds)
        recall = recall_score(y_true, y_preds)
        f1 = f1_score(y_true, y_preds)
        metric_dict = {"accuracy": round(accuracy, 2),
                    "precision": round(precision, 2),
                    "recall": round(recall, 2),
                    "f1": round(f1, 2)}
        print(f"Acc: {accuracy * 100:.2f}%")
        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"F1 score: {f1:.2f}")

        return metric_dict
    
    
    @staticmethod
    def create_model(input_d=30, neurons=8, dropout_rate=0.2, l_rate=0.001, optimizer='Adam'):
        """
        Create the TensorFlow model.

        Parameters:
        -----------
        input_d : int, optional (default=30)
            Number of input dimensions.

        neurons : int, optional (default=8)
            Number of neurons in the hidden layer.

        dropout_rate : float, optional (default=0.2)
            Dropout rate for regularization.

        l_rate : float, optional (default=0.001)
            Learning rate for the optimizer.

        optimizer : str, optional (default='Adam')
            Optimizer to use (supported options: 'Adam', 'SGD', 'RMSprop').

        Returns:
        -----------
        model : object
            TensorFlow model.
        """
        
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Dense(neurons, input_dim=input_d))
        model.add(tf.keras.layers.Activation('relu'))
        model.add(tf.keras.layers.Dropout(dropout_rate))
        model.add(tf.keras.layers.Dense(units=1))
        model.add(tf.keras.layers.Activation('sigmoid'))
        
        # Dictionary mapping optimizer to its class
        optimizer_dict = {'Adam': tf.keras.optimizers.Adam,
                        'SGD': tf.keras.optimizers.SGD,
                        'RMSprop': tf.keras.optimizers.RMSprop}

        # Instanciate the correspondent optimizer
        if optimizer in optimizer_dict:
            opt_class = optimizer_dict[optimizer]
            opt = opt_class(learning_rate=l_rate)
        else:
            raise ValueError("Invalid optimizer specified. Supported options are 'Adam', 'SGD', and 'RMSprop'!!!")

        model.compile(loss='binary_crossentropy',
                    optimizer=opt,
                    metrics=['accuracy'])

        
        return model
    
    
    @staticmethod
    def model_to_save(m_path, all_features=True):
        """
        Create the name of the model to save.

        Parameters:
        -----------
        m_path : str
            Path where the model will be saved.

        all_features : bool, optional (default=True)
            Flag indicating whether all features were used in the model.

        Returns:
        -----------
        model_filepath : str
            Filepath for saving the model.
        """
        
        if all_features:
            prefix = "Model_AllFeatures_"
        else:
            prefix = "Model_SomeFeatures_"
            
        model_filename = prefix + datetime.datetime.now().strftime("%d_%m_%Y-%Hh_%Mm_%Ss") + ".hdf5"
        model_filepath = os.path.join(m_path, model_filename)
        
        return model_filepath
    
    
    @staticmethod
    def plot_metrics(modelfit, metric, title, color1='blue', color2='red'):
        """
        Plot Loss/Accuracy vs Epoch.

        Parameters:
        -----------
        modelfit : object
            Object containing the model training history.

        metric : str
            Metric to plot (e.g., 'loss', 'accuracy').

        title : str
            Title of the plot.

        color1 : str, optional (default='blue')
            Color for training metric.

        color2 : str, optional (default='red')
            Color for validation metric.
        """
        
        metric_cap = metric.capitalize()
        plt.plot(modelfit.history[metric], color1, label=f'Training {metric_cap}')
        plt.plot(modelfit.history[f'val_{metric}'], color2, label=f'Validation {metric_cap}')
        plt.title(title)
        plt.xlabel('Epochs')
        plt.ylabel(metric_cap)
        # Get the current axis
        ax = plt.gca()
        # Set x-axis to display only integer values
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        # Format x-axis tick labels as integers
        ax.xaxis.set_major_formatter(ScalarFormatter())

        plt.legend()
        plt.show()
        

class CustomColumnTransformer(BaseEstimator, TransformerMixin):
    """
    Custom transformer class to select specific columns from a DataFrame.
    """
    
    def __init__(self, columns=None):
        """
        Initialize the transformer.

        Parameters:
        -----------
        columns : list or None, optional (default=None)
            List of column names to select from the DataFrame. If None, all columns are selected.
            
        """
        self.columns = columns
        
    def fit(self, X, y=None):
        """
        Fit method. Does nothing and returns self.
            
        """
        return self

    def transform(self, X, y=None):
        """
        Transform method. Selects the specified columns from the input DataFrame.

        Parameters:
        -----------
        X : DataFrame
            Input DataFrame.

        y : array-like or None, optional (default=None)
            Target values (unused).

        Returns:
        -----------
        X_selected : DataFrame
            DataFrame containing only the selected columns.
        """
        
        cols_to_transform = list(X.columns)
        if self.columns:
            cols_to_transform = self.columns
            
        return X[cols_to_transform]
