# VFX Project 2: Automatic Image Stitching

## Author

- 網媒所 王哲瑋 Che Wei Wang r10944037


## Code Structure

- `run.sh`：run `main.py` with predefined arguments.
- `main.py`：will handle command line arguments and then `import msop`, `import stitching` and `import utilities` to do image stitching.
- `msop.py`：implementation of MSOP feature detecion, description method.
- `stitching.py`：implementation of KNN-feature-matching, image-alignment, image blending
- `utilities.py`：handle some trivial functions.


## How To Execute
- Data format:
	- Images should be named from 0 to N, where N is the number of your images.
	- Focal-length file should list focal-lengths of images in the structure of one line one focal-length, see the provided data as examples
- Execution methods:
	1. Execute `run.sh`.
	2. Run `python main.py` with arguments:

|  Argument  |                         Explanation                          | Required |
| :--------: | :----------------------------------------------------------: | :------: |
| input_dir  |                 The directory where you put all your input images|   Yes    |
| image_extension | The extension of your image files | Yes |
| image_num | The number of your input images | Yes |
| focal_length_path |            The path to your focal-length file             | Yes |


## Feature Detection

The feature detection algorithm being implemented in this project is MSOP's feature detection, which is multi-scale Harris Corner Detection.

The following steps under "Feature detection" section have to be done for every input image. Here I use one image as an example.

The first thing I do is scale input images into 4 scales: 1, 1/2, 1/4, 1/8, and also the grayscale image of them.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/1_build_img_pyramid.png?raw=true)

Then, I compute the Harris Corner Response for all scales of the image. Below is a image that shows the pixels of higher Harris Corner Response as red.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/2_compute_harris_response.png?raw=true)

Next, I do cylindrical projection on the image. The below image shows the projected images with Harris Response

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/3_cylindrical_proj_img_and_response.png?raw=true)

Then, I pick the feature points using non-maximal suppression methid to try to pick well-distributed feature points.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/4_get_feature_points.png?raw=true)

## Feature Description

After I pcik the feature points for every scale of every image, now I can make descriptions for them.

The following steps under "Feature Description" section have to be done for every input image. Here I use one image as an example.

To describe a feature point, I first decide the orientation of it.

The orientation of a feature point is defined by first doing a Gaussian Blur on the image to decrease noise, then compute the gradient at the feature point and use the gradient as the orientation of it. Like the below formula.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/formula1.png?raw=true)

Then I rotate the image to align the orientation of the feature point toward right and then sample a 40\*40 patch around the feature point.

If a feature point does not have a complete 40\*40 patch around it, like sitting on the eade of the image, then the feature point will be ignored.

The 40\*40 patch is then standardized and resized to an 8\*8 patch. This 8\*8 patch will be the description of this feature point.

Below image shows how feature point gets its description patch.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/5_get_descriptions__ignoreIncompleteDescription.png?raw=true)

Below is an example of how a 8*8 description patch looks like.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/6_description_patch_example.png?raw=true)

## Feature Matching

After I got the descriptions of every feature point of every image, I want to match the feature points between every consecutive images.

The following steps under "Feature Matching" section have to be done for every consecutive images. Here I use one image pair as an example.

To match feature points, I use KNN algorithm, and below is the result:

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/7_2_pairwise_alignment_without_ignore.png?raw=true)

You can see there are some obvious matching errors, and those errors happen because those feature points sit on the edge of the image, and dont have a complete 40*40 description patch. 

So like I said in previous section, I ignore those kind of feautre points, and this is the result:

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/7_1_pairwise_alignment.png?raw=true)

Much better, right?

## Image Alignment

After we match the feature points between each consecutive images, we can compute the transform between each image and then align them together.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/9_2_combine_without_blending.png?raw=true)

Hmmm, the image are aligned correctly, but the color between them are not merged well. We can easily see the connection boundary between images.

## Image Blending

To solve the "color between them are not merged well" issue. I use linear interpolation toe blend the colors between images, illustrated as below image.

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/formula2.png?raw=true)

Then I get a much better result:

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/9_1_combine_with_blending.png?raw=true)

## Result

Here are the final complete results of the stitched images:

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/10_result.png?raw=true)

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/10_result_library.png?raw=true)

![img](https://github.com/wayne0419/NTUVFX/blob/main/proj2/readme_material/10_result_mountain.png?raw=true)
