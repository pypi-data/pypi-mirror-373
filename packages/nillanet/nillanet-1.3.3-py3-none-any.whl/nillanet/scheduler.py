import math

class Scheduler:

    """Learning rate scheduler for NN class"""

    def __init__(self, mode, lr, lowbound=1e-8, scaler=0, warmup=0, interval=1, maxsteps=0, custom=None):

        """Read parameters for initializing the scheduler.

        Args:
            mode (str): the mode of learning rate decay
                required
            lr (float): the initial learning rate
                required
            lowbound (float): the lower bound for the learning rate
                default: 1e-8
            scaler (float): the scaling factor for the constant mode
                range: { x | 0 < x < 1 }
                optional, set zero to skip
            warmup (int): the number of epochs for an optional warmup period
                optional, set zero to skip
            interval (int): the interval at which a step is applied
                default: 1
            maxsteps (int): the maximum number of updates applied to the learning rate
                optional, set zero to skip
            custom (function): a custom function for updating the learning rate
                optional, set None to skip

        Attributes:
            sigma (float): the current learning rate
            steps (int): the number of updates applied so far
        """

        self.mode = mode
        if self.mode not in ['inverse', 'linear', 'cosine', 'constant', 'custom']:
            raise ValueError(f"unknown mode {self.mode}")

        # remains constant throughout training
        self.lr = lr
        # varies as training progresses
        self.sigma = self.lr
        # lowbound for lr
        self.lowbound = lowbound

        # scaling factor for constant mode e.g. 0.90
        self.scaler = scaler

        # units: epochs, defines a warmup period of reduced lr, set zero to skip
        self.warmup = warmup
        # units: epochs, interval at which a step is applied
        self.interval = interval

        # progress count with coarser granularity than epochs
        self.steps = 0
        # units: steps
        self.maxsteps = maxsteps

        # optional custom function for updating lr
        # must set mode = 'custom'
        self.custom = custom

    def step(self, epoch, epochs):
        """Update the learning rate based on the current epoch and mode.

        Args:
            epoch (int): the current epoch
            epochs (int): the total number of epochs

        Returns:
            sigma (float): the updated learning rate
        """

        if self.warmup > 0 and epoch <= self.warmup:
            epoch = epoch + 1
            self.sigma = self.lr * (epoch / self.warmup)
            return self.sigma
        elif epoch % self.interval != 0:
            return self.sigma
        elif self.maxsteps > 0 and self.steps > self.maxsteps:
            return self.sigma

        self.steps += 1

        if self.mode == 'inverse':
            self.sigma = self.inverse(epoch, epochs)
        elif self.mode == 'linear':
            self.sigma = self.linear(epoch, epochs)
        elif self.mode == 'cosine':
            self.sigma = self.cosine(epoch, epochs)
        elif self.mode == 'constant':
            if self.scaler <= 0 or self.scaler >= 1:
                raise ValueError("scaler must be between zero and one")
            self.sigma = self.constant(epoch, epochs)
        elif self.mode == 'custom':
            if self.custom is None:
                raise ValueError("custom function must be provided")
            self.sigma = self.custom(epoch, epochs)

        return max(self.sigma, self.lowbound)

    def inverse(self, epoch, epochs):
        """varies sigma as the inverse square of the number of steps taken"""
        self.sigma *= (self.steps ** -0.5)
        return self.sigma

    def linear(self, epoch, epochs):
        """varies sigma linearly as the number of remaining epochs"""
        self.sigma *= (1 - epoch / epochs)
        return self.sigma

    def cosine(self, epoch, epochs):
        """varies sigma trigonometrically from lr to lowbound"""
        self.sigma = self.lowbound + (abs(self.lr - self.lowbound) / 2) * (1 + math.cos(math.pi * epoch / epochs))
        return self.sigma

    def constant(self, epoch, epochs):
        """varies sigma by a constant factor of scaler which ranges from 0 to 1"""
        self.sigma *= self.scaler
        return self.sigma
