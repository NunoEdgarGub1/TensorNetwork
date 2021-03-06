# Copyright 2019 The TensorNetwork Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#pylint: disable=line-too-long
from typing import Optional, Any, Sequence, Tuple, Type, Callable, List, Text
from tensornetwork.backends import base_backend
from tensornetwork.backends.tensorflow import decompositions
from tensornetwork.backends.tensorflow import tensordot2

# This might seem bad, but pytype treats tf.Tensor as Any anyway, so
# we don't actually lose anything by doing this.
import numpy as np
Tensor = Any


class TensorFlowBackend(base_backend.BaseBackend):
  """See base_backend.BaseBackend for documentation."""

  def __init__(self):
    super(TensorFlowBackend, self).__init__()
    try:
      #pylint: disable=import-outside-toplevel
      import tensorflow as tf
    except ImportError:
      raise ImportError("Tensorflow not installed, please switch to a "
                        "different backend or install Tensorflow.")
    self.tf = tf
    self.name = "tensorflow"

  def tensordot(self, a: Tensor, b: Tensor, axes: Sequence[Sequence[int]]):
    return tensordot2.tensordot(self.tf, a, b, axes)

  def reshape(self, tensor: Tensor, shape: Tensor):
    return self.tf.reshape(tensor, shape)

  def transpose(self, tensor, perm):
    return self.tf.transpose(tensor, perm)

  def slice(self,
            tensor: Tensor,
            start_indices: Tuple[int, ...],
            slice_sizes: Tuple[int, ...]) -> Tensor:
    if len(start_indices) != len(slice_sizes):
      raise ValueError("Lengths of start_indices and slice_sizes must be"
                       "identical.")
    return self.tf.slice(tensor, start_indices, slice_sizes)

  def svd_decomposition(self,
                        tensor: Tensor,
                        split_axis: int,
                        max_singular_values: Optional[int] = None,
                        max_truncation_error: Optional[float] = None,
                        relative: Optional[bool] = False
                       ) -> Tuple[Tensor, Tensor, Tensor, Tensor]:
    return decompositions.svd_decomposition(
        self.tf,
        tensor,
        split_axis,
        max_singular_values,
        max_truncation_error,
        relative=relative)

  def qr_decomposition(self, tensor: Tensor,
                       split_axis: int) -> Tuple[Tensor, Tensor]:
    return decompositions.qr_decomposition(self.tf, tensor, split_axis)

  def rq_decomposition(self, tensor: Tensor,
                       split_axis: int) -> Tuple[Tensor, Tensor]:
    return decompositions.rq_decomposition(self.tf, tensor, split_axis)

  def shape_concat(self, values: Tensor, axis: int) -> Tensor:
    return self.tf.concat(values, axis)

  def shape_tensor(self, tensor: Tensor) -> Tensor:
    return self.tf.shape(tensor)

  def shape_tuple(self, tensor: Tensor) -> Tuple[Optional[int], ...]:
    return tuple(tensor.shape.as_list())

  def sparse_shape(self, tensor: Tensor) -> Tuple[Optional[int], ...]:
    return self.shape_tuple(tensor)

  def shape_prod(self, values: Tensor) -> Tensor:
    return self.tf.reduce_prod(values)

  def sqrt(self, tensor: Tensor) -> Tensor:
    return self.tf.sqrt(tensor)

  def diag(self, tensor: Tensor) -> Tensor:
    return self.tf.linalg.diag(tensor)

  def convert_to_tensor(self, tensor: Tensor) -> Tensor:
    result = self.tf.convert_to_tensor(tensor)
    return result

  def trace(self, tensor: Tensor) -> Tensor:
    return self.tf.linalg.trace(tensor)

  def outer_product(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
    return tensordot2.tensordot(self.tf, tensor1, tensor2, 0)

  def einsum(self, expression: str, *tensors: Tensor) -> Tensor:
    return self.tf.einsum(expression, *tensors)

  def norm(self, tensor: Tensor) -> Tensor:
    return self.tf.linalg.norm(tensor)

  def eye(self,
          N: int,
          dtype: Optional[Type[np.number]] = None,
          M: Optional[int] = None) -> Tensor:
    dtype = dtype if dtype is not None else self.tf.float64
    return self.tf.eye(num_rows=N, num_columns=M, dtype=dtype)

  def ones(self,
           shape: Tuple[int, ...],
           dtype: Optional[Type[np.number]] = None) -> Tensor:
    dtype = dtype if dtype is not None else self.tf.float64
    return self.tf.ones(shape=shape, dtype=dtype)

  def zeros(self,
            shape: Tuple[int, ...],
            dtype: Optional[Type[np.number]] = None) -> Tensor:
    dtype = dtype if dtype is not None else self.tf.float64
    return self.tf.zeros(shape, dtype=dtype)

  def randn(self,
            shape: Tuple[int, ...],
            dtype: Optional[Type[np.number]] = None,
            seed: Optional[int] = None) -> Tensor:
    if seed:
      self.tf.random.set_seed(seed)

    dtype = dtype if dtype is not None else self.tf.float64
    if (dtype is self.tf.complex128) or (dtype is self.tf.complex64):
      return self.tf.complex(
          self.tf.random.normal(shape=shape, dtype=dtype.real_dtype),
          self.tf.random.normal(shape=shape, dtype=dtype.real_dtype))
    return self.tf.random.normal(shape=shape, dtype=dtype)

  def random_uniform(self,
                     shape: Tuple[int, ...],
                     boundaries: Optional[Tuple[float, float]] = (0.0, 1.0),
                     dtype: Optional[Type[np.number]] = None,
                     seed: Optional[int] = None) -> Tensor:
    if seed:
      self.tf.random.set_seed(seed)

    dtype = dtype if dtype is not None else self.tf.float64
    if (dtype is self.tf.complex128) or (dtype is self.tf.complex64):
      return self.tf.complex(
          self.tf.random.uniform(
              shape=shape,
              minval=boundaries[0],
              maxval=boundaries[1],
              dtype=dtype.real_dtype),
          self.tf.random.uniform(
              shape=shape,
              minval=boundaries[0],
              maxval=boundaries[1],
              dtype=dtype.real_dtype))
    self.tf.random.set_seed(10)
    a = self.tf.random.uniform(
        shape=shape, minval=boundaries[0], maxval=boundaries[1], dtype=dtype)
    return a

  def conj(self, tensor: Tensor) -> Tensor:
    return self.tf.math.conj(tensor)

  def eigh(self, matrix: Tensor) -> Tuple[Tensor, Tensor]:
    return self.tf.linalg.eigh(matrix)

  def eigs(self,
           A: Callable,
           initial_state: Optional[Tensor] = None,
           num_krylov_vecs: Optional[int] = 200,
           numeig: Optional[int] = 1,
           tol: Optional[float] = 1E-8,
           which: Optional[Text] = 'LR',
           maxiter: Optional[int] = None,
           dtype: Optional[Type] = None) -> Tuple[List, List]:
    raise NotImplementedError("Backend '{}' has not implemented eigs.".format(
        self.name))

  def eigsh_lanczos(
      self,
      A: Callable,
      initial_state: Optional[Tensor] = None,
      num_krylov_vecs: Optional[int] = 200,
      numeig: Optional[int] = 1,
      tol: Optional[float] = 1E-8,
      delta: Optional[float] = 1E-8,
      ndiag: Optional[int] = 20,
      reorthogonalize: Optional[bool] = False) -> Tuple[List, List]:
    raise NotImplementedError(
        "Backend '{}' has not implemented eighs_lanczos.".format(self.name))

  def addition(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
    return tensor1 + tensor2

  def subtraction(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
    return tensor1 - tensor2

  def multiply(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
    return tensor1 * tensor2

  def divide(self, tensor1: Tensor, tensor2: Tensor) -> Tensor:
    return tensor1 / tensor2

  def index_update(self, tensor: Tensor, mask: Tensor,
                   assignee: Tensor) -> Tensor:
    #returns a copy (unfortunately)
    return self.tf.where(mask, assignee, tensor)

  def inv(self, matrix: Tensor) -> Tensor:
    if len(matrix.shape) > 2:
      raise ValueError("input to tensorflow backend method `inv` has shape {}. "
                       "Only matrices are supported.".format(
                           self.tf.shape(matrix)))
    return self.tf.linalg.inv(matrix)

  def broadcast_right_multiplication(self, tensor1: Tensor, tensor2: Tensor):
    if len(tensor2.shape) != 1:
      raise ValueError("only order-1 tensors are allowed for `tensor2`, "
                       "found `tensor2.shape = {}`".format(
                           self.tf.shape(tensor2)))

    return tensor1 * tensor2

  def broadcast_left_multiplication(self, tensor1: Tensor, tensor2: Tensor):
    if len(tensor1.shape) != 1:
      raise ValueError("only order-1 tensors are allowed for `tensor1`,"
                       " found `tensor1.shape = {}`".format(
                           self.tf.shape(tensor1)))

    t1_broadcast_shape = self.shape_concat(
        [self.shape_tensor(tensor1), [1] * (len(tensor2.shape) - 1)],
        axis=-1)
    return tensor2 * self.reshape(tensor1, t1_broadcast_shape)

  def sin(self, tensor: Tensor):
    return self.tf.math.sin(tensor)

  def cos(self, tensor: Tensor):
    return self.tf.math.cos(tensor)

  def exp(self, tensor: Tensor):
    return self.tf.math.exp(tensor)

  def log(self, tensor: Tensor):
    return self.tf.math.log(tensor)

  def expm(self, matrix: Tensor):
    if len(matrix.shape) != 2:
      raise ValueError("input to tensorflow backend method `expm` has shape {}."
                       " Only matrices are supported.".format(matrix.shape))
    if matrix.shape[0] != matrix.shape[1]:
      raise ValueError("input to tensorflow backend method `expm` only supports"
                       "N*N matrix, {x}*{y} matrix is given"
                       .format(x=matrix.shape[0], y=matrix.shape[1]))
    return self.tf.linalg.expm(matrix)
