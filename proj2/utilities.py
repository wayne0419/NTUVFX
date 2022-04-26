import math
from re import L, X
from struct import Struct
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
from scipy.ndimage import filters

def zero_aounrd_center(image, center_coord, radius):
	image = np.copy(image)
	height = image.shape[0]
	width = image.shape[1]
	cx = center_coord[1]
	cy = center_coord[0]
	L = max(cx - radius + 1, 0)
	R = min(cx + radius, width)
	U = max(cy - radius + 1, 0)
	D = min(cy + radius, height)
	image[U:D, L:R] = 0
	return image

def get_around_center(image, center_coord, radius):
	image = np.copy(image)
	height = image.shape[0]
	width = image.shape[1]
	cx = center_coord[1]
	cy = center_coord[0]
	L = max(cx - radius, 0)
	R = min(cx + radius, width)
	U = max(cy - radius, 0)
	D = min(cy + radius, height)
	patch = np.copy(image[U:D, L:R])
	return patch