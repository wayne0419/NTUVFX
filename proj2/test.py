import numpy as np
import msop
import math
import cv2
import utilities
a = np.array(range(25))
a = np.reshape(a, (5,5))
print(a)

# rmat = cv2.getRotationMatrix2D((3,2), -90, scale=1)
# rimg = cv2.warpAffine(np.uint8(a), rmat, (a.shape[1], a.shape[0]))
# print(rimg)

b = utilities.get_around_center(a, (1,2), 1)
print(b.shape)
print(b)

