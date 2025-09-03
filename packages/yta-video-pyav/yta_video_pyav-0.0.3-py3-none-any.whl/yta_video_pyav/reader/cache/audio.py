
from yta_video_pyav.reader.cache import FrameCache
from yta_video_pyav.reader.cache.utils import trim_audio_frame
from yta_video_frame_time.t_fraction import THandler, get_audio_frame_duration
from yta_validation.parameter import ParameterValidator
from av.container import InputContainer
from av.audio.stream import AudioStream
from av.audio.frame import AudioFrame
from quicktions import Fraction
from typing import Union


class AudioFrameCache(FrameCache):
    """
    Cache for the audio frames.
    """

    @property
    def fps(
        self
    ) -> Union[Fraction, int]:
        """
        The frames per second.

        The formula:
        - `stream.rate`
        """
        return self.stream.rate

    def __init__(
        self,
        container: InputContainer,
        stream: AudioStream,
        size: Union[int, None] = None
    ):
        ParameterValidator.validate_mandatory_instance_of('stream', stream, AudioStream)

        super().__init__(container, stream, size)

        self._t_handler: THandler = THandler(self.fps, self.time_base)
        """
        Internal THandler instance to make time and
        pts conversions.
        """

    def _seek(
        self,
        pts: int
    ):
        """
        Seek to the given 'pts' only if it is not
        the next 'pts' to the last read, and it 
        will also apply a pad to avoid problems
        when reading audio frames.
        """
        # I found that it is recommended to
        # read ~100ms before the pts we want to
        # actually read so we obtain the frames
        # clean (this is important in audio).
        # This solves a problem I had related
        # to some artifacts on the audio when
        # trimming exactly without this pad.
        pts_pad = int(0.1 / self.time_base)
        self.container.seek(
            offset = max(0, pts - pts_pad),
            stream = self.stream
        )

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> AudioFrame:
        """
        Get the video frame that is in the 't'
        time moment provided.
        """
        t_start = self._t_handler.t.truncated(t)
        t_end = self._t_handler.t.next(t, 1, do_truncate = True)
        
        for frame in self.get_frames(t_start, t_end):
            return frame

    def get_frames(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        """
        Get all the audio frames in the range
        between the provided 'start' and 'end'
        time (in seconds).

        This method is an iterator that yields
        the frame, its t and its index.
        """
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)

        # Make sure the 'start' and 'end' time moments
        # provided are truncated values based on the
        # stream time base
        start = self._t_handler.t.truncated(start)
        end = self._t_handler.t.truncated(end)

        if end <= start:
            raise Exception(f'The time range start:{str(float(start))} - end:{str(float(end))}) is not valid.')
        
        key_frame_pts = self._get_nearest_keyframe_pts(self._t_handler.pts.from_t(start))

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

                # TODO: I need to refactor THandler and 
                # also remove some comments here below

                current_frame_start_t = self._t_handler.pts.to_t(frame.pts, do_truncate = True)
                duration = get_audio_frame_duration(frame.samples, self.fps)
                # End is not included, its the start of the
                # next frame actually
                current_frame_end_t = Fraction(current_frame_start_t + duration)

                # For the next comments imagine we are looking
                # for the [1.0, 2.0) audio time range
                # Previous frame and nothing is inside
                if current_frame_end_t <= start:
                    # From 0.25 to 1.0 => nothing
                    continue
                
                # We finished, nothing is inside and its after
                if current_frame_start_t >= end:
                    # From 2.0 to 2.75 => finished
                    return

                """
                If we need audio from 1 to 2, audio is:
                - from 0 to 0.75    (Not included, omit)
                - from 0.5 to 1.5   (Included, take 1.0 to 1.5)
                - from 0.5 to 2.5   (Included, take 1.0 to 2.0)
                - from 1.25 to 1.5  (Included, take 1.25 to 1.5)
                - from 1.25 to 2.5  (Included, take 1.25 to 2.0)
                - from 2.5 to 3.5   (Not included, omit)
                """
                
                # Here below, at least a part is inside
                if (
                    current_frame_start_t < start and
                    current_frame_end_t > start
                ):
                    # A part at the end is included
                    end_time = (
                        # From 0.5 to 1.5 => take 1.0 to 1.5
                        current_frame_end_t
                        if current_frame_end_t <= end else
                        # From 0.5 to 2.5 => take 1.0 to 2.0
                        end
                    )
                    #print('A part at the end is included.')
                    frame = trim_audio_frame(
                        frame = frame,
                        start = start,
                        end = end_time,
                        time_base = self.time_base
                    )
                elif (
                    current_frame_start_t >= start and
                    current_frame_start_t < end
                ):
                    end_time = (
                        # From 1.25 to 1.5 => take 1.25 to 1.5
                        current_frame_end_t
                        if current_frame_end_t <= end else
                        # From 1.25 to 2.5 => take 1.25 to 2.0
                        end
                    )
                    # A part at the begining is included
                    #print('A part at the begining is included.')
                    frame = trim_audio_frame(
                        frame = frame,
                        start = current_frame_start_t,
                        end = end_time,
                        time_base = self.time_base
                    )

                # If the whole frame is in just pass it
                yield frame