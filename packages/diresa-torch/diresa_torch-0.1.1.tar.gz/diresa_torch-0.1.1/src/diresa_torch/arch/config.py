from dataclasses import dataclass
from typing import Tuple, Optional, Literal
import torch.nn as nn


@dataclass
class CNNConfig:
    stack: Tuple[int, ...] = (1,)
    stack_filters: Tuple[int, ...] = (32,)
    kernel_size: Tuple[int, int] = (3, 3)
    type: Literal["cnn"] = "cnn"

    def __post_init__(self):
        if len(self.stack) <= 0:
            raise ValueError("Stack must be positive")
        if any(f <= 0 for f in self.stack_filters):
            raise ValueError("All filter values must be positive")
        if any(v <= 0 for v in self.kernel_size):
            raise ValueError("Kernel values must be positive")
        if len(self.stack) != len(self.stack_filters):
            raise ValueError("Length of stacks and length of stack filters must correspond."
                             f" Got {len(self.stack)} != {len(self.stack_filters)}")


@dataclass
class DenseConfig:
    type: Literal["dense"] = "dense"
    dense_units: Tuple[int, ...] = (128, 64)

    def __post_init__(self):
        if any(u <= 0 for u in self.dense_units):
            raise ValueError("dense_units must contain positive values")
        if len(self.dense_units) < 1:
            raise ValueError(
                "dense_units should contain at least an output layer")


@dataclass
class DiresaConfig:
    """
    Global configuration that contains specific architecture configs.
    Can have CNN, Dense, or both.
    """
    input_shape: Tuple[int, ...] = ()
    activation: nn.Module = nn.ReLU()
    cnn_config: Optional[CNNConfig] = None
    dense_config: Optional[DenseConfig] = None

    def __post_init__(self):
        if len(self.input_shape) == 1:
            if self.cnn_config is not None:
                raise ValueError(
                    "Input shape of 1 is valid only when using dense layers")
        elif len(self.input_shape) == 3:
            if self.cnn_config is None:
                raise ValueError(
                    "Input shape of 3 is only valid when using CNN layers")

            # used to verify input shape
            def check_function(x): return x % (
                2 ** len(self.cnn_config.stack)) == 0
            # do not need to check la t dimension as it is depth of input. Only the 2 first are required
            # to have the right dimensions
            multiple_of_stack_len = list(
                map(check_function, self.input_shape[:-1]))

            if not all(multiple_of_stack_len):

                offenders = [v for v in self.input_shape[:-1]
                             if v not in filter(check_function, self.input_shape[:-1])]
                raise ValueError("Dimensions of input shape should be multiple of 2^len(stack)."
                                 f" Got {offenders} from {self.input_shape} which are not multiple"
                                 f" of 2^{len(self.cnn_config.stack)} (={2**len(self.cnn_config.stack)}) from"
                                 f" stack = {self.cnn_config.stack} and input_shape = {self.input_shape}."
                                 " This requirement is present because of the pooling layers in the CNN layers"
                                 " which divide the dimensions by 2 at each stack.")
        else:
            raise ValueError("Must provide valid input_shape. Rank 3 with Conv2D layers "
                             "with shape (Height, Width, Depth) and Dims should be a multiple of 2^len(stack)"
                             f"; Rank 1 if only Dense layer. Got {self.input_shape}")


class DiresaSetup:
    """
        Factory class providing ``create_config`` as factory method to create configuration from user parameters
    """

    @staticmethod
    def create_config(
        input_shape: Tuple[int, ...] = (),
        # CNN parameters
        stack: Optional[int] = None,
        stack_filters: Optional[Tuple[int, ...]] = None,
        kernel_size: Tuple[int, int] = (3, 3),
        # Dense parameters
        dense_units: Optional[Tuple[int, ...]] = None,
        # Global parameters
        activation: nn.Module = nn.ReLU()
    ) -> DiresaConfig:
        """
            Factory Method to build a DiresaConfig from hyperparameters

            :param input_shape: is the shape of input features. Rank 2 with Conv2D layers, first 2 dims should be a multiple of 2^len(stack); rank 1 if only Dense layers
            :param stack: are the number of Conv2D layers in each block
            :param stack_filters: number of filters in a block
            :param kernel_size: kernel size for convultion
            :param dense_units: tuple which describes the width of each full connected feedforward layers. First layer describes the input size, the last layer defines the output layer which is the size of latent space. E.g. ``(3, 16, 32, 64)`` is a FFN with one input layer of size ``3``, two hidden layers ``(16, 32)`` and last layer which defines latent space of size ``64``. When using dense_units in combination with CNN layers an additional layer is added to match CNN output to FFN input. The input layer to the FNN is effectively already computed by the model.
            :param activation: activation function used through the network.

            :return: ``DiresaConfig`` which is the global configuration object containing the appropriate sub-configs


            :raises ValueError: in case of an invalid configuration
        """
        # Check what type of arch we deal with
        has_cnn_params = stack is not None and stack_filters is not None
        has_dense_params = dense_units is not None

        if not has_cnn_params and not has_dense_params:
            raise ValueError(
                "Must provide either CNN parameters (stack + stack_filters) "
                "or dense parameters (dense_units) or both"
            )

        # CNN config if parameters provided
        cnn_config = None
        if has_cnn_params:
            cnn_config = CNNConfig(
                stack=stack,
                stack_filters=stack_filters,
                kernel_size=kernel_size,
            )

        # Dense config if parameters provided
        dense_config = None
        if has_dense_params:
            dense_config = DenseConfig(
                dense_units=dense_units
            )

        # Create global config
        return DiresaConfig(
            input_shape=input_shape,
            activation=activation,
            cnn_config=cnn_config,
            dense_config=dense_config,
        )
