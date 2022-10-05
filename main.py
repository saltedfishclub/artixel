import tensorflow as tf
import numpy as np

import PIL


def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return PIL.Image.fromarray(tensor)


generator = tf.saved_model.load('./saved_model/generator')

image_tensor = generator(tf.constant(["Iron Ingot"]))

tensor_to_image(image_tensor).save("./out.png")
