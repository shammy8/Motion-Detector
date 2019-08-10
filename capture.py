"""Motion detector, uses the first frame as reference for no motion. Anything that is different compared to the first frame is considered motion
hence when you run the app make sure there is no motion and no foreign objects in the frame at the beginning. Also detects faces and smiles, creates
a .jpg of your last smile and tells user how long he/she smiled for :D"""

import cv2, time, pandas
from datetime import datetime

first_frame = None                                          #set the first frame = None. The actual first frame of the video capture is used as a reference to check for motion.
motion_detected = [None, None]                              #0 is used when no foreign objects and no motion is detected and 1 used otherwise, None is set for for first two indexes so index doesn't go out of boundary
smile_detected = [0, 0]                                     #0 is used when no smile is detected and 1 when at least one smile is detected
times = []                                                  #list of times for when foreign objects and motion come in and out of frame
video = cv2.VideoCapture(0)                                 #use video capture from webcam
times_df = pandas.DataFrame(columns=["Start", "End"])       #create a pandas dataframe to record times when foreign objects and motion come in and out of frame
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') #load the haar cascade for face detection
smile_classifier = cv2.CascadeClassifier('haarcascade_smile.xml')           #load the haar cascade for smile detection
total_smile_time = 0                                        #set the initial total smiling time to 0 

while True:
    check, frame = video.read()                             #store each frame record by webcam in the variable called frame
    status = 0                                              #set the inital status to 0 ie. no motion and no foreign objects in frame
    smile_status = 0                                        #set the inital smile_status to 0 ie. no smiles in frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)          #convert the current frame into a gray frame and name it gray
    gray = cv2.GaussianBlur(gray, (21,21), 0)               #apply gaussian blur to the gray frame to remove noise and increase accuracy  

    #detect faces and draw a rectangle around it, detect smiles inside faces and draw another rectangle around smiles
    faces = face_cascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 2)   #draw rectangle around faces
        roi_gray = gray[y:y + h, x:x + w]
        roi_frame = frame[y:y + h, x:x + w]
        smile = smile_classifier.detectMultiScale(roi_gray, scaleFactor=1.2, minNeighbors=22, minSize=(25, 25)) #detect smile inside faces
        #if there is a smile detected set the smile_status to 1 else set it to 0
        if len(smile) > 0:                                  
            smile_status = 1
        else:
            smile_status = 0 
        for (sx, sy, sw, sh) in smile:                      #draw rectangle around smiles
            cv2.rectangle(roi_frame, (sx, sy), (sx + sw, sy + sh), (0, 0, 255), 1)
            smile_frame = frame                             #set the current frame as the smile frame, used to change to a jpg later
        smile_detected.append(smile_status)                 #add the current smile status to a list
        smile_detected = smile_detected[-2:]                #just keep the last two numbers of smile_detected to save space
        if (smile_detected[-1] == 1 and smile_detected[-2] == 0):   #if a smile is detected after a frame with no smiles, start the timer
            smile_start_time = time.time()
        elif (smile_detected[-1] == 0 and smile_detected[-2] == 1): #if a frame with smile(s) becomes a frame with no smiles, end the timer
            smile_end_time = time.time()
            total_smile_time +=  (smile_end_time - smile_start_time)#add the time to the total smile time    

    #if first_frame hasn't been set yet change it to the current frame ie. save the first frame of the video to the variable first_frame
    if first_frame is None:     
        first_frame = gray
        continue

    delta_frame = cv2.absdiff(first_frame, gray)                                #calculate the difference between the first frame and the current frame and name it delta_frame
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]    #if any pixels in the delta_frame are above 30 set it to 255 (ie. total white)
    thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)               #smooth the threshold frame for accuracy

    (contours,_) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)    #find all contours in the threshold_frame

    #if the contour is smaller than 5000 in size check the next contour. Change this number to find objects of different size
    for contour in contours:
        if cv2.contourArea(contour) < 5000:        
            continue
        #if it's not smaller than 5000 then
        status = 1                                          #motion / foreign object is detected, set status to 1 
        #get the coordinates of the contour and draw a rectangle around the contour
        (x, y, w, h) = cv2.boundingRect(contour)            
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3 )

    #add the current time to the times list when foreign object or motion appears and when all object and motion is gone
    motion_detected.append(status)
    motion_detected = motion_detected[-2:]                  #just save the last two numbers of motion_detected to save space
    if (motion_detected[-1] == 1 and motion_detected[-2] == 0) or (motion_detected[-1] == 0 and motion_detected[-2] == 1):
        times.append(datetime.now())

    #display the four frames
    cv2.imshow("Gray Frame", gray)
    cv2.imshow("Delta Frame", delta_frame)
    cv2.imshow("Threshold Frame", thresh_frame)
    cv2.imshow("Colour Frame", frame)

    key = cv2.waitKey(33)

    #quit the app when 'q' is pressed
    if key == ord('q'):
        if status == 1:                                     #if there is object or motion detected when app is quit add the quitting time to the list
            times.append(datetime.now())
        if smile_status == 1:                               #if smile is detected at quit, end the smiling timer and add it to the total smiling time
            smile_end_time = time.time()
            total_smile_time +=  (smile_end_time - smile_start_time)
        break

#add the start and end times of motion and objects detected into the times dataframe
for i in range(0, len(times), 2):
    times_df = times_df.append({"Start":times[i], "End":times[i+1]}, ignore_index = True)

times_df.to_csv("Times.csv")      #export the dataframe to a csv file

video.release()

#create a jpg of the last smile and tell user how long he/she smiled for. Do nothing if no smile was detected.
try: 
    cv2.putText(smile_frame, 'You smiled for ' + str(round(total_smile_time)) + 's. Keep on smiling.', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.imwrite("smile.jpg", smile_frame)
    cv2.imshow("Smile", smile_frame)
    cv2.waitKey(2000)
except NameError:
    pass

cv2.destroyAllWindows()