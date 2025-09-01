import pathlib
import pandas as pd
import tensorflow as tf
import numpy as np

from tensorflow import keras
from tensorflow.keras import layers, regularizers
from tensorflow.keras.utils import plot_model
from tensorflow.keras.constraints import max_norm


# All the data dumped from the database as JSON
# read in the data
# Read the data into Pandas
raw_dataset = pd.read_json("../../data/training_data.json")

# Make a copy
dataset = raw_dataset.copy()

# Not required felds. Note that Crypto is already merged into the appropriate dry or green fraction
[dataset.pop(x) for x in ['crypto','pg','pnpv']]
# Adding in these makes no difference to the model so they're dropped
[dataset.pop(x) for x in ['burn','ndvi','ndwi']]
# Dropping out the SWIR to test
[dataset.pop(x) for x in ['b5','b7']]

# Get a training Subset
train_dataset = dataset.sample(frac=1.00)
print(train_dataset.shape)


train_stats = train_dataset.describe()
[train_stats.pop(x) for x in ['bare','pv','npv']]
train_stats = train_stats.transpose()

train_labels = pd.concat([train_dataset.pop(x) for x in ['bare','pv','npv']], 1)

# I've retured the test/train split for the moment
#test_dataset = dataset.drop(train_dataset.index)
#print(test_dataset.shape)
#test_labels = pd.concat([test_dataset.pop(x) for x in ['bare','pv','npv']], 1)


def build_model():
  model = keras.Sequential([
    layers.Dense(128, activation='relu',kernel_constraint=max_norm(2),input_shape=[len(train_dataset.keys())]),
    layers.Dropout(0.25),
    layers.Dense(128, activation='relu', kernel_constraint=max_norm(2)),
    layers.Dropout(0.25),
    layers.Dense(64, activation='relu',kernel_constraint=max_norm(2)),
    layers.Dropout(0.25),
    layers.Dense(3)
  ])

  #optimizer = tf.keras.optimizers.RMSprop(0.001)
  optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
  #optimizer = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
    

  model.compile(loss='mean_squared_error',
                optimizer=optimizer,
                metrics=['mean_absolute_error', 'mean_squared_error']) #'huber_loss'
  return model

model = build_model()
model.summary()


# Display training progress by printing a single dot for each completed epoch
class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')

# The patience parameter is the amount of epochs to check for improvement
early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', mode='min', verbose=1, patience=1000)

# Fit the Model
history = model.fit(train_dataset, train_labels, epochs=5000,
                    validation_split = 0.1, verbose=0,
                    callbacks=[early_stop,PrintDot()])
print('\n')

# Save the model
model.save('../../data/fcModel20191201.h5')
