from yta_video_pyav.complete.frame_wrapper import AudioFrameWrapped
from yta_video_pyav.complete.frame_generator import AudioFrameGenerator
from yta_video_pyav.utils import audio_frames_and_remainder_per_video_frame


# TODO: Is this method here ok (?)
def generate_silent_frames(
    fps: int,
    audio_fps: int,
    audio_samples_per_frame: int,
    layout: str = 'stereo',
    format: str = 'fltp'
) -> list[AudioFrameWrapped]:
    """
    Get the audio silent frames we need for
    a video with the given 'fps', 'audio_fps'
    and 'audio_samples_per_frame', using the
    also provided 'layout' and 'format' for
    the audio frames.

    This method is used when we have empty
    parts on our tracks and we need to 
    provide the frames, that are passed as
    AudioFrameWrapped instances and tagged as
    coming from empty parts.
    """
    audio_frame_generator: AudioFrameGenerator = AudioFrameGenerator()

    # Check how many full and partial silent
    # audio frames we need
    number_of_frames, number_of_remaining_samples = audio_frames_and_remainder_per_video_frame(
        video_fps = fps,
        sample_rate = audio_fps,
        number_of_samples_per_audio_frame = audio_samples_per_frame
    )

    # The complete silent frames we need
    silent_frame = audio_frame_generator.silent(
        sample_rate = audio_fps,
        layout = layout,
        number_of_samples = audio_samples_per_frame,
        format = format,
        pts = None,
        time_base = None
    )
    
    frames = (
        [
            AudioFrameWrapped(
                frame = silent_frame,
                is_from_empty_part = True
            )
        ] * number_of_frames
        if number_of_frames > 0 else
        []
    )

    # The remaining partial silent frames we need
    if number_of_remaining_samples > 0:
        silent_frame = audio_frame_generator.silent(
            sample_rate = audio_fps,
            # TODO: Check where do we get this value from
            layout = layout,
            number_of_samples = number_of_remaining_samples,
            # TODO: Check where do we get this value from
            format = format,
            pts = None,
            time_base = None
        )
        
        frames.append(
            AudioFrameWrapped(
                frame = silent_frame,
                is_from_empty_part = True
            )
        )

    return frames