# Import required modules
import os
import math
import time
import cv2 as cv
from .PDetector import p_detect
from os.path import dirname, join

def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])

    return bboxes


def age_gender_detector(frame, ageNet, faceNet, padding, MODEL_MEAN_VALUES, ageList):
    # Read frame
    t = time.time()
    bboxes = getFaceBox(faceNet, frame)
    for bbox in bboxes:
        # print(bbox)
        face = frame[max(0, bbox[1] - padding):min(bbox[3] + padding, frame.shape[0] - 1),
               max(0, bbox[0] - padding):min(bbox[2] + padding, frame.shape[1] - 1)]

        blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
        ageNet.setInput(blob)
        agePreds = ageNet.forward()
        age = ageList[agePreds[0].argmax()]
        label = "{} Year Range".format(age)

        return age


def detect_age_and_p(path):
    # setting up
    MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
    ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']


    faceProto = os.path.join(os.path.join(os.path.join(os.getcwd(),"HomeApp"),"models"),'opencv_face_detector.pbtxt')
    faceModel = os.path.join(os.path.join(os.path.join(os.getcwd(),"HomeApp"),"models"),'opencv_face_detector_uint8.pb')
    padding = 20
    ageProto = os.path.join(os.path.join(os.path.join(os.getcwd(),"HomeApp"),"models"),'age_deploy.prototxt')
    ageModel = os.path.join(os.path.join(os.path.join(os.getcwd(),"HomeApp"),"models"),'age_net.caffemodel')

    # Load network
    ageNet = cv.dnn.readNet(ageModel, ageProto)
    faceNet = cv.dnn.readNet(faceModel, faceProto)


    analysis = {}

    input = cv.imread(path)
    print(path)
    if path.endswith('.jpg'):
        try:
            age_prediction = age_gender_detector(input, ageNet, faceNet, padding, MODEL_MEAN_VALUES, ageList)
            print(age_prediction)
            if age_prediction:
                if age_prediction == '(0-2)' or age_prediction == '(4-6)' or age_prediction == '(8-12)' or age_prediction ==  '(15-20)':
                    # child detected
                    try:
                        predictions = p_detect(path)
                        analysis[path] = predictions[0][path]
                        analysis[path]['age'] = age_prediction

                    except Exception as ex:
                            print("Exception in P- Detect:")
                            print(ex)
                            return "P- Detection Error!"
                else:
                    return "Child not found!"

            else:
                return "Age Not Detected!"

        except Exception as ex:
                    print("Exception in Age Prediction:")
                    print(ex)
                    return "Age Detection Error!"

    return analysis
