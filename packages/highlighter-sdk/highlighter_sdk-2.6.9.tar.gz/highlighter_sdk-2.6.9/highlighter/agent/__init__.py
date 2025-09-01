try:
    import aiko_services

    # ToDo: Consider a better way to import DataSchemes from aiko,
    #       importing DataSchemes will add the to the DataScheme.LOOKUP dict
    from aiko_services.elements import media as aiko_media_elements
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "To user Highlighter agents you must install aiko_services. "
        "Use `pip install highlighter-sdk[agent]` or, "
        " `pip install aiko_services` manually."
    )
from .agent import *
from .data_schemes import *
