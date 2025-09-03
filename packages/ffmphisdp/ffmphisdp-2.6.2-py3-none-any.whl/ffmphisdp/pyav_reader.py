import logging
import typing

import av
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Avoid cv2 dependency by copying the values
cv2_CAP_PROP_POS_FRAMES = 1
cv2_CAP_PROP_FRAME_COUNT = 7


class ControlledVideoReader:
    def __init__(
        self,
        video_path: str,
        start_frame: int = 0,
        frame_infos: list[float] = None,
        frame_selection: list[bool] = None,
        video_stream_idx=0,
        **kwargs,
    ):
        self.logger = kwargs.pop('logger', logger)
        self.logger.info('Initializing ControlledVideoCapture')

        if 'fps' in kwargs:
            self.logger.info('use frame_infos and frame_selection instead of fps')
            raise ValueError('fps is not used anymore in this version')

        self.frame_infos = frame_infos
        self.frame_selection = frame_selection
        if self.frame_infos is None or self.frame_selection is None:
            raise ValueError('frame_infos and frame_selection are required')
        if 'ignore_editlist' not in kwargs:
            kwargs['ignore_editlist'] = 'True'
        self.video_path = video_path
        self.container = av.open(self.video_path, options={'ignore_editlist': kwargs['ignore_editlist']})
        self.video_stream_idx = video_stream_idx
        self.video_stream = self.container.streams.video[self.video_stream_idx]
        if len(self.container.streams.video) == 0:
            raise ValueError(f'No video stream found at {video_path}')
        if len(self.frame_infos) != len(self.frame_selection):
            msg = f'frame_infos ({len(self.frame_infos)}) != frame_selection ({len(self.frame_selection)})'
            raise ValueError(msg)
        if len(self.frame_infos) != self.video_stream.frames:
            msg = f'frame_infos ({len(self.frame_infos)}) != video_stream.frames ({self.video_stream.frames})'
            logging.warning(msg)
        self.selected_pts = {pts: selected for pts, selected in zip(self.frame_infos, self.frame_selection)}
        self.width = self.video_stream.width
        self.height = self.video_stream.height

        self.decoder = self.container.decode(video=self.video_stream_idx)
        self.pts_offset = 0
        self.current_frame = next(self.decoder)
        self.already_has_next = True
        self._current_frame_index = 0
        if self.current_frame.pts != self.frame_infos[0]:
            self.pts_offset = self.current_frame.pts - self.frame_infos[0]

        if start_frame != 0:
            self.set_frame_idx(start_frame)

    def read(self) -> typing.Tuple[bool, typing.Optional[np.ndarray]]:
        """Read the next frame from the video stream,
        return True if the frame was read successfully, False usually indicates end of stream
        return the frame as a numpy array of shape (height, width, 3) each color channel is a uint8

        """
        try:
            if not self.already_has_next:
                self.current_frame = next(self.decoder)
                self._current_frame_index += 1
            self.already_has_next = False
            while not (self.selected_pts.get(self.current_frame.pts - self.pts_offset, False)):
                self.current_frame = next(self.decoder)
            self._current_frame_index = self.frame_infos.index(self.current_frame.pts - self.pts_offset)
            rgb_frame = self.current_frame.to_rgb().to_ndarray().reshape([self.height, self.width, 3])
            return True, rgb_frame[..., [2, 1, 0]]
        except StopIteration:
            return False, None

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
        if frame_idx < 0 or frame_idx >= self.video_stream.frames:
            raise ValueError(f'frame_idx {frame_idx} out of range [0, {self.video_stream.frames})')
        pts = self.frame_infos[frame_idx] + self.pts_offset
        self.container.seek(int(pts), backward=True, any_frame=False, stream=self.video_stream)
        self.current_frame = next(self.decoder)
        while self.current_frame.pts < pts:
            self.current_frame = next(self.decoder)
        self.already_has_next = True
        self._current_frame_index = frame_idx

    def get(self, prop_id):
        """legacy method, avoid using as much as possible"""
        if prop_id == cv2_CAP_PROP_POS_FRAMES:
            return self.current_frame_index
        elif prop_id == cv2_CAP_PROP_FRAME_COUNT:
            return self.video_stream.frames
        else:
            raise NotImplementedError

    def set(self, prop_id, value):
        if prop_id == cv2_CAP_PROP_POS_FRAMES:
            self.set_frame_idx(value)
        else:
            raise NotImplementedError
