# To Do
# ~~~~~

import sys

import aiko_services as aiko

__all__ = ["HLDataSchemePipe"]

# --------------------------------------------------------------------------- #


class HLDataSchemePipe(aiko.DataScheme):

    def create_sources(self, stream, data_sources, frame_generator=None, use_create_frame=True):

        source_buffers = []
        for _ in data_sources:
            try:
                source_buffers.append(sys.stdin.buffer)
            except Exception as e:
                diagnostic = f'Error loading file, "{e}"'
                return aiko.StreamEvent.ERROR, {"diagnostic": diagnostic}

        pipeline_element = self.pipeline_element
        if use_create_frame:
            """
            - Not sure how to determine the frame_data keys ahead of time.
            - Not sure how this makes sense for DataSource Elements that
              produce many frames for one file, ie VideoFileRead
            """
            NotImplementedError()
        else:
            stream.variables["source_buffers"] = source_buffers
            rate, _ = pipeline_element.get_parameter("rate", default=None)
            rate = float(rate) if rate else None
            pipeline_element.create_frames(stream, frame_generator, rate=rate)
        return aiko.StreamEvent.OKAY, {}

    def create_targets(self, stream, data_targets):
        return aiko.StreamEvent.OKAY, {}

    def destroy_sources(self, stream):
        self.terminate = True

    def frame_generator(self, stream, frame_id):
        raise ValueError("Use the DataSourceCapability frame_generator")


aiko.DataScheme.add_data_scheme("hlpipe", HLDataSchemePipe)

# --------------------------------------------------------------------------- #
