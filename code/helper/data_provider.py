import numpy as np
import keras.preprocessing.image
import helper.external.SegDataGenerator

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import skimage.io

def data_from_array(data_dir):
    
    # load  x
    training_x = np.load(data_dir+"training/x.npy")
    test_x = np.load(data_dir+"test/x.npy")
    validation_x = np.load(data_dir+"validation/x.npy")

    print(training_x.shape)
    print(test_x.shape)
    print(validation_x.shape)

    # normalize
    training_x = training_x / 255
    test_x = test_x / 255
    validation_x = validation_x / 255

    # load y
    training_y = np.load(data_dir+"training/y.npy")
    test_y = np.load(data_dir+"test/y.npy")
    validation_y = np.load(data_dir+"validation/y.npy")

    print(training_y.shape)
    print(test_y.shape)
    print(validation_y.shape)
    
    return [training_x, training_y, validation_x, validation_y, test_x, test_y]

def data_from_images(data_dir, batch_size, bit_depth, dim1, dim2):
    
    flow_train = single_data_from_images(data_dir + 'training/x/', data_dir + 'training/y/', batch_size, bit_depth, dim1, dim2)
    flow_validation = single_data_from_images(data_dir + 'validation/x', data_dir + 'validation/y', batch_size, bit_depth, dim1, dim2)
    flow_test = single_data_from_images(data_dir + 'test/x', data_dir + 'test/y', batch_size, bit_depth, dim1, dim2)
    
    return [flow_train, flow_validation, flow_test]

def single_data_from_images(x_dir, y_dir, batch_size, bit_depth, dim1, dim2):

    rescale_factor = 1./(2**bit_depth - 1)
    rescale_labels = True
    
    if(rescale_labels):
        rescale_factor_labels = rescale_factor
    else:
        rescale_factor_labels = 1

    gen_x = keras.preprocessing.image.ImageDataGenerator(rescale=rescale_factor)
    gen_y = keras.preprocessing.image.ImageDataGenerator(rescale=rescale_factor_labels)
    
    seed = 42

    stream_x = gen_x.flow_from_directory(
        x_dir,
        target_size=(dim1,dim2),
        color_mode='grayscale',
        batch_size=batch_size,
        class_mode=None,
        seed=seed
    )
    stream_y = gen_y.flow_from_directory(
        y_dir,
        target_size=(dim1,dim2),
        color_mode='rgb',
        batch_size=batch_size,
        class_mode=None,
        seed=seed
    )
    
    flow = zip(stream_x, stream_y)
    
    return flow

def single_data_from_images_1d_y(x_dir, y_dir, batch_size, bit_depth, dim1, dim2):

    rescale_factor = 1./(2**bit_depth - 1)
    rescale_labels = False
    
    if(rescale_labels):
        rescale_factor_labels = rescale_factor
    else:
        rescale_factor_labels = 1

    gen_x = keras.preprocessing.image.ImageDataGenerator(rescale=rescale_factor)
    gen_y = keras.preprocessing.image.ImageDataGenerator(rescale=rescale_factor_labels)
    
    seed = 42

    stream_x = gen_x.flow_from_directory(
        x_dir,
        target_size=(dim1,dim2),
        color_mode='grayscale',
        batch_size=batch_size,
        class_mode=None,
        seed=seed
    )
    stream_y = gen_y.flow_from_directory(
        y_dir,
        target_size=(dim1,dim2),
        color_mode='grayscale',
        batch_size=batch_size,
        class_mode=None,
        seed=seed
    )
    
    flow = zip(stream_x, stream_y)
    
    return flow


def random_sample_generator(x_big_dir, y_big_dir, batch_size, bit_depth, dim1, dim2):

    debug = False
    
    # get images
    x_big = skimage.io.imread_collection(x_big_dir + '*.png').concatenate()
    print('Found',len(x_big), 'images.')
    y_big = skimage.io.imread_collection(y_big_dir + '*.png').concatenate()
    print('Found',len(y_big), 'annotations.')
    
    if(debug):
        fig = plt.figure()
        plt.hist(y_big.flatten())
        plt.savefig('/home/jr0th/github/segmentation/code/generated/y_hist')
        plt.close(fig)

        fig = plt.figure()
        plt.hist(x_big.flatten())
        plt.savefig('/home/jr0th/github/segmentation/code/generated/x_hist')
        plt.close(fig)
    
    # get dimensions right – understand data set
    n_images = x_big.shape[0]
    dim1_size = x_big.shape[1]
    dim2_size = x_big.shape[2]
    
    # rescale images
    rescale_factor = 1./(2**bit_depth - 1)
    rescale_labels = False
    
    if(rescale_labels):
        rescale_factor_labels = rescale_factor
    else:
        rescale_factor_labels = 1
        
    while(True):
        
        # buffers for a batch of data
        x = np.zeros((batch_size, dim1, dim2, 1))
        y = np.zeros((batch_size, dim1, dim2, 1))
        
        # get one image at a time
        for i in range(batch_size):
                       
            # get random image
            img_index = np.random.randint(low=0, high=n_images)
            
            # get random crop
            start_dim1 = np.random.randint(low=0, high=dim1_size+1-dim1)
            start_dim2 = np.random.randint(low=0, high=dim2_size+1-dim2)
            
            # save image to buffer
            x[i, :, :, 0] = x_big[img_index, start_dim1:start_dim1 + dim1, start_dim2:start_dim2 + dim2] * rescale_factor
            y[i, :, :, 0] = y_big[img_index, start_dim1:start_dim1 + dim1, start_dim2:start_dim2 + dim2] * rescale_factor_labels
            
            if(debug):
                fig = plt.figure()
                plt.imshow(x[i, :, :, 0])
                plt.colorbar()
                plt.savefig('/home/jr0th/github/segmentation/code/generated/x_' + str(i))
                plt.close(fig)

                fig = plt.figure()
                plt.imshow(y[i, :, :, 0])
                plt.colorbar()
                plt.savefig('/home/jr0th/github/segmentation/code/generated/y_' + str(i))
                plt.close(fig)
            
        # return the buffer
        yield(x, y)
        


def single_data_from_images_random(x_dir, y_dir, batch_size, bit_depth, dim1, dim2):
    
    rescale_factor = 1./(2**bit_depth - 1)
    rescale_labels = False
    
    if(rescale_labels):
        rescale_factor_labels = rescale_factor
    else:
        rescale_factor_labels = 1

    gen_x = keras.preprocessing.image.ImageDataGenerator(
        rescale=rescale_factor,
        preprocessing_function=pick_random_sample,
        width_shift_range=1,
        height_shift_range=1
    )
    gen_y = keras.preprocessing.image.ImageDataGenerator(
        rescale=rescale_factor_labels,
        preprocessing_function=pick_random_sample,
        width_shift_range=1,
        height_shift_range=1
    )
    
    seed = 42

    stream_x = gen_x.flow_from_directory(
        x_dir,
        target_size=(dim1,dim2),
        color_mode='grayscale',
        batch_size=batch_size,
        class_mode=None,
        save_to_dir='/home/jr0th/github/segmentation/code/generated',
        save_format='png',
        seed=seed
    )
    stream_y = gen_y.flow_from_directory(
        y_dir,
        target_size=(dim1,dim2),
        color_mode='grayscale',
        batch_size=batch_size,
        class_mode=None,
        seed=seed
    )
    
    flow = zip(stream_x, stream_y)
    print('RETURN FLOW')
    return flow

def data_from_images_segmentation(file_path, data_dir, label_dir, classes, batch_size, dim1, dim2):
    generator = helper.external.SegDataGenerator.SegDataGenerator()
    iterator = generator.flow_from_directory(
        file_path,
        data_dir, '.png', 
        label_dir, '.png', 
        classes, 
        target_size=(dim1, dim2), 
        color_mode='grayscale',
        batch_size=batch_size,
        save_to_dir='./temp/'
    )
    return iterator 
