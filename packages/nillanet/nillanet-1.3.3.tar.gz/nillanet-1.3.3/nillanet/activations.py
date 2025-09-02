import cupy as cp
import math

class Activations(object):

  """Nonlinearities for NN class."""

  def __init__(self):
    pass

  def sigmoid(self,x):
      """
      Computes the sigmoid function for the given input.

      :param x: The values for which the sigmoid function needs to be computed.
      :type x: tensor
      :return: The computed sigmoid values corresponding to the input x.
      :rtype: tensor
      """
      return 1 / (1 + cp.exp(-x))

  def sigmoid_derivative(self,x):
      """
      Computes the derivative of the sigmoid function for the given input.

      :param x: The values for which the derivative of the sigmoid function needs to be computed.
      :type x: tensor
      :return: The computed derivative values corresponding to the input x.
      :rtype: tensor
      """
      return self.sigmoid(x) * (1 - self.sigmoid(x))

  def tanh(self,x):
      """
      Computes the hyperbolic tangent function for the given input.

      :param x: The values for which the hyperbolic tangent function needs to be computed.
      :type x: tensor
      :return: The computed hyperbolic tangent values corresponding to the input x.
      :rtype: tensor
      """
      return (1 - cp.exp(-2 * x)) / (1 + cp.exp(-2 * x))

  def tanh_derivative(self,x):
      """
      Computes the derivative of the hyperbolic tangent function for the given input.

      :param x: The values for which the derivative of the hyperbolic tangent function needs to be computed.
      :type x: tensor
      :return: The computed derivative values corresponding to the input x.
      :rtype: tensor
      """
      return 1 - (self.tanh(x) ** 2)

  def linear(self,x):
      """
      Computes the identity function for the given input.

      :param x: The values for which the identity function needs to be computed.
      :type x: tensor
      :return: The values corresponding to the input x.
      :rtype: tensor
      """
      return x

  def linear_derivative(self,x):
      """
      Computes the derivative of the identity function for the given input.

      :param x: The values for which the derivative of the identity function needs to be computed.
      :type x: tensor
      :return: The derivative values corresponding to the input x.
      :rtype: tensor
      """
      if isinstance(x,cp.ndarray) or isinstance(x,list):
        return cp.atleast_2d(cp.ones(x.shape)).astype(cp.float64)
      return 1

  def relu(self,x):
      """
      Computes the rectified linear unit (ReLU) function for the given input.

      :param x: The values for which the ReLU function needs to be computed.
      :type x: tensor
      :return: The ReLU values corresponding to the input x.
      :rtype: tensor
      """
      return cp.maximum(0,x)

  def relu_derivative(self,x):
      """
      Computes the derivative of the rectified linear unit (ReLU) function for the given input.

      :param x: The values for which the derivative of the ReLU function needs to be computed.
      :type x: tensor
      :return: The derivative ReLU values corresponding to the input x.
      :rtype: tensor
      """
      a = cp.asarray(x)
      a[a > 0] = 1
      a[a < 0] = 0
      return a

  def softmax(self,x):
      """
      Computes the softmax function for the given input.

      :param x: The input values for which the softmax function needs to be computed.
      :type x: tensor
      :return: The computed softmax values corresponding to the input x.
      :rtype: tensor
      """
      a = cp.exp(x)
      sums = cp.sum(a, axis=1)
      sums = sums.reshape(sums.shape[0],1)
      a /= sums
      return a