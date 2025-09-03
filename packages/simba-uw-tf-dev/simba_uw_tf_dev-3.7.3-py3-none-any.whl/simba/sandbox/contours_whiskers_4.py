from simba.utils.read_write import read_img_batch_from_video_gpu, get_video_meta_data, read_frm_of_video
import cv2
import numpy as np
video_path = r"C:\Users\sroni\Downloads\best_80mil_2.h264"
from simba.mixins.image_mixin import ImageMixin

#video_meta_data = get_video_meta_data(video_path=video_path)


for i in range(0, 221):
    img = read_frm_of_video(video_path=video_path, frame_index=i, use_ffmpeg=True)
    #bw = ImageMixin.img_to_bw(img=img, upper_thresh=250, lower_thresh=37)

    #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #black_pixels = np.all(img == [0, 0, 0], axis=-1)
    #out = np.ones_like(img) * 255
    #out[black_pixels] = [0, 0, 0]
#
#
    ## img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ## edges = cv2.Canny(img, 5, 10)
    ## _, contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
    cv2.imshow("Unique Contours", img)
    cv2.waitKey(33)
