import io
import logging
import os
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import BinaryIO, Iterable, Union

import av
import numpy as np
from PIL import Image

from highlighter.agent.utilities import (
    EntityAggregator,
    FileAvroEntityWriter,
    FileAvroObservationWriter,
)
from highlighter.client import ENTITY_AVRO_SCHEMA
from highlighter.core.data_models.data_sample import DataSample
from highlighter.io.base import PayloadWriter

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EncodeSettings:
    codec: str = "h264"
    pix_fmt: str = "yuv420p"
    crf: int = 23
    preset: str = "medium"
    scenecut: str = "0"


class ImageWriter(PayloadWriter):
    """
    Serialise one or many image samples as a single **PNG**.

    * If exactly one sample is supplied, the payload is just that image.
    * If more than one sample is supplied, the images are tiled into a
      square-ish grid:  ``cols = ceil(sqrt(N)), rows = ceil(N/cols)``.
    """

    extension = "png"  # DataFile.original_source_url <uuid>.png

    def __init__(self, *, mode: str = "RGB", extension: str = "PNG"):
        """
        Parameters
        ----------
        mode
            PIL/Pillow image mode for the final canvas (defaults to ``"RGB"``).
        extension
            PIL/Pillow image extension for the final canvas (defaults to ``"PNG"``).
        """
        self.mode = mode
        self.extension = extension

    # The signature mirrors VideoWriter so DataFile.save_local can treat every
    # writer uniformly.
    def write(
        self,
        samples: Iterable[DataSample],
        sink: Union[str, os.PathLike, BinaryIO],
    ) -> None:
        samples = list(samples)
        if not samples:
            raise ValueError("ImageWriter.write() received no samples")

        # Convert every DataSample → PIL.Image
        pil_images = []
        for s in samples:
            if isinstance(s.content, Image.Image):
                img = s.content.convert(self.mode)
            else:
                arr = s.to_ndarray()
                if arr.ndim == 2:  # greyscale → RGB
                    arr = np.stack([arr] * 3, axis=-1)
                img = Image.fromarray(arr).convert(self.mode)
            pil_images.append(img)

        # Tile if necessary
        if len(pil_images) == 1:
            final_img = pil_images[0]
        else:
            w, h = pil_images[0].size
            n = len(pil_images)
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
            canvas = Image.new(self.mode, (cols * w, rows * h))
            for idx, img in enumerate(pil_images):
                r, c = divmod(idx, cols)
                canvas.paste(img.resize((w, h)), (c * w, r * h))
            final_img = canvas

        # Write to the requested sink
        close_sink = False
        if isinstance(sink, (str, Path)):
            sink = open(sink, "wb")  # type: ignore[assignment]
            close_sink = True
        final_img.save(sink, format=self.extension)
        if close_sink:
            sink.close()


class TextWriter(PayloadWriter):
    def write():
        pass


class ObservationWriter(PayloadWriter):
    extension = "avro"

    def write(
        self,
        samples: Iterable[DataSample],
        sink: Union[str, os.PathLike, BinaryIO],
    ) -> None:
        """
        Encode all Observations into *sink*
        """
        samples = list(samples)
        grouped: Dict[UUID, List[Observation]] = defaultdict(list)
        for sample in samples:
            obs = sample.content
            obs.datum_source.frame_id = sample.media_frame_index
            obs.annotation.datum_source.frame_id = sample.media_frame_index
            grouped[obs.entity_id].append(obs)

        writer = FileAvroObservationWriter(
            ENTITY_AVRO_SCHEMA,
            sink,
        )

        writer.write(grouped)


class VideoWriter(PayloadWriter):
    """
    Stream-encode frames into a video sink with efficient, C-based resizing:
      • configurable frame_rate, bit_rate, resolution
      • pre-flight probing for resolution and bitrate
      • `av.VideoFrame.reformat` for on-the-fly scaling (fast C)
    """

    extension = "mp4"
    supports_resize = True

    def __init__(
        self,
        *,
        frame_rate: float = 24.0,
        bit_rate: int | None = None,
        resolution: tuple[int, int] | None = None,
        extension: str = "mp4",
        settings: EncodeSettings = EncodeSettings(),
    ):
        self.frame_rate = frame_rate
        self.bit_rate = bit_rate
        self.resolution = resolution
        self.settings = settings
        self.extension = extension

    def _prepare(self, first_frame: DataSample) -> tuple[int, int]:
        """
        Determine target width/height and estimate bit_rate if unset.
        """
        arr = first_frame.to_ndarray()
        h, w = arr.shape[:2]
        if self.resolution:
            width, height = self.resolution
        else:
            width, height = w, h
        if self.bit_rate is None:
            raw_bytes = arr.nbytes
            # use 25% of raw size as heuristic
            self.bit_rate = int(raw_bytes * self.frame_rate * 8 * 0.25)
        return width, height

    def write(
        self,
        samples: Iterable[DataSample],
        sink: Union[str, os.PathLike, BinaryIO],
    ) -> None:
        """
        Encode all frames into *sink*, streaming scaled frames via C.
        """
        frames = list(samples)
        if not frames:
            raise ValueError("VideoWriter.write() received no samples")

        width, height = self._prepare(frames[0])

        close_sink = False
        if isinstance(sink, (str, Path)):
            sink = open(sink, "wb")  # type: ignore[assignment]
            close_sink = True

        container = av.open(sink, mode="w", format=self.extension)
        stream = container.add_stream(self.settings.codec, rate=Fraction(self.frame_rate))
        stream.width, stream.height = width, height
        stream.pix_fmt = self.settings.pix_fmt
        stream.options.update(
            {
                "crf": str(self.settings.crf),
                "preset": self.settings.preset,
                "scenecut": self.settings.scenecut,
            }
        )
        if self.bit_rate:
            stream.bit_rate = self.bit_rate

        for frame in frames:
            arr = frame.to_ndarray()
            if not isinstance(arr, np.ndarray):
                raise TypeError(f"Expected a NumPy ndarray, got {type(arr).__name__}")
            vf = av.VideoFrame.from_ndarray(arr, format="rgb24")
            # fast, C-level reformat for scaling/pad
            if (vf.width, vf.height) != (width, height):
                vf = vf.reformat(width=width, height=height, format="rgb24")  # C-based scaling
            for packet in stream.encode(vf):
                container.mux(packet)

        # flush and close
        for packet in stream.encode():
            container.mux(packet)
        container.close()
        if close_sink:
            sink.close()
