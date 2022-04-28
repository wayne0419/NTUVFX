import numpy as np
import cv2
import matplotlib.pyplot as plt
import msop
from matplotlib.patches import Rectangle
import math
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

def get_paired_points(descriptionsA, descriptionsB, ratio_threshold = 0.7):
	# preapare data
	des_patchsA = []
	for description in descriptionsA:
		des_patch = description.des_patch.flatten()
		des_patchsA.append(des_patch)
	des_patchsA = np.array(des_patchsA)
	des_patchsB = []
	for description in descriptionsB:
		des_patch = description.des_patch.flatten()
		des_patchsB.append(des_patch)
	des_patchsB = np.array(des_patchsB)
	# return [] if either no decription in A or no description in B
	if len(des_patchsA.shape) == 1 or len(des_patchsB.shape) == 1:
		return []


	# do knn
	if des_patchsA.shape[0] < 2 and des_patchsB.shape[0] < 2:
		return []
	elif des_patchsA.shape[0] >= 2 and des_patchsB.shape[0] < 2:
		pool = des_patchsA
		samples = des_patchsB
	else:
		pool = des_patchsB
		samples = des_patchsA

	neigh = NearestNeighbors(n_neighbors=2).fit(pool)
	distances, indices = neigh.kneighbors(samples)
	paired_points = []
	for i in range(len(distances)):
		# for ith description in A, get 1st-closet, 2nd-closest descriptions in B
		dis = distances[i]
		index = indices[i]
		first_dis = dis[0]
		first_index = index[0]
		second_dis = dis[1]
		# ration_threshold test
		if first_dis / second_dis > ratio_threshold:
			continue
		else:
			pair = (descriptionsA[i].point, descriptionsB[first_index].point)
			paired_points.append(pair)
	return paired_points


def build_paired_points_pyramids(description_pyramids, ratio_threshold = 0.7):	
	# build paired_points_pyramids using knn
	paired_points_pyramids = []
	print("Building paired_points_pyramids.....")
	for i in tqdm(range(len(description_pyramids))[:-1]):
		# build paired_points_pyramid
		des_pyramidA = description_pyramids[i]
		des_pyramidB = description_pyramids[i+1]
		depth = len(des_pyramidA)
		paired_points_pyramid = []
		for j in range(depth):
			# build paired_points
			descriptionsA = des_pyramidA[j]
			descriptionsB = des_pyramidB[j]
			paired_points = get_paired_points(descriptionsA, descriptionsB, ratio_threshold = ratio_threshold)
			paired_points_pyramid.append(paired_points)
		paired_points_pyramids.append(paired_points_pyramid)
	return paired_points_pyramids

def compute_average_translation(coords_A, coords_B):
	translations = coords_A - coords_B
	average_translation = np.mean(translations, axis=0)
	my = int(average_translation[0])
	mx = int(average_translation[1])
	return my, mx

def get_B2A_translation(paired_points_pyramid):
	# use RANSAC to get B2A_translation (my,mx)

	# prepare data
	coords_A = []	# point (y,x) in image A, left
	coords_B = []	# point (y,x) in image B, right
	depth = len(paired_points_pyramid)
	for i in range(depth):
		paired_points = paired_points_pyramid[i]
		for pair in paired_points:
			pA = pair[0]
			pB = pair[1]
			coord_A = [pA.y * (2**i), pA.x * (2**i)]
			coord_B = [pB.y * (2**i), pB.x * (2**i)]
			coords_A.append(coord_A)
			coords_B.append(coord_B)
	coords_A = np.array(coords_A)
	coords_B = np.array(coords_B)

	# do RANSAC
	N_SAMPLES = 2
	K_TRIALS = 60
	DIS_THRESHOLD = 5
	maxvote = 0
	bestm = (0,0)	#(my,mx)
	N_PAIRS = len(coords_A)
	for i in range(K_TRIALS):
		samples_indices = np.random.choice(N_PAIRS, N_SAMPLES)
		samples_A = coords_A[samples_indices]
		samples_B = coords_B[samples_indices]
		my, mx = compute_average_translation(samples_A, samples_B)
		m_coords_B = coords_B + np.array([[my,mx]])
		difference = np.abs(coords_A - m_coords_B)
		close_enough = difference < DIS_THRESHOLD
		vote = np.sum(close_enough[:,0] & close_enough[:,1])
		
		if vote > maxvote:
			bestm = (my,mx)
	
	return bestm




def build_B2A_translations(paired_points_pyramids):
	# Do pair-wise-alignment to build B2A_translations, list of (my,mx), length = N_IMG-1
	B2A_translations = []
	for i in range(len(paired_points_pyramids)):
		paired_points_pyramid = paired_points_pyramids[i]
		# get_B2A_translation
		B2A_translation = get_B2A_translation(paired_points_pyramid)
		B2A_translations.append(B2A_translation)
	return B2A_translations

def combine_images(proj_images, B2A_translations):	# assume proj_images are connected left to right
	heights = []
	widths = []
	for proj_image in proj_images:
		height = proj_image.shape[0]
		width = proj_image.shape[1]
		heights.append(height)
		widths.append(width)
	total_my = np.sum(np.array(B2A_translations)[:,0])
	total_mx = np.sum(np.array(B2A_translations)[:,1])

	# Set combined_image size
	combined_image = np.zeros((np.max(heights) +  total_my*2 + 1, total_mx + widths[-1], 3), dtype="uint8") #kkkkk

	# Plot images onto combined_image
	origin = np.array((total_my, 0))
	for i in range(len(proj_images)):
		proj_image = np.copy(proj_images[i])

		# update origin
		if i == 0:
			origin = origin
		else:
			translation = np.array(B2A_translations[i-1])
			origin = origin + translation
		
		# update hieght, width
		height = proj_image.shape[0]
		width = proj_image.shape[1]

		# plot this image onto the combined_image
		L = origin[1] + 0
		R = origin[1] + width
		U = origin[0] + 0
		D = origin[0] + height
		# linear color blending
		if i==0:
			combined_image[U:D, L:R] = proj_image
		else:
			blend_ratio = np.ones(proj_image.shape)
			translation = np.array(B2A_translations[i-1])
			prev_proj_image_width = proj_images[i-1].shape[1]
			blend_width = prev_proj_image_width - translation[1]
			for i in range(blend_width):
				blend_ratio[:,i] = i / blend_width
			combined_image[U:D, L:R] = combined_image[U:D, L:R] * (1-blend_ratio) + proj_image * blend_ratio
		# # TODO: without blending
		# combined_image[U:D, L:R] = proj_image
	
	# Output
	return combined_image