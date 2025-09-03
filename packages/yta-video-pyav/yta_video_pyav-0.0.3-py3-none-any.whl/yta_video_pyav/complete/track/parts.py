from yta_video_pyav.complete.track.media import AudioOnTrack, VideoOnTrack
from yta_video_pyav.complete.track.utils import generate_silent_frames
from yta_video_pyav.complete.frame_wrapper import AudioFrameWrapped
from yta_video_pyav.complete.frame_wrapper import VideoFrameWrapped
from yta_video_pyav.complete.frame_generator import VideoFrameGenerator, AudioFrameGenerator
from yta_video_frame_time.t_fraction import fps_to_time_base
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union
from abc import ABC


NON_LIMITED_EMPTY_PART_END = 999
"""
A value to indicate that the empty part
has no end because it is in the last
position and there is no video after it.
"""

class _Part(ABC):
    """
    Abstract class to represent an element
    that is on the track, that can be an
    empty space or a vide or audio. This
    class must be inherited by our own
    custom part classes.
    """

    @property
    def is_empty_part(
        self
    ) -> bool:
        """
        Flag to indicate if the part is an empty part,
        which means that there is no media associated
        but an empty space.
        """
        return self.media is None

    def __init__(
        self,
        track: Union['AudioTrack', 'VideoTrack'],
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union[AudioOnTrack, VideoOnTrack, None] = None
    ):
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)
        ParameterValidator.validate_instance_of('audimediao', media, [AudioOnTrack, VideoOnTrack])

        self._track: Union['AudioTrack', 'VideoTrack'] = track
        """
        The instance of the track this part belongs
        to.
        """
        self.start: Fraction = Fraction(start)
        """
        The start 't' time moment of the part.
        """
        self.end: Fraction = Fraction(end)
        """
        The end 't' time moment of the part.
        """
        self.media: Union[AudioOnTrack, VideoOnTrack, None] = media
        """
        The media associated, if existing, or
        None if it is an empty space that we need
        to fulfill.
        """

class _PartWithAudio(_Part):
    """
    TODO: Explain
    """

    def __init__(
        self,
        track: Union['AudioTrack', 'VideoTrack'],
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union[AudioOnTrack, VideoOnTrack, None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, [AudioOnTrack, VideoOnTrack])

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )

        # TODO: Can I refactor this below (?)
        self._audio_frame_generator: AudioFrameGenerator = AudioFrameGenerator()
        """
        Useful internal tool to generate silent
        audio frames for the empty parts.
        """

    def get_audio_frames_at(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Iterate over all the audio frames that
        exist at the time moment 't' provided.
        """
        frames = []
        if not self.is_empty_part:
            # TODO: What do we do in this case (?)
            frames = list(self.media.get_audio_frames_at(t))

            if len(frames) == 0:
                print(f'   [ERROR] Audio frame {str(float(t))} was not obtained')
            else:
                frames = [
                    AudioFrameWrapped(
                        frame = frame,
                        is_from_empty_part = False
                    )
                    for frame in frames
                ]

        # This could be because is empty part or
        # because we couldn't obtain the frames
        if len(frames) == 0:
            frames = generate_silent_frames(
                fps = self._track.fps,
                audio_fps = self._track.audio_fps,
                audio_samples_per_frame = self._track.audio_samples_per_frame,
                # TODO: Where do this 2 formats come from (?)
                layout = self._track.audio_layout,
                format = self._track.audio_format
            )

        for frame in frames:
            yield frame

class _PartWithVideo(_Part):
    """
    TODO: Explain
    """

    def __init__(
        self,
        track: 'VideoTrack',
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union[VideoOnTrack, None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, VideoOnTrack)

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )

        # TODO: Can I refactor this below (?)
        self._video_frame_generator: VideoFrameGenerator = VideoFrameGenerator()
        """
        Useful internal tool to generate background
        frames for the empty parts.
        """

    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrameWrapped':
        """
        Get the frame that must be displayed at 
        the given 't' time moment.
        """
        is_from_empty_part = False
        if self.is_empty_part:
            frame = self._video_frame_generator.background.full_black(
                size = self._track.size,
                time_base = fps_to_time_base(self._track.fps)
            )

            is_from_empty_part = True
        else:
            # TODO: This can be None, why? I don't know...
            frame = self.media.get_frame_at(t)

            if frame is None:
                print(f'   [ERROR] Frame {str(float(t))} was not obtained')

            frame = (
                # I'm using a red full frame to be able to detect
                # fast the frames that were not available, but
                # I need to find the error and find a real solution
                self._video_frame_generator.background.full_red(
                    size = self._track.size,
                    time_base = fps_to_time_base(self._track.fps)
                )
                if frame is None else
                frame
            )

        # TODO: What about the 'format' (?)
        # TODO: Maybe I shouldn't set the 'time_base'
        # here and do it just in the Timeline 'render'
        #return get_black_background_video_frame(self._track.size)
        # TODO: This 'time_base' maybe has to be related
        # to a Timeline general 'time_base' and not the fps
        frame = VideoFrameWrapped(
            frame = frame,
            is_from_empty_part = is_from_empty_part
        )

        # TODO: This should not happen because of
        # the way we handle the videos here but the
        # video could send us a None frame here, so
        # do we raise exception (?)
        if frame._frame is None:
            #frame = get_black_background_video_frame(self._track.size)
            # TODO: By now I'm raising exception to check if
            # this happens or not because I think it would
            # be malfunctioning
            raise Exception(f'Video is returning None video frame at t={str(t)}.')
        
        return frame

class _AudioPart(_PartWithAudio):
    """
    Class to represent an element that is on the
    track, that can be an empty space or an audio.
    """

    def __init__(
        self,
        track: 'AudioTrack',
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union[AudioOnTrack, None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, AudioOnTrack)

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )

class _VideoPart(_PartWithAudio, _PartWithVideo):
    """
    Class to represent an element that is on the
    track, that can be an empty space or a video.
    """

    def __init__(
        self,
        track: 'VideoTrack',
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        media: Union[VideoOnTrack, None] = None
    ):
        ParameterValidator.validate_instance_of('media', media, VideoOnTrack)

        super().__init__(
            track = track,
            start = start,
            end = end,
            media = media
        )