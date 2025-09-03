"""This module contains a class to read a video stream from a file or a url and control the output framerate"""

import logging
import math
import time
import typing

import ffmpeg  # type: ignore
import numpy as np  # type: ignore

from ffmphisdp.utils import Timeout

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Avoid cv2 dependency by copying the values
cv2_CAP_PROP_POS_FRAMES = 1
cv2_CAP_PROP_FRAME_COUNT = 7


class ControlledFPSVideoCapture:
    """
    Video Reader from any input fps (CFR or VFR) to any output fps (CFR).
    """

    def __init__(self, video_path: str, start_frame: int = 0, start_time: int = 0, fps: int = 10, **kwargs):
        self.logger = kwargs.pop('logger', logger)
        message = f'Initializing ControlledFPSVideoCapture with output_fps={fps}'
        self.logger.info(message)

        self.video_path = video_path
        self.output_fps = fps

        self.quiet = True
        if 'quiet' in kwargs:
            self.quiet = kwargs.pop('quiet')
        try:
            self.probe = ffmpeg.probe(video_path)
        except Exception as exc:
            raise Exception(f'ffmpeg probe failed to read video file at {video_path}') from exc
        for stream in self.probe['streams']:
            if stream['codec_type'] == 'video':
                self.video_stream = stream
                break
        else:
            raise ValueError(f'No video stream found at {video_path}')
        self.width = self.video_stream['width']
        self.height = self.video_stream['height']

        self.framerate_process = None
        self._prepare_process(start_frame=start_frame, start_time=start_time)

    def _prepare_process(self, start_frame: int = 0, start_time: int = 0):
        """Prepare the ffmpeg process to stream the video from the given frame index or time in ms"""
        if start_frame != 0 and start_time != 0:
            raise ValueError('Cannot set both start_frame and start_time')
        if self.framerate_process is not None:
            self.framerate_process.terminate()
        self._current_frame_index = -1
        process = ffmpeg.input(self.video_path)
        if self.output_fps != 'same':
            process = process.filter('fps', fps=self.output_fps)
        if start_frame > 0:
            self._current_frame_index = start_frame - 1
            process = process.filter_('select', f'gte(n,{start_frame})')
            process = process.filter_('setpts', 'PTS-STARTPTS')
        elif start_time > 0:
            self._current_frame_index = math.ceil(start_time * self.output_fps / 1000) - 1
            process = process.filter_('select', f'gte(t,{start_time / 1000})')
            process = process.filter_('setpts', 'PTS-STARTPTS')
        self.framerate_process = process.output('pipe:', format='rawvideo', pix_fmt='bgr24').run_async(
            pipe_stdout=True, quiet=self.quiet
        )
        if self.framerate_process is None:
            raise ValueError('Failed to start ffmpeg process')
        self.logger.debug(self.framerate_process.args)

    def __del__(self):
        if self.framerate_process is not None:
            self.framerate_process.terminate()

    def read(self) -> typing.Tuple[bool, typing.Optional[np.ndarray]]:
        """Read the next frame from the video stream,
        return True if the frame was read successfully, False usually indicates end of stream
        return the frame as a numpy array of shape (height, width, 3) each color channel is a uint8

        """
        self._current_frame_index += 1
        if self.framerate_process is None:
            raise ValueError('The stream is not initialized')

        if self.quiet and self._current_frame_index % 100 == 0:
            # We only flush once in a while to reduce the overhead of the flush
            self._flush_stderr()
        in_bytes = self.framerate_process.stdout.read(self.width * self.height * 3)
        if not in_bytes:
            return False, None
        in_frame = np.frombuffer(in_bytes, np.uint8).reshape([self.height, self.width, 3])
        return True, in_frame

    @property
    def current_frame_index(self):
        """Return the current frame index of the stream, this is the index of the last frame read"""
        return self._current_frame_index

    @property
    def output_frame(self):
        """Legacy name for the current_frame_index property"""
        return self._current_frame_index

    def set_frame_idx(self, frame_idx: int):
        """Change the current frame of the stream to read from the given frame index"""
        self._prepare_process(start_frame=frame_idx)

    def set_time_ms(self, time_ms: int):
        """Change the current frame of the stream to read from the given time in ms"""
        self._prepare_process(start_time=time_ms)

    def get(self, prop_id):
        """legacy method, avoid using as much as possible"""
        if prop_id == cv2_CAP_PROP_POS_FRAMES:
            return self.current_frame_index
        elif prop_id == cv2_CAP_PROP_FRAME_COUNT:
            if 'format' in self.probe and 'duration' in self.probe['format']:
                duration = float(self.probe['format']['duration'])
                return int(math.floor(duration * self.output_fps))
            self.logger.warning('Could not get frame count from framerate converted video')
            return None
        else:
            raise NotImplementedError

    def set(self, prop_id, value):
        if prop_id == cv2_CAP_PROP_POS_FRAMES:
            self.set_frame_idx(value)
        else:
            raise NotImplementedError

    # ruff: noqa: SIM105
    def _flush_stderr(self):
        with Timeout(0.001):
            while True:
                self.framerate_process.stderr.read(1000)
        try:
            time.sleep(0.001)
        except Timeout.TimeoutException:
            pass
