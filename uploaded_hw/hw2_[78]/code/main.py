import numpy as np
import cv2
import matplotlib.pyplot as plt
import msop
from matplotlib.patches import Rectangle
import math
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
import stitching
import argparse

# Handle arguments
parser = argparse.ArgumentParser()
parser.add_argument('--img_dir', type=str)
parser.add_argument('--image_extension', type=str, default=".jpg")
parser.add_argument('--image_num', type=int)
parser.add_argument('--focal_length_path', type=str)
config = parser.parse_args()

IMG_DIR = config.img_dir
IMG_FORMAT = config.image_extension
N_IMG = config.image_num
FOCAL_LENGTH_SRC = config.focal_length_path
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


			
# Do Feature -Matching to get paired_points_pyramids
paired_points_pyramids = stitching.build_paired_points_pyramids(description_pyramids, ratio_threshold=0.5) #TODO may use ratio_threshold = 0.8





# Do pair-wise-alignment to build B2A_translations, list of (my,mx), length = N_IMG-1
B2A_translations = stitching.build_B2A_translations(paired_points_pyramids)



proj_images = []
for proj_img_pyramid in proj_img_pyramids:
	proj_img = proj_img_pyramid[0]
	proj_images.append(proj_img)

# Combine proj_images together, assume proj_images are connected left to right
combined_image = stitching.combine_images(proj_images, B2A_translations)
# Plot Result ###########################################################
plt.imshow(cv2.cvtColor(combined_image, cv2.COLOR_BGR2RGB))
plt.show()
# cv2.imwrite("report_material/10_result_library.png",combined_image)
#########################################################################
		

		
