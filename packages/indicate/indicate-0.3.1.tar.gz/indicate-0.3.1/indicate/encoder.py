from typing import Any, List, Tuple

import tensorflow as tf


class Encoder(tf.keras.Model):
    def __init__(
        self, vocab_size: int, embedding_dim: int, enc_units: int, batch_sz: int
    ) -> None:
        super(Encoder, self).__init__()
        self.batch_sz = batch_sz
        self.enc_units = enc_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)

        ##-------- LSTM layer in Encoder ------- ##
        self.lstm_layer = tf.keras.layers.LSTM(
            self.enc_units,
            return_sequences=True,
            return_state=True,
            recurrent_initializer="glorot_uniform",
        )

    def call(
        self, x: tf.Tensor, hidden: List[tf.Tensor], training: bool = None
    ) -> Tuple[tf.Tensor, tf.Tensor, tf.Tensor]:
        x = self.embedding(x)
        output, h, c = self.lstm_layer(x, initial_state=hidden)
        return output, h, c

    def initialize_hidden_state(self) -> List[tf.Tensor]:
        return [
            tf.zeros((self.batch_sz, self.enc_units)),
            tf.zeros((self.batch_sz, self.enc_units)),
        ]
