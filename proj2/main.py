import numpy as np
import cv2
import matplotlib.pyplot as plt
import msop
from matplotlib.patches import Rectangle
import math
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm
import stitching

IMG_DIR = "./image/prtn/"
IMG_FORMAT = ".jpg"
N_IMG = 4
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


			
# Do Feature -Matching to get paired_points_pyramids
paired_points_pyramids = stitching.build_paired_points_pyramids(description_pyramids, ratio_threshold=0.7) #TODO may use ratio_threshold = 0.8

# # Plot Result #######################################################################
# columns = PYRAMID_DEPTH
# rows = N_IMG
# fig=plt.figure(figsize=(columns*5, rows*5))
# for i in range(0, rows-1):
	
# 	for p in range(columns):
# 		proj_img = proj_img_pyramids[i][p]
# 		proj_img_next = proj_img_pyramids[i+1][p]
# 		paired_points = paired_points_pyramids[i][p]

# 		fig.subplots_adjust(wspace=0.2)
# 		fig.add_subplot(rows, columns, i*PYRAMID_DEPTH+1+p)
		
# 		(hA, wA) = proj_img.shape[:2]
# 		(hB, wB) = proj_img_next.shape[:2]

# 		# Plot image
# 		vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
# 		vis[0:hA, 0:wA] = proj_img
# 		vis[0:hB, wA:] = proj_img_next
# 		plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))

#         # Plot points, lines
# 		for (apoint, bpoint) in paired_points:

# 			color = np.random.randint(0, high=255, size=(3,))
# 			# Plot point in image A, left, i
# 			plt.plot(apoint.x, apoint.y, 'ro')
# 			ptA = (int(apoint.y), int(apoint.x))
# 			# Plot point in image B, right, i+1
# 			plt.plot(bpoint.x + wA, bpoint.y, 'ro')
# 			ptB = (int(bpoint.y), int(bpoint.x + wA))

# 			# Plot line between points
# 			plt.plot([ptA[1], ptB[1]], [ptA[0], ptB[0]])

# plt.show()
# ####################################################################################

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

# Do pair-wise-alignment to build B2A_translations, list of (my,mx), length = N_IMG-1
B2A_translations = build_B2A_translations(paired_points_pyramids)

# Plot Result #######################################################################
columns = 1
rows = len(B2A_translations)
fig=plt.figure(figsize=(columns*5, rows*5))
for i in range(0, rows):
	fig.subplots_adjust(wspace=0.2)
	fig.add_subplot(rows, columns, i+1)

	# set image size
	proj_img = proj_img_pyramids[i][0]
	proj_img_next = proj_img_pyramids[i+1][0]
	my ,mx = B2A_translations[i]
	(hA, wA) = proj_img.shape[:2]
	(hB, wB) = proj_img_next.shape[:2]
	vis = np.zeros((max(hA, hB) +  int(math.fabs(my))*2+1, wA +int(math.fabs(mx))*2+1, 3), dtype="uint8")

	# plot imageA, left
	# AOH = int(math.fabs(my))
	# AOW = int(math.fabs(mx))
	AOH = int(math.fabs(my))
	AOW = 0
	vis[AOH : AOH + hA, AOW : AOW + wA] = proj_img

	# plot imageB, right
	bOH = int(AOH + my)
	bOW = int(AOW + mx)
	vis[ bOH : bOH + hB, bOW : bOW + wB] = proj_img_next
	plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))
	plt.plot(AOW, AOH, 'r*')
	plt.plot(bOW, bOH, 'b*')
    
plt.show()
#####################################################################################