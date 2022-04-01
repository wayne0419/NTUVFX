from cmath import inf
import lib
import numpy as np
import cv2
from utilities import show_image
import matplotlib.pyplot as plt
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_dir', type=str, default="../data/")
parser.add_argument('--image_extension', type=str, default=".jpg")
parser.add_argument('--image_num', type=int)
parser.add_argument('--exposure_path', type=str, default=None)
parser.add_argument('--output_dir', type=str, default="..")
config = parser.parse_args()

destination_dir = config.output_dir

photo_list = lib.read_photoes(file_dir=config.input_dir, file_num=config.image_num, file_extension=config.image_extension, exposure_filename=config.exposure_path, scale=1, scale_method=cv2.INTER_LANCZOS4)
picked_pixels_b = lib.pick_pixels(photo_list, channel=0, number_picked_pixels=400)
picked_pixels_g = lib.pick_pixels(photo_list, channel=1, number_picked_pixels=400)
picked_pixels_r = lib.pick_pixels(photo_list, channel=2, number_picked_pixels=400)
g_b = lib.solve_debevec(photo_list, picked_pixels_b, channel=0, L=400)
g_g = lib.solve_debevec(photo_list, picked_pixels_g, channel=1, L=400)
g_r = lib.solve_debevec(photo_list, picked_pixels_r, channel=2, L=400)

# test
xpoints = np.array(range(256))
plt.plot(g_b, xpoints, "b", label = "b")
plt.plot(g_g, xpoints, "g", label = "g")
plt.plot(g_r, xpoints, "r", label = "r")
plt.legend()
plt.xlabel('ln(exposure), ln(E*dt)', fontsize=14)
plt.ylabel('intensity, z', fontsize=14)
plt.savefig(destination_dir + "/g_function.png")
plt.show()
########################################

irradiance_b = lib.merge_irradiance(photo_list, g_b, 0)
irradiance_g = lib.merge_irradiance(photo_list, g_g, 1)
irradiance_r = lib.merge_irradiance(photo_list, g_r, 2)

irradiance = np.stack((irradiance_b,irradiance_g,irradiance_r), axis=2)
cv2.imwrite(destination_dir + "/hdr.hdr", irradiance)

for a in [0.18, 0.3, 0.4, 0.5, 0.75]:
	for L_white in [0.5, 1, 1.5, 3, inf]:
		lib.reinhard_global_tone_map(irradiance_b, irradiance_g, irradiance_r, a=a, sigma=0.00000001, L_white=L_white, 
									destination=destination_dir + "/tone_mapped_a{}_white{}.png".format(str(a), L_white))




# # test
# cv2.imwrite("hdr.hdr", irradiance)
# irradiance = irradiance / np.max(irradiance) * 255
# show_image(irradiance)
# #####################################################

# # test
# def print_radiance_map(rads, channel, color=["b","g","r"]):
# 	plt.imshow(rads, cmap = plt.cm.jet)
# 	plt.title(color[channel])
# 	plt.colorbar()
# 	plt.show()

# print_radiance_map(irradiance_b, 0)
#######################################################