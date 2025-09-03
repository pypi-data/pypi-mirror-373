import cv2
import numpy as np
import torch
import bm4d
from simba.utils.read_write import read_img_batch_from_video_gpu
from skimage.restoration import denoise_wavelet
from skimage.restoration import denoise_nl_means
from skimage.util import img_as_float


def denoise_image_stack(img_stack, patch_size=5, patch_distance=6, h=0.1):
    """
    Denoise a stack of images using Non-Local Means denoising.

    :param img_stack: 3D numpy array where each slice is an image.
    :param patch_size: Size of the patch used for denoising.
    :param patch_distance: Maximum distance between patches for denoising.
    :param h: The filter strength.
    :return: Denoised image stack.
    """
    denoised_stack = []
    for cnt, img in enumerate(img_stack):
        # Ensure that the image is in float format
        img_float = img_as_float(img)
        print(cnt)
        denoised_img = denoise_nl_means(img_float, patch_size=patch_size, patch_distance=patch_distance, h=h)
        denoised_stack.append(denoised_img)

    return np.stack(denoised_stack)


video_path = "/mnt/d/OF_7/bg/cliopped/1.mp4"
save_path = "/mnt/d/OF_7/bg/cliopped/1.jpg"


imgs = read_img_batch_from_video_gpu(video_path=video_path, start_frm=0, end_frm=10)
imgs = np.stack(list(imgs.values()), axis=0)
denoise_image_stack(img_stack=imgs)



#
#
#
# gpu_imgs = torch.tensor(imgs).permute(0, 3, 1, 2).cuda() / 255.0
# denoised_imgs = wiener_filter(gpu_imgs, sigma=10)
# denoised_imgs_np = denoised_imgs.permute(0, 2, 3, 1).cpu().numpy() * 255
# print(denoised_imgs_np.shape)
# print(denoised_imgs_np[0])
#
# cv2.imwrite(save_path, denoised_imgs_np[5].astype(np.uint8))
#
# #
# # cv2.imshow('asdasdasd', denoised_imgs_np[0])
# # cv2.waitKey(30000)