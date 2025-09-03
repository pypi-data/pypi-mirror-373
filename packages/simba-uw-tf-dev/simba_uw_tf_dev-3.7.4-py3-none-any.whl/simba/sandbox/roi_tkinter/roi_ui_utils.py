import numpy as np
from PIL import Image, ImageTk
from tkinter import *
from simba.utils.errors import InvalidInputError
import cv2




def get_image_from_label(tk_lbl: Label):
    """ Given a tkinter label with an image, retrieve image in array format"""

    if not hasattr(tk_lbl, 'image'):
        raise InvalidInputError(msg=f'The label {tk_lbl} does not have a valid image')
    else:
        tk_img = tk_lbl.image
        pil_image = ImageTk.getimage(tk_img)
        img = np.asarray(pil_image)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)