import numpy as np
# import msop
import math
import cv2
import utilities
a = np.array(range(24))
a = np.reshape(a, (12,2))
print(a)

# rmat = cv2.getRotationMatrix2D((3,2), -90, scale=1)
# rimg = cv2.warpAffine(np.uint8(a), rmat, (a.shape[1], a.shape[0]))
# print(rimg)

# b = utilities.get_around_center(a, (1,2), 1)
# print(b.shape)
# print(b)

# c = np.array(range(9))
# c = np.reshape(c, (3,3))
# print(c)
# b = np.copy(a)
# b[2:5, 2:5] = c
# print(b)
# c[2,2] = 999
# print(b)
# print(c)

b = np.abs(a-10)
print(b)
c = b < 5
print(c)
d = (c[:,0] & c[:,1])
print(d)
print(np.sum(d))

