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

# Plot Result #######################################################################
columns = PYRAMID_DEPTH
rows = N_IMG
fig=plt.figure(figsize=(columns*5, rows*5))
for i in range(0, rows-1):
	
	for p in range(columns):
		proj_img = proj_img_pyramids[i][p]
		proj_img_next = proj_img_pyramids[i+1][p]
		paired_points = paired_points_pyramids[i][p]

		fig.subplots_adjust(wspace=0.2)
		fig.add_subplot(rows, columns, i*PYRAMID_DEPTH+1+p)
		
		(hA, wA) = proj_img.shape[:2]
		(hB, wB) = proj_img_next.shape[:2]

		# Plot image
		vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
		vis[0:hA, 0:wA] = proj_img
		vis[0:hB, wA:] = proj_img_next
		plt.imshow(cv2.cvtColor(vis, cv2.COLOR_BGR2RGB))

        # Plot points, lines
		for (apoint, bpoint) in paired_points:

			color = np.random.randint(0, high=255, size=(3,))
			# Plot point in image A, left, i
			plt.plot(apoint.x, apoint.y, 'ro')
			ptA = (int(apoint.y), int(apoint.x))
			# Plot point in image B, right, i+1
			plt.plot(bpoint.x + wA, bpoint.y, 'ro')
			ptB = (int(bpoint.y), int(bpoint.x + wA))

			# Plot line between points
			plt.plot([ptA[1], ptB[1]], [ptA[0], ptB[0]])

plt.show()
####################################################################################