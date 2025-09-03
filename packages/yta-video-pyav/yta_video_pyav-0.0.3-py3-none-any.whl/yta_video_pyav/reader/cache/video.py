
from yta_video_pyav.reader.cache import FrameCache
from yta_video_frame_time.t_fraction import THandler
from yta_validation.parameter import ParameterValidator
from av.container import InputContainer
from av.video.stream import VideoStream
from av.video.frame import VideoFrame
from quicktions import Fraction
from typing import Union


class VideoFrameCache(FrameCache):
    """
    Cache for the video frames.
    """

    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The frames per second.
        """
        return self.stream.average_rate

    @property
    def frame_duration(
        self
    ) -> int:
        """
        The frame duration in ticks, which is the
        minimum amount of time, 1 / time_base.
        """
        return self.stream.duration / self.stream.frames
    
    def __init__(
        self,
        container: InputContainer,
        stream: VideoStream,
        size: Union[int, None] = None
    ):
        ParameterValidator.validate_mandatory_instance_of('stream', stream, VideoStream)

        super().__init__(container, stream, size)

        self._t_handler: THandler = THandler(self.fps, self.time_base)
        """
        Internal THandler instance to make time and
        pts conversions.
        """

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame that is in the 't'
        time moment provided.
        """
        t_start = self._t_handler.t.truncated(t)
        t_end = self._t_handler.t.next(t, 1, do_truncate = True)
        
        print(f'Getting frame from {str(float(t))}')
        print(f'FPS: {str(self.fps)}')
        print(f'So the actual frame is from {str(float(t_start))} to {str(float(t_end))}')
        for frame in self.get_frames(t_start, t_end):
            return frame

    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        """
        Get all the frames in the range between
        the provided 'start' and 'end' time in
        seconds.

        This method is an iterator that yields
        the frame, its t and its index.
        """
        # TODO: Validate 'start' and 'end' are mandatory
        # positive numbers
        # Make sure the 'start' and 'end' time moments
        # provided are truncated values based on the
        # stream time base
        start = self._t_handler.t.truncated(start)
        end = self._t_handler.t.truncated(end)

        if end <= start:
            raise Exception(f'The time range start:{str(float(start))} - end:{str(float(end))}) is not valid.')
        
        key_frame_pts = self._get_nearest_keyframe_pts(start / self.time_base)

        if (
            self._last_packet_accessed is None or
            self._last_packet_accessed.pts != key_frame_pts
        ):
            self._seek(key_frame_pts)

        for packet in self.container.demux(self.stream):
            if packet.pts is None:
                continue

            self._last_packet_accessed = packet

            for frame in packet.decode():
                if frame.pts is None:
                    continue

                # We store all the frames in cache
                self._store_frame_in_cache(frame)
                
                current_frame_start_t = self._t_handler.pts.to_t(frame.pts, do_truncate = True)
                
                # We want the range [start, end)
                if start <= current_frame_start_t < end:
                    yield frame

                if current_frame_start_t >= end:
                    break