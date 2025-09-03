"""
This is a very nice tool to interact with
the powerfull ffmpeg but making it easier.

Check these links below:
- https://www.reddit.com/r/ffmpeg/comments/ks8zfs/comment/gieu7x6/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
- https://stackoverflow.com/questions/38368105/ffmpeg-custom-sequence-input-images/51618079#51618079
- https://stackoverflow.com/a/66014158
"""
from yta_video_ffmpeg.flag import FfmpegFlag
from yta_video_ffmpeg.command import FfmpegCommand
from yta_image_utils.resize import get_cropping_points_to_keep_aspect_ratio
from yta_video_utils.dimensions import get_video_size
from yta_positioning.coordinate import NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_file.handler import FileHandler
from yta_constants.file import FileType, FileExtension
from yta_constants.video import FfmpegAudioCodec, FfmpegFilter, FfmpegPixelFormat, FfmpegVideoCodec, FfmpegVideoFormat
from yta_programming.output import Output
from yta_temp import Temp
from typing import Union
from subprocess import run


class _VideoFfmpegHandlerEncoding:
    """
    Class to wrap the functionality related
    to encoding videos and audios. Useful
    when we need to transform a video into
    a I-frame video to be able to edit it
    more efficiently.
    """

    def to_prores(
        self,
        video_filename: str,
        output_filename: str
    ):
        """
        Encode the 'video_filename' to a ProRes
        video that is perfect for edition (it has
        I-frames).

        The recommended extensions are:
        - `.mov`
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileExtension.MOV)

        """
        Help:
        -c:v prores_ks → ProRes coder
        -profile:v 3 → 'standard' profile (HQ is 4, bigger size)
        -c:a copy → copy without recompressing
        """

        # Valid example:
        # ffmpeg -i input.mp4 -c:v prores_ks -profile:v 3 -c:a copy output_prores.mov
        run(f'ffmpeg -i {video_filename} -c:v prores_ks -profile:v 3 -c:a copy {output_filename}')

        return output_filename
    
    def to_dnxhr(
        self,
        video_filename: str,
        output_filename: str
    ):
        """
        Encode the 'video_filename' to a DNxHR
        video that is perfect for edition (it has
        I-frames).

        The recommended extensions are:
        - `.mov`
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileExtension.MOV)

        # Valid example:
        # ffmpeg -i input.mp4 -c:v dnxhd -b:v 36M -c:a copy output_dnxhr.mov
        run(f'ffmpeg -i {video_filename} -c:v dnxhd -b:v 36M -c:a copy {output_filename}')

        return output_filename
    
    def to_mjpeg(
        self,
        video_filename: str,
        output_filename: str
    ):
        """
        Encode the 'video_filename' to a MJPEG
        video that is perfect for edition (it has
        I-frames).

        The recommended extensions are:
        - `.avi`
        - `.mov`
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileExtension.AVI)

        """
        Help:
        -c:v mjpeg → Motion JPEG (MJPEG) codec
        -q:v 3 → JPEG quality (1 = best, 31 = worst)
        -c:a copy → copy without recompressing
        """

        # Valid example:
        # ffmpeg -i input.mp4 -c:v mjpeg -q:v 3 -c:a copy output_mjpeg.avi
        run(f'ffmpeg -i {video_filename} -c:v mjpeg -q:v 3 -c:a copy {output_filename}')

        return output_filename

class _VideoFfmpegHandlerInterpolation:
    """
    Class to wrap the functionality related
    to interpolation.
    """

    def interpolate_slow(
        self,
        video_filename: str,
        fps: int,
        output_filename: str
    ):
        """
        Interpolate the 'video_filename' video to
        have the given 'fps'.

        This process can take a lot of time but 
        the result should be very nice. A test with
        a 20s video has taken 21 minutes in my
        sh*tty laptop.
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        # Valid example:
        # 'ffmpeg -i input.mp4 -vf "minterpolate=fps=60" output.mp4'
        run(f'ffmpeg -i {video_filename} -vf "minterpolate=fps={str(fps)}" {output_filename}')

        return output_filename

    def interpolate_normal(
        self,
        video_filename: str,
        fps: int,
        output_filename: str
    ):
        """
        Generate intermediate frames at the provided
        'fps' with simplified interpolation.

        Soft results, a bit slower than level 1 but
        better results.
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        # Valid example:
        # 'ffmpeg -i input.mp4 -vf "minterpolate=fps=60" -c:v libx264 -preset fast -crf 18 output.mp4'
        run(f'ffmpeg -i {video_filename} -vf "minterpolate=fps={str(fps)}" -c:v libx264 -preset ultrafast -crf 23 {output_filename}')

        return output_filename
    
    def interpolate_fast(
        self,
        video_filename: str,
        fps: int,
        output_filename: str
    ):
        """
        Make a blend between frames to be smooth,
        but scenes with a lot of movement can be
        blurry.

        Depends a lot on the input, but could be a
        good and not too slow option.
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        # Valid example:
        # 'ffmpeg -i input.mp4 -vf "fps=60,tblend=all_mode=average" output.mp4'
        run(f'ffmpeg -i {video_filename} -vf "fps={str(fps)},tblend=all_mode=average" {output_filename}')

        return output_filename
        
    def interpolate_instant(
        self,
        video_filename: str,
        fps: int,
        output_filename: str
    ):
        """
        Modify the amount of fps to the given 'fps'
        parameter but with no improvement.

        Not a good result but the fastest one.

        The command:
        - `-i {video_filename} -vf "fps={fps}" -c:v libx264 -preset ultrafast -crf 23 {output_filename}`
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        # Valid example:
        # TODO: This -crf 18 below is apparently max
        # quality, so it is very slow
        # 'ffmpeg -i input.mp4 -vf "fps=60" -c:v libx264 -preset fast -crf 18 output.mp4'
        # run(f'ffmpeg -i {video_filename} -vf "fps={str(fps)}" -c:v libx264 -preset fast -crf 18 {output_filename}')
        # Use this for a fast result:
        # ffmpeg -i input.mp4 -vf "fps=60" -c:v libx264 -preset ultrafast -crf 23 output.mp4
        run(f'ffmpeg -i {video_filename} -vf "fps={str(fps)}" -c:v libx264 -preset ultrafast -crf 23 {output_filename}')

        return output_filename
        

class _VideoFfmpegHandler:
    """
    Class to wrap the functionality related
    to videos.
    """

    def __init__(
        self
    ):
        self.interpolation: _VideoFfmpegHandlerInterpolation = _VideoFfmpegHandlerInterpolation()
        """
        Shortcut to the functionality related to
        video interpolation.
        """
        self.encoding: _VideoFfmpegHandlerEncoding = _VideoFfmpegHandlerEncoding()
        """
        Shortcut to the functionality related to
        video encoding.
        """
        
    # TODO: Check this one below
    def extract_audio_deprecated(
        self,
        video_filename: str,
        codec: FfmpegAudioCodec = None,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Exports the audio of the provided video to a local file named
        'output_filename' if provided or as a temporary file.

        # TODO: This has not been tested yet.

        Pro tip: You can read the return with AudioParser.as_audioclip
        method.

        This method returns the filename of the file that has been
        generated as a the audio of the provided video.
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        codec = (
            FfmpegAudioCodec.to_enum(codec)
            if codec is not None else
            None
        )

        FfmpegCommand([
            FfmpegFlag.input(video_filename),
            (
                FfmpegFlag.audio_codec(codec)
                if codec else
                None
            ),
            output_filename
        ]).run()

        return output_filename
    
    def extract_audio(
        self,
        video_filename: str,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Exports the audio of the provided video to a local file named
        'output_filename' if provided or as a temporary file.

        Pro tip: You can read the return with AudioParser.as_audioclip
        method.

        This method returns the filename of the file that has been
        generated as a the audio of the provided video.
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)
        # TODO: Verify valid output_filename extension

        FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.map('0:1'),
            output_filename
        ]).run()

        return output_filename
    
    def get_best_thumbnail(
        self,
        video_filename: str,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Gets the best thumbnail of the provided 'video_filename'.

        Pro tip: You can read the return with ImageParser.to_pillow
        method.

        This method returns the filename of the file that has been
        generated as a the thumbnail of the provided video.
        """
        validate_video_filename(video_filename)
        output_filename = Output.get_filename(output_filename, FileType.IMAGE)

        FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.filter(FfmpegFilter.THUMBNAIL),
            output_filename
        ]).run()

        return output_filename
    
    def concatenate(
        self,
        video_filenames: list[str],
        output_filename: str = None
    ) -> str:
        """
        Concatenates the provided 'video_filenames' in the order in
        which they are provided.

        Using Ffmpeg is very useful when trying to concatenate similar
        videos (the ones that we create always with the same 
        specifications) because the codecs are the same so the speed
        is completely awesome.

        Pro tip: You can read the return with VideoParser.to_moviepy
        method.

        This method returns the filename of the file that has been
        generated as a concatenation of the provided ones.
        """
        for video_filename in video_filenames:
            validate_video_filename(video_filename)

        output_filename = Output.get_filename(output_filename, FileType.VIDEO)
        concat_filename = FfmpegHandler.write_concat_file(video_filenames)

        FfmpegCommand([
            FfmpegFlag.overwrite(True),
            FfmpegFlag.force_format(FfmpegVideoFormat.CONCAT),
            FfmpegFlag.safe_routes(0),
            FfmpegFlag.input(concat_filename),
            FfmpegFlag.codec('copy'),
            output_filename
        ]).run()

        return output_filename
    
    def resize(
        self,
        video_filename: str,
        size: tuple,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Resize the provided 'video_filename', by keeping
        the aspect ratio (cropping if necessary), to the
        given 'size' and stores it locally as
        'output_filename'.

        This method returns the generated file filename.

        See more: 
        https://www.gumlet.com/learn/ffmpeg-resize-video/
        """
        validate_video_filename(video_filename)
        ParameterValidator.validate_mandatory_tuple('size', size, None)
        # TODO: I think we don't need this with the 'Output.get_filename'
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)
        
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        # Validate that 'size' is a valid size
        # TODO: This code is a bit strange, but was refactored from the
        # original one that was in 'yta_multimedia' to remove the
        # dependency. Maybe update it?
        if not PythonValidator.is_numeric_tuple_or_list_or_array_of_2_elements_between_values(size, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE, NORMALIZATION_MIN_VALUE, NORMALIZATION_MAX_VALUE):
            # TODO: Raise error
            raise Exception(f'The provided size parameter is not a tuple or array, or does not have 2 elements that are numbers between {str(NORMALIZATION_MIN_VALUE)} and {str(NORMALIZATION_MAX_VALUE)}.')

        w, h = get_video_size(video_filename)

        if (w, h) == size:
            # No need to resize, we just copy it to output
            FileHandler.copy_file(video_filename, output_filename)
        else:
            # First, we need to know if we need to scale it
            original_ratio = w / h
            new_ratio = size[0] / size[1]

            new_size = (
                (w * (size[1] / h), size[1])
                # Original video is wider than the expected one
                if original_ratio > new_ratio else
                # Original video is higher than the expected one
                (size[0], h * (size[0] / w))
                if original_ratio < new_ratio else
                (size[0], size[1])
            )

            tmp_filename = Temp.get_wip_filename('tmp_ffmpeg_scaling.mp4')

            # Scale to new dimensions
            FfmpegCommand([
                FfmpegFlag.input(video_filename),
                FfmpegFlag.scale_with_size(new_size),
                tmp_filename
            ]).run()

            # Now, with the new video resized, we look for the
            # cropping points we need to apply and we crop it
            top_left, _ = get_cropping_points_to_keep_aspect_ratio(new_size, size)

            # Second, we need to know if we need to crop it
            FfmpegCommand([
                FfmpegFlag.input(tmp_filename),
                FfmpegFlag.crop(size, top_left),
                FfmpegFlag.overwrite(True),
                output_filename
            ]).run()

        return output_filename
    
    def trim_fast(
        self,
        video_filename: str,
        start: Union[int, float],
        end: Union[int, float],
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Fast but can be inaccurate. It can fail if no video
        keyframe found on the times provided. I recommend
        you to use the 'trim_accurate' instead.

        Trims the provided 'video_filename' and generates a
        shorter resource that is stored as 'output_filename'.
        This new resource will last from 'start' to 'end'.

        This method is very fast but can be inaccurate
        according to keyframes and can start before. 
        Consider using the 'trim_accurate' method instead if
        you need accuracy, but it will take more time to
        finish.

        This method returns the generated file filename.

        The command:
        - `-i {video_filename} -ss {start} -to {end} -c copy {output_filename}`

        Thank you:
        https://www.plainlyvideos.com/blog/ffmpeg-trim-videos
        https://trac.ffmpeg.org/wiki/Seeking
        """
        validate_video_filename(video_filename)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = True)
        
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        command = FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.seeking(start),
            FfmpegFlag.to(end),
            FfmpegFlag.codec(FfmpegVideoCodec.COPY),
            FfmpegFlag.overwrite(True),
            output_filename
        ])

        command.run()

        #ffmpeg_command = f'-ss 00:02:05 -i {video} -to 00:03:10 -c copy video-cutted-ffmpeg.mp4'
        return output_filename

    def trim_accurate(
        self,
        video_filename: str,
        start: Union[int, float],
        end: Union[int, float],
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Accurate but can be slow.

        Trims the provided 'video_filename' and generates a
        shorter resource that is stored as 'output_filename'.
        This new resource will last from 'start' to 'end'.

        This method is accurate but can be slow as it has to
        be decoded and coded again to be accurate. Consider
        using the 'trim_fast' method instead if you need
        speed, but the result could be longer than expected.

        This method returns the generated file filename.

        The command:
        - `-i {video_filename} -ss {start} -to {end} -c:v libx264 -c:a aac {output_filename}`
        """
        validate_video_filename(video_filename)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = True)
        
        # TODO: The extension should match the codec
        # but we want this dynamic
        output_filename = Output.get_filename(output_filename, FileExtension.MP4)

        command = FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.seeking(start),
            FfmpegFlag.to(end),
            FfmpegFlag.video_codec(FfmpegVideoCodec.LIBX264),
            FfmpegFlag.audio_codec(FfmpegAudioCodec.AAC),
            #FfmpegFlag.strict(-2), # old, not needed now
            FfmpegFlag.overwrite(True),
            output_filename
        ])

        command.run()

        #ffmpeg -i input.mp4 -ss 00:01:00 -to 00:02:00 -c:v libx264 -c:a aac -strict -2 output.mp4
        return output_filename
    
    def set_audio(
        self,
        video_filename: str,
        audio_filename: str,
        output_filename: Union[str, None] = None
    ):
        """
        TODO: This method has not been properly tested yet.

        Set the audio given in the 'audio_filename' in the also
        provided video (in 'video_filename') and creates a new
        file containing the video with the audio.

        This method returns the generated file filename.
        """
        validate_video_filename(video_filename)
        validate_audio_filename(audio_filename)
        # TODO: I think we don't need this with the 'Output.get_filename'
        ParameterValidator.validate_mandatory_string('output_filename', output_filename)
        
        output_filename = Output.get_filename(output_filename, FileType.VIDEO)

        command = FfmpegCommand([
            FfmpegFlag.input(video_filename),
            FfmpegFlag.input(audio_filename),
            FfmpegFlag.video_codec(FfmpegVideoCodec.COPY),
            FfmpegFlag.audio_codec(FfmpegAudioCodec.AAC),
            #FfmpegFlag.strict(-2), # old, not needed now
            FfmpegFlag.overwrite(True),
            output_filename
        ])

        command.run()
        
        # cls.run_command([
        #     FfmpegFlag.input(video_filename),
        #     FfmpegFlag.input(audio_filename),
        #     output_filename
        # # TODO: Unfinished
        # ])

        # TODO: Is this actually working (?)
        #run(f"ffmpeg -i {video_filename} -i {audio_filename} -c:v copy -c:a aac -strict experimental -y {output_filename}")

        return output_filename
        
        # Apparently this is the equivalent command according
        # to ChatGPT, but maybe it doesn't work
        # ffmpeg -i input_video -i input_audio -c:v copy -c:a aac -strict experimental -y output_filename

        # There is also a post that says this:
        # ffmpeg -i input.mp4 -i input.mp3 -c copy -map 0:v:0 -map 1:a:0 output.mp4
        # in (https://superuser.com/a/590210)


        # # TODO: What about longer audio than video (?)
        # # TODO: This is what was being used before FFmpegHandler
        # input_video = ffmpeg.input(video_filename)
        # input_audio = ffmpeg.input(audio_filename)

        # ffmpeg.concat(input_video, input_audio, v = 1, a = 1).output(output_filename).run(overwrite_output = True)
        
class _AudioFfmpegHandler:
    """
    Class to wrap the functionality related
    to audios.
    """

    def __init__(
        self
    ):
        pass

    def trim_fast(
        self,
        audio_filename: str,
        start: Union[int, float],
        end: Union[int, float],
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Fast but can be inaccurate.

        Trims the provided 'audio_filename' and generates a
        shorter resource that is stored as 'output_filename'.
        This new resource will last from 'start' to 'end'.

        This method is very fast but can be inaccurate
        according to keyframes and can start before. 
        Consider using the 'trim_accurate' method instead if
        you need accuracy, but it will take more time to
        finish.

        This method returns the generated file filename.

        The command:
        - `-i {audio_filename} -ss {start} -to {end} -c copy {output_filename}`
        """
        validate_audio_filename(audio_filename)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = True)
        
        output_filename = Output.get_filename(output_filename, FileType.AUDIO)

        command = FfmpegCommand([
            FfmpegFlag.input(audio_filename),
            FfmpegFlag.seeking(start),
            FfmpegFlag.to(end),
            FfmpegFlag.codec(FfmpegVideoCodec.COPY),
            FfmpegFlag.overwrite(True),
            output_filename
        ])

        command.run()

        #ffmpeg -i input.mp3 -ss 30 -to 90 -c copy output.mp3
        return output_filename 
    
    def trim_accurate(
        self,
        audio_filename: str,
        start: Union[int, float],
        end: Union[int, float],
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Accurate but can be slow.

        Trims the provided 'audio_filename' and generates a
        shorter resource that is stored as 'output_filename'.
        This new resource will last from 'start' to 'end'.

        This method is accurate but can be slow as it has to
        be decoded and coded again to be accurate. Consider
        using the 'trim_fast' method instead if you need
        speed, but the result could be longer than expected.

        This method returns the generated file filename.

        The command:
        - `-i {audio_filename} -ss {start} -to {end} -c:a libmp3lame -b:a 192k {output_filename}`
        """
        validate_audio_filename(audio_filename)
        ParameterValidator.validate_mandatory_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_mandatory_positive_number('end', end, do_include_zero = True)
        
        # TODO: The extension should match the codec
        # but we want this dynamic
        output_filename = Output.get_filename(output_filename, FileExtension.MP3)

        command = FfmpegCommand([
            FfmpegFlag.input(audio_filename),
            FfmpegFlag.seeking(start),
            FfmpegFlag.to(end),
            FfmpegFlag.audio_codec(FfmpegAudioCodec.LIBMP3LAME),
            FfmpegFlag.audio_bit_rate('192k'),
            FfmpegFlag.overwrite(True),
            output_filename
        ])

        command.run()

        #ffmpeg -i input.mp3 -ss 30 -to 90 -c:a libmp3lame -b:a 192k output.mp3
        return output_filename
    

    # TODO: Implement something for audio files
        
class _ImageFfmpegHandler:
    """
    Class to wrap the functionality related
    to images.
    """

    def __init__(
        self
    ):
        pass

    def concatenate(
        self,
        image_filenames: list[str],
        frame_rate = 60,
        pixel_format: FfmpegPixelFormat = FfmpegPixelFormat.YUV420p,
        output_filename: Union[str, None] = None
    ) -> str:
        """
        Concatenates the provided 'image_filenames' in the order in
        which they are provided.

        Using Ffmpeg is very useful when trying to concatenate similar
        images because the speed is completely awesome.

        Pro tip: You can read the return with VideoParser.to_moviepy().

        This method returns the filename of the file that has been
        generated as a concatenation of the provided ones.
        """
        for image_filename in image_filenames:
            validate_image_filename(image_filename)

        output_filename = Output.get_filename(output_filename, FileType.VIDEO)
        concat_filename = FfmpegHandler.write_concat_file(image_filenames)

        # TODO: Should we check the pixel format or give freedom (?)
        # pixel_format = FfmpegPixelFormat.to_enum(pixel_format)

        FfmpegCommand([
            FfmpegFlag.force_format(FfmpegVideoFormat.CONCAT),
            FfmpegFlag.safe_routes(0),
            FfmpegFlag.overwrite(True),
            FfmpegFlag.frame_rate(frame_rate),
            FfmpegFlag.input(concat_filename),
            FfmpegFlag.video_codec(FfmpegVideoCodec.QTRLE),
            FfmpegFlag.pixel_format(pixel_format), # I used 'argb' in the past
            output_filename
        ]).run()

        return output_filename

class FfmpegHandler:
    """
    Class to simplify and encapsulate ffmpeg functionality.
    """

    def __init__(
        self
    ):
        self.video: _VideoFfmpegHandler = _VideoFfmpegHandler()
        """
        Shortcut to the functionality related to
        videos.
        """
        self.audio: _AudioFfmpegHandler = _AudioFfmpegHandler()
        """
        Shortcut to the functionality related to
        audios.
        """
        self.image: _ImageFfmpegHandler = _ImageFfmpegHandler()
        """
        Shortcut to the functionality related to
        images.
        """

    def write_concat_file(
        self,
        filenames: str
    ) -> str:
        """
        Write the files to concat in a temporary text file with
        the required format and return that file filename. This
        is required to use different files as input.

        This method returns the created file filename that 
        includes the list with the 'filenames' provided ready
        to be concatenated.
        """
        text = '\n'.join(
            f"file '{filename}'"
            for filename in filenames
        )

        # TODO: Maybe this below is interesting for the 'yta_general_utils.file.writer'
        # open('concat.txt', 'w').writelines([('file %s\n' % input_path) for input_path in input_paths])
        filename = Temp.get_wip_filename('concat_ffmpeg.txt')
        FileHandler.write_str(filename, text)

        return filename

    def run_command(
        self,
        command: Union[list[FfmpegFlag, any], FfmpegCommand]
    ) -> None:
        """
        Runs the provided ffmpeg 'command'.
        """
        command = (
            FfmpegCommand(command)
            if not PythonValidator.is_instance_of(command, FfmpegCommand) else
            command
        )

        command.run()

def validate_video_filename(
    video_filename: str
) -> None:
    """
    Validate if the provided 'video_filename'
    parameter is a string and a valid video file
    (based on its extension).
    """
    ParameterValidator.validate_mandatory_string('video_filename', video_filename, do_accept_empty = False)

    # TODO: If possible (and no dependency issue) check 
    # the content to validate it is parseable as video
    if not FileHandler.is_video_file(video_filename):
        raise Exception('The provided "video_filename" is not a valid video file name.')
    
def validate_audio_filename(
    audio_filename: str
) -> None:
    """
    Validate if the provided 'audio_filename'
    parameter is a string and a valid audio file
    (based on its extension).
    """
    ParameterValidator.validate_mandatory_string('audio_filename', audio_filename, do_accept_empty = False)

    # TODO: If possible (and no dependency issue) check 
    # the content to validate it is parseable as audio
    if not FileHandler.is_audio_file(audio_filename):
        raise Exception('The provided "audio_filename" is not a valid audio file name.')
    
def validate_image_filename(
    image_filename: str
):
    """
    Validate if the provided 'image_filename'
    parameter is a string and a valid image file
    (based on its extension).
    """
    ParameterValidator.validate_mandatory_string('image_filename', image_filename, do_accept_empty = False)

    # TODO: If possible (and no dependency issue) check 
    # the content to validate it is parseable as image
    if not FileHandler.is_image_file(image_filename):
        raise Exception('The provided "image_filename" is not a valid image file name.')

    # TODO: Keep going