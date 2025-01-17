# toxicity_app/model/train_model.py
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Bidirectional
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import TextVectorization

# Only run the training script if this file is executed directly
if __name__ == "__main__":
    # Load and preprocess data
    df = pd.read_csv('csv/train.csv')
    X = df['comment_text']
    y = df[df.columns[2:]].values
    MAX_FEATURES = 200000     # number of words in the vocab
    vectorizer = TextVectorization(max_tokens=MAX_FEATURES,
                                   output_sequence_length=1800,
                                   output_mode='int')
    vectorizer.adapt(X.values)
    vectorized_text = vectorizer(X.values)
    # MCSHBAP - map, chache, shuffle, batch, prefetch  from_tensor_slices, list_file
    dataset = tf.data.Dataset.from_tensor_slices((vectorized_text, y))
    dataset = dataset.cache()
    dataset = dataset.shuffle(160000)
    dataset = dataset.batch(16)
    dataset = dataset.prefetch(8)  # helps bottlenecks
    train = dataset.take(int(len(dataset) * .7))
    val = dataset.skip(int(len(dataset) * .7)).take(int(len(dataset) * .2))
    test = dataset.skip(int(len(dataset) * .9)).take(int(len(dataset) * .1))

    #Build new model
    model = Sequential()
    # Create the embedding layer
    model.add(Embedding(MAX_FEATURES + 1, 32))
    # Bidirectional LSTM Layer
    model.add(Bidirectional(LSTM(32, activation='tanh')))
    # Feature extractor Fully connected layers
    model.add(Dense(128, activation='relu'))
    model.add(Dense(256, activation='relu'))
    model.add(Dense(128, activation='relu'))
    # Final layer
    model.add(Dense(6, activation='sigmoid'))
    # compile model
    model.compile(loss='BinaryCrossentropy', optimizer='Adam', metrics=['accuracy'])
    # Train the model
    history = model.fit(train, epochs=1, validation_data=val)
    # Save the model
    model.save('toxicity_app/model/toxicity_model.keras')
    # Save the vectorizer configuration
    vectorizer_model = tf.keras.Sequential([vectorizer])
    vectorizer_model.compile()
    vectorizer_model.save('toxicity_app/model/vectorizer.keras')