from nn.model import NN
from nn.tools import Tools
from tests.distributions import Distributions

distribution = Distributions()
x,y = distribution.tally(10,3,mode="one_hot")
print(x.shape)
print(y.shape)
print(x)
print(y)

tools = Tools()
input = x
output = y
architecture = [2,4,4]
activation = tools.sigmoid
derivative1 = tools.sigmoid_derivative
classifier = tools.sigmoid
derivative2 = tools.sigmoid_derivative
loss = tools.mse
derivative3 = tools.mse_derivative
learning_rate = 0.1

model = NN(input,output,architecture,activation,derivative1,classifier,derivative2,loss,derivative3,learning_rate)
model.train(10000,0)
prediction = model.predict(x)

print("prediction")
print(prediction)
print("expected")
print(y)
