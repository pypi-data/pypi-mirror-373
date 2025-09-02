from scipy import stats

class Initializer(object):
    """Base class for weight initializers."""
    def __init__(self):
        pass

    def normal(self, shape, mean=0.0, std=1.0):
        return stats.truncnorm.rvs(-2, 2, loc=mean, scale=std, size=shape)

    def uniform(self, shape, low=0.0, high=1.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape)

    def xavier(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def he(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=2.0/shape[0]**0.5, size=shape)

    def lecun(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def bengio(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def glorot(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def he_uniform(self, shape):
        return stats.uniform.rvs(scale=6.0/shape[0]**0.5, size=shape)

    def lecun_uniform(self, shape):
        return stats.uniform.rvs(scale=1.0/shape[0]**0.5, size=shape)

    def bengio_uniform(self, shape):
        return stats.uniform.rvs(scale=1.0/shape[0]**0.5, size=shape)

    def glorot_uniform(self, shape):
        return stats.uniform.rvs(scale=1.0/shape[0]**0.5, size=shape)

    def he_normal(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=2.0/shape[0]**0.5, size=shape)

    def lecun_normal(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def bengio_normal(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def glorot_normal(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0/shape[0]**0.5, size=shape)

    def identity(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0, size=shape)

    def zero(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=0.0, size=shape)

    def one(self, shape):
        return stats.truncnorm.rvs(-2, 2, scale=1.0, size=shape)

    def constant(self, shape, value=0.0):
        return stats.truncnorm.rvs(-2, 2, scale=value, size=shape)

    def random(self, shape):
        return stats.truncnorm.rvs(-2, 2, size=shape)

    def uniform_random(self, shape, low=0.0, high=1.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape)

    def normal_random(self, shape, mean=0.0, std=1.0):
        return stats.truncnorm.rvs(-2, 2, loc=mean, scale=std, size=shape)

    def constant_random(self, shape, value=0.0):
        return stats.truncnorm.rvs(-2, 2, scale=value, size=shape)

    def random_random(self, shape):
        return stats.truncnorm.rvs(-2, 2, size=shape)

    def truncated_normal(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape)

    def truncated_uniform(self, shape, low=-1.0, high=1.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape)

    def truncated_normal_random(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape)

    def truncated_uniform_random(self, shape, low=-1.0, high=1.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape)

    def truncated_normal_constant(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0, value=0.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape) + value

    def truncated_uniform_constant(self, shape, low=-1.0, high=1.0, value=0.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape) + value

    def truncated_normal_random_constant(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0, value=0.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape) + value

    def truncated_uniform_random_constant(self, shape, low=-1.0, high=1.0, value=0.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape) + value

    def truncated_normal_constant_random(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0, value=0.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape) + value

    def truncated_uniform_constant_random(self, shape, low=-1.0, high=1.0, value=0.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape) + value

    def truncated_normal_constant_random_constant(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0, value=0.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape) + value

    def truncated_uniform_constant_random_constant(self, shape, low=-1.0, high=1.0, value=0.0):
        return stats.uniform.rvs(loc=low, scale=high-low, size=shape) + value

    def truncated_normal_constant_random_constant_random(self, shape, mean=0.0, std=1.0, low=-2.0, high=2.0, value=0.0):
        return stats.truncnorm.rvs(low, high, loc=mean, scale=std, size=shape) + value
