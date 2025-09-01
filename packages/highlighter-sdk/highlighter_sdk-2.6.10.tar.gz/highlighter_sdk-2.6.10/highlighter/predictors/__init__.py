try:
    import onnxruntime
except ModuleNotFoundError as _:
    from highlighter.core.exceptions import OptionalPackageMissingError

    raise OptionalPackageMissingError("onnxruntime", "predictors")
