import aiko_services as aiko

__all__ = ["HLDataSchemeHTTP"]


class HLDataSchemeHTTP(aiko.DataScheme):

    def create_sources(self, stream, data_sources, frame_generator=None, use_create_frame=True):

        urls = []
        for data_source in data_sources:
            try:
                urls.append(data_source.replace("hlhttp://", ""))

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
            task_id = None
            stream.variables["source_paths_generator"] = iter([(u, task_id) for u in urls])
            rate, _ = pipeline_element.get_parameter("rate", default=None)
            rate = float(rate) if rate else None
            pipeline_element.create_frames(stream, frame_generator, rate=rate)
        return aiko.StreamEvent.OKAY, {}


HLDataSchemeHTTP.add_data_scheme("hlhttp", HLDataSchemeHTTP)
