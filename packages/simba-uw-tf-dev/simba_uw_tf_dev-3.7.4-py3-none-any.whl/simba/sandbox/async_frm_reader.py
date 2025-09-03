import os
from typing import Union, Optional
import threading
from queue import Queue
import numpy as np

from simba.utils.read_write import get_video_meta_data,read_img_batch_from_video_gpu, read_img_batch_from_video
from simba.utils.checks import check_int, check_valid_boolean

class AsyncVideoFrameReader():

    def __init__(self,
                 video_path: Union[str, os.PathLike],
                 batch_size: int = 100,
                 max_que_size: int = 2,
                 start_idx: Optional[int] = None,
                 end_idx: Optional[int] = None,
                 gpu: bool = True,
                 verbose: bool = True,
                 greyscale: bool = False,
                 black_and_white: bool = False):

        self.video_meta_data = get_video_meta_data(video_path=video_path)
        self.start_idx = 0 if start_idx is None else start_idx
        self.end_idx = self.video_meta_data['frame_count'] if end_idx is None else end_idx
        check_int(name=f'{self.__class__.__name__} max_que_size', value=max_que_size, min_value=1, raise_error=True)
        check_int(name=f'{self.__class__.__name__} batch_size', value=batch_size, min_value=1, raise_error=True)
        check_valid_boolean(value=gpu, source=f'{self.__class__.__name__} gpu', raise_error=True)
        check_valid_boolean(value=verbose, source=f'{self.__class__.__name__} verbose', raise_error=True)
        check_valid_boolean(value=greyscale, source=f'{self.__class__.__name__} greyscale', raise_error=True)
        check_valid_boolean(value=black_and_white, source=f'{self.__class__.__name__} black_and_white', raise_error=True)
        self.frame_queue = Queue(maxsize=max_que_size)
        self.batch_size, self.video_path, self.gpu = batch_size, video_path, gpu
        self.verbose, self.greyscale, self.black_and_white = verbose, greyscale, black_and_white
        self.batch_end_idxs = np.append(np.arange(batch_size, self.end_idx, batch_size), self.end_idx)
        self._stop, self._thread = False, None

    def run(self):
        try:
            for batch_cnt, batch_end_idx in enumerate(self.batch_end_idxs):
                if self._stop:
                    break
                batch_start_idx = batch_end_idx - self.batch_size
                if self.gpu:
                    imgs = read_img_batch_from_video_gpu(video_path=self.video_path, start_frm=batch_start_idx, end_frm=batch_end_idx-1, greyscale=self.greyscale, black_and_white=self.black_and_white)
                else:
                    imgs = read_img_batch_from_video(video_path=self.video_path, start_frm=batch_start_idx, end_frm=batch_end_idx-1, greyscale=self.greyscale, black_and_white=self.black_and_white)
                imgs = np.stack(list(imgs.values()), axis=0)
                self.frame_queue.put((batch_start_idx, batch_end_idx, imgs))
                if self.verbose:
                    print(f'[{self.__class__.__name__}] ({self.video_meta_data["video_name"]}) frames queued {batch_start_idx}-{batch_end_idx-1}.')
        except Exception as e:
            if self.verbose:
                print(f"[{self.__class__.__name__}] ERROR: {e.args}")
            self.frame_queue.put(e)
        finally:
            self.frame_queue.put(None)

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self.run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop = True


    def kill(self) -> None:
        self.stop()
        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None
        with self.frame_queue.mutex:
            self.frame_queue.queue.clear()
        self.frame_queue, self.batch_end_idxs, self.video_meta_data  = None, None, None
        self.video_path, self._stop = None, None
        if self.verbose:
            print(f"[{self.__class__.__name__}] Reader thread killed and state cleared.")



video_path = "/mnt/c/troubleshooting/RAT_NOR/project_folder/videos/03152021_NOB_IOT_8.mp4"
runner = AsyncVideoFrameReader(video_path=video_path, batch_size=500)

reader_thread = threading.Thread(target=runner.run, daemon=True)
reader_thread.start()
#
# for i in range(20):
#     x = runner.frame_queue.get(timeout=10)
#     if x is None:
#         print('s')
#         break
#     elif isinstance(x, Exception):
#         print('ss')
#         raise x


            #self.end_idx = min(self.start_idx + self.batch_size, self.end_idx)
            #print(f"[Reader] Loading frames {self.start_idx}-{self.end_idx}...")
            #print(self.start_idx, self.end_idx)
            #self.start_idx = self.end_idx










