from nillanet.model import NN
from nillanet.activations import Activations
from nillanet.loss import Loss
from nillanet.distributions import Distributions

d = Distributions()
x,y = d.sort(10,5)
print(x.shape)
print(y.shape)

a = Activations()
activation = a.sigmoid
derivative1 = a.sigmoid_derivative
resolver = a.linear
derivative2 = a.linear_derivative

l = Loss()
loss = l.mae
derivative3 = l.mae_derivative

input = x
output = y
features = x.shape[1]
architecture = [32,16,8,5]
learning_rate = 0.01
epochs = 10000

model = NN(features,architecture,activation,derivative1,resolver,derivative2,loss,derivative3,learning_rate)
model.train(input,output,epochs,verbose=True,step=1000,autosave=True)
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