from nillanet.model import NN
from nillanet.activations import Activations
from nillanet.loss import Loss
from nillanet.distributions import Distributions
from nillanet.initializer import Initializer

d = Distributions()
x,y = d.logical_distribution(10,"and")
print(x.shape)
print(y.shape)

a = Activations()
activation = a.relu
derivative1 = a.relu_derivative
resolver = a.sigmoid
derivative2 = a.sigmoid_derivative

l = Loss()
loss = l.mse
derivative3 = l.mse_derivative

input = x
output = y
features = x.shape[1]
architecture = [4,8,1]
learning_rate = 0.01
epochs = 1000
initializer = Initializer(distribution=Initializer.he, low=0, high=1, mean=0, std=0.5)

model = NN(features,architecture,activation,derivative1,resolver,derivative2,loss,derivative3,learning_rate,initializer=initializer)
model.train(input,output,epochs,verbose=True,step=100,autosave=True)
prediction = model.predict(x)

print("prediction")
print(prediction)
print("expected")
print(y)

from nillanet.io import IO
io = IO()
best = io.load(model.backup)
prediction = best.predict(x)
print("best")
print(prediction)