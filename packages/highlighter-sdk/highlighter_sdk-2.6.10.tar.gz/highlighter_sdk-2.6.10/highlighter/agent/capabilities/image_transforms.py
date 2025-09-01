from typing import Dict, List, Optional, Tuple

from aiko_services.elements.media import image_io

from highlighter.agent.capabilities import Capability
from highlighter.agent.capabilities.base_capability import StreamEvent
from highlighter.core.data_models import DataSample

__all__ = ["ImageOverlay", "ImageResize"]


class ImageResize(Capability):
    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        width: int = 0  # If zero, will maintain aspect ratio with respect to height
        height: int = 0  # If zero, will maintain aspect ratio with respect to width

    @property
    def width(self) -> int:
        return self._get_parameter("width")[0]

    @property
    def height(self) -> int:
        return self._get_parameter("height")[0]

    def process_frame(self, data_samples: List[DataSample]) -> Tuple[StreamEvent, Optional[Dict]]:
        data_samples = [ds.resize(width=self.width, height=self.height) for ds in data_samples]
        return StreamEvent.OKAY, {"data_samples": data_samples}


class ImageOverlay(image_io.ImageOverlay, Capability):

    def process_frame(self, stream, data_samples, annotations):
        for ds, annos in zip(data_samples, annotations):
            ds_anns = [a for a in annos if a.data_file_id == ds.data_file_id]
            overlay = ds.draw_annotations(ds_anns)
            ds.content = overlay
        return StreamEvent.OKAY, {"data_samples": data_samples}
