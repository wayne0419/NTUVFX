import cv2
import numpy as np

def show_image(img):
	cv2.imshow('image', img)
	cv2.waitKey(0)       
	cv2.destroyAllWindows()