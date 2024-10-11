from keras import datasets, Sequential
from keras.layers import Conv2D, Dense, MaxPooling2D, Flatten
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import confusion_matrix
from keras.datasets import cifar100
from keras.layers.core import Dense, Activation, Dropout, Flatten

(x_train, y_train), (x_test, y_test) = cifar100.load_data()

y_train = y_train.reshape(-1,)
y_test = y_test.reshape(-1,)

plt.figure(figsize=(10, 10))
for image in range(0, 20):
    i = image
    plt.subplot(5,5,i+1)
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    j=i+0
    data_plot = x_train[j]
    plt.imshow(data_plot)
    plt.xlabel(str(y_train[j]))
plt.show()

x_train = x_train/255
x_test = x_test/255

model = Sequential()

model.add(Conv2D(32,(3,3),padding='same',input_shape=(32,32,3)))
model.add(Activation('relu'))
model.add(Conv2D(32,(3,3),padding='same'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))
 
model.add(Conv2D(64,(3,3),padding='same'))
model.add(Activation('relu'))
model.add(Conv2D(64,(3,3),padding='same'))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(0.25))
 
model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(100,activation='softmax'))

model.summary()

opt = 'adam'

model.compile(loss = 'sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

model.fit(x_train, y_train, epochs=100)

test_loss, test_acc = model.evaluate(x_test, y_test)
print("test accuracy: ", test_acc)

model.save("cifar100_1.h5")