import numpy as np
import cv2
import matplotlib.pyplot as plt
import msop
from matplotlib.patches import Rectangle
import math
IMG_SRC = "./image/prtn/17.jpg"
FOCAL_LENGTH_SRC = "image/prtn/focal-length.txt"
PYRAMID_DEPTH = 4

image = cv2.imread(IMG_SRC)
focal_length = msop.read_focal_length(FOCAL_LENGTH_SRC)

img_pyramid, grayimg_pyramid = msop.build_img_pyramid(image, depth=PYRAMID_DEPTH)
# # Plot Result ###############################
# plt.figure(figsize=(20, 10))
# columns = 2
# rows = PYRAMID_DEPTH
# for i in range(rows):
# 	plt.subplot(rows, columns, i*columns + 1)
# 	plt.imshow(img_pyramid[i])
# 	plt.subplot(rows, columns, i*columns + 2)
# 	plt.imshow(grayimg_pyramid[i])
# plt.show()
# # ###########################################

harris_response_pyramid = msop.get_harris_response_pyramid(grayimg_pyramid, sigma=1.5)
# # Plot Result ###############################
# plt.figure(figsize=(20, 10))
# columns = PYRAMID_DEPTH
# rows = 1
# for i in range(columns):
# 	img = np.copy(img_pyramid[i])
# 	response = np.copy(harris_response_pyramid[i])
# 	img[response > 0.01*response.max()] = np.array([0, 0, 255])
# 	plt.subplot(rows, columns, i*rows + 1)
# 	plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

# plt.show()
# # ###########################################

proj_img_pyramid = msop.build_projected_pyramid(img_pyramid, focal_length[17])
proj_grayimg_pyramid = msop.build_projected_pyramid(grayimg_pyramid, focal_length[17])
proj_harris_response_pyramid = msop.build_projected_pyramid(harris_response_pyramid, focal_length[17])
# # Plot Result ###############################
# plt.figure(figsize=(20, 10))
# columns = PYRAMID_DEPTH
# rows = 1
# for i in range(columns):
# 	img = np.copy(proj_img_pyramid[i])
# 	response = np.copy(proj_harris_response_pyramid[i])
# 	img[response > 0.01*response.max()] = np.array([0, 0, 255])
# 	plt.subplot(rows, columns, i*rows + 1)
# 	plt.imshow(cv2.cvtColor(np.uint8(img), cv2.COLOR_BGR2RGB))

# plt.show()
# # ###########################################

fpts_pyramid = msop.build_feature_points_pyramid(proj_harris_response_pyramid , 150)	#TODO: may try n_features=300
# Plot Result ###############################
plt.figure(figsize=(20, 10))
columns = PYRAMID_DEPTH
rows = 1
for i in range(columns):
	img = np.copy(proj_img_pyramid[i])
	fpts = np.copy(fpts_pyramid[i])
	plt.subplot(rows, columns, i*rows + 1)
	plt.imshow(cv2.cvtColor(np.uint8(img), cv2.COLOR_BGR2RGB))
	for fpt in fpts:
		plt.plot( fpt.x, fpt.y, 'r.')

plt.show()
# ###########################################

descriptions_pyramid = msop.build_descriptions_pyramid(fpts_pyramid, proj_grayimg_pyramid)
# Plot Result ###############################
plt.figure(figsize=(20, 10))
columns = PYRAMID_DEPTH
rows = 1
for i in range(columns):
	img = np.copy(proj_img_pyramid[i])
	descriptions = np.copy(descriptions_pyramid[i])
	plt.subplot(rows, columns, i*rows + 1)
	plt.imshow(cv2.cvtColor(np.uint8(img), cv2.COLOR_BGR2RGB))
	ax = plt.gca()
	for d in descriptions:
		rect = Rectangle( (d.point.x, d.point.y), 40, 40, angle=d.orientation, linewidth=1, edgecolor='r', facecolor='none')
		ax.add_patch(rect)

plt.show()
# ###########################################
# # Plot Result ###############################
# for i in range(PYRAMID_DEPTH):
# 	for j in range(len(fpts_pyramid[i])):
# 		fpt = fpts_pyramid[i][j]
# 		description = descriptions_pyramid[i][j]
# 		print((fpt.x, fpt.y), (description.point.x, description.point.y, description.orientation))
# 		plt.imshow(description.des_patch)
# 		plt.show()
# # ###########################################