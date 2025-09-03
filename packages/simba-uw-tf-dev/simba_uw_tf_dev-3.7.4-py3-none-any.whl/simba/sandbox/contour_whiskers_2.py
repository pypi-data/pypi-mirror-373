import cv2
import numpy as np


def contour_bboxes(contours):
    """Returns a list of bounding boxes for each contour."""
    return [cv2.boundingRect(c) for c in contours]

from simba.utils.read_write import read_img_batch_from_video_gpu


def overlap(bbox1, bbox2, threshold=0.50):
    """Checks if two bounding boxes overlap with the given threshold."""
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    # Calculate the intersection area
    x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))

    # Calculate the area of overlap and area of both boxes
    intersection = x_overlap * y_overlap
    area1 = w1 * h1
    area2 = w2 * h2
    union = area1 + area2 - intersection

    # Return the overlap ratio
    return intersection / union > threshold



video_path = r"D:\troubleshooting\netholabs\original_videos\whiskers\original\tile_1_1_cropped.mp4"


imgs = read_img_batch_from_video_gpu(video_path=video_path, start_frm=551, end_frm=552, out_format='array')
img1 = imgs[0]
img2 = imgs[-1]

# Convert to grayscale and find edges (you can use any thresholding method)
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

edges1 = cv2.Canny(gray1, 10, 40)
edges2 = cv2.Canny(gray2, 10, 40)

# Find contours in both images
_, contours1, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
_, contours2, _ = cv2.findContours(edges2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Get bounding boxes for contours in both images
bboxes1 = contour_bboxes(contours1)
bboxes2 = contour_bboxes(contours2)

# Filter out contours in contours2 that overlap with contours1
new_contours2 = []
for i, bbox2 in enumerate(bboxes2):
    is_new = True
    for bbox1 in bboxes1:
        if overlap(bbox1, bbox2):  # Check if the bounding boxes overlap
            is_new = False
            break
    if is_new:
        new_contours2.append(contours2[i])

# Draw the new contours from image2 on a copy of img2
result = img2.copy()
cv2.drawContours(result, new_contours2, -1, (0, 255, 0), 2)

# Show the result
cv2.imshow("New Contours", result)
cv2.waitKey(0)
cv2.destroyAllWindows()