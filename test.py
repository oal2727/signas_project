import cv2
import time
import os

# /Users/dash/Desktop/signas_project
      
# weightsPath_vehicles = os.path.sep.join(["darknet/parameters/yolov4-custom_last.weights"])
# configPath = os.path.sep.join(["darknet/parameters/yolov4-custom.cfg"])

CONFIDENCE_THRESHOLD = 0.6
NMS_THRESHOLD = 0.5
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

class_names=[]
with open(os.path.join(os.getcwd(),"parameter","obj.names"), 'r') as archivo:
    lineas = archivo.read().splitlines()
    for item in lineas:
      class_names.append(item)


final = os.path.join(os.getcwd(),"imagenes","wll")
print(final)

weightsPath_vehicles = os.path.join(os.getcwd(),"parameter","yolov4-custom_last_4500.weights")# "/Users/dash/Desktop/signas_project/parameter/yolov4-custom_last_4500.weights"# os.path.sep.join(["C://Users//dash//backend//parameter//yolov4-custom_last.weights"])
configPath =  os.path.join(os.getcwd(),"parameter","yolov4-custom.cfg") # "/Users/dash/Desktop/signas_project/parameter/yolov4-custom.cfg" # os.path.sep.join(["C://Users//dash//backend//parameter//yolov4-custom.cfg"])
net = cv2.dnn.readNet(configPath, weightsPath_vehicles)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)
image = cv2.imread("/Users/dash/Desktop/signas_project/detectado.png")

fluxo = time.time()
classes, scores, boxes = model.detect(image, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
for (classid, score, box) in zip(classes, scores, boxes):
    color = COLORS[int(classid) % len(COLORS)]
    #print(classid)
    label = "%s : %f" % (class_names[classid], score)
    cv2.rectangle(image, box, color, 2)
    cv2.putText(image, label, (box[0], box[1]-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    #print(image)

cv2.imshow("original",image)
cv2.waitKey(0)
cv2.destroyAllWindows()
