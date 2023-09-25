import cv2

hc = "cars.xml"  # haar cascade classifier
video = "../data/video1.avi"

cap = cv2.VideoCapture(video)
car_cascade = cv2.CascadeClassifier(hc)

while True:
    ret, img = cap.read()
    if type(img) == type(None):
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cars = car_cascade.detectMultiScale(gray, 1.1, 1)

    for (x, y, w, h) in cars:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imshow("video", img)

    if cv2.waitKey(33) == 27:
        break

cv2.destroyAllWindows()
