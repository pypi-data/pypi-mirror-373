{ pkgs }:
let
  python = pkgs.python3.override {
    self = python;
    packageOverrides = pythonOverrides;
  };
  pythonOverrides = pythonFinal: pythonPrev: {
    {{ cookiecutter.__pname }} = pythonFinal.mkPythonEditablePackage {
      pname = "{{ cookiecutter.__pname }}";
      version = "0.1";
      dependencies = [pythonFinal.highlighter-sdk] ++ pythonFinal.highlighter-sdk.optional-dependencies.yolo;
      root = "$REPO_ROOT/src";
    };
    highlighter-sdk = pythonFinal.buildPythonPackage rec {
      pname = "highlighter_sdk";
      version = "2.5.2";
      format = "pyproject";
      buildInputs = [ pythonFinal.hatchling ];
      src = pythonFinal.fetchPypi {
        inherit pname version;
        hash = "sha256-pxicqqakui5tJngwfWoZxom2b2xTauL4EGeqv8oogXo=";
      };
      postPatch = ''
        substituteInPlace pyproject.toml \
          --replace-fail 'packages = ["src/highlighter", "src/aiko_services"]' \
                         'packages = ["highlighter", "aiko_services"]'

      '';
      nativeCheckInputs = [
        pkgs.writableTmpDirAsHomeHook
      ];
      dependencies =
        with pythonFinal;
        [
          alembic
          av
          boto3
          click
          colorama
          cookiecutter
          fastavro
          gql
          pandas
          pillow
          pooch
          pydantic
          python-magic
          pyyaml
          requests
          shapely
          sqlmodel
          tables
          tomli-w
          tqdm
          jupyterlab

          # aiko
          asciimatics
          avro
          avro-validator
          paho-mqtt
          psutil
          pyperclip
          pyzmq
          transitions
          wrapt
        ]
        ++ pythonFinal.gql.optional-dependencies.aiohttp
        ++ pythonFinal.gql.optional-dependencies.requests;
      optional-dependencies = {
        cv2 = with pythonFinal; [ opencv4 ];
        predictors = with pythonFinal; [ opencv4 torch onnxruntime ];
        yolo = with pythonFinal; [ opencv4 torch onnxruntime ultralytics onnx];
      };
      pythonRelaxDeps = [
        "avro"
        "pyperclip"
        "pyzmq"
        "boto3"
        "pillow"
        "psutil"
        "pydantic"
        "wrapt"
        "paho-mqtt"
      ];
      nativeBuildInputs = [ pythonFinal.pythonRelaxDepsHook ];
      pythonRemoveDeps = [
        "shapely"
        "opencv-python"
      ];
      pythonImportsCheck = [ "highlighter" "aiko_services" ];
    };
    avro-validator = pythonFinal.buildPythonPackage (rec {
      pname = "avro_validator";
      version = "1.2.1";
      format = "setuptools";
      src = pkgs.fetchFromGitHub {
        owner = "leocalm";
        repo = pname;
        rev = "refs/tags/${version}";
        hash = "sha256:17lxwy68r6wn3mpz3l7bi3ajg7xibp2sdz94hhjigfkxvz9jyi2f";
      };
      pythonImportsCheck = [ "avro_validator" ];
    });
    torch = pythonPrev.torch.override (old: {
      cudaSupport = true;
      inherit cudaPackages;
    });
    onnxruntime = pythonPrev.onnxruntime.override (old: {
      onnxruntime = old.onnxruntime.override (old: {
        cudaSupport = true;
        ncclSupport = true;
        inherit cudaPackages;
      });
    });
  };
  cudaPackages = pkgs.cudaPackages // {
    cudaFlags = pkgs.cudaPackages.cudaFlags // {
      cudaCapabilities = [
        # https://en.wikipedia.org/wiki/CUDA#Version_features_and_specifications#GPUs-supported
        "6.1" # GTX 1080 ti
        "7.5" # RTX 2080 ti, T4
      ];
    };
  };
in
python.withPackages (ps: with ps; [
  numpy ipython magic highlighter-sdk {{ cookiecutter.__pname }}
] ++ highlighter-sdk.optional-dependencies.yolo)
