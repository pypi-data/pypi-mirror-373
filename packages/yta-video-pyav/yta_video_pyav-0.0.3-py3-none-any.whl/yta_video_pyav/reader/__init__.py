"""
A video reader using the PyAv (av) library
that, using ffmpeg, detects the video and
audio streams from a filename (that can be
a video file including both streams or an
audio file including only the audio stream).
"""
from yta_video_pyav.reader.cache.video import VideoFrameCache
from yta_video_pyav.reader.cache.audio import AudioFrameCache
from yta_video_frame_time.t_fraction import THandler
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from av.packet import Packet
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from av.container.input import InputContainer
from quicktions import Fraction
from av import open as av_open
from typing import Union
from dataclasses import dataclass


@dataclass
class VideoReaderFrame:
    """
    Class to wrap a frame of a video that is
    being read, that can be a video or audio
    frame, and has been decoded.
    """

    @property
    def is_video(
        self
    ):
        """
        Flag to indicate if the instance is a video
        frame.
        """
        return PythonValidator.is_instance_of(self.value, VideoFrame)
    
    @property
    def is_audio(
        self
    ):
        """
        Flag to indicate if the instance is an audio
        frame.
        """
        return PythonValidator.is_instance_of(self.value, AudioFrame)
    
    @property
    def as_numpy(
        self
    ):
        """
        The frame as a numpy array.
        """
        return self.value.to_ndarray(format = self.pixel_format)
    
    def __init__(
        self,
        # TODO: Add the type, please
        frame: any,
        t: Union[int, float, Fraction] = None,
        pixel_format: str = 'rgb24'
    ):
        self.value: Union[AudioFrame, VideoFrame] = frame
        """
        The frame content, that can be audio or video
        frame.
        """
        self.t: Fraction = Fraction(t)
        """
        The 't' time moment of the frame.
        """
        self.pixel_format: str = pixel_format
        """
        The pixel format of the frame.
        """

@dataclass
class VideoReaderPacket:
    """
    Class to wrap a packet of a video that is
    being read, that can contain video or audio
    frames.
    """

    @property
    def is_video(
        self
    ) -> bool:
        """
        Flag to indicate if the packet includes video
        frames or not.
        """
        return self.value.stream.type == 'video'
    
    @property
    def is_audio(
        self
    ) -> bool:
        """
        Flag to indicate if the packet includes audio
        frames or not.
        """
        return self.value.stream.type == 'audio'

    def __init__(
        self,
        packet: Packet
    ):
        self.value: Packet = packet
        """
        The packet, that can include video or audio
        frames and can be decoded.
        """

    def decode(
        self
    ) -> list['SubtitleSet']:
        """
        Get the frames but decoded, perfect to make
        modifications and encode to save them again.
        """
        return self.value.decode()
    
class _Reader:
    """
    Internal class to be inherited by our
    specific reader classes.
    """

    @property
    def has_video(
        self
    ) -> bool:
        """
        Flag to indicate if there is a video stream
        or not.
        """
        return self.video_stream is not None

    @property
    def has_audio(
        self
    ) -> bool:
        """
        Flag to indicate if there is an audio stream
        or not.
        """
        return self.audio_stream is not None

    def __init__(
        self,
        filename: str
    ):
        self.filename: str = filename
        """
        The filename of the video source.
        """
        self.container: InputContainer = None
        """
        The av input general container of the
        video (that also includes the audio) we
        are reading.
        """
        self.video_stream: Union[VideoStream, None] = None
        """
        The stream that includes the video. If
        no video stream this will be None.
        """
        self.audio_stream: Union[AudioStream, None] = None
        """
        The stream that includes the audio. If
        no audio stream this will be None.
        """

    def reset(
        self
    ) -> 'VideoReader':
        """
        Reset all the instances, closing the file
        and opening again.

        This will also return to the first frame.
        """
        if self.container is not None:
            # TODO: Maybe accept forcing it (?)
            self.seek_video(0)
            self.seek_audio(0)
            #self.container.seek(0)
            #self.container.close()
        else:
            self.container = av_open(self.filename)
            
            self.video_stream = (
                self.container.streams.video[0]
                if self.container.streams.video else
                None
            )

            self.audio_stream = (
                self.container.streams.audio[0]
                if self.container.streams.audio else
                None
            )

            if (
                not self.has_video and
                not self.has_audio
            ):
                raise Exception(f'No video nor audio stream found in the "{self.filename}" file.')

            if self.has_video:
                # TODO: Should this be 'AUTO' (?)
                self.video_stream.thread_type = 'AUTO'

            if self.has_audio:
                # TODO: Should this be 'AUTO' (?)
                self.audio_stream.thread_type = 'AUTO'

            self.video_cache = (
                VideoFrameCache(self.container, self.video_stream)
                if self.has_video else
                None
            )

            self.audio_cache = (
                AudioFrameCache(self.container, self.audio_stream)
                if self.has_audio else
                None
            )

    def seek_video(
        self,
        pts: int
    ) -> '_Reader':
        """
        Call the container '.seek()' method with
        the given 'pts' packet time stamp for the
        video stream.
        """
        self.container.seek(
            offset = pts,
            # TODO: What happens if this is None (?)
            stream = self.video_stream
        )

        return self
    
    def seek_audio(
        self,
        pts: int
    ) -> '_Reader':
        """
        Call the container '.seek()' method with
        the given 'pts' packet time stamp for the
        audio stream.
        """
        self.container.seek(
            offset = pts,
            # TODO: What happens if this is None (?)
            stream = self.audio_stream
        )

        return self

    def close(
        self
    ) -> None:
        """
        Close the container to free it.
        """
        self.container.close()

class VideoReader(_Reader):
    """
    Class to read video files with the pyav
    library. Those videos include a video stream
    but also could include an audio stream.
    """

    @property
    def frame_iterator(
        self
    ) -> 'Iterator[VideoFrame]':
        """
        Iterator to iterate over all the video frames
        decodified.
        """
        return self.container.decode(self.video_stream)
    
    # TODO: Remove this when possible, we are not
    # using 'next' properties
    @property
    def next_frame(
        self
    ) -> Union[VideoFrame, None]:
        """
        Get the next video frame (decoded) from the
        iterator.
        """
        return next(self.frame_iterator)

    @property
    def audio_frame_iterator(
        self
    ) -> 'Iterator[AudioFrame]':
        """
        Iterator to iterate over all the audio frames
        decodified.
        """
        return self.container.decode(self.audio_stream)
        
    @property
    def packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        as packets (not decodified).
        """
        return self.container.demux(self.video_stream)
    
    @property
    def audio_packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the audio frames
        as packets (not decodified).
        """
        return self.container.demux(self.audio_stream)
    
    @property
    def packet_with_audio_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the video frames
        as packets (not decodified) including also the
        audio as packets.
        """
        return self.container.demux((self.video_stream, self.audio_stream))

    @property
    def codec_name(
        self
    ) -> Union[str, None]:
        """
        Get the name of the video codec.
        """
        return (
            self.video_stream.codec_context.name
            if self.has_video else
            None
        )
    
    @property
    def audio_codec_name(
        self
    ) -> str:
        """
        Get the name of the audio codec.
        """
        return (
            self.audio_stream.codec_context.name
            if self.has_audio else
            None
        )

    @property
    def number_of_frames(
        self
    ) -> Union[int, None]:
        """
        The number of frames in the video.
        """
        return (
            self.video_stream.frames
            if self.has_video else
            None
        )
    
    @property
    def fps(
        self
    ) -> Union[Fraction, None]:
        """
        The fps of the video.
        """
        return (
            self.video_stream.average_rate
            if self.has_video else
            None
        )
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The fps of the audio.
        """
        return (
            self.audio_stream.rate
            if self.has_audio else
            None
        )
    
    @property
    def time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the video.
        """
        return (
            self.video_stream.time_base
            if self.has_video else
            None
        )

    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return (
            self.audio_stream.time_base
            if self.has_audio else
            None
        )
    
    @property
    def ticks_per_frame(
        self
    ) -> int:
        """
        The number of ticks per video frame. A
        tick is the minimum amount of time and
        is the way 'pts' is measured, in ticks.

        This means that the 'pts' value will
        be increased this amount from one video
        frame to the next one.

        How we obtain it:
        - `(1 / fps) / time_base`
        """
        return Fraction(1, int(self.fps)) / self.time_base
    
    @property
    def duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the video.
        """
        # TODO: What to do in the case we have
        # video stream but not 'duration' 
        # attribute (?)
        return (
            float(self.video_stream.duration * self.video_stream.time_base)
            if (
                self.has_video and
                self.video_stream.duration
            ) else
            None
        )

    @property
    def audio_duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the audio.
        """
        # TODO: What to do in the case we have
        # audio stream but not 'duration' 
        # attribute (?)
        return (
            float(self.audio_stream.duration * self.audio_stream.time_base)
            if (
                self.has_audio and
                self.audio_stream.duration
            ) else
            None
        )
    
    @property
    def size(
        self
    ) -> Union[tuple[int, int], None]:
        """
        The size of the video in a (width, height) format.
        """
        return (
            (
                self.video_stream.width,
                self.video_stream.height
            )
            if self.has_video else
            None
        )
    
    @property
    def width(
        self
    ) -> Union[int, None]:
        """
        The width of the video, in pixels.
        """
        return (
            self.size[0]
            if self.size is not None else
            None
        )
    
    @property
    def height(
        self
    ) -> Union[int, None]:
        """
        The height of the video, in pixels.
        """
        return (
            self.size[1]
            if self.size is not None else
            None
        )
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str,
        # Use 'rgba' if alpha channel
        pixel_format: str = 'rgb24'
    ):
        _Reader.__init__(
            self,
            filename = filename
        )

        self.pixel_format: str = pixel_format
        """
        The pixel format.
        """
        self.video_cache: VideoFrameCache = None
        """
        The video frame cache system to optimize
        the way we access to the frames.
        """
        self.audio_cache: AudioFrameCache = None
        """
        The audio frame cache system to optimize
        the way we access to the frames.
        """

        # TODO: Maybe we can read the first 
        # frame, store it and reset, so we have
        # it in memory since the first moment.
        # We should do it here because if we
        # iterate in some moment and then we
        # want to obtain it... it will be 
        # difficult.
        # Lets load the variables
        self.reset()

    def get_frame(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame that is in the 't' time
        moment provided.
        """
        return self.video_cache.get_frame(t)

    def get_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Iterator to get the video frames in between
        the provided 'start' and 'end' time moments.
        """
        for frame in get_frames(
            cache = self.video_cache,
            start = start,
            end = end
        ):
            yield frame

    def get_audio_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'AudioFrame':
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system.
        """
        return self.audio_cache.get_frame(t)
    
    def get_audio_frames_from_t(
        self,
        t: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for the 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        for frame in get_audio_frames_from_t(
            cache = self.audio_cache,
            t = t,
            video_fps = self.fps
        ):
            yield frame

    def get_audio_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Iterator to get the audio frames in between
        the provided 'start' and 'end' time moments.
        """
        for frame in get_frames(
            cache = self.audio_cache,
            start = start,
            end = end
        ):
            yield frame

@dataclass
class AudioReaderFrame:
    """
    Class to wrap a frame of an audio that is
    being read and has been decoded.
    """

    def __init__(
        self,
        # TODO: Add the type, please
        frame: any,
        t: Union[int, float, Fraction] = None
    ):
        self.value: AudioFrame = frame
        """
        The frame content, that can be audio or video
        frame.
        """
        self.t: Fraction = Fraction(t)
        """
        The 't' time moment of the frame.
        """

class AudioReader(_Reader):
    """
    Class to read video files with the PyAv (av)
    library that uses ffmpeg on the background.
    """

    @property
    def audio_frame_iterator(
        self
    ) -> 'Iterator[AudioFrame]':
        """
        Iterator to iterate over all the audio frames
        decodified.
        """
        return self.container.decode(self.audio_stream)
        
    @property
    def audio_packet_iterator(
        self
    ) -> 'Iterator[Packet]':
        """
        Iterator to iterate over all the audio frames
        as packets (not decodified).
        """
        return self.container.demux(self.audio_stream)
    
    @property
    def has_audio(
        self
    ) -> bool:
        """
        Flag to indicate if there is an audio stream
        or not.
        """
        return self.audio_stream is not None

    @property
    def audio_codec_name(
        self
    ) -> str:
        """
        Get the name of the audio codec.
        """
        return (
            self.audio_stream.codec_context.name
            if self.has_audio else
            None
        )

    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The fps of the audio.
        """
        return (
            self.audio_stream.rate
            if self.has_audio else
            None
        )
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return (
            self.audio_stream.time_base
            if self.has_audio else
            None
        )
    
    @property
    def audio_duration(
        self
    ) -> Union[float, None]:
        """
        The duration of the audio.
        """
        # TODO: What to do in the case we have
        # audio stream but not 'duration' 
        # attribute (?)
        return (
            float(self.audio_stream.duration * self.audio_stream.time_base)
            if (
                self.has_audio and
                self.audio_stream.duration
            ) else
            None
        )
    
    # Any property related to audio has to
    # start with 'audio_property_name'

    def __init__(
        self,
        filename: str
    ):
        _Reader.__init__(
            self,
            filename = filename
        )

        self.audio_cache: AudioFrameCache = None
        """
        The audio frame cache system to optimize
        the way we access to the frames.
        """

        # TODO: Maybe we can read the first 
        # frame, store it and reset, so we have
        # it in memory since the first moment.
        # We should do it here because if we
        # iterate in some moment and then we
        # want to obtain it... it will be 
        # difficult.
        # Lets load the variables
        self.reset()

    def get_audio_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'AudioFrame':
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system.
        """
        return self.audio_cache.get_frame(t)
    
    def get_audio_frames_from_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for the 
        given video 't' time moment, using the
        audio cache system and the provided
        'video_fps' to be able to claculate the
        time range.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        for frame in get_audio_frames_from_t(
            cache = self.audio_cache,
            t = t,
            video_fps = video_fps
        ):
            yield frame

    def get_audio_frames(
        self,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        """
        Iterator to get the audio frames in between
        the provided 'start' and 'end' time moments.
        """
        for frame in get_frames(
            cache = self.audio_cache,
            start = start,
            end = end
        ):
            yield frame

def get_frames(
    cache: Union[AudioFrameCache, VideoFrameCache],
    start: Union[int, float, Fraction] = 0.0,
    end: Union[int, float, Fraction, None] = None
):
    """
    Iterator to get the frames in the time range
    defined by the given 'start' and 'end' time
    moments.
    """
    for frame in cache.get_frames(start, end):
        yield frame

def get_audio_frames_from_t(
    cache: AudioFrameCache,
    t: Union[int, float, Fraction],
    video_fps: Union[int, float, Fraction]
):
    thandler = THandler(video_fps)
    t_start = thandler.t.truncated(t)
    t_end = thandler.t.next(t, 1, do_truncate = True)

    # We want all the audios that must be played
    # during the video frame that starts in the
    # 't' time moment
    for frame in get_frames(
        cache = cache,
        start = t_start,
        end = t_end
    ):
        yield frame


"""
When reading packets directly from the stream
we can receive packets with size=0, but we need
to process them and decode (or yield them). It
is only when we are passing packets to the mux
when we need to ignore teh ones thar are empty
(size=0).

TODO: Do we need to ignore all? By now, ignoring
not is causing exceptions, and ignoring them is
making it work perfectly.
"""