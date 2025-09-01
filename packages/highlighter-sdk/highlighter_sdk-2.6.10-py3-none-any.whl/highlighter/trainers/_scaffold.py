import importlib
import json
import shutil
from enum import Enum
from pathlib import Path
from sys import activate_stack_trampoline
from typing import Union

from pydantic import ValidationError


class TrainerType(str, Enum):
    YOLO_DET = "yolo-det"
    YOLO_SEG = "yolo-seg"
    YOLO_CLS = "yolo-cls"
    # ToDo: Add when the sdk can generate the correct dataset formats
    # YOLO_POSE = "yolo-det"
    # YOLO_OOB = "yolo-det"


class DIRS:

    @staticmethod
    def training_run_dir(ml_training_dir: Path, training_run_id: Union[str, int]) -> Path:
        """This is for storing user facing dataset stuff"""
        return ml_training_dir / str(training_run_id)

    @staticmethod
    def hl_cache(ml_training_dir: Path, training_run_id: Union[str, int]) -> Path:
        d = ml_training_dir / str(training_run_id) / ".hl"
        d.mkdir(exist_ok=True, parents=True)
        return d

    @staticmethod
    def hl_training_config(ml_training_dir: Path, training_run_id: Union[str, int]) -> Path:
        """This is for storing non-user facing dataset stuff"""
        return DIRS.hl_cache(ml_training_dir, training_run_id) / "training_config.json"

    @staticmethod
    def hl_training_run_cache_datasets_dir(ml_training_dir: Path, training_run_id: Union[str, int]) -> Path:
        """This is for storing non-user facing dataset stuff"""
        d = DIRS.hl_cache(ml_training_dir, training_run_id) / "datasets"
        d.mkdir(exist_ok=True, parents=True)
        return d


def load_trainer_module(training_run_dir):
    trainer_module_path = training_run_dir / "trainer.py"
    module_name = "trainer"
    spec = importlib.util.spec_from_file_location(module_name, trainer_module_path)
    trainer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trainer)
    return trainer


def ask_to_mkdir(dir, terminate=False):
    response = input(f"Create directory '{dir}'? (y/n):").lower() in ("y", "yes")
    if response:
        Path(dir).mkdir(exist_ok=True, parents=True)
    if terminate:
        raise SystemExit(f"Terminating, {dir} exists.")
    else:
        return False


def ask_to_remove(pth, terminate=False):
    pth = Path(pth)
    response = input(f"Do you want to remove '{pth}'? (y/n):").lower() in ("y", "yes")
    if response:
        shutil.rmtree(pth)
        return True
    elif terminate:
        raise SystemExit(f"Terminating, did not remove {pth}")
    else:
        return False


def ask_to_overwrite(src, dst, terminate=False):
    src = Path(src)
    dst = Path(dst)
    overwrite = input(f"Do you want to overwrite '{dst}'? (y/n):").lower() in ("y", "yes")
    if overwrite:
        if dst.is_file():
            src.rename(dst)
        elif dst.is_dir():
            shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            raise ValueError(f"Unable to overwrite {src} with {dst}")
        return True
    elif terminate:
        raise SystemExit(f"Terminating, {dst} exists.")
    else:
        return False


def safe_move(src, dst):
    if dst.exists():
        ask_to_overwrite(src, dst, terminate=True)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            src.rename(dst)
        elif src.is_dir():
            shutil.copytree(src, dst)
