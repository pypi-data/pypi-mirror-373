from nillanet.io import IO
from nillanet.model import NN
from nillanet.activations import Activations
from nillanet.loss import Loss
from nillanet.distributions import Distributions

d = Distributions()
x,y = d.linear_distribution(10)
print(x.shape)
print(y.shape)
print(x)
print(y)

a = Activations()
activation = a.sigmoid
derivative1 = a.sigmoid_derivative
resolver = a.linear
derivative2 = a.linear_derivative

l = Loss()
loss = l.mse
derivative3 = l.mse_derivative

input = x
output = y
architecture = [2,4,1]
learning_rate = 0.1

model = NN(input,output,architecture,activation,derivative1,resolver,derivative2,loss,derivative3,learning_rate)
model.train(1000,0)
prediction = model.predict(x)

io = IO()
io.save(model,"linearmodel.pkl")

model = io.load_("linearmodel.pkl")
prediction = model.predict(x)

print("prediction")
print(prediction)
print("expected")
print(y)
