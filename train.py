import datetime
import os
import tensorflow as tf
import time
from IPython import display
from matplotlib import pyplot as plt

BUFFER_SIZE = 1000
BATCH_SIZE = 32


def load(image_file):
  image = tf.io.read_file(image_file)
  image = tf.io.decode_image(image, channels=3, expand_animations=False)
  image = tf.image.resize_with_pad(image, 32, 32)
  image = tf.cast(image, tf.float32)

  name_file = tf.strings.substr(image_file, tf.zeros(tf.shape(image_file), dtype=tf.dtypes.int32), tf.strings.length(image_file) - 3) + 'txt'
  name = tf.io.read_file(name_file)
  return name, image
def normalize(image):
  image = (image / 127.5) - 1
  return image
@tf.function
def random_jitter(image):
  if tf.random.uniform(()) > 0.5:
    image = tf.image.flip_left_right(image)

  return image
def load_train(image_file):
  name, image = load(image_file)
  image = random_jitter(image)
  image = normalize(image)

  return name, image
def load_test(image_file):
  name, image = load(image_file)
  image = normalize(image)

  return name, image
train_dataset = tf.data.Dataset.list_files('./train/*.png')
train_dataset = train_dataset.map(load_train, num_parallel_calls=tf.data.AUTOTUNE)
train_dataset = train_dataset.shuffle(BUFFER_SIZE)
train_dataset = train_dataset.batch(BATCH_SIZE)
train_dataset = train_dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

test_dataset = tf.data.Dataset.list_files('./test/*.png')
test_dataset = test_dataset.map(load_test)
test_dataset = test_dataset.batch(BATCH_SIZE)
test_dataset = test_dataset.prefetch(buffer_size=tf.data.AUTOTUNE)

encoder_input = tf.keras.Input(shape=(), dtype=tf.string)
vocabulary = 0
def Encoder():
  x = tf.keras.layers.TextVectorization(max_tokens=32767,
                         output_mode='int',
                         standardize='lower_and_strip_punctuation',
                         output_sequence_length=32)
  x.adapt(train_dataset.map(lambda name, image: name))
  global vocabulary
  vocabulary = len(x.get_vocabulary())
  x = x(encoder_input)
  return x
encoder = Encoder()
def NLP():
  x = encoder
  x = tf.keras.layers.Embedding(
        input_dim=vocabulary,
        input_length=32,
        output_dim=32)(x)
  x = tf.keras.layers.LSTM(32, return_sequences=True)(x)
  x = tf.keras.layers.Reshape((32, 32, 1))(x)
  return x
nlp = NLP()
def Generator():
  initializer = tf.random_normal_initializer(0., 0.02)
  x = nlp;
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.Dropout(0.2)(x)
  x = tf.keras.layers.Conv2DTranspose(3, 4,
                    strides=1,
                    padding='same',
                    kernel_initializer=initializer,
                    activation='tanh')(x)
  return tf.keras.Model(inputs=encoder_input, outputs=x)
generator = Generator()
def Discriminator():
  initializer = tf.random_normal_initializer(0., 0.02)
  img = tf.keras.Input(shape=(32, 32, 3))
  x = tf.keras.layers.Concatenate()([nlp, img])
  x = tf.keras.layers.Conv2D(64, 4,
                 strides=1,
                 padding='same',
                 kernel_initializer=initializer,
                 use_bias=False)(x)
  x = tf.keras.layers.BatchNormalization()(x)
  x = tf.keras.layers.LeakyReLU()(x)
  x = tf.keras.layers.Conv2D(1, 4, strides=1, padding='same', kernel_initializer=initializer)(x)
  return tf.keras.Model(inputs=[encoder_input, img], outputs=x)
discriminator = Discriminator()

LAMBDA = 100
loss_object = tf.keras.losses.BinaryCrossentropy(from_logits=True)
def generator_loss(disc_generated_output, gen_output, target):
  gan_loss = loss_object(tf.ones_like(disc_generated_output), disc_generated_output)

  # Mean absolute error
  l1_loss = tf.reduce_mean(tf.abs(target - gen_output))

  total_gen_loss = gan_loss + (LAMBDA * l1_loss)

  return total_gen_loss, gan_loss, l1_loss
def discriminator_loss(disc_real_output, disc_generated_output):
  real_loss = loss_object(tf.ones_like(disc_real_output), disc_real_output)

  generated_loss = loss_object(tf.zeros_like(disc_generated_output), disc_generated_output)

  total_disc_loss = real_loss + generated_loss

  return total_disc_loss

generator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
discriminator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
checkpoint_dir = './training_checkpoints'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                 discriminator_optimizer=discriminator_optimizer,
                 generator=generator,
                 discriminator=discriminator)

def generate_images(model, test_input, tar):
  prediction = model(test_input, training=True)
  plt.figure(figsize=(15, 15))

  display_list = [tar[0], prediction[0]]
  title = [test_input[0], 'Predicted Image']

  for i in range(2):
    plt.subplot(1, 2, i+1)
    plt.title(title[i])
    # Getting the pixel values in the [0, 1] range to plot.
    plt.imshow(display_list[i] * 0.5 + 0.5)
    plt.axis('off')
  plt.show(block=False)

log_dir="./logs/"
summary_writer = tf.summary.create_file_writer(log_dir + "fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
@tf.function
def train_step(name, target, step):
  with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
    gen_output = generator(name, training=True)

    disc_real_output = discriminator([name, target], training=True)
    disc_generated_output = discriminator([name, gen_output], training=True)

    gen_total_loss, gen_gan_loss, gen_l1_loss = generator_loss(disc_generated_output, gen_output, target)
    disc_loss = discriminator_loss(disc_real_output, disc_generated_output)

  generator_gradients = gen_tape.gradient(gen_total_loss, generator.trainable_variables)
  discriminator_gradients = disc_tape.gradient(disc_loss, discriminator.trainable_variables)

  generator_optimizer.apply_gradients(zip(generator_gradients, generator.trainable_variables))
  discriminator_optimizer.apply_gradients(zip(discriminator_gradients, discriminator.trainable_variables))

  with summary_writer.as_default():
    tf.summary.scalar('gen_total_loss', gen_total_loss, step=step//1000)
    tf.summary.scalar('gen_gan_loss', gen_gan_loss, step=step//1000)
    tf.summary.scalar('gen_l1_loss', gen_l1_loss, step=step//1000)
    tf.summary.scalar('disc_loss', disc_loss, step=step//1000)

def fit(train_ds, test_ds, steps):
  example_input, example_target = next(iter(test_ds.take(1)))
  start = time.time()

  for step, (input_image, target) in train_ds.repeat().take(steps).enumerate():
    if (step) % 1000 == 0:
      display.clear_output(wait=True)

      if step != 0:
        print(f'Time taken for 1000 steps: {time.time()-start:.2f} sec\n')

      start = time.time()

      generate_images(generator, example_input, example_target)
      print(f"Step: {step//1000}k")

    train_step(input_image, target, step)

    # Training step
    if (step+1) % 10 == 0:
      print('.', end='', flush=True)


    # Save (checkpoint) the model every 5k steps
    if (step + 1) % 5000 == 0:
      checkpoint.save(file_prefix=checkpoint_prefix)


if __name__ == "__main__":
  checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))
  fit(train_dataset, test_dataset, steps=40000)
