import sys
import torch
import torch.nn as nn
import tensorflow as tf
from tensorflow.keras.layers import Dense, Conv2D, LSTM, GRU, RNN
from calculadorapnav.external.logger import logger


class ModelData:
    _model: object
    _num_parameters: int
    _model_size_bytes: int
    _precision_arithmetic: float
    _num_features: int
    _num_flops: int
    _energy_epoch: float
    _energy_bath: float
    _time_epoch: float
    _time_batch: float
    _n_batches: int
    _n_epoch: int
    _type_process: str
    _framework: str

    def __init__(
        self,
        type_process="training",
        result=None,
        argument=None,
        n_batch=0,
        n_epoch=0,
        duration=0,
        total_energy=0,
    ):
        self._type_process = type_process
        self._result = result
        self._argument = argument
        self._model = None
        self._framework = None
        self._num_parameters = 0
        self._model_size = "small"
        self._precision_arithmetic = 0
        self._num_features = 0
        self._num_flops = 0
        self._duration = duration
        self._total_energy = total_energy
        self._energy_bath = 0
        self._n_batches = n_batch
        self._time_batch = 0
        self._energy_epoch = 0
        self._n_epoch = n_epoch
        self._time_epoch = 0

    def determine_framework(self) -> str:
        if self._argument:
            items = (
                self._argument
                if isinstance(self._argument, (list, tuple))
                else [self._argument]
            )
            for item in items:
                if item is not None:
                    try:
                        if isinstance(item, torch.nn.Module):
                            self._framework = "torch"
                            self._model = item
                            return self._framework
                        elif isinstance(item, tf.keras.models.Model):
                            self._framework = "tensorflow"
                            self._model = item
                            return self._framework
                    except AttributeError:
                        continue

        if self._result:
            items = (
                self._result
                if isinstance(self._result, (list, tuple))
                else [self._result]
            )
            for item in items:
                if item is not None:
                    try:
                        if isinstance(item, torch.nn.Module):
                            self._framework = "torch"
                            self._model = item
                            return self._framework
                        elif isinstance(item, tf.keras.models.Model):
                            self._framework = "tensorflow"
                            self._model = item
                            return self._framework
                    except AttributeError:
                        continue

        self._framework = "Unknown library"
        return self._framework

    def calculate_general_data(self) -> None:
        found_features = False
        if self._framework == "torch":
            self._num_parameters = sum(p.numel() for p in self._model.parameters())
            for layer in self._model.modules():
                if isinstance(layer, (nn.Conv1d, nn.Conv2d, nn.Conv3d)):
                    self._num_features = layer.in_channels
                    found_features = True
                    break
                elif isinstance(
                    layer, (nn.Linear, nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d)
                ):
                    self._num_features = layer.in_features
                    found_features = True
                    break
                elif isinstance(layer, (nn.LSTM, nn.GRU, nn.RNN)):
                    self._num_features = layer.input_size
                    found_features = True
                    break
            if not found_features:
                logger.info("Could not determine the number of features.")

        elif self._framework == "tensorflow":
            self._num_parameters = self._model.count_params()
            if hasattr(self._model, "input_shape"):
                input_shape = self._model.input_shape
                if input_shape:
                    if isinstance(input_shape, tuple):
                        self._num_features = input_shape[1:]
                    elif isinstance(input_shape, list):
                        self._num_features = [
                            shape[1:] for shape in input_shape if shape is not None
                        ]
                    else:
                        logger.info(
                            "Could not determine the number of features from the model's input shape."
                        )
                else:
                    logger.info("Could not determine the number of features.")

            elif hasattr(self._model, "layers"):
                for layer in self._model.layers:
                    if isinstance(
                        layer,
                        (
                            tf.keras.layers.Conv1D,
                            tf.keras.layers.Conv2D,
                            tf.keras.layers.Conv3D,
                            tf.keras.layers.Dense,
                            tf.keras.layers.BatchNormalization,
                            tf.keras.layers.LSTM,
                            tf.keras.layers.GRU,
                            tf.keras.layers.SimpleRNN,
                        ),
                    ):
                        if hasattr(layer, "input_shape"):
                            input_shape = layer.input_shape
                            if isinstance(input_shape, list):
                                self._num_features = [
                                    shape[1:]
                                    for shape in input_shape
                                    if shape is not None
                                ]
                            elif input_shape:
                                self._num_features = input_shape[1:]
                            break
                    else:
                        logger.info(
                            "Could not determine the number of features for the layer."
                        )
            else:
                logger.info("Could not determine the input shape of the model.")

        if self._num_parameters != 0:
            if self._num_parameters == 0:
                self._model_size = "unknown"
            elif self._num_parameters < 100_000_000:
                self._model_size = "small"
            elif self._num_parameters < 1_000_000_000:
                self._model_size = "medium"
            else:
                self._model_size = "large"

    def measurements(self) -> None:
        if self._n_batches:
            self._energy_bath = self._total_energy.kWh / self._n_batches
            self._time_batch = self._duration / self._n_batches

        if self._type_process == "training" and self._n_epoch:
            self._energy_epoch = self._total_energy.kWh / self._n_epoch
            self._time_epoch = self._duration / self._n_epoch

    def do_model_measurements(self) -> dict:
        self.determine_framework()
        if self._framework != "Unknown library":
            self.calculate_general_data()

            logger.info(f"Number of parameters: {self._num_parameters}")
            logger.info(f"Model size in bytes: {self._model_size}")
            logger.info(f"Number of features: {self._num_features}")

        else:
            logger.info(
                "Could not determine the framework from the provided arguments."
            )

        self.measurements()
        if self._energy_bath:
            logger.info(f"Energy per batch: {self._energy_bath} kWh")
            logger.info(f"Time per batch: {self._time_batch}")
        else:
            logger.info("Energy per batch not available.")

        if self._energy_epoch:
            logger.info(f"Energy per epoch: {self._energy_epoch} kWh")
            logger.info(f"Time per epoch: {self._time_epoch}")
        else:
            logger.info("Energy per epoch not available.")

        return {
            "framework": self._framework,
            "num_parameters": self._num_parameters,
            "model_size": self._model_size,
            "num_features": self._num_features,
            "energy_batch": self._energy_bath,
            "time_batch": self._time_batch,
            "energy_epoch": self._energy_epoch,
            "time_epoch": self._time_epoch,
        }
