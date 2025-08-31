import cupy as cp
import numpy as np
import os
import math
import random
import re
import sys

cp.random.seed()
cp.set_printoptions(precision=2,floatmode='fixed',suppress=True)

class Distributions(object):

  """Random training distributions for test modules."""

  def __init__(self):
    pass

  def linear_distribution(self, depth):
    """linear regression that predicts y from x for x-values on a random line with slope and intercept

        Args:
          depth (int):
              The number of x-values to generate.

        Returns:
          tuple of (generated vector of x-values, vector of expected y-values)
    """
    # random input values
    x = cp.random.random((depth,1)).astype(cp.float32)
    # target weight, bias
    z = cp.random.random((2,1)).astype(cp.float32)
    # y = wx + b
    y = [ z[0] * x[j] + z[1] for j in range(0,len(x)) ]
    y = cp.array(y).astype(cp.float32)
    return x,y

  def logical_distribution(self, depth, mode):
    """boolean logic

        Args:
          depth (int):
              The number of rows for the generated two-column binary matrix.
          mode (str):
              Accepts "and", "or", "xor", or "xnor".

        Returns:
          tuple of (generated binary matrix, expected output)
    """
    x = cp.round(cp.random.random((depth,2))).astype(cp.float32)
    y = cp.zeros([depth,1]).astype(cp.float32).flatten()
    if mode=="and":
      y = cp.array([x[j,0] * x[j,1] for j in range(0,len(x))])
    elif mode=="or":
      y = cp.array( [ cp.max(x[j]) for j in range(0,len(x)) ] )
    elif mode=="xor":
      y = cp.array([abs(x[j,0] - x[j,1]) for j in range(0,len(x))])
    elif mode=="xnor":
      y = cp.array([1 if x[j,0]==x[j,1] else 0 for j in range(0,len(x))])
    else:
      return None,None
    return x,y

  def arithmetic_distribution(self, depth, mode):
    """predict arithmetic result from distributions of two input values

        Args:
          depth (int):
              The number of rows for the generated matrix of floating point numbers.
          mode (str):
              The mode of operation. Accepts either "add", "subtract", "multiply", "divide", or "zero" (always predict 0).

        Returns:
          tuple of (generated matrix, expected output)

        Raises:
          SystemExit
              If the provided `mode` is not "summation" or "one_hot".
    """
    x = cp.random.random((depth,2)).astype(cp.float32)
    y = cp.zeros([depth,1]).astype(cp.float32)
    if mode=="add":
      y = cp.array([x[j,0] + x[j,1] for j in range(0,len(x))]) # weights = 1
    elif mode=="subtract":
      y = cp.array([x[j,0] - x[j,1] for j in range(0,len(x))]) # w1 = 1, w2 = -1
    elif mode=="multiply":
      y = cp.array([x[j,0] * x[j,1] for j in range(0,len(x))])
    elif mode=="divide":
      y = cp.array([x[j,0] / x[j,1] for j in range(0,len(x))])
    elif mode=="zero": # weights = 0
      y = y.flatten()
    else:
      return None,None
    return x,y

  def summation(self, rows, cols, mode="one_hot"):
    """distributions of binary vectors for testing binary cross entropy (one-hot mode only)

        Args:
          rows (int):
              The number of rows for the generated binary matrix.
          cols (int):
              The number of columns for the generated binary matrix.
          mode (str):
              The mode of operation. Accepts either "summation" or "one_hot".
              - "summation": Produces a scalar count of the number of ones in each x vector.
              - "one_hot": Produces a one-hot encoded representation of the count of ones in each x vector.
              Defaults to "one_hot".

        Returns:
          tuple of (generated binary matrix, expected output)

        Raises:
          SystemExit if the provided `mode` is not "summation" or "one_hot".
    """
    x = cp.array([random.randrange(2) for i in range(rows * cols)]).reshape(rows,cols)
    if mode=="summation":
      # y = a scalar for the number of ones in each x vector
      y = cp.array([[cp.sum(x[i])] for i in range(0,len(x))])
    elif mode=="one_hot":
      # y = one hot vector with a 1 in the place of the number of ones in x vector
      y = cp.array([[0] * (cols + 1) for i in range(rows)])
      for i in range(rows):
        y[i,cp.sum(x[i])] = 1
    else:
      sys.exit("mode must be summation or one_hot")
    return x,y

  def sort(self, rows, cols):
    """numerical sort

        Args:
          rows (int):
            the number of rows for the generated matrix
          cols (int):
            the number of columns for the generated matrix

        Returns:
          tuple of (generated matrix, sorted matrix)
    """
    x = cp.random.random((rows,cols))
    y = cp.array([sorted(x[i]) for i in range(0,len(x))])
    return x,y
