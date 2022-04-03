import numpy as np

a = np.array([[1],[2]])
b = np.array([[3],[4]])
c = np.concatenate((a,b), 1)
print(c)
a[0,:][0] = 5
print(c)