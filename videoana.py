# This program enables teachers to implement active learning (AL) by helping them to grade student-created screencasts (SCSs). 
# The program uses computer vision to extract important keywords from the SCSs based on the teacher's requirements. 
# The teacher defines his/her requirements in a simple text file. The program reports its findings in a log file in text format.
#
# The program was developed by Dr. Adam Wong at PolyU SPEED with the assistance from research assistant Mr. Kia Tsang.
 
# Adam 2024 Feb - Show only the first occurence of a target

#### ===== IMPORT PACKAGES =====
####
from PIL import Image
import os, sys
import cv2

import pytesseract
#pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\hyintsang\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'

# WKL 2024.01.12
# WK-S1236
#pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Swift3
pytesseract.pytesseract.tesseract_cmd = 'D:\\Program Files\\Tesseract-OCR\\tesseract.exe'

#### ===== DEFINE FUNCTIONS =====
####

# Show a message on the console and write it into the log file
def textLog(msg):
    print(msg, file=myLog)
    print(msg)

# Create a dictionary to record the timestamp at which each targetText appears in each video
# w is the targetText
# v is the initial count, which is 0 
def mkTextTimestamp(w,v):
    d = {}
    for i in range(len(w)):
            d[w[i]] = v
    return d

#### ===== THE MAIN PROGRAM =====
####
# Initialse variables
myLog = open('Log.txt', 'w') # Log file
# textLog("v 2024.02.12v Adam Wong - Show only the first occurence of a target\n")
# textLog("Please prepare the following file and folder:\n- texts to find.txt: Define your target texts\n- Folder 'Source Videos' (Case sensitive): A folder contained all the videos to be OCRed\n")
# textLog("*** Names of video files and target texts : Long strings and special characters  may cause errors. ***");

targetTexts = ['common','Restart','France','SimpleImputer','OneHotEncoder','LabelEncoder','train_test_split','StandardScaler','Error']
targetTextPath = './Target Text-' + '/'

# try:
    ### The first frame of video always results in all strings found and bounding boxes drawn
    ### Replace it with hardcoding to improve performance
    
    # target = open("texts to find.txt", "r") # User-defined target texts to be found
    # targetString = target.read()
    # targetTexts = targetString.split("\n")
#     targetTextPath = './Target Text-' + targetString.replace('\n', " ") + '/'
    # targetTextPath = './Target Text-' + '/'
    # textLog(f"Texts to find (Target texts defined in the 'texts to find.txt' file):\n{targetTexts}\n")
    # target.close()
# except:
    # textLog("Target text file missing. Please define your target texts in a 'texts to find.txt' file.")
    # sys.exit(0)
userInterval = 0.5
#userInterval = int(input("Enter interval (in seconds) to extract (e.g. 1)"))

# Create directory for the frames
if not os.path.exists(targetTextPath):
    os.makedirs(targetTextPath)

# Create video path
textLog("Capturing videos\n")

prevStudent = "dummy";

for vidFile in os.listdir('./Source Videos/'):
    
    realPath = "./Source Videos/" + vidFile
    vid = cv2.VideoCapture(realPath)
    vidFile = vidFile.split("@")
    vidFile = str(vidFile[0])
    vidFile = str(vidFile[-18:-1])
    print (vidFile)
    
    # Start index or count for the frames
    index = 1
    vid.set(1, index)
    success, frame = vid.read()
    while success:
   
        # Assign a name for files
        if not os.path.exists(targetTextPath + vidFile):
            os.makedirs(targetTextPath + vidFile)
        name = targetTextPath + vidFile + '/' + vidFile + ' second-' + str(round(index / cv2.CAP_PROP_FPS,2)) +'.png'

        # Save every Xth frame
#        textLog("Extracting frames to '" + name + "'\n")
        cv2.imwrite(name, frame)
        index = index + userInterval*vid.get(cv2.CAP_PROP_FPS)
        vid.set(1, index)
        success, frame = vid.read()

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    vid.release()
    cv2.destroyAllWindows() # Destroy all the opened windows

    # Detect text
    # textLog("Finding target text\n")
    matched_list = []

    textTimestamps = mkTextTimestamp(targetTexts, -1)   ### For this video, reset all timestamps

    for i in os.listdir(targetTextPath + vidFile + '/'):
        if vidFile != prevStudent:
            textLog("\n ================  in " + vidFile + "found ...\n")         
            prevStudent = vidFile
        demo = Image.open(targetTextPath + vidFile + '/' + i)
        text = pytesseract.image_to_string(demo, lang = 'eng')
#        textLog("\nIn " + i + ", found ")

        fileNamePrinted = False

        for targetText in targetTexts:
            if targetText in text and textTimestamps[targetText] <0 :
                if fileNamePrinted == False:
                   # textLog("found ....")
                   fileNamePrinted = True
                
                textLog(targetText + "; ")
                matched_list.append(i)
                textTimestamps[targetText] = 999 ### actual value to be inserted in a later version
                img = cv2.imread(targetTextPath + vidFile + '/' + i)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Place bounding boxes
                heightImg, widthImg,_  = img.shape
                boundingBox = pytesseract.image_to_data(img, lang = 'eng')
                for x, b in enumerate(boundingBox.splitlines()):
                    if x != 0:
                        b = b.split()
                        if len(b) == 12 and targetText in b[11]:
#                            textLog("Drawing bounding boxes in '" + i + "'\n")
                            xCoord, yCoord, wDim, hDim = int(b[6]), int(b[7]), int(b[8]), int(b[9])
                            cv2.rectangle(img, (xCoord, yCoord), (xCoord+wDim, yCoord+hDim), (0, 0, 255), 1)
                            cv2.putText(img, targetText, (xCoord, yCoord-3), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 255), 1)
                            cv2.imwrite(targetTextPath + vidFile + '/' + i, img)
    
    # Remove extra frames
    textLog("Removing extra frames\n")
    for i in os.listdir(targetTextPath + vidFile + '/'):
        if i not in matched_list:
            os.remove(targetTextPath + vidFile + '/' + i)
#            textLog("Deleted '" + i + "' as there is no matching target text\n")
# End of program message
textLog("OCR completed. Please check the respective target text folders.")
myLog.close()
