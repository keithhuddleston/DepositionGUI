import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt('05152020Dep02.txt', unpack=True)

time = data[0]
time2 = [i-time[0] for i in time]
current = data[1]
wave = data[3]
sk = current/(6*10**-7)
QE = 1240/350*sk*100

plt.plot(time2[-900:], current[-900:])
plt.grid()