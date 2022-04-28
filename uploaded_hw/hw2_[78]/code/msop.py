import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
import utilities
from matplotlib.patches import Rectangle

def read_focal_length(filename):
	file = open(filename, "r")
	f = []
	lines = file.readlines()
	file.close()
	for line in lines:
		f.append(float(line))
	return f

def build_img_pyramid(image, depth = 4):
	img_pyramid = []
	grayimg_pyramid = []
	image = np.copy(image)
	print("Building img_pyramid, grayimg_pyramid.....")
	for i in tqdm(range(depth)):
		img_pyramid.append(image)
		grayimg_pyramid.append(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) )
		image = cv2.pyrDown(image)
	return img_pyramid, grayimg_pyramid

def get_harris_response_pyramid(grayimg_pyramid, sigma=1.5):
	depth = len(grayimg_pyramid)
	harris_response_pyramid = []
	print("Building harris_response_pyramid.....")
	for d in tqdm(range(depth)):
		image = grayimg_pyramid[d]
		g_image = cv2.GaussianBlur(image, ksize=(0,0), sigmaX=sigma, sigmaY=sigma)	#TODO may use sigma = 1.0
		Ix = np.gradient(g_image, axis=1)
		Iy = np.gradient(g_image, axis=0)
		Ixx = Ix * Ix
		Iyy = Iy * Iy
		Ixy = Ix * Iy
		Sxx = cv2.GaussianBlur(Ixx, ksize=(0,0), sigmaX=sigma, sigmaY=sigma)
		Syy = cv2.GaussianBlur(Iyy, ksize=(0,0), sigmaX=sigma, sigmaY=sigma)
		Sxy = cv2.GaussianBlur(Ixy, ksize=(0,0), sigmaX=sigma, sigmaY=sigma)
		Mdet = Sxx * Syy - Sxy ** 2
		Mtr = Sxx + Syy
		R = Mdet/(Mtr+1e-8)
		harris_response_pyramid.append(R)
	
	return harris_response_pyramid

def cylindrical_projection(image, focal_length):
	width = image.shape[1]
	height = image.shape[0]
	origin = (height//2, width//2)
	projected_img = np.zeros(image.shape)
	for yp in range(height):
		for xp in range(width):
			x = int(math.atan2((xp-origin[1]), focal_length) * focal_length + origin[1])
			y = int((yp-origin[0])/focal_length * math.sqrt((x-origin[1])**2 + focal_length**2) + origin[0])
			if x < 0 or x >= width or y < 0 or y >= height:
				continue
			projected_img[yp, xp] = np.copy(image[y, x])
	return projected_img

def build_projected_pyramid(image_pyramid, focal_length):
	depth = len(image_pyramid)
	proj_image_pyramid = []
	print("Building projected_pyramid.....")
	for i in tqdm(range(depth)):
		image = image_pyramid[i]
		proj_image = cylindrical_projection(image, focal_length)
		proj_image_pyramid.append(proj_image)
	return proj_image_pyramid

class point2D():
	def __init__(self, value=0, x=-1, y=-1):
		self.x = x
		self.y = y
		self.value = value



def pick_feature_points(harris_response, n_features):
	# Pick features using non-maximal suppression method
	max_radius = harris_response.shape[0] // 10
	response = np.copy(harris_response)
	threshold = response.max() * 0.03	#TODO: may try *0.05
	features = []
	for r in range(max_radius, 0, -1):
		response = np.copy(harris_response)
		feature_points= []
		while len(feature_points) < n_features:
			cand_coord = np.unravel_index(np.argmax(response, axis=None), response.shape)
			x = cand_coord[1]
			y = cand_coord[0]
			value = response[y][x]
			if value < threshold:
				break
			feature_points.append(point2D(response[y][x], x=x, y=y))
			response = utilities.zero_aounrd_center(response, cand_coord, r)
		
		if len(feature_points) >= n_features:
			return feature_points
	# if not enough feature points pass the threshold, return what we got
	return feature_points


def build_feature_points_pyramid(harris_response_pyramid , n_features):
	depth = len(harris_response_pyramid)
	feature_points_pyramid = []
	print("Building feature_points_pyramid.....")
	for i in tqdm(range(depth)):
		response = np.copy(harris_response_pyramid[i])
		feature_points = pick_feature_points(response, n_features//(1**i)) # TODO: decide if higher pyramid levels get lower feature points
		feature_points_pyramid.append(feature_points)
	return feature_points_pyramid

class description():
	def __init__(self, point, orientation, des_patch):
		self.point = point
		self.orientation = orientation
		self.des_patch = des_patch

def build_descriptions(fpts, proj_grayimg):
	image = np.copy(proj_grayimg)
	blurred_image = cv2.GaussianBlur(image, (0,0), sigmaX=4.5, sigmaY=4.5)
	gx = np.gradient(blurred_image, axis=1)
	gy = np.gradient(blurred_image, axis=0)
	angles = np.degrees(-np.arctan(gy/(gx + 1e-8)))
	descriptions = []
	for fpt in fpts:
		center = (int(fpt.x), int(fpt.y))
		angle = angles[fpt.y][fpt.x]
		rmat = cv2.getRotationMatrix2D(center, -angle, scale=1)
		rotated_image = cv2.warpAffine(image, rmat, (image.shape[1], image.shape[0]))
		# get 40*40 patch around the fpt
		patch = utilities.get_around_center(rotated_image, (int(fpt.y), int(fpt.x)), int(40/2))
		if patch.shape[0] < 40 or patch.shape[1] < 40:	#TODO: may need this
			# ignore fpt that dont have complete patch
			continue
		blurred_patch = cv2.GaussianBlur(patch, (0,0), sigmaX=1, sigmaY=1)
		resized_patch = cv2.resize(blurred_patch, (8, 8))
		normalized_patch = (resized_patch-np.mean(resized_patch))/(np.std(resized_patch) + 1e-8)
		descriptions.append(description(fpt, angle, normalized_patch))
	return descriptions

def build_descriptions_pyramid(fpts_pyramid, proj_grayimg_pyramid):
	depth = len(fpts_pyramid)
	descriptions_pyramid = []
	print("Building descriptions_pyramid.....")
	for i in range(depth):
		fpts = fpts_pyramid[i]
		proj_grayimg = proj_grayimg_pyramid[i]
		descriptions = build_descriptions(fpts, proj_grayimg)
		descriptions_pyramid.append(descriptions)
	return descriptions_pyramid

def msop(images, focal_lengths, pyramid_depth=4):
	proj_img_pyramids = []
	description_pyramids = []
	for i in range(len(images)):
		image = np.copy(images[i])
		focal_length = focal_lengths[i]

		img_pyramid, grayimg_pyramid = build_img_pyramid(image, depth=pyramid_depth)

		harris_response_pyramid = get_harris_response_pyramid(grayimg_pyramid, sigma=1.5)


		proj_img_pyramid = build_projected_pyramid(img_pyramid, focal_length)
		proj_grayimg_pyramid = build_projected_pyramid(grayimg_pyramid, focal_length)
		proj_harris_response_pyramid = build_projected_pyramid(harris_response_pyramid, focal_length)


		fpts_pyramid = build_feature_points_pyramid(proj_harris_response_pyramid , 150)	#TODO: may try n_features=300


		descriptions_pyramid = build_descriptions_pyramid(fpts_pyramid, proj_grayimg_pyramid)

		proj_img_pyramids.append(proj_img_pyramid)
		description_pyramids.append(descriptions_pyramid)
	
	return proj_img_pyramids, description_pyramids


