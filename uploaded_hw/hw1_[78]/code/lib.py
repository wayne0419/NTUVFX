from cmath import inf
from random import random
import cv2
from PIL import Image
from PIL.ExifTags import TAGS
from cv2 import cvtColor
from cv2 import exp
import numpy as np
from scipy import rand
from torch import exp2
import utilities
import random
# np.set_printoptions(threshold=np.inf)  # test

class Photo:
	def __init__(self, img, dt, lu):
		self.img = img
		self.dt = dt
		self.luminosity = lu
		self.mask = self.get_mask()

	def get_mask(self):
		# Get the mask that indicate valid pixels as True, invalid pixels as False
		return ~np.all(self.img == np.array([255,0,0]), axis=2)

class Pixel:
	def __init__(self, i, j, lu):
		self.i = i
		self.j = j
		self.luminosity = lu

def weight(z):
	# Hat weighting function
	if z <= 127:
		return z - 0 + 1	# test
	else:
		return 255 - z + 1	# test

# Read photoes
def get_photo_metadata(file_name):
	metadata = {}
	# extracting the exif metadata
	image = Image.open(file_name)
	exifdata = image.getexif()
	
	# looping through all the tags present in exifdata
	for tagid in exifdata:
		# getting the tag name instead of tag id
		tagname = TAGS.get(tagid, tagid)
		# passing the tagid to get its respective value
		value = exifdata.get(tagid)
		# add the final result
		metadata[tagname] = value

	return metadata

def read_exposure_time(file_dir, file_num, exposure_filename, file_extension=".jpg"):
	exposure_time_list = []
	if exposure_filename == None:
		for i in range(file_num):
			file_name = file_dir + "/" + str(i) + file_extension
			metadata = get_photo_metadata(file_name)
			exposure_time_list.append(float(metadata["ExposureTime"]))
	else:
		exposure_file = open(exposure_filename,"r")
		lines = exposure_file.readlines()
		for line in lines:
			exposure_time = float(line.split(" ")[1].strip("\n"))
			exposure_time_list.append(exposure_time)
		exposure_file.close()
	return exposure_time_list


def read_photoes(file_dir, file_num, file_extension=".png", exposure_filename = None, scale=1, scale_method=cv2.INTER_LANCZOS4):
	photo_list = []

	# Read exposure time
	dt_list = read_exposure_time(file_dir, file_num, exposure_filename, file_extension)
	# Read image
	img_list = []
	for i in range(file_num):
		file_name = file_dir + "/" + str(i) + file_extension
		img = cv2.imread(file_name)
		# resize image
		width = int(img.shape[1] * scale / 1)
		height = int(img.shape[0] * scale / 1)
		dim = (width, height)
		img = cv2.resize(img, dim, interpolation = scale_method)

		img_list.append(img)

	# Combine image data and exposure-time data
	for i in range(len(img_list)):
		photo_list.append(Photo( img=img_list[i], 
								dt=dt_list[i], 
								lu=cvtColor(img_list[i], cv2.COLOR_BGR2XYZ)[:,:,1] ))

	return photo_list

# Pick pixels (around 25) for Debevec HDR recovery algorithm
def pick_pixels(photo_list, channel, number_picked_pixels = 25):
	photo = photo_list[0]
	img = photo.img[:,:,channel]
	width = img.shape[1]
	height = img.shape[0]
	pixel_list = []
	for i in range(height):
		for j in range(width):
			# Neglect this pixel if it is bluued in any one of the 16 phtoes
			blueed = False
			for p in photo_list:
				if not p.mask[i,j]:
					blueed = True
					break
			if not blueed:
				pixel_list.append(Pixel(i, j, img[i,j]))
			

	pixel_list.sort(key=lambda pixel : pixel.luminosity)
	picked_pixels = []
	# for i in range(number_picked_pixels):
	# 	picked_pixels.append( pixel_list[ int( (len(pixel_list)-1)*i/(number_picked_pixels-1) ) ] )
	# 	# picked_pixels.append( pixel_list[ random.randint(int(len(pixel_list)/2), len(pixel_list)) ] )		# test
	# 	# picked_pixels.append( pixel_list[ random.randint( 0, int(len(pixel_list)/2) ) ] )		# test
	picked_pixels = np.random.choice(pixel_list, number_picked_pixels)	# test
	return picked_pixels

def solve_debevec(photo_list, picked_pixels, channel, L = 20):
	# Build and solve least squared error of Ax = b
	# 	Build A and b
	# 		Build n*p part of A and b
	P = len(photo_list)
	N = len(picked_pixels)
	A_list = []
	b_list = []
	for i in range(N):
		for j in range(P):
			photo = photo_list[j]
			pixel = picked_pixels[i]
			z_ij = photo.img[pixel.i, pixel.j, channel]
			w = weight(z_ij)
			ln_dt = np.log(photo.dt)
			A_256 = np.zeros((1, 256), dtype=np.float)
			A_256[0, z_ij] = w
			A_N = np.zeros((1, N), dtype=np.float)
			A_N[0, i] = -w
			A = np.concatenate([A_256, A_N], axis=1)
			b = w * ln_dt
			A_list.append(A)
			b_list.append(b)


	# 		Add fixed g(127) = 0 into A, b
	A_g127 = np.zeros((1, 256+N), dtype=np.float)
	A_g127[0, 127] = 1
	b_g127 = 0
	A_list.append(A_g127)
	b_list.append(b_g127)

	# 		Build 254 part of A and b
	sqrt_L = L**(1/2)
	for z in range(255)[1:]:
		w = weight(z)
		A = np.zeros((1, 256+N), dtype=np.float)
		A[0,z-1] = sqrt_L * w
		A[0,z] = sqrt_L * w * (-2)
		A[0,z+1] = sqrt_L * w
		b = 0
		A_list.append(A)
		b_list.append(b)

	
	# 		Combine to get complete A, b
	A = np.concatenate(A_list, axis=0)
	b = np.array(b_list, dtype=np.float)

	# 	Solve least squared error of Ax = b
	x = np.linalg.lstsq(A, b, rcond = None)[0]
	g = x[0:256]

	return g

def merge_irradiance(photo_list, g, channel):
	# Use average irradiance among all photoes as our final irradiance
	irradiance_list = []
	w_list = []
	for photo in photo_list:
		img = photo.img[:,:,channel]
		width = img.shape[1]
		height = img.shape[0]
		ln_dt = np.log(photo.dt)
		irradiance = np.zeros(img.shape, dtype=np.float)
		w = np.zeros(img.shape, dtype=np.float)
		for i in range(height):
			for j in range(width):
				z = img[i,j]
				irradiance[i,j] = g[z] - ln_dt
				if photo.mask[i,j]:
					w[i,j] = weight(z)
				else:
					w[i,j] = 0
		irradiance_list.append(irradiance)
		w_list.append(w)


	irradiance_list = np.stack(irradiance_list, axis=2)
	w_list = np.stack(w_list, axis=2)
	irradiance = np.exp(np.average(irradiance_list, axis=2, weights=w_list)) # kkk

	return irradiance

def reinhard_global_tone_map(irradiance_b, irradiance_g, irradiance_r, a=0.5, sigma=0.0000001, L_white=inf, destination="."):
	img = np.float32(np.stack((irradiance_b, irradiance_g, irradiance_r), axis=2))
	L_w = cvtColor(img, cv2.COLOR_BGR2XYZ)[:,:,1]
	L_w_mean = np.exp(np.mean(np.log(sigma + L_w)))
	L_m = a / L_w_mean * L_w
	L_d = L_m*(1+L_m/(L_white**2)) / (L_m + 1)
	L_ratio = L_d / L_w
	img = img * np.stack((L_ratio, L_ratio, L_ratio), axis=2 )
	# utilities.show_image(img)
	cv2.imwrite(destination, img*255)


		



