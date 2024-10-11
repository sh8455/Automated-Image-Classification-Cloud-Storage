from keras.models import load_model, Sequential
import cv2 as cv
from keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Activation, Dropout
from keras.utils import img_to_array

import os
import getpass

model = load_model('cifar100_1.h5')
username = getpass.getuser()

def classificationn(filename, model):
    start_dir = "C:/Users/"+username+"/Desktop/Newbie_Assignment"
    target_dir = "client"

    filepath = find_dirs(start_dir, target_dir)
    pathname = filepath +"\\"+ filename

    test_img = cv.imread(pathname)
    test_img = cv.cvtColor(test_img, cv.COLOR_BGR2RGB)

    test_img = cv.resize(test_img,dsize=(32,32))

    test_img = img_to_array(test_img)

    test_img = test_img.reshape((1, test_img.shape[0], test_img.shape[1], test_img.shape[2]))

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

    model.load_weights('cifar100_1.h5')

    r = model.predict(test_img)

    print(r)

    res = r[0]

    labels = [
        'apple', 'aquarium_fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 'beetle',
        'bicycle', 'bottle', 'bowl', 'boy', 'bridge', 'bus', 'butterfly', 'camel',
        'can', 'castle', 'caterpillar', 'cattle', 'chair', 'chimpanzee', 'clock',
        'cloud', 'cockroach', 'couch', 'crab', 'crocodile', 'cup', 'dinosaur',
        'dolphin', 'elephant', 'flatfish', 'forest', 'fox', 'girl', 'hamster',
        'house', 'kangaroo', 'keyboard', 'lamp', 'lawn_mower', 'leopard', 'lion',
        'lizard', 'lobster', 'man', 'maple_tree', 'motorcycle', 'mountain', 'mouse',
        'mushroom', 'oak_tree', 'orange', 'orchid', 'otter', 'palm_tree', 'pear',
        'pickup_truck', 'pine_tree', 'plain', 'plate', 'poppy', 'porcupine',
        'possum', 'rabbit', 'raccoon', 'ray', 'road', 'rocket', 'rose',
        'sea', 'seal', 'shark', 'shrew', 'skunk', 'skyscraper', 'snail', 'snake',
        'spider', 'squirrel', 'streetcar', 'sunflower', 'sweet_pepper', 'table',
        'tank', 'telephone', 'television', 'tiger', 'tractor', 'train', 'trout',
        'tulip', 'turtle', 'wardrobe', 'whale', 'willow_tree', 'wolf', 'woman',
        'worm'
    ]

    result = labels[res.argmax()]
    print("예측한 결과 = ", result)

    return result

def find_dirs(start_dir, target_dir):
    for dirpath, dirnames, filenames in os.walk(start_dir):
        for dirname in dirnames:
            if dirname == target_dir:
                ppath = os.path.join(dirpath, dirname)
                print(ppath)
                return ppath
    print('해당 디렉토리에 파일[%s]이 존재하지 않음' %target_dir)

