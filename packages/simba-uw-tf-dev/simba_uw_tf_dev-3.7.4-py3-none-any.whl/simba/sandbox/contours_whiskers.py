from simba.utils.read_write import read_img_batch_from_video_gpu, get_video_meta_data
import cv2
import numpy as np
from simba.mixins.image_mixin import ImageMixin
from simba.mixins.geometry_mixin import GeometryMixin
from simba.utils.enums import Formats
def get_unique_contours(contours2, contours1):
    unique = []
    for c2 in contours2:
        if not any(np.array_equal(c2, c1) for c1 in contours1):
            unique.append(c2)
    return unique


video_path = r"D:\weights\bg_remove\4_sam.avi"

fourcc = cv2.VideoWriter_fourcc(*Formats.MP4_CODEC.value)
SAVE_PATH = r"D:\troubleshooting\netholabs\original_videos\whiskers\out_video\step_7.mp4"

imgs = read_img_batch_from_video_gpu(video_path=video_path, out_format='array', greyscale=False)

video_meta_data = get_video_meta_data(video_path=video_path)
video_writer = cv2.VideoWriter(SAVE_PATH, fourcc, 30, (video_meta_data["width"], video_meta_data["height"]))

for img_idx in range(imgs.shape[0]):
    img = cv2.cvtColor(imgs[img_idx], cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(img, 10, 200)
    _, contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    results = imgs[img_idx].copy()
    results = cv2.drawContours(results, contours, -1, (0, 255, 0), 2)
    #video_writer.write(results.astype(np.uint8))
    cv2.imshow("Unique Contours", results)

    cv2.waitKey(33)
    #cv2.destroyAllWindows()

video_writer.release()

img1 = imgs[0]
img2 = imgs[-1]

gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)




gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# Apply edge detection
edges1 = cv2.Canny(gray1, 10, 30)
edges2 = cv2.Canny(gray2, 10, 30)

# Find contours (note: return signature varies by OpenCV version)
_, contours1, _ = cv2.findContours(edges1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
_, contours2, _ = cv2.findContours(edges2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Keep only contours in image2 that are NOT in image1
unique_contours = get_unique_contours(contours2, contours1)

# Draw the unique contours on img2
result = img2.copy()
cv2.drawContours(result, contours1, -1, (0, 255, 0), 2)

# Show the result
cv2.imshow("Unique Contours", result)
cv2.waitKey(0)
cv2.destroyAllWindows()


#
# diff = cv2.absdiff(test_img_2, test_img_1)
#
# _, thresh = cv2.threshold(diff, 10, 30, cv2.THRESH_BINARY)
# thresh = cv2.dilate(thresh, None, iterations=2)
# thresh_gray = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
#
# thresh = thresh.astype(np.uint8)
# print(thresh.shape, thresh.dtype)
#
# _, contours, _ = cv2.findContours(thresh_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
# output = test_img_2.copy()
# output = cv2.drawContours(output, contours, -1, (0, 255, 0), thickness=2)
#
# cv2.imshow("Contours Overlay", output)
# cv2.waitKey(0)
#
# test_img_1 = cv2.GaussianBlur(test_img_1, (3, 3), 0)
#
# edges = cv2.Canny(test_img_1, threshold1=5, threshold2=20)
#
# contours = ImageMixin.find_contours(img=edges, mode='all', method='simple')
#
# output_img = test_img_1.copy()
# output_img = cv2.drawContours(output_img, contours, -1, (0, 255, 0), 2)


#
# img_1 = ImageMixin.canny_edge_detection(img=imgs[0], l2_gradient=False, threshold_1=5, threshold_2=35)
# img_2 = ImageMixin.canny_edge_detection(img=imgs[1], l2_gradient=False, threshold_1=5, threshold_2=35)
#
# mathed = cv2.matchShapes(img_1[0], img_2[0], cv2.CONTOURS_MATCH_I1, 0.0)
#
#
# # contours = ImageMixin.find_contours(img=test_img)
# #
# # geometries = GeometryMixin.contours_to_geometries(contours=contours, force_rectangles=False, convex_hull=True)
# #
# # out_img = GeometryMixin.view_shapes(shapes=geometries, bg_img=test_img)
# #
# cv2.imshow('asdasdasd', img)
# cv2.waitKey(0)
