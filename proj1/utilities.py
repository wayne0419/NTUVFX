import cv2
import numpy as np

def show_image(img):
	cv2.imshow('image', img)
	cv2.waitKey(0)       
	cv2.destroyAllWindows()

def show_multi_images(imgs):
	for i in range(len(imgs)):
		cv2.imshow(str(i), imgs[i])
	cv2.waitKey(0)       
	cv2.destroyAllWindows()