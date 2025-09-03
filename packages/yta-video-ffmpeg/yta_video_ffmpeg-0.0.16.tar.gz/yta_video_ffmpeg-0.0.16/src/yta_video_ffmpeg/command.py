from yta_video_ffmpeg.flag import FfmpegFlag
from typing import Union
from subprocess import run


class FfmpegCommand:
    """
    Class to represent a command to be built and
    executed by the FfmpegHandler.

    A valid example of a command is built like this:
    
    FfmpegCommand([
        FfmpegFlag.force_format(FfmpegVideoFormat.CONCAT),
        FfmpegFlag.safe_routes(0),
        FfmpegFlag.overwrite(True),
        FfmpegFlag.frame_rate(frame_rate),
        FfmpegFlag.input(concat_filename),
        FfmpegFlag.video_codec(FfmpegVideoCodec.QTRLE),
        FfmpegFlag.pixel_format(pixel_format), # I used 'argb' in the past
        output_filename
    ])
    """
    args: list[Union[FfmpegFlag, any]] = None
    
    def __init__(
        self,
        args: list[Union[FfmpegFlag, any]]
    ):
        # TODO: Validate args
        self.args = args

    def run(
        self
    ):
        """
        Run the command.
        """
        run(self.__str__())

    def __str__(
        self
    ) -> str:
        """
        Turn the command to a string that can be directly
        executed as a ffmpeg command.
        """
        # TODO: Clean args (?)
        # Remove 'None' args, our logic allows them to make it easier
        args = [
            arg
            for arg in self.args
            if arg is not None
        ]

        return f"ffmpeg {' '.join(args)}"