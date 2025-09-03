"""
Module to simplify the use of Ffmpeg and to make
awesome things with simple methods.

Nice help: https://www.bannerbear.com/blog/how-to-use-ffmpeg-in-python-with-examples/
Official doc: https://www.ffmpeg.org/ffmpeg-resampler.html
More help: https://kkroening.github.io/ffmpeg-python/
Nice guide: https://img.ly/blog/ultimate-guide-to-ffmpeg/
Available flags: https://gist.github.com/tayvano/6e2d456a9897f55025e25035478a3a50

Interesting usage: https://stackoverflow.com/a/20325676
Maybe avoid writting on disk?: https://github.com/kkroening/ffmpeg-python/issues/500#issuecomment-792281072
"""
from yta_video_ffmpeg.handler import FfmpegHandler


__all__ = [
    'FfmpegHandler'
]


if __name__ == '__main__':
    from yta_video_ffmpeg.reader import FfmpegReader

    info = FfmpegReader.get_video_metadata('test_files/test_1.mp4')
    print(info.has_alpha)
    print(info.duration)