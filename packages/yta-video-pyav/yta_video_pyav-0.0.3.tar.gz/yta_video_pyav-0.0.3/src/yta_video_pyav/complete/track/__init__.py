
from yta_video_pyav.complete.track.media import AudioOnTrack, VideoOnTrack
from yta_video_pyav.complete.track.parts import _AudioPart, _VideoPart, NON_LIMITED_EMPTY_PART_END
from yta_video_pyav.complete.track.utils import generate_silent_frames
from yta_video_pyav.audio import Audio
from yta_video_frame_time.t_fraction import THandler
from yta_validation.parameter import ParameterValidator
from quicktions import Fraction
from typing import Union
from abc import ABC, abstractmethod


class _Track(ABC):
    """
    Abstract class to be inherited by the
    different track classes we implement.
    """

    @property
    def parts(
        self
    ) -> list[Union['_AudioPart', '_VideoPart']]:
        """
        The list of parts that build this track,
        but with the empty parts detected to 
        be fulfilled with black frames and silent
        audios.

        A part can be a video or an empty space.
        """
        if (
            not hasattr(self, '_parts') or
            self._parts is None
        ):
            self._recalculate_parts()

        return self._parts
    
    @property
    def end(
        self
    ) -> Fraction:
        """
        The end of the last audio of this track,
        which is also the end of the track. This
        is the last time moment that has not to
        be rendered because its the end and it
        is not included -> [start, end).
        """
        return Fraction(
            max(
                (
                    media.end
                    for media in self.medias
                ),
                default = 0.0
            )
        )
    
    @property
    def medias(
        self
    ) -> list[AudioOnTrack]:
        """
        The list of medias we have in the track
        but ordered using the 'start' attribute
        from first to last.
        """
        return sorted(self._medias, key = lambda media: media.start)
    
    @property
    def is_muted(
        self
    ) -> bool:
        """
        Flag to indicate if the track is muted or
        not. Being muted means that no audio frames
        will be retured from this track.
        """
        return self._is_muted
    
    def __init__(
        self,
        index: int
    ):
        self._medias: list['AudioOnTrack', 'VideoOnTrack'] = []
        """
        The list of 'AudioOnTrack' or 'VideoOnTrack'
        instances that must be played on this track.
        """
        self._is_muted: bool = False
        """
        Internal flag to indicate if the track is
        muted or not.
        """
        self.index: int = index
        """
        The index of the track within the timeline.
        """

    def _is_free(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ) -> bool:
        """
        Check if the time range in between the 
        'start' and 'end' time given is free or
        there is some media playing at any moment.
        """
        return not any(
            (
                media.start < end and
                media.end > start
            )
            for media in self.medias
        )
    
    def _get_part_at_t(
        self,
        t: Union[int, float, Fraction]
    ) -> Union['_AudioPart', '_VideoPart']:
        """
        Get the part at the given 't' time
        moment, that will always exist because
        we have an special non ended last 
        empty part that would be returned if
        accessing to an empty 't'.
        """
        for part in self.parts:
            if part.start <= t < part.end:
                return part
            
        # TODO: This will only happen if they are
        # asking for a value greater than the
        # NON_LIMITED_EMPTY_PART_END...
        raise Exception('NON_LIMITED_EMPTY_PART_END exceeded.')
        return None
    
    def mute(
        self
    ) -> 'AudioTrack':
        """
        Set the track as muted so no audio frame will
        be played from this track.
        """
        self._is_muted = True

    def unmute(
        self
    ) -> 'AudioTrack':
        """
        Set the track as unmuted so the audio frames
        will be played as normal.
        """
        self._is_muted = False

    def add_media(
        self,
        media: Union['Audio', 'Video'],
        t: Union[int, float, Fraction, None] = None
    ) -> '_Track':
        """
        Add the 'media' provided to the track. If
        a 't' time moment is provided, the media
        will be added to that time moment if 
        possible. If there is no other media 
        placed in the time gap between the given
        't' and the provided 'media' duration, it
        will be added succesfully. In the other
        case, an exception will be raised.

        If 't' is None, the first available 't'
        time moment will be used, that will be 0.0
        if no media, or the end of the last media.
        """
        ParameterValidator.validate_mandatory_instance_of('media', media, ['Audio', 'Video'])
        ParameterValidator.validate_positive_number('t', t, do_include_zero = True)

        if t is not None:
            # TODO: We can have many different strategies
            # that we could define in the '__init__' maybe
            thandler = THandler(self.fps)
            t_start = thandler.t.truncated(t)
            # TODO: What about the 'media.duration', is
            # it accurate (?)
            t_end = thandler.t.next(t, 1, do_truncate = True) + media.duration
            if not self._is_free(t_start, t_end):
                raise Exception('The media cannot be added at the "t" time moment, something blocks it.')
        else:
            t = self.end

        self._medias.append(self._make_media_on_track(
            media = media,
            start = t
        ))

        self._recalculate_parts()

        # TODO: Maybe return the AudioOnTrack instead (?)
        return self

    @abstractmethod
    def _make_part(
        self,
        **kwargs
    ):
        """
        Factory method to return an instance of the
        '_Part' class that the specific '_Track' class
        is using.
        """
        pass

    @abstractmethod
    def _make_media_on_track(
        self,
        **kwargs
    ):
        """
        Factory method to return an instance of the
        'MediaOnTrack' class that the specific '_Track'
        class is using.
        """
        pass

    def _recalculate_parts(
        self
    ) -> '_Track':
        """
        Check the track and get all the parts. A
        part can be empty (no audio or video on
        that time period, which means silent audio
        or black frame), or a video or audio.
        """
        parts = []
        cursor = 0.0

        for media in self.medias:
            # Empty space between cursor and start of
            # the next clip
            if media.start > cursor:
                parts.append(self._make_part(
                    track = self,
                    start = cursor,
                    end = media.start,
                    media = None
                ))

            # The media itself
            parts.append(self._make_part(
                track = self,
                start = media.start,
                end = media.end,
                media = media
            ))
            
            cursor = media.end

        # Add the non limited last empty part
        parts.append(self._make_part(
            track = self,
            start = cursor,
            end = NON_LIMITED_EMPTY_PART_END,
            media = None
        ))

        self._parts = parts

        return self
    
class _TrackWithAudio(_Track):
    """
    Class that has the ability to obtain the
    audio frames from the source and must be
    inherited by those tracks that have audio
    (or video, that includes audio).
    """

    def __init__(
        self,
        index: int,
        fps: float,
        audio_fps: float,
        # TODO: Where does it come from (?)
        audio_samples_per_frame: int,
        audio_layout: str = 'stereo',
        audio_format: str = 'fltp'
    ):
        _Track.__init__(
            self,
            index = index
        )

        self.fps: float = float(fps)
        """
        The fps of the the video that is associated
        with the Timeline this track belongs to,
        needed to calculate the base t time moments
        to be precise and to obtain or generate the
        frames.
        """
        self.audio_fps: float = float(audio_fps)
        """
        The fps of the audio track, needed to 
        generate silent audios for the empty parts.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The number of samples per audio frame.
        """
        self.audio_layout: str = audio_layout
        """
        The layout of the audio, that can be 'mono'
        or 'stereo'.
        """
        self.audio_format: str = audio_format
        """
        The format of the audio, that can be 's16',
        'flt', 'fltp', etc.
        """

    # TODO: This is not working well when
    # source has different fps
    def get_audio_frames_at(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames that
        must be displayed at the 't' time 
        moment provided, which the collection
        of audio frames corresponding to the
        audio that is being played at that time
        moment.

        Remember, this 't' time moment provided
        is about the track, and we make the
        conversion to the actual audio 't' to
        get the frame.
        """
        frames = (
            generate_silent_frames(
                fps = self.fps,
                audio_fps = self.audio_fps,
                audio_samples_per_frame = self.audio_samples_per_frame,
                layout = self.audio_layout,
                format = self.audio_format
            )
            if self.is_muted else
            # TODO: What if we find None here (?)
            self._get_part_at_t(t).get_audio_frames_at(t)
        )

        for frame in frames:
            print('      HELLO       ')
            print(frame)
            if frame == []:
                print(f'   [ERROR] Audio frame t:{str(float(t))} not obtained.')
            yield frame

class _TrackWithVideo(_Track):
    """
    Class that has the ability to obtain the
    video frames from the source and must be
    inherited by those tracks that have video.
    """

    def __init__(
        self,
        index: int,
        size: tuple[int, int],
        fps: float
    ):
        _Track.__init__(
            self,
            index = index
        )

        # TODO: This is not needed actually...
        self.fps: float = float(fps)
        """
        The fps of the the video that is associated
        with the Timeline this track belongs to,
        needed to calculate the base t time moments
        to be precise and to obtain or generate the
        frames.
        """
        self.size: tuple[int, int] = size
        """
        The size that the output video will have.
        """

    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrameWrapped':
        """
        Get the frame that must be displayed at
        the 't' time moment provided, which is
        a frame from the video audio that is
        being played at that time moment.

        Remember, this 't' time moment provided
        is about the track, and we make the
        conversion to the actual video 't' to
        get the frame.
        """
        # TODO: What if the frame, that comes from
        # a video, doesn't have the expected size (?)
        return self._get_part_at_t(t).get_frame_at(t)
    
class AudioTrack(_TrackWithAudio):
    """
    Class to represent a track in which we place
    audios to build a video project.
    """

    def __init__(
        self,
        index: int,
        fps: float,
        audio_fps: float,
        # TODO: Where does it come from (?)
        audio_samples_per_frame: int,
        audio_layout: str = 'stereo',
        audio_format: str = 'fltp'
    ):
        _TrackWithAudio.__init__(
            index = index,
            fps = fps,
            audio_fps = audio_fps,
            audio_samples_per_frame = audio_samples_per_frame,
            audio_layout = audio_layout,
            audio_format = audio_format
        )

    def _make_part(
        self,
        **kwargs
    ):
        return _AudioPart(**kwargs)
    
    def _make_media_on_track(
        self,
        **kwargs
    ):
        return AudioOnTrack(**kwargs)

class VideoTrack(_TrackWithVideo, _TrackWithAudio):
    """
    Class to represent a track in which we place
    videos to build a video project.
    """

    def __init__(
        self,
        index: int,
        size: tuple[int, int],
        fps: float,
        audio_fps: float,
        # TODO: Where does it come from (?)
        audio_samples_per_frame: int,
        audio_layout: str = 'stereo',
        audio_format: str = 'fltp',
    ):
        # super().__init__(
        #     index = index,
        #     size = size,
        #     fps = fps,
        #     audio_fps = audio_fps,
        #     audio_samples_per_frame = audio_samples_per_frame,
        #     audio_layout = audio_layout,
        #     audio_format = audio_format
        # )
        _TrackWithVideo.__init__(
            self,
            index = index,
            size = size,
            fps = fps
        )
        _TrackWithAudio.__init__(
            self,
            index = index,
            fps = fps,
            audio_fps = audio_fps,
            audio_samples_per_frame = audio_samples_per_frame,
            audio_layout = audio_layout,
            audio_format = audio_format
        )
        
    def _make_part(
        self,
        **kwargs
    ):
        return _VideoPart(**kwargs)
    
    def _make_media_on_track(
        self,
        **kwargs
    ):
        return VideoOnTrack(**kwargs)