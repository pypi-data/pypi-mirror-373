"""
Manual tests that are working and are interesting
to learn about the code, refactor and build
classes.
"""
def video_modified_stored():
    # This path below was trimmed in an online platform
    # and seems to be bad codified and generates error
    # when processing it, but it is readable in the
    # file explorer...
    #VIDEO_PATH = 'test_files/test_1_short_broken.mp4'
    # This is short but is working well
    VIDEO_PATH = 'test_files/test_1_short_2.mp4'
    AUDIO_PATH = 'test_files/test_audio.mp3'
    # Long version below, comment to test faster
    #VIDEO_PATH = 'test_files/test_1.mp4'
    OUTPUT_PATH = 'test_files/output.mp4'
    # TODO: This has to be dynamic, but
    # according to what (?)
    NUMPY_FORMAT = 'rgb24'
    # TODO: Where do we obtain this from (?)
    VIDEO_CODEC_NAME = 'libx264'
    # TODO: Where do we obtain this from (?)
    PIXEL_FORMAT = 'yuv420p'

    from yta_video_pyav.video import Video
    from yta_video_pyav.audio import Audio
    from yta_video_pyav.complete.timeline import Timeline

    # TODO: This test below is just to validate
    # that it is cropping and placing correctly
    # but the videos are only in one track
    # video = Video(VIDEO_PATH, 0.25, 0.75)
    # timeline = Timeline()
    # timeline.add_video(Video(VIDEO_PATH, 0.25, 1.0), 0.5)
    # # This is successfully raising an exception
    # #timeline.add_video(Video(VIDEO_PATH, 0.25, 0.75), 0.6)
    # timeline.add_video(Video(VIDEO_PATH, 0.25, 0.75), 1.75)
    # timeline.add_video(Video('C:/Users/dania/Downloads/Y2meta.app-TOP 12 SIMPLE LIQUID TRANSITION _ GREEN SCREEN TRANSITION PACK-(1080p60).mp4', 4.0, 5.0), 3)
    # # timeline.add_video(Video('C:/Users/dania/Downloads/Y2meta.app-10 Smooth Transitions Green Screen Template For Kinemaster, Alight Motion, Filmora, premiere pro-(1080p).mp4', 2.25, 3.0), 3)
    # timeline.render(OUTPUT_PATH)

    # # Testing concatenating
    # timeline = Timeline()
    # # When you concat like this, some of the
    # # videos have frames that cannot be accessed
    # # and I don't know why...
    # timeline.add_video(Video('test_files/glitch_rgb_frame.mp4'))
    # timeline.add_video(Video('test_files/output.mp4'))
    # timeline.add_video(Video('test_files/output_render.mp4'))
    # timeline.add_video(Video('test_files/strange_tv_frame.mp4'))
    # timeline.add_video(Video('test_files/test_1.mp4'))
    # timeline.add_video(Video('test_files/test_1_short_2.mp4'))
    # timeline.add_video(Video('test_files/test_audio_1st_track_solo_v0_0_15.mp4'))
    # timeline.add_video(Video('test_files/test_audio_2nd_track_solo_v0_0_15.mp4'))
    # timeline.add_video(Video('test_files/test_audio_combined_tracks_v0_0_015.mp4'))
    # timeline.add_video(Video('test_files/test_audio_combined_v0_0_15.mp4'))
    # timeline.add_video(Video('test_files/test_blend_add_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_difference_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_multiply_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_overlay_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_blend_screen_v0_0_16.mp4'))
    # timeline.add_video(Video('test_files/test_combine_skipping_empty_using_priority_v0_0_18.mp4'))
    # timeline.add_video(Video('test_files/test_ok_v0_0_13.mp4'))

    # timeline.render('test_files/concatenated.mp4')

    # from yta_video_pyav.media import ImageMedia, ColorMedia

    # image_media = ImageMedia('test_files/mobile_alpha.png', 0, 1).save_as('test_files/test_image.mp4')

    # color_media = ColorMedia('random', 0, 1).save_as('test_files/test_color.mp4')

    # return

    # TODO: This test will add videos that
    # must be played at the same time

    # from yta_video_ffmpeg.handler import FfmpegHandler

    # ffmpeg_handler = FfmpegHandler()

    # # ffmpeg_handler.video.encoding.to_dnxhr(VIDEO_PATH, 'test_files/video_dnxhr.mov')
    # # ffmpeg_handler.video.encoding.to_prores(VIDEO_PATH, 'test_files/video_prores.mov')
    # # ffmpeg_handler.video.encoding.to_mjpeg(VIDEO_PATH, 'test_files/video_mjpeg.mov')

    # ffmpeg_handler.video.trim_fast(VIDEO_PATH, 0.25, 0.75, 'test_files/trimmed_fast.mp4')
    # ffmpeg_handler.video.trim_accurate(VIDEO_PATH, 0.25, 0.75, 'test_files/trimmed_accurate.mp4')
    # ffmpeg_handler.audio.trim_fast(AUDIO_PATH, 0.25, 1.75, 'test_files/trimmed_fast.mp3')
    # ffmpeg_handler.audio.trim_accurate(AUDIO_PATH, 0.25, 1.75, 'test_files/trimmed_accurate.mp3')

    # return


    # audio = Audio(AUDIO_PATH, 3, 6).save_as('test_files/output.mp3')

    # return

    video = Video(VIDEO_PATH, 0.25, 0.75)
    timeline = Timeline()

    transitions_30fps = 'C:/Users/dania/Downloads/Y2meta.app-10 Smooth Transitions Green Screen Template For Kinemaster, Alight Motion, Filmora, premiere pro-(1080p).mp4'
    simpsons_60fps = 'C:/Users/dania/Downloads/Y_una_porra_los_simpsons_castellano_60fps.mp4'

    prores_path = 'test_files/video_prores.mov'
    mjpeg_path = 'test_files/video_mjpeg.avi' # gives error
    dnxhr_path = 'test_files/video_dnxhr.mov'

    # Simplified test just to check no errors
    timeline.add_video(Video(mjpeg_path, 0.25, 1.0), 0.75, track_index = 0)

    timeline.add_video(Video(mjpeg_path, 0.1, 0.8), 0.2, track_index = 1)

    timeline.render(OUTPUT_PATH)

    return

    # Track 1
    timeline.add_video(Video(VIDEO_PATH, 0.25, 1.0), 0.75, track_index = 0)
    timeline.add_video(Video(simpsons_60fps, 1.5, 2.0), 3.0, track_index = 0)
    timeline.add_video(Video(VIDEO_PATH, 0.5, 1.0), 2.0, track_index = 0)

    #timeline.tracks[0].mute()

    # Track 2
    timeline.add_video(Video(VIDEO_PATH, 0.5, 1.0), 2.7, track_index = 1)
    timeline.add_video(Video(simpsons_60fps, 5.8, 7.8), 0.6, track_index = 1)
    # 30fps
    # timeline.add_video(Video('C:/Users/dania/Downloads/Y2meta.app-TOP 12 SIMPLE LIQUID TRANSITION _ GREEN SCREEN TRANSITION PACK-(1080p60).mp4', 0.25, 1.5), 0.25, do_use_second_track = True)
    # 29.97fps
    # timeline.add_video(Video('C:/Users/dania/Downloads/Y_una_porra_los_simpsons_castellano.mp4', 5.8, 6.8), 3.6, do_use_second_track = True)
    
    timeline.render(OUTPUT_PATH)

    return

    Video(VIDEO_PATH, 0.25, 0.75).save_as(OUTPUT_PATH)

    return