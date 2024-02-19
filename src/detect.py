"""
Library of functions used with YOLOv8 detection model.
"""

def IoU(A, B):
    """
    A,B - boxes in xyxy list format
    """
    
    # determine the (x, y)-coordinates of the intersection rectangle
    maxx = max(A[0], B[0])
    maxy = max(A[1], B[1])
    minx = min(A[2], B[2])
    miny = min(A[3], B[3])
    # compute the area of intersection rectangle
    intersection = max(0, minx - maxx + 1) * max(0, miny - maxy + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    areaA = (A[2] - A[0] + 1) * (A[3] - A[1] + 1)
    areaB = (B[2] - B[0] + 1) * (B[3] - B[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = intersection / float(areaA + areaB - intersection)
    # return the intersection over union value
    return iou
