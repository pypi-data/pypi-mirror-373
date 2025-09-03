from yta_date import Date
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator
from yta_constants.video import FfmpegAudioCodec, FfmpegFilter, FfmpegPixelFormat, FfmpegVideoCodec, FfmpegVideoFormat
from typing import Union


class FfmpegFlag:
    """
    Class to simplify the way we push flags into
    the ffmpeg command.
    """

    @staticmethod
    def overwrite(
        do_overwrite: bool = True
    ) -> str:
        """
        Set the overwriting strategy if a video with
        the same name is found when trying to write a
        file.

        If yes, the file will be overwritten, and if
        no, the ffmpeg execution will fail and exit.

        The command:
        - `-y` (if yes, overwrite)
        - `-n` (if no, don't overwrite)
        """
        ParameterValidator.validate_mandatory_bool('do_overwrite', do_overwrite)

        return (
            '-y'
            if do_overwrite else
            '-n'
        )

    @staticmethod
    def force_format(
        format: FfmpegVideoFormat
    ) -> str:
        """
        Force the output format to be the provided 'format'.

        Code: `-f {format}`
        """
        format = FfmpegVideoFormat.to_enum(format).value

        return f'-f {format}'
    
    @staticmethod
    def safe_routes(
        value: int
    ) -> str:
        """
        To enable or disable unsafe paths.

        Code: `-safe {value}`
        """
        ParameterValidator.validate_mandatory_int('value', value)
        # TODO: Check that 'value' is a number between -1 and 1

        return f'-safe {str(value)}'
    
    @staticmethod
    def input(
        input: str
    ) -> str:
        """
        To set the input (or inputs) we want.

        Code: `-i {input}`
        """
        ParameterValidator.validate_mandatory_string('input', input, do_accept_empty = False)

        return f'-i {input}'
    
    @staticmethod
    def audio_codec(
        codec: Union[FfmpegAudioCodec, str]
    ) -> str:
        """
        Sets the general audio codec.

        Code: `-c:a {codec}`
        """
        # We cannot control the big amount of audio codecs that
        # are available so we allow any string as parameter
        try:
            codec = FfmpegAudioCodec.to_enum(codec).value
        except:
            pass

        return f'-c:a {codec}'
    
    @staticmethod
    def video_codec(
        codec: Union[FfmpegVideoCodec, str]
    ) -> str:
        """
        Sets the general video codec.

        Code: `-c:v {codec}`
        """
        # We cannot control the big amount of video codecs that
        # are available so we allow any string as parameter
        try:
            codec = FfmpegVideoCodec.to_enum(codec).value
        except:
            pass

        return f'-c:v {codec}'

    @staticmethod
    def v_codec(
        codec: Union[FfmpegVideoCodec, str]
    ) -> str:
        """
        Sets the video codec.

        TODO: I don't know exactly the difference between '-c:v {codec}'
        and the '-vcodec' generated in this method. I keep this method
        until I actually find the difference. I don't even know if the
        video codecs I can provide as values are the same as in the other
        method.

        Code: `-vcodec {codec}`
        """
        # We cannot control the big amount of video codecs that
        # are available so we allow any string as parameter
        try:
            codec = FfmpegVideoCodec.to_enum(codec).value
        except:
            pass

        return f'-vcodec {codec}'

    @staticmethod
    def codec(
        codec: Union[FfmpegVideoCodec, FfmpegAudioCodec, str]
    ) -> str:
        """
        Sets the general codec with '-c {codec}'.

        -c copy indica que se deben copiar los flujos de audio y video sin recodificación, lo que hace que la operación sea rápida y sin pérdida de calidad.

        Code: `-c {codec}`
        """
        # We cannot control the big amount of video codecs that
        # are available so we allow any string as parameter

        # TODO: Validate provided 'codec'
        # TODO: This method has a variation, it can be '-c:a' or '-c:v'
        if not PythonValidator.is_instance_of(codec, [FfmpegVideoCodec, FfmpegAudioCodec]):
            try:
                codec = FfmpegVideoCodec.to_enum(codec)
            except:
                pass

        if not PythonValidator.is_instance_of(codec, [FfmpegVideoCodec, FfmpegAudioCodec]):
            try:
                codec = FfmpegAudioCodec.to_enum(codec)
            except:
                pass

        if PythonValidator.is_instance_of(codec, [FfmpegVideoCodec, FfmpegAudioCodec]):
            codec = codec.value

        return f'-c {codec}'
    
    @staticmethod
    def strict(
        strictness: int
    ) -> str:
        """
        Set the level of strictness for the codec,
        that means allowing using experimental codecs
        and things that haven't been completely
        tested.

        There are different levels of strictness:
        - `-strict 0`: normal (default)
        - `-strict -1`: allow non standard things
        - `-strict -2`: allow experimental codecs

        It is not common to use it, but sometimes you
        will need it, so here it is.

        The command text:
        - `-strict {strictness}`
        """
        ParameterValidator.validate_mandatory_int('strictness', strictness)

        return f'-strict {strictness}'
    
    @staticmethod
    def map(
        map: str
    ) -> str:
        """
        Set input stream mapping.
        -map [-]input_file_id[:stream_specifier][,sync_file_id[:stream_s set input stream mapping

        # TODO: Improve this

        Code: `-map {map}`
        """
        ParameterValidator.validate_mandatory_string('map', map, do_accept_empty = False)

        return f'-map {map}'
    
    @staticmethod
    def filter(
        filter: FfmpegFilter
    ) -> str:
        """
        Sets the expected filter to be used.

        Code: `-filter {filter}`
        """
        filter = FfmpegFilter.to_enum(filter).value

        return f'-filter {filter}'
    
    @staticmethod
    def frame_rate(
        frame_rate: int
    ) -> str:
        """
        Sets the frame rate (Hz value, fraction or abbreviation)

        Code: `-r {frame_rate}`
        """
        ParameterValidator.validate_mandatory_int('frame_rate', frame_rate)
        # TODO: Maybe accept some range (?)

        return f'-r {str(frame_rate)}'
    
    @staticmethod
    def audio_bit_rate(
        bit_rate: str
    ) -> str:
        """
        Set the bit rate for the audio.

        Code: `-b:a {bit_rate}`

        Valid value: `-b:a 192k`
        """
        ParameterValidator.validate_mandatory_string('bit_rate', bit_rate, do_accept_empty = False)

        return f'-b:a {bit_rate}'
    
    @staticmethod
    def pixel_format(
        format: FfmpegPixelFormat
    ) -> str:
        """
        Set the pixel format.

        Code: `-pix_fmt {format}`
        """
        format = FfmpegPixelFormat.to_enum(format).value

        return f'-pix_fmt {format}'
    
    @staticmethod
    def scale_with_size(
        size: tuple
    ) -> str:
        """
        Set a new size.

        Code: `-vf scale=size[0]:size[1]`
        """
        ParameterValidator.validate_mandatory_tuple('size', size, 2)

        return f'-vf scale={str(int(size[0]))}:{str(int(size[1]))}'

    @staticmethod
    def scale_with_factor(
        w_factor: float,
        h_factor: float
    ) -> str:
        """
        Set a new size multiplying by a factor.

        Code: `-vf "scale=iw*w_factor:ih*h_factor"`
        """
        ParameterValidator.validate_mandatory_float('w_factor', w_factor)
        ParameterValidator.validate_mandatory_float('h_factor', h_factor)

        return f'-vf "scale=iw*{str(w_factor)}:ih*{str(h_factor)}"'

    @staticmethod
    def crop(
        size: tuple,
        origin: tuple
    ) -> str:
        """
        Crop the video to a new with the provided 'size'
        starting with the top left corner at the given
        'origin' position of the original video.
        
        Code: `-vf "crop=size[0]:size[1]:origin[0]:origin[1]"`
        """
        ParameterValidator.validate_mandatory_tuple('size', size, 2)
        ParameterValidator.validate_mandatory_tuple('origin', origin, 2)

        return f"-vf \"crop={str(int(size[0]))}:{str(int(size[1]))}:{str(int(origin[0]))}:{str(int(origin[1]))}\""
    
    @staticmethod
    def preset(
        preset: str
    ) -> str:
        """
        Apply the given 'preset', that can be 'fast',
        'ultrafast', etc.

        The command:
        - `-preset {preset}`
        """
        ParameterValidator.validate_mandatory_string('preset', preset, do_accept_empty = False)

        return f'-preset {preset}'
    
    @staticmethod
    def constant_rate_factor(
        rate_factor: int
    ) -> str:
        """
        Apply the given 'rate_factor' that will result
        in a better or worst quality.

        The command:
        - `-crf {rate_factor}`
        """
        # TODO: Is 0 included? I don't know the accepted values
        ParameterValidator.validate_mandatory_positive_int('rate_factor', rate_factor, do_include_zero = False)

        return f'-crf {str(rate_factor)}'
    
    @staticmethod
    def crf(
        rate_factor: int
    ) -> str:
        """
        Alias of `constant_rate_factor` to match the
        exact name when used as command.

        Apply the given 'rate_factor' that will result
        in a better or worst quality.

        The command:
        - `-crf {rate_factor}`
        """
        return FfmpegFlag.constant_rate_factor(rate_factor)
    
    @staticmethod
    def seeking(
        seconds: Union[int, float]
    ) -> str:
        """
        Skip the necessary amount of time to go directly
        to the provided 'seconds' time of the input (that
        must be provided after this).

        Code: `-ss {seconds}`

        Valid value: `-ss 0.5`
        """
        ParameterValidator.validate_positive_number('seconds', seconds)

        return f'-ss {str(seconds)}'
    
    @staticmethod
    def to(
        seconds: Union[int, float]
    ) -> str:
        """
        Used with 'seeking' to match the end time we want
        to apply to the new trimmed input. In general, 
        this will be the time moment in 'seconds' to end
        being played.

        Code: `-to {seconds}`

        Valid value: `-to 0.75`
        """
        ParameterValidator.validate_positive_number('seconds', seconds)

        return f'-to {str(seconds)}'

    def time(
        seconds: Union[int, float]
    ) -> str:
        """
        Used with 'seeking' to match the duration we want
        to apply to the new trimmed input. In general, 
        this will be the time in 'seconds' it will last
        being played.

        Code: `-t {seconds}`

        Valid value: `-t 0.75`
        """
        ParameterValidator.validate_positive_number('seconds', seconds)

        return f'-t {str(seconds)}'