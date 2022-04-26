import numpy as np
import cv2
import matplotlib.pyplot as plt
import msop
from matplotlib.patches import Rectangle
import math
IMG_DIR = "./image/prtn/"
IMG_FORMAT = ".jpg"
N_IMG = 2
FOCAL_LENGTH_SRC = "image/prtn/focal-length.txt"
PYRAMID_DEPTH = 4

# Read images, focal_lengths
images = []
for i in range(N_IMG):
	img_src = IMG_DIR + str(i) + IMG_FORMAT
	image = cv2.imread(img_src)
	images.append(image)
focal_lengths = msop.read_focal_length(FOCAL_LENGTH_SRC)

# Run MSOP to get proj_img_pyramids, description_pyramids
proj_img_pyramids, description_pyramids = msop.msop(images, focal_lengths, pyramid_depth=PYRAMID_DEPTH)


def build_paired_points_pyramids(description_pyramids, ratio_threshold = 0.7):	#TODO may use ratio_threshold = 0.8
	# build paired_points_pyramids using knn
	paired_points_pyramids = []
	for i in range(len(description_pyramids))[:-1]:
		# build paired_points_pyramid
		des_pyramidA = description_pyramids[i]
		des_pyramidB = description_pyramids[i+1]
		depth = len(des_pyramidA)
		paired_points_pyramid = []
		for j in range(depth):
			# build paired_points
			descriptionsA = des_pyramidA[j]
			descriptionsB = des_pyramidB[j]
			pair_points = []

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
			print(des_patchsA.shape)
			# do knn
			for des_patch in des_patchsA:
				# kkkkkkkkkk
			

				
build_paired_points_pyramids(description_pyramids)