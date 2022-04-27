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

	# do knn
	neigh = NearestNeighbors(n_neighbors=2).fit(des_patchsB)
	distances, indices = neigh.kneighbors(des_patchsA)
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