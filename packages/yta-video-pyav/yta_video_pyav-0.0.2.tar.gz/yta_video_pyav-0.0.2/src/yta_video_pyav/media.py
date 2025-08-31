
"""
The pyav uses Pillow to load an image as
a numpy array but using not the alpha.
"""
from yta_video_pyav.complete.frame_generator import VideoFrameGenerator
from yta_video_pyav.writer import VideoWriter
from av.video.frame import VideoFrame
from yta_video_frame_time.t_fraction import get_ts
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from quicktions import Fraction
from PIL import Image
from abc import ABC, abstractmethod
from typing import Union

import numpy as np


class _Media(ABC):
    """
    Class to represent an element that can be
    used in our video editor, that can be a
    video, an audio, an image, a color frame,
    etc.
    """

    @property
    def duration(
        self
    ) -> Fraction:
        """
        The duration of the media.
        """
        return self.end - self.start

    def __init__(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        self.start: Fraction = Fraction(start)
        """
        The time moment 't' in which the media
        should start.
        """
        self.end: Fraction = Fraction(end)
        """
        The time moment 't' in which the media
        should end.
        """

    def _get_t(
        self,
        t: Union[int, float, Fraction]
    ) -> Fraction:
        """
        Get the real 't' time moment based on the
        media 'start' and 'end'. If they were 
        asking for the t=0.5s but our media was
        subclipped to [1.0, 2.0), the 0.5s must be
        actually the 1.5s of the media because of
        the subclipped time range.

        This method will raise an exception if the
        't' time moment provided, when adjusted to
        the internal media start and end time, is
        not valid (is after the end).
        """
        t += self.start
        
        if t >= self.end:
            raise Exception(f'The "t" ({str(t)}) provided is out of range. This media lasts from [{str(self.start)}, {str(self.end)}).')
        
        return t
    
class _CanBeSavedAsVideo:
    """
    Class to implement the functionality of
    being written into a video file, frame
    by frame.
    """

    def save_as(
        self,
        output_filename: str,
        fps: Union[int, float, Fraction] = 60.0,
        video_codec: str = 'h264',
        video_pixel_format: str = 'yuv420p'
    ) -> '_CanBeSavedAsVideo':
        """
        Save the media as a video to the
        given 'output_filename' file.
        """
        writer = VideoWriter(output_filename)

        fps = int(fps)

        # TODO: This has to be dynamic according to the
        # video we are writing (?)
        writer.set_video_stream(
            codec_name = video_codec,
            fps = fps,
            size = self.size,
            pixel_format = video_pixel_format
        )

        for index, t in enumerate(get_ts(self.start, self.end, fps)):
            frame = self.get_frame_from_t(t)
            frame.pts = index
            frame.time_base = Fraction(1, fps)

            writer.mux_video_frame(
                frame = frame
            )

        writer.mux_video_frame(None)
        writer.output.close()

        return self
    
class _HasVideoFrame(ABC):
    """
    Class to be inherited by all those classes
    that have video frames.
    """

    # TODO: Maybe force
    # size: tuple[int, int] = (1920, 1080),
    # dtype: dtype = np.uint8,
    # format: str = 'rgb24'
    # on __init__ (?)

    @abstractmethod
    def get_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrame':
        """
        Get the video frame with the given 't' time
        moment.
        """
        # TODO: Maybe 
        pass

class _HasAudioFrame(ABC):
    """
    Class to be inherited by all those classes
    that have audio frames.
    """

    @abstractmethod
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
        pass
    
class _StaticMedia(_Media, _HasVideoFrame, _CanBeSavedAsVideo):
    """
    Class to represent a media that doesn't
    change during its whole duration and
    the frame is the same, it remains static.

    This class must be implemented by our
    ImageMedia and ColorMedia as the frame
    will be always the same, an image or
    a color frame.
    """

    @property
    @abstractmethod
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        pass

    def __init__(
        self,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction]
    ):
        _Media.__init__(
            self,
            start = start,
            end = end
        )

    def get_frame_from_t(
        self,
        t: Union[int, float, Fraction]
    ) -> VideoFrame:
        """
        Get the video frame with the given 't' time
        moment.
        """
        # This will raise an exception if invalid 't'
        # when adapted to its internal 'start' and 'end'
        t = self._get_t(t)

        # TODO: What if we need to resize the source
        # before putting it into a video frame (?)

        return self.frame

class ColorMedia(_StaticMedia):
    """
    A media that will be a single color video
    frame during its whole duration.
    """

    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        # TODO: Make this use the 'color'
        # TODO: I need to implement the alpha layer
        return VideoFrameGenerator().background.full_white(
            size = self.size
        )

    def __init__(
        self,
        # TODO: Apply format
        color: any,
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        size: tuple[int, int] = (1920, 1080),
        # TODO: Do I need this (?)
        # dtype: dtype = np.uint8,
        # format: str = 'rgb24',
    ):
        # TODO: Apply format
        self._color: any = color
        """
        The color that will be used to make the
        frame that will be played its whole
        duration.
        """
        self.size: tuple[int, int] = size
        """
        The size of the media frame.
        """

        super().__init__(
            start = start,
            end = end
        )

class ImageMedia(_StaticMedia):
    """
    A media that will be a single image 
    during its whole duration.
    """

    @property
    def frame(
        self
    ) -> VideoFrame:
        """
        The frame that must be displayed.
        """
        # By default we use it accepting transparency
        # TODO: The image must be like this:
        # arr = np.array(img)  # shape (h, w, 4), dtype=uint8
        # TODO: What value if no alpha (?)
        return VideoFrame.from_ndarray(self._image, format = 'rgba')

    def __init__(
        self,
        # TODO: It must be RGB
        image: Union[np.ndarray, str],
        start: Union[int, float, Fraction],
        end: Union[int, float, Fraction],
        size: tuple[int, int] = (1920, 1080),
        do_include_alpha: bool = True,
        # TODO: Do I need this (?)
        # dtype: dtype = np.uint8,
        # TODO: Maybe this 'format' need to be
        # dynamic according to if we are reading
        # the alpha channel or not...
        # format: str = 'rgb24',
    ):
        ParameterValidator.validate_mandatory_instance_of('image', image, [str, np.ndarray])
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = False)
        ParameterValidator.validate_mandatory_bool('do_include_alpha', do_include_alpha)

        image = (
            image_to_numpy_pillow(image, do_include_alpha = do_include_alpha)
            if PythonValidator.is_string(image) else
            image
        )

        self._image: np.ndarray = image
        """
        The image that will be used to make the
        frame that will be played its whole
        duration.
        """
        self.size: tuple[int, int] = size
        """
        The size of the media frame.
        """

        super().__init__(
            start = start,
            end = end
        )

# TODO: Need to implement Video as the others
# are implemented here

# TODO: I think I have this util in another
# library, so please check it...
def image_to_numpy_pillow(
    filename: str,
    do_include_alpha: bool = True
) -> 'np.ndarray':
    """
    Read the imagen file 'filename' and transform
    it into a numpy, reading also the alpha channel.
    """
    mode = (
        'RGBA'
        if do_include_alpha else
        'RGB'
    )

    return np.array(Image.open(filename).convert(mode))