"""
When we are reading from a source, the reader
has its own time base and properties. When we
are writing, the writer has different time
base and properties. We need to adjust our
writer to be able to write, because the videos
we read can be different, and the video we are
writing is defined by us. The 'time_base' is
an important property or will make ffmpeg
become crazy and deny packets (that means no
video written).
"""
from yta_video_pyav.complete.track import VideoTrack, AudioTrack
from yta_video_pyav.video import Video
from yta_video_pyav.complete.frame_wrapper import AudioFrameWrapped
from yta_video_pyav.complete.frame_combinator import AudioFrameCombinator
from yta_video_pyav.writer import VideoWriter
from yta_video_frame_time.t_fraction import get_ts, fps_to_time_base, T
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from av.video.frame import VideoFrame
from av.audio.frame import AudioFrame
from quicktions import Fraction
from functools import reduce
from typing import Union

import numpy as np


class Timeline:
    """
    Class to represent all the tracks that
    exist on the project and to handle the
    combination of all their frames.
    """

    @property
    def end(
        self
    ) -> Fraction:
        """
        The end of the last video of the track
        that lasts longer. This is the last time
        moment that has to be rendered.
        """
        return max(
            track.end
            for track in self.tracks
        )
    
    @property
    def tracks(
        self
    ) -> list[Union['AudioTrack', 'VideoTrack']]:
        """
        All the tracks we have but ordered by 
        their indexes, from lower index (highest
        priority) to highest index (lowest
        priority).
        """
        return sorted(self._tracks, key = lambda track: track.index)
    
    @property
    def video_tracks(
        self
    ) -> list['VideoTrack']:
        """
        All the video tracks we have but ordered
        by their indexes, from lower index
        (highest priority) to highest index
        (lowest priority).
        """
        return [
            track
            for track in self.tracks
            if PythonValidator.is_instance_of(track, 'VideoTrack')
        ]
    
    @property
    def audio_tracks(
        self
    ) -> list['AudioTrack']:
        """
        All the audio tracks we have but ordered
        by their indexes, from lower index
        (highest priority) to highest index
        (lowest priority).
        """
        return [
            track
            for track in self.tracks
            if PythonValidator.is_instance_of(track, 'AudioTrack')
        ]
    
    @property
    def number_of_tracks(
        self
    ) -> int:
        """
        The number of tracks we have in the
        timeline.
        """
        return len(self.tracks)

    @property
    def number_of_video_tracks(
        self
    ) -> int:
        """
        The number of video tracks we have in the
        timeline.
        """
        return len(self.video_tracks)
    
    @property
    def number_of_audio_tracks(
        self
    ) -> int:
        """
        The number of audio tracks we have in the
        timeline.
        """
        return len(self.audio_tracks)

    def __init__(
        self,
        size: tuple[int, int] = (1_920, 1_080),
        fps: Union[int, float, Fraction] = 60.0,
        audio_fps: Union[int, Fraction] = 44_100.0, # 48_000.0 for aac
        # TODO: I don't like this name
        # TODO: Where does this come from (?)
        audio_samples_per_frame: int = 1024,
        video_codec: str = 'h264',
        video_pixel_format: str = 'yuv420p',
        audio_codec: str = 'aac',
        # TODO: What about this below (?)
        # audio_layout = 'stereo',
        # audio_format = 'fltp'
    ):
        # TODO: By now I'm having only video
        # tracks
        self._tracks: list[VideoTrack] = []
        """
        All the video tracks we are handling.
        """

        self.size: tuple[int, int] = size
        """
        The size that the final video must have.
        """
        self.fps: Union[int, float, Fraction] = fps
        """
        The fps of the output video.
        """
        self.audio_fps: Union[int, Fraction] = audio_fps
        """
        The fps of the output audio.
        """
        self.audio_samples_per_frame: int = audio_samples_per_frame
        """
        The audio samples each audio frame must
        have.
        """
        self.video_codec: str = video_codec
        """
        The video codec for the video exported.
        """
        self.video_pixel_format: str = video_pixel_format
        """
        The pixel format for the video exported.
        """
        self.audio_codec: str = audio_codec
        """
        The audio codec for the audio exported.
        """

        # We will have 2 video tracks by now
        self.add_video_track().add_video_track()

    def _add_track(
        self,
        index: Union[int, None] = None,
        is_audio: bool = False
    ) -> 'Timeline':
        """
        Add a new track to the timeline that will
        be placed in the last position (highest 
        index, lowest priority).

        It will be a video track unless you send
        the 'is_audio' parameter as True.
        """
        number_of_tracks = (
            self.number_of_audio_tracks
            if is_audio else
            self.number_of_video_tracks
        )

        tracks = (
            self.audio_tracks
            if is_audio else
            self.video_tracks
        )

        index = (
            index
            if (
                index is not None and
                index <= number_of_tracks
            ) else
            number_of_tracks
        )

        # We need to change the index of the
        # affected tracks (the ones that are
        # in that index and after it)
        if index < number_of_tracks:
            for track in tracks:
                if track.index >= index:
                    track.index += 1

        track = (
            AudioTrack(
                index = index,
                fps = self.fps,
                audio_fps = self.audio_fps,
                audio_samples_per_frame = self.audio_samples_per_frame,
                # TODO: Where do we obtain this from (?)
                audio_layout = 'stereo',
                audio_format = 'fltp'
            )
            if is_audio else
            VideoTrack(
                index = index,
                size = self.size,
                fps = self.fps,
                audio_fps = self.audio_fps,
                audio_samples_per_frame = self.audio_samples_per_frame,
                # TODO: Where do we obtain this from (?)
                audio_layout = 'stereo',
                audio_format = 'fltp'
            )
        )
            
        self._tracks.append(track)

        return self

    def add_video_track(
        self,
        index: Union[int, None] = None
    ) -> 'Timeline':
        """
        Add a new video track to the timeline, that
        will be placed in the last position (highest
        index, lowest priority).
        """
        return self._add_track(
            index = index,
            is_audio = False
        )
    
    def add_audio_track(
        self,
        index: Union[int, None] = None
    ) -> 'Timeline':  
        """
        Add a new audio track to the timeline, that
        will be placed in the last position (highest
        index, lowest priority).
        """  
        return self._add_track(
            index = index,
            is_audio = True
        )
    
    # TODO: Create a 'remove_track'

    def add_video(
        self,
        video: Video,
        t: Union[int, float, Fraction, None] = None,
        track_index: int = 0
    ) -> 'Timeline':
        """
        Add the provided 'video' to the timeline,
        starting at the provided 't' time moment.

        TODO: The 'do_use_second_track' parameter
        is temporary.
        """
        ParameterValidator.validate_mandatory_number_between('track_index', track_index, 0, self.number_of_tracks)

        if track_index >= self.number_of_video_tracks:
            raise Exception(f'The "track_index" {str(track_index)} provided does not exist in this timeline.')

        # TODO: This should be, maybe, looking for
        # tracks by using the index property, not
        # as array index, but by now it is like
        # this as it is not very robust yet
        self.video_tracks[track_index].add_media(video, t)

        return self
    
    # TODO: Create a 'remove_video' 
    # TODO: Create a 'add_audio'
    # TODO: Create a 'remove_audio'
    
    def get_frame_at(
        self,
        t: Union[int, float, Fraction]
    ) -> 'VideoFrame':
        """
        Get all the frames that are played at the
        't' time provided, but combined in one.
        """
        frames = list(
            track.get_frame_at(t)
            for track in self.video_tracks
        )
        # TODO: Combinate frames, we force them to
        # rgb24 to obtain them with the same shape,
        # but maybe we have to change this because
        # we also need to handle alphas

        """
        We need to ignore the frames that are tagged
        as coming from an empty part, so we can have:

        1. Only empty frames
            -> Black background, keep one
        2. Empty frames but other frames:
            -> Skip all empty frames and apply
               track orders
        """

        output_frame = frames[0]._frame.to_ndarray(format = 'rgb24')

        for frame in frames:
            # We just need the first non-empty frame,
            # that must be from the track with the
            # bigger priority
            # TODO: I assume, by now, that the frames
            # come in order (bigger priority first)
            if not frame.is_from_empty_part:
                # TODO: By now I'm just returning the first
                # one but we will need to check the alpha
                # layer to combine if possible
                output_frame = frame._frame.to_ndarray(format = 'rgb24')
                break

            # # TODO: This code below is to combine the
            # # frames but merging all of them, that is
            # # unexpected in a video editor but we have
            # # the way to do it
            # from yta_video_opengl.complete.frame_combinator import VideoFrameCombinator
            # # TODO: What about the 'format' (?)
            # output_frame = VideoFrameCombinator.blend_add(output_frame, frame.to_ndarray(format = 'rgb24'))

        # TODO: How to build this VideoFrame correctly
        # and what about the 'format' (?)
        # We don't handle pts here, just the image
        return VideoFrame.from_ndarray(output_frame, format = 'rgb24')
    
    def get_audio_frames_at(
        self,
        t: float
    ):
        audio_frames: list[AudioFrameWrapped] = []
        """
        Matrix in which the rows are the different
        tracks we have, and the column includes all
        the audio frames for this 't' time moment
        for the track of that row. We can have more
        than one frame per column per row (track)
        but we need a single frame to combine all
        the tracks.
        """
        # TODO: What if the different audio streams
        # have also different fps (?)
        # We use both tracks because videos and
        # audio tracks have both audios
        for track in self.tracks:
            # TODO: Make this work properly
            audio_frames.append(list(track.get_audio_frames_at(t)))

        # TODO: I am receiving empty array here []
        # that doesn't include any frame in a specific
        # track that contains a video, why (?)
        print(audio_frames)

        # We need only 1 single audio frame per column
        collapsed_frames = [
            concatenate_audio_frames(frames)
            for frames in audio_frames
        ]

        # TODO: What about the lenghts and those
        # things? They should be ok because they are
        # based on our output but I'm not completely
        # sure here..
        print(collapsed_frames)

        # We keep only the non-silent frames because
        # we will sum them after and keeping them
        # will change the results.
        non_empty_collapsed_frames = [
            frame._frame
            for frame in collapsed_frames
            if not frame.is_from_empty_part
        ]

        if len(non_empty_collapsed_frames) == 0:
            # If they were all silent, just keep one
            non_empty_collapsed_frames = [collapsed_frames[0]._frame]

        # Now, mix column by column (track by track)
        # TODO: I do this to have an iterator, but 
        # maybe we need more than one single audio
        # frame because of the size at the original
        # video or something...
        frames = [
            AudioFrameCombinator.sum_tracks_frames(non_empty_collapsed_frames, self.audio_fps)
        ]

        for audio_frame in frames:
            yield audio_frame
            
    def render(
        self,
        output_filename: str = 'test_files/output_render.mp4',
        start: Union[int, float, Fraction] = 0.0,
        end: Union[int, float, Fraction, None] = None,
    ) -> 'Timeline':
        """
        Render the time range in between the given
        'start' and 'end' and store the result with
        the also provided 'fillename'.

        If no 'start' and 'end' provided, the whole
        project will be rendered.
        """
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = False)

        end = (
            self.end
            if end is None else
            end
        )

        # Limit 'end' a bit...
        if end >= 300:
            raise Exception('More than 5 minutes not supported yet.')

        if start >= end:
            raise Exception('The provided "start" cannot be greater or equal to the "end" provided.')

        writer = VideoWriter(output_filename)

        # TODO: This has to be dynamic according to the
        # video we are writing (?)
        writer.set_video_stream(
            codec_name = self.video_codec,
            fps = self.fps,
            size = self.size,
            pixel_format = self.video_pixel_format
        )
        
        writer.set_audio_stream(
            codec_name = self.audio_codec,
            fps = self.audio_fps
        )

        time_base = fps_to_time_base(self.fps)
        audio_time_base = fps_to_time_base(self.audio_fps)

        audio_pts = 0
        for t in get_ts(start, end, self.fps):
            frame = self.get_frame_at(t)

            print(f'Getting t:{str(float(t))}')

            # We need to adjust our output elements to be
            # consecutive and with the right values
            # TODO: We are using int() for fps but its float...
            frame.time_base = time_base
            frame.pts = T(t, time_base).truncated_pts

            writer.mux_video_frame(
                frame = frame
            )

            for audio_frame in self.get_audio_frames_at(t):
                # We need to adjust our output elements to be
                # consecutive and with the right values
                # TODO: We are using int() for fps but its float...
                audio_frame.time_base = audio_time_base
                audio_frame.pts = audio_pts

                # We increment for the next iteration
                audio_pts += audio_frame.samples

                writer.mux_audio_frame(audio_frame)

        writer.mux_video_frame(None)
        writer.mux_audio_frame(None)
        writer.output.close()

# TODO: Refactor and move please
# TODO: This has to work for AudioFrame
# also, but I need it working for Wrapped
def concatenate_audio_frames(
    frames: list[AudioFrameWrapped]
) -> AudioFrameWrapped:
    """
    Concatenate all the given 'frames' in one
    single audio frame and return it.

    The audio frames must have the same layout
    and sample rate.
    """
    if not frames:
        # TODO: This should not happen
        return None
    
    if len(frames) == 1:
        return frames[0]

    # We need to preserve the metadata
    is_from_empty_part = all(
        frame.is_from_empty_part
        for frame in frames
    )
    metadata = reduce(lambda key_values, frame: {**key_values, **frame.metadata}, frames, {})
    
    sample_rate = frames[0]._frame.sample_rate
    layout = frames[0]._frame.layout.name

    arrays = []
    # TODO: What about 'metadata' (?)
    for frame in frames:
        if (
            frame._frame.sample_rate != sample_rate or
            frame._frame.layout.name != layout
        ):
            raise ValueError("Los frames deben tener mismo sample_rate y layout")

        # arr = frame.to_ndarray()  # (channels, samples)
        # if arr.dtype == np.int16:
        #     arr = arr.astype(np.float32) / 32768.0
        # elif arr.dtype != np.float32:
        #     arr = arr.astype(np.float32)

        arrays.append(frame._frame.to_ndarray())

    combined = np.concatenate(arrays, axis = 1)

    out = AudioFrame.from_ndarray(
        array = combined,
        format = frames[0].format,
        layout = layout
    )
    out.sample_rate = sample_rate

    return AudioFrameWrapped(
        frame = out,
        metadata = metadata,
        is_from_empty_part = is_from_empty_part
    )