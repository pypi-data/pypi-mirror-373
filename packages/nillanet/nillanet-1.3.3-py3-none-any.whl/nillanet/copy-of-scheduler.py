import math
import scipy

class Scheduler:
    def __init__(self, lr, mode, interval=1, lowbound=1e-8, maxsteps=0, warmup=0):
        self.lr = lr
        self.delta = self.lr
        self.mode = mode
        self.interval = interval # epochs interval at which update applied
        self.lowbound = lowbound # lowbound for lr
        self.steps = 0
        self.maxsteps = maxsteps # units: steps
        self.warmup = warmup # units: epochs
    def step(self, epoch, epochs):
        if epoch % self.interval != 0:
            return self.delta
        self.steps += 1
        if self.maxsteps > 0 and self.steps > self.maxsteps:
            return self.delta
        if self.warmup > 0 and epoch < self.warmup:
            epoch = epoch + 1
            self.delta = self.lr * (epoch / self.warmup)
        if self.mode == 'inverse':
            self.delta = self.delta * (self.steps ** -0.05)
        elif self.mode == 'cosine':
            self.delta = self.lowbound + (abs(self.lr - self.lowbound) / 2) * (1 + math.cos(math.pi * epoch / epochs))
        elif self.mode == 'exponential':
            self.delta = self.delta * math.exp(-0.01 * epoch)
        elif self.mode == 'linear':
            self.delta = self.delta * (1 - epoch / epochs)
        elif self.mode == 'constant':
            self.delta = self.lr
        else:
            raise ValueError(f"mode {self.mode} not recognized")
        return max(self.delta, self.lowbound)
