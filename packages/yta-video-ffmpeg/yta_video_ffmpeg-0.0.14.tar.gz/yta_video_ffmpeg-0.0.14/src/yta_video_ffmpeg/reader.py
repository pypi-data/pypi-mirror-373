
"""
TODO: Check the 'yta_video_opengl' because 
I'm using pyav there, which is using ffmpeg
in the background, so this is unnecessary.
"""
from dataclasses import dataclass

import numpy as np
import subprocess
import json


@dataclass
class FfmpegVideoInfo:
    """
    Dataclass to hold the information about
    a video read with Ffmpeg.
    """

    def __init__(
        self,
        filename: str,
        json_data: any
    ):
        self.filename: str = filename
        """
        The video file name.
        """

        format_data = json_data.get('format', {})
        self.duration = format_data.get('duration', 0)
        """
        The duration of the video in seconds.
        """
        self.size = format_data.get('size', 0)
        self.bit_rate = format_data.get('bit_rate', 0)
        self.video = {
            'codec': None,
            'size': None,
            'fps': None,
            'pix_fmt': None
        }
        self.audio = {}

        for stream in json_data.get('streams', []):
            if stream.get('codec_type') == 'video':
                # FPS se calcula a partir de r_frame_rate
                fps_str = stream.get("r_frame_rate", "0/0")
                try:
                    num, den = map(int, fps_str.split("/"))
                    fps = num / den if den != 0 else 0
                except ValueError:
                    fps = 0

                self.video_codec: str = stream.get('codec_name', None)
                self.size: tuple[int, int] = (
                    int(stream.get('width', 0)),
                    int(stream.get('height', 0))
                )
                self.fps = fps
                self.pixel_format = stream.get('pix_fmt')

                self.has_alpha = False
                if (
                    self.pixel_format and
                    any(
                        a in self.pixel_format
                        for a in ['a', 'alpha']
                    )
                ):
                    # Ej: yuva420p, rgba, bgra...
                    if self.pixel_format.startswith(('yuva', 'rgba', 'bgra', 'argb', 'ya')):
                        self.has_alpha = True

                # Rotation
                # TODO: None or 0 (?)
                rotation = None
                if 'tags' in stream and 'rotate' in stream['tags']:
                    try:
                        rotation = int(stream['tags']['rotate'])
                    except ValueError:
                        pass

                # Caso 2: side_data_list con "rotation"
                for side_data in stream.get('side_data_list', []):
                    if 'rotation' in side_data:
                        try:
                            rotation = int(side_data['rotation'])
                        except ValueError:
                            pass

                self.rotation = rotation
            elif stream.get('codec_type') == 'audio':
                self.audio_codec: str = stream.get('codec_name', None)
                self.number_of_channels = int(stream.get('channels', 0))
                self.sample_rate = int(stream.get('sample_rate', 0))

class FfmpegReader:
    """
    Class to wrap functionality related to
    reading videos.
    """

    @property
    def process(
        self
    ):
        if not hasattr(self, '_process'):
            self._process = subprocess.Popen(
                [
                    "ffmpeg",
                    "-i", self.filename,
                    "-f", "image2pipe",
                    "-pix_fmt", self.pixel_format,
                    "-vcodec", "rawvideo",
                    "-"
                ],
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE
            )

        return self._process
    
    @property
    def width(
        self
    ) -> int:
        return self.metadata.size[0]
    
    @property
    def height(
        self
    ) -> int:
        return self.metadata.size[1]

    def __init__(
        self,
        filename: str,
        pixel_format: str = 'rgba'
    ):
        self.filename: str = filename
        """
        The filename of the video we are reading.
        """
        self.metadata: FfmpegVideoInfo = FfmpegReader.get_video_metadata(filename)
        """
        The information about the video.
        """

        # TODO: Why this 'pixel_format' (?)
        self.pixel_format = pixel_format
        self.process = None

    def read_frame(
        self
    ):
        frame_size = self.width * self.height * len(self.pixel_format)
        raw_frame = self.process.stdout.read(frame_size)

        if len(raw_frame) != frame_size:
            # End of the video
            return None

        frame = np.frombuffer(raw_frame, np.uint8).reshape((self.height, self.width, len(self.pix_fmt)))
        return frame
    
    def close(self):
        if self.process:
            self.process.stdout.close()
            self.process.terminate()
            self.process.wait()
            self.process = None

    # TODO: Maybe move this to a utils
    @staticmethod
    def get_video_metadata(
        filename: str
    ) -> FfmpegVideoInfo:
        cmd = [
            "ffprobe",
            # Errors only
            "-v", "error",
            # General data (duration, bitrate, etc.)
            "-show_format",
            # Stream info (video, audio, etc.)
            "-show_streams",
            "-print_format", "json",# Salida en JSON
            filename
        ]
        
        result = subprocess.run(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text = True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Error ejecutando ffprobe: {result.stderr}")
        
        json_data = json.loads(result.stdout)

        return FfmpegVideoInfo(filename, json_data)
