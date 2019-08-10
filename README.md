# Motion-and-Smile-Detector

Motion detector, uses the first frame as reference for no motion. Anything that is different compared to the first frame is considered motion hence when you run the app make sure there is no motion and no foreign objects in the frame at the beginning. Plots a bar graph showing times when motion or foreign object were detected.

Facial and smile detection, creates a .jpg of your last smile and tells user how long he/she smiled for :D

Run the plotting.py file, press q to quit.

Uses OpenCV2 and bokeh libraries. Uses haarcascades for facial and smile detection.
