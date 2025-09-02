import cupy as cp
import pickle

class IO(object):

  """Helper functions for NN class."""

  def __init__(self):
    pass

  def save(self, model, filename):
    """Serialize the model to disk using pickle.

       Args:
           filename: Path to the output pickle file.
    """

    with open(filename, "wb") as fh:
      pickle.dump(model, fh)

  def load(self,filename):
    """Read serialized file
    
    Args:
        filename: Path to the model pickle file.
    """
    with open(filename, "rb") as r:
      model = pickle.load(r)
    return model

