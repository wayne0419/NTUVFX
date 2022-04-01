Data format:
	(1) Images should be named from 0 to N, where N is the number of your images.
	(2) ExposureTime should be stored in a file named exposures.txt , this file is not required if you have exposure time kept in your images' metadata.
Execution method
	(1) Execute ./code/run.sh while in ./code
	or
	(2) Run ./code/main.py with arguments:
	--input_dir : the directory where you put all your input images.
	--image_extension : the extension of your image files.
	--image_num : the number of your input images.
	--exposure_path : the path to your exposures.txt.
	--output_dir : the directory where you want to store all the outputs (including g_function plot, hdr file, tone_mapped hdr file with different parameters).
	example:
	python main.py --input_dir ../data/ --image_extension .jpg --image_num 14 --exposure_path ../data/exposures.txt --output_dir ../output