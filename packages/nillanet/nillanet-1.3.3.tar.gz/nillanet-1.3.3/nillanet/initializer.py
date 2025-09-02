from scipy import stats
import sys

class Initializer(object):

    """Weight distributions for custom initializations."""

    def __init__(self, distribution=None, low=0.0, high=1.0, mean=0.0, std=1.0):
        """Models a configurable statistical distribution for initializing weights.

        Args:
            distribution (function): A function representing the desired
                distribution. If None, a default normal distribution will be used.
            low (float):
                normal distribution:
                    the lower boundary for standard deviations away from the mean
                otherwise:
                    the lower boundary of the abscissae of the distribution
                Defaults to 0.0.
            high (float):
                normal distribution:
                    the upper boundary for standard deviations away from the mean
                otherwise:
                    the upper boundary of the abscissae of the distribution
                Defaults to 1.0.
            mean (float): The mean value for the distribution. Defaults to 0.0.
            std (float): The standard deviation for the distribution. Defaults to 1.0.
        """
        self.distribution = distribution
        if distribution is None:
            self.distribution = self.normal
        self.low = low
        self.high = high
        self.mean = mean
        self.std = std

    def __call__(self, shape):
        return self.distribution(self, shape)

    def normal(self, shape):
        """Generates random numbers from a bell-shaped distribution within the defined range.

        Note that the `low` and `high` parameters are interpreted as standard deviations away from the mean.

        Args:
            shape (tuple): The desired shape of the output array containing samples.

        Returns:
            numpy.ndarray
                An array of random samples drawn from the truncated normal distribution.
        """
        return stats.truncnorm.rvs(self.low, self.high, loc=self.mean, scale=self.std, size=shape)

    def uniform(self, shape):
        """Generates random numbers from a plateau-shaped distribution within the defined range.

        The `low` and `high` parameters are interpreted as the lower and upper bounds of the plateau.

        Args:
            shape (tuple): The desired shape of the output array containing samples.

        Returns:
            numpy.ndarray
                An array of random samples drawn from the uniform distribution.
        """
        return stats.uniform.rvs(loc=self.low, scale=self.high-self.low, size=shape)

    def xavier(self, shape):
        """Generates random numbers with variance equal to 1 over the square of n.

        `Xavier` demonstrated its usefulness for tanh or sigmoid activation functions.
        The `low` and `high` parameters are interpreted as the lower and upper bounds of the plateau.

        Args:
            shape (tuple): The desired shape of the output array containing samples.

        Returns:
            numpy.ndarray
                An array of random samples drawn from the truncated normal distribution.
        """
        return stats.truncnorm.rvs(self.low, self.high, scale=1.0/shape[0]**0.5, size=shape)

    def he(self, shape):
        """Generates random numbers with variance equal to 2 over the square of n.

        `He` demonstrated its usefulness for the relu activation function.
        The `low` and `high` parameters are interpreted as the lower and upper bounds of the plateau.

        Args:
            shape (tuple): The desired shape of the output array containing samples.

        Returns:
            numpy.ndarray
                An array of random samples drawn from the truncated normal distribution.
        """
        return stats.truncnorm.rvs(self.low, self.high, scale=2.0/shape[0]**0.5, size=shape)

if __name__ == '__main__':
    shape = (3, 3)
    low,high,mean,std = (
        0.0, 1.0, 0.0, 1.0
    )
    if len(sys.argv) >= 3:
        low = float(sys.argv[1])
        high = float(sys.argv[2])
    if len(sys.argv) >= 5:
        mean = float(sys.argv[3])
        std = float(sys.argv[4])
    print("shape %s low %s high %s mean %s std %s" % (shape, low, high, mean, std))
    print("normal")
    intl = Initializer(distribution=Initializer.normal, low=low, high=high, mean=mean, std=std)
    print(intl.normal(shape))
    print("uniform")
    intl = Initializer(distribution=Initializer.uniform, low=low, high=high, mean=mean, std=std)
    print(intl.uniform(shape))
    print("xavier")
    intl = Initializer(distribution=Initializer.xavier, low=low, high=high, mean=mean, std=std)
    print(intl.xavier(shape))
    print("he")
    intl = Initializer(distribution=Initializer.he, low=low, high=high, mean=mean, std=std)
    print(intl.he(shape))
