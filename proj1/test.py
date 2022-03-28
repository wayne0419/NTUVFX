import cv2
import numpy as np
import utilities

img = cv2.imread("Images\Memorial_SourceImages\memorial0064.png")  # BGR
 
print(type(img))
print(img.shape)

utilities.show_image(img)



 
