from simba.utils.checks import check_valid_dict, check_int, check_str
from copy import copy
def get_labelling_video_kbd_bindings() -> dict:
    """
    Returns a dictionary of OpenCV-compatible keyboard bindings for video labeling.

    Notes:
        - Change the `kbd` values to customize keyboard shortcuts.
        - OpenCV key codes differ from Tkinter bindings (see `get_labelling_img_kbd_bindings`).
        - Use either single-character strings (e.g. 'p') or integer ASCII codes (e.g. 32 for space bar).

    Examples:
        Remap space bar to Pause/Play:
            {'Pause/Play': {'label': 'Space = Pause/Play', 'kbd': 32}}
    """
    bindings = {
        'Pause/Play': {
            'label': 'p = Pause/Play',
            'kbd': 'p'
        },
        'forward_two_frames': {
            'label': 'o = +2 frames',
            'kbd': 'o'
        },
        'forward_ten_frames': {
            'label': 'e = +10 frames',
            'kbd': 'e'
        },
        'forward_one_second': {
            'label': 'w = +1 second',
            'kbd': 'w'
        },
        'backwards_two_frames': {
            'label': 't = -2 frames',
            'kbd': 't'
        },
        'backwards_ten_frames': {
            'label': 's = -10 frames',
            'kbd': 's'
        },
        'backwards_one_second': {
            'label': 'x = -1 second',
            'kbd': 'x'
        },
        'close_window': {
            'label': 'q = Close video window',
            'kbd': 'q'
        },
    }


    #PERFORM CHECKS THAT BINDINGS ARE DEFINED CORRECTLY.
    check_valid_dict( x=bindings, valid_key_dtypes=(str,), valid_values_dtypes=(dict,), source=f'{get_labelling_video_kbd_bindings.__name__} bindings')
    cleaned_bindings = {}
    for action, config in bindings.items():
        check_valid_dict(x=config, valid_key_dtypes=(str,), valid_values_dtypes=(str, int), required_keys=('label', 'kbd'))
        kbd_val = config['kbd']
        check_str(value=config['label'], allow_blank=False, raise_error=True)
        if check_int(name=f'{action} kbd', value=kbd_val, raise_error=False)[0]:
            new_config = copy(config)
            new_config['kbd'] = int(kbd_val)
            cleaned_bindings[action] = new_config
        else:
            cleaned_bindings[action] = config

    return cleaned_bindings