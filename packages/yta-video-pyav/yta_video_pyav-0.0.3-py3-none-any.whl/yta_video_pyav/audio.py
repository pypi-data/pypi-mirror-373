"""
TODO: This class has not been refactored nor
tested. I need to put some love on it to make
it work and test that it is working properly.
"""
from yta_video_pyav.reader import AudioReader
from yta_video_pyav.writer import VideoWriter
from yta_video_frame_time.t_fraction import THandler
from quicktions import Fraction
from typing import Union


# TODO: Where can I obtain this dynamically (?)
PIXEL_FORMAT = 'yuv420p'

# TODO: Maybe create a _Media(ABC) to put
# some code shared with the Video class
class Audio:
    """
    Class to wrap the functionality related to
    handling and modifying a video.
    """

    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the video.
        """
        return self.end - self.start
    
    @property
    def audio_fps(
        self
    ) -> Union[int, None]:
        """
        The frames per second of the audio.
        """
        return self.reader.audio_fps
    
    @property
    def audio_time_base(
        self
    ) -> Union[Fraction, None]:
        """
        The time base of the audio.
        """
        return self.reader.audio_time_base
    
    @property
    def frames(
        self
    ):
        """
        Iterator to yield all the frames, one by
        one, within the range defined by the
        'start' and 'end' parameters provided when
        instantiating it.

        The iterator will iterate first over the
        audio frames.
        """
        for frame in self.reader.get_audio_frames(self.start, self.end):
            yield frame

    def __init__(
        self,
        filename: str,
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None
    ):
        self.filename: str = filename
        """
        The filename of the original audio.
        """
        self.reader: AudioReader = AudioReader(self.filename)
        """
        The pyav audio reader.
        """
        self.start: Fraction = Fraction(start)
        """
        The time moment 't' in which the audio
        should start.
        """
        self.end: Union[Fraction, None] = Fraction(
            # TODO: Is this 'end' ok (?)
            self.reader.audio_duration
            if end is None else
            end
        )
        """
        The time moment 't' in which the audio
        should end.
        """

        if (
            self.start >= self.reader.audio_duration and
            self.end >= self.reader.audio_duration
        ):
            raise Exception(f'The provided "start" and "end" are invalid values considering the real audio duration of {str(float(self.reader.audio_duration))}s')
        
        if self.end <= self.start:
            raise Exception('The "end" value cannot be equal or smaller than the "start" value.')
        
        self.end = (
            self.reader.audio_duration
            if self.end > self.reader.audio_duration else
            self.end
        )

    def _get_t(
        self,
        t: Union[int, float, Fraction]
    ) -> Fraction:
        """
        Get the real 't' time moment based on the
        audio 'start' and 'end'. If they were 
        asking for the t=0.5s but our audio was
        subclipped to [1.0, 2.0), the 0.5s must be
        actually the 1.5s of the audio because of
        the subclipped time range.
        """
        t += self.start
        
        print(f'Audio real t is {str(float(t))}')
        if t >= self.end:
            raise Exception(f'The "t" ({str(t)}) provided is out of range. This audio lasts from [{str(self.start)}, {str(self.end)}).')
        
        return t

    def get_audio_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'AudioFrame':
        """
        Get the audio frame with the given 't' time
        moment, using the audio cache system. This
        method is useful when we need to combine 
        many different frames so we can obtain them
        one by one.

        TODO: Is this actually necessary (?)
        """
        return self.reader.get_audio_frame_from_t(self._get_t(t))
    
    def get_audio_frames_from_t(
        self,
        t: Union[int, float, Fraction],
        video_fps: Union[int, float, Fraction]
    ):
        """
        Get the sequence of audio frames for a 
        given video 't' time moment, using the
        audio cache system.

        This is useful when we want to write a
        video frame with its audio, so we obtain
        all the audio frames associated to it
        (remember that a video frame is associated
        with more than 1 audio frame).
        """
        print(f'Getting audio frames from {str(float(t))} that is actually {str(float(self._get_t(t)))}')
        for frame in self.reader.get_audio_frames_from_t(self._get_t(t), video_fps = video_fps):
            yield frame

    def save_as(
        self,
        filename: str
    ) -> 'Video':
        """
        Save the audio locally as the given 'filename'.

        TODO: By now we are doing tests inside so the
        functionality is a manual test. Use it 
        carefully.
        """
        writer = VideoWriter(filename)
        writer.set_audio_stream_from_template(self.reader.audio_stream)

        thandler = THandler(self.audio_fps, self.audio_time_base)
        for frame in self.frames:
            t = thandler.t.from_pts(frame.pts)

            print(f'Saving audio frame with t = {str(t)}')

            # TODO: Process any audio frame change
            # Test setting audio
            # frame = fade_in.process(frame, t)

            writer.mux_audio_frame(
                frame = frame
            )

        # Flush the remaining frames to write
        writer.mux_audio_frame(None)

        # TODO: Maybe move this to the '__del__' (?)
        writer.output.close()
        self.reader.container.close()