from yta_video_frame_time.t_fraction import fps_to_time_base
from av.container import InputContainer
from av.video.stream import VideoStream
from av.audio.stream import AudioStream
from quicktions import Fraction
from typing import Union


def iterate_streams_packets(
    container: 'InputContainer',
    video_stream: 'VideoStream',
    audio_stream: 'AudioStream',
    video_start_pts: int = 0,
    video_end_pts: Union[int, None] = None,
    audio_start_pts: int = 0,
    audio_end_pts: Union[int, None] = None
):
    """
    Iterate over the provided 'stream' packets
    and yield the ones in the expected range.
    This is nice when trying to copy a stream
    without modifications.
    """
    # 'video_start_pts' and 'audio_start_pts' must
    # be 0 or a positive tps

    if (
        video_stream is None and
        audio_stream is None
    ):
        raise Exception('No streams provided.')
    
    # We only need to seek on video
    if video_stream is not None:
        container.seek(video_start_pts, stream = video_stream)
    if audio_stream is not None:
        container.seek(audio_start_pts, stream = audio_stream)
    
    stream = [
        stream
        for stream in (video_stream, audio_stream)
        if stream
    ]

    """
    Apparently, if we ignore some packets based
    on the 'pts', we can be ignoring information
    that is needed for the next frames to be 
    decoded, so we need to decode them all...

    If we can find some strategy to seek not for
    the inmediate but some before and read from
    that one to avoid reading all of the packets
    we could save some time, but at what cost? 
    We cannot skip any crucial frame so we need
    to know how many we can skip, and that sounds
    a bit difficult depending on the codec.
    """
    stream_finished: str = ''
    for packet in container.demux(stream):
        if packet.pts is None:
            continue

        # TODO: We cannot skip like this, we need to
        # look for the nearest keyframe to be able 
        # to decode the frames later. Take a look at
        # the VideoFrameCache class and use it.

        # start_pts = (
        #     video_start_pts
        #     if packet.stream.type == 'video' else
        #     audio_start_pts
        # )
        # end_pts = (
        #     video_end_pts
        #     if packet.stream.type == 'video' else
        #     audio_end_pts
        # )

        # if packet.pts < start_pts:
        #     continue

        # if (
        #     end_pts is not None and
        #     packet.pts > end_pts
        # ):
        #     if (
        #         stream_finished != '' and
        #         (
        #             # Finish if only one stream
        #             stream_finished != packet.stream.type or
        #             video_stream is None or
        #             audio_stream is None
        #         )
        #     ):
        #         # We have yielded all the frames in the
        #         # expected range, no more needed
        #         return
            
        #     stream_finished = packet.stream.type
        #     continue
        
        yield packet

def iterate_stream_frames_demuxing(
    container: 'InputContainer',
    video_stream: 'VideoStream',
    audio_stream: 'AudioStream',
    video_start_pts : int = 0,
    video_end_pts: Union[int, None] = None,
    audio_start_pts: int = 0,
    audio_end_pts: Union[int, None] = None
):
    """
    Iterate over the provided 'stream' packets
    and decode only the ones in the expected
    range, so only those frames are decoded
    (which is an expensive process).

    This method returns a pyav frame instance.

    You can easy transform the frame received
    to a numpy array by using this:
    - `frame.to_ndarray(format = format)`
    """
    # 'start_pts' must be 0 or a positive tps
    # 'end_pts' must be None or a positive tps

    # We cannot skip packets or we will lose
    # information needed to build the video
    for packet in iterate_streams_packets(
        container = container,
        video_stream = video_stream,
        audio_stream = audio_stream,
        video_start_pts = video_start_pts,
        video_end_pts = video_end_pts,
        audio_start_pts = audio_start_pts,
        audio_end_pts = audio_end_pts
    ):
        # Only valid and in range packets here
        # Here only the accepted ones
        stream_finished: str = ''
        for frame in packet.decode():
            if frame.pts is None:
                continue

            start_pts = (
                video_start_pts
                if packet.stream.type == 'video' else
                audio_start_pts
            )

            end_pts = (
                video_end_pts
                if packet.stream.type == 'video' else
                audio_end_pts
            )

            if frame.pts < start_pts:
                continue

            if (
                end_pts is not None and
                frame.pts > end_pts
            ):
                if (
                    stream_finished != '' and
                    (
                        # Finish if only one stream
                        stream_finished != packet.stream.type or
                        video_stream is None or
                        audio_stream is None
                    )
                ):
                    # We have yielded all the frames in the
                    # expected range, no more needed
                    return
                
                stream_finished = packet.stream.type
                continue
            
            yield frame

def audio_frames_and_remainder_per_video_frame(
    # TODO: Maybe force 'fps' as int (?)
    video_fps: Union[float, Fraction],
    sample_rate: int, # audio_fps
    number_of_samples_per_audio_frame: int
) -> tuple[int, int]:
    """
    Get how many full silent audio frames we
    need and the remainder for the last one
    (that could be not complete), according
    to the parameters provided.

    This method returns a tuple containing
    the number of full silent audio frames
    we need and the number of samples we need
    in the last non-full audio frame.
    """
    # Video frame duration (in seconds)
    time_base = fps_to_time_base(video_fps)
    sample_rate = Fraction(int(sample_rate), 1)

    # Example:
    # 44_100 / 60 = 735  ->  This means that we
    # will have 735 samples of sound per each
    # video frame
    # The amount of samples per frame is actually
    # the amount of samples we need, because we
    # are generating it...
    samples_per_frame = sample_rate * time_base
    # The 'nb_samples' is the amount of samples
    # we are including on each audio frame
    full_audio_frames_needed = samples_per_frame // number_of_samples_per_audio_frame
    remainder = samples_per_frame % number_of_samples_per_audio_frame
    
    return int(full_audio_frames_needed), int(remainder)