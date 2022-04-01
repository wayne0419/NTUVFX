from PIL import Image
import piexif
import cv2
import numpy as np

hdr_path = "hdr.hdr"

hdr = cv2.imread(hdr_path, flags=cv2.IMREAD_ANYDEPTH)
tonemap1 = cv2.createTonemap(gamma=2.2)
res_debevec = tonemap1.process(hdr.copy())
res_debevec_8bit = np.clip(res_debevec*255, 0, 255).astype('uint8')
cv2.imwrite("test2.png", res_debevec_8bit)




 
