import cv2
import csv
import pathlib

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False

def click_and_crop(event, x, y, flags, param):
	# grab references to the global variables
	global refPt, cropping

	# if the left mouse button was clicked, record the starting
	# (x, y) coordinates and indicate that cropping is being
	# performed
	if event == cv2.EVENT_LBUTTONDOWN:
		refPt = [(x, y)]
		cropping = True

	# check to see if the left mouse button was released
	elif event == cv2.EVENT_LBUTTONUP:
		# record the ending (x, y) coordinates and indicate that
		# the cropping operation is finished
		refPt.append((x, y))
		cropping = False

		# draw a rectangle around the region of interest
		cv2.rectangle(image, refPt[0], refPt[1], (0, 255, 0), 2)
		cv2.imshow("image", image)

FramePerImage = 10
videoName = 'output.avi'
path = videoName.split('.')[0]

vidcap = cv2.VideoCapture(videoName)

count = 0

pathlib.Path(path).mkdir(parents=True, exist_ok=True)


f = open(path + '/train.txt', 'w', encoding='utf-8')
classes = open(path + '/classes.txt', 'w', encoding='utf-8')
class_names = []


while(vidcap.isOpened()):
    ret, image = vidcap.read()

    if not ret:
        break

    if(int(vidcap.get(1)) % FramePerImage == 0):
        print('Saved frame number : ' + str(int(vidcap.get(1))))
        cv2.imwrite(path + "/frame%d.jpg" % count, image)
        print('Saved frame%d.jpg' % count)
        count += 1

        image = cv2.imread(path + "/frame%d.jpg" % count)
        clone = image.copy()
        cv2.namedWindow("image")
        cv2.setMouseCallback("image", click_and_crop)

        # keep looping until the 'q' key is pressed
        while True:
        	# display the image and wait for a keypress
        	cv2.imshow("image", image)
        	key = cv2.waitKey(1) & 0xFF

        	# if the 'r' key is pressed, reset the cropping region
        	if key == ord("r"):
        		image = clone.copy()

        	# if the 'c' key is pressed, break from the loop
        	elif key == ord("c"):
        		break

        # if there are two reference points, then crop the region of interest
        # from teh image and display it
        if len(refPt) == 2:
            if refPt[0][1] - refPt[1][1] < 0 :
                x_min = refPt[0][1]
                x_max = refPt[1][1]
            else:
                x_min = refPt[1][1]
                x_max = refPt[0][1]
            if refPt[0][0] - refPt[1][0] < 0 :
                y_min = refPt[0][0]
                y_max = refPt[1][0]
            else:
                y_min = refPt[1][0]
                y_max = refPt[0][0]

            print(refPt[0], refPt[1])
            if x_max-x_min > 0 and y_max - y_min > 0:
                roi = clone[x_min:x_max, y_min:y_max]
                print(x_min, y_min, x_max, y_max)
                class_name = input("Please enter a class: ")
                class_num = 0
                if class_name not in class_names:
                    class_names.append(class_name)
                class_num = class_names.index(class_name)
                f.write(path + "/frame%d.jpg " % count + str(x_min) + "," + str(y_min) +"," + str(x_max) + "," + str(y_max) + "," + str(class_num) +"\n")
                cv2.imshow("ROI", roi)

        refPt = []
        x_min, x_max, y_min, y_max = 0,0,0,0
        # Press Q on keyboard to stop
        if cv2.waitKey(0) & 0xFF == ord('q'):
           break
for i in range(len(class_names)):
    classes.write(class_names[i] + "\n")

f.close()
classes.close()
vidcap.release()
cv2.destroyAllWindows()
