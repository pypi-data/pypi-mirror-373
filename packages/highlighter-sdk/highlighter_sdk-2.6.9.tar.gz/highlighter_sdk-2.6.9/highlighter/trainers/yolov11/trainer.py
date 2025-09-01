import json
import logging
from abc import abstractmethod
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

import numpy as np
import ultralytics
import yaml

from highlighter.client import json_tools
from highlighter.client.evaluation import (
    EvaluationMetric,
    EvaluationMetricCodeEnum,
    EvaluationMetricResult,
    find_or_create_evaluation_metric,
)
from highlighter.client.gql_client import HLClient
from highlighter.client.io import multithread_graphql_file_download
from highlighter.client.training_config import TrainingConfigType
from highlighter.core.const import OBJECT_CLASS_ATTRIBUTE_UUID
from highlighter.core.labeled_uuid import LabeledUUID
from highlighter.datasets.cropping import CropArgs
from highlighter.datasets.dataset import Dataset
from highlighter.datasets.formats.yolo.writer import YoloWriter
from highlighter.trainers._scaffold import TrainerType

__all__ = ["YoloV11Trainer"]


class BaseTrainer:

    head_idx: int = 0

    crop_args: CropArgs = CropArgs()

    # Only use attributes with this specific attribute_id as the
    # categories for your dataset
    category_attribute_id: UUID = OBJECT_CLASS_ATTRIBUTE_UUID

    # Optionally define a list of attribute values to use for your dataset.
    # If None, then use the output attributes defined in the TrainingConfigType.input_output_schema.
    # If categories is set then the YoloWrite will respect the order they are
    # listed.
    categories: Optional[List[str]] = None

    def __init__(
        self,
        training_run_dir: Path,
        highlighter_training_config: TrainingConfigType,
        trainer_type: TrainerType,
    ):
        self._trainer_type = trainer_type

        self._logger = logging.getLogger(__name__)
        self._training_run_dir = training_run_dir
        self._hl_training_config = highlighter_training_config
        self._hl_training_config.dump("json", self._hl_training_config_path)
        with (self._hl_cache_dir / "trainer-type").open("w") as f:
            f.write(trainer_type.value)

    @property
    def _hl_cache_dir(self):
        d = self._training_run_dir / ".hl"
        d.mkdir(exist_ok=True, parents=True)
        return d

    @property
    def _hl_cache_dataset_dir(self):
        d = self._hl_cache_dir / "datasets"
        d.mkdir(exist_ok=True, parents=True)
        return d

    @property
    def _hl_training_config_path(self):
        d = self._hl_cache_dir / "training_config.json"
        return d

    @abstractmethod
    def generate_boilerplate(self):
        """Puts the standard boilerplate files and makes directories required
        by in the Trainer in the training_run_dir. Downloads as caches
        the dataset annotations
        """
        pass

    @abstractmethod
    def training_data_dir(self) -> Path:
        """Path to data used to store training data"""

    @abstractmethod
    def generate_trainer_specific_dataset(self, hl_dataset: Dataset):
        pass

    @abstractmethod
    def train(self) -> Any:
        """Trains the Model, return the trained model instance"""
        pass

    @abstractmethod
    def evaluate(
        self, checkpoint: Path, object_classes: List[LabeledUUID], cfg_path: Optional[Path] = None
    ) -> Dict[str, EvaluationMetricResult]:
        """Evaluate a model given a Path to a checkpoint, onnx_file or model instance"""
        pass

    @abstractmethod
    def export_to_onnx(self, trained_model) -> Path:
        """Export the trained model to onnx

        Return:
            Path to the onnx model
        """
        pass

    @abstractmethod
    def make_artefact(self, onnx_file_path: Path) -> Path:
        """Create a Highlighter training run artefact give the input checkpoint

        Return:
            Path to the artefact.yaml
        """
        pass

    @property
    def training_run_id(self) -> int:
        return self._hl_training_config.training_run_id

    @property
    def research_plan_id(self) -> int:
        return self._hl_training_config.evaluation_id

    def get_datasets(self, client: HLClient, page_size=100) -> Dataset:
        """Returns a Highlighter SDK Dataset object containing data from each
        split in the one object. `dataset.data_files_id.split` identifies the
        which split each data_file belongs to.
        """
        datasets = Dataset.read_training_config(
            client, self._hl_training_config, self._hl_cache_dataset_dir, page_size=page_size
        )
        return self._combine_hl_datasets(datasets)

    def _combine_hl_datasets(self, datasets):
        # When creating a training run in Highlighter the train split is required
        # but a user can supply either a test or dev set, or both. If not both we
        # duplicate the one that exists here
        if "test" not in datasets:
            datasets["test"] = deepcopy(datasets["dev"])
            datasets["test"].data_files_df.split = "test"
        if "dev" not in datasets:
            datasets["dev"] = deepcopy(datasets["test"])
            datasets["dev"].data_files_df.split = "dev"

        # Combine the Highlighter Datasets together because this is what the YoloWriter
        # expects
        combined_ds = datasets["train"]
        combined_ds.append([datasets["dev"], datasets["test"]])

        # Ultralytics name their dataset splits differently so
        # we need to map them
        #   their "val" is our "test"
        #   their "test" is our "dev"
        combined_ds.data_files_df.loc[combined_ds.data_files_df.split == "test", "split"] = "val"
        combined_ds.data_files_df.loc[combined_ds.data_files_df.split == "dev", "split"] = "test"
        return combined_ds

    def filter_dataset(self, dataset: Dataset) -> Dataset:
        """Optionally add some code to filter the Highlighter Datasets as required.
        The YoloWriter will only use entities with both a pixel_location attribute
        and a 'category_attribute_id' attribute when converting to the Yolo dataset format.
        It will the unique values for the object_class attribute as the detection
        categories.

        For example, if you want to train a detector that finds Apples and Bananas,
        and your taxonomy looks like this:

            - object_class: Apple
            - object_class: Orange
            - object_class: Banana

        Then you may do something like this:

            adf = combined_ds.annotations_df
            ddf = combined_ds.data_files_df

            orange_entity_ids = adf[(adf.attribute_id == OBJECT_CLASS_ATTRIBUTE_UUID) &
                                   (adf.value == "Orange")].entity_id.unique()

            # Filter out offending entities
            adf = adf[adf.entity_id.isin(orange_entity_ids)]

            # clean up images that are no longer needed
            ddf = ddf[ddf.data_file_id.isin(adf.data_file_id)]

            combined_ds.annotations_df = adf
        """
        return dataset

    def _train(self, hl_dataset: Dataset):

        self.generate_trainer_specific_dataset(hl_dataset)

        trained_model = self.train()
        onnx_model_path = self.export_to_onnx(trained_model)
        artefact_path = self.make_artefact(onnx_model_path)
        eval_metric_results = self.evaluate(onnx_model_path, self.get_categories())
        return trained_model, artefact_path.absolute(), onnx_model_path, eval_metric_results

    def get_categories(self) -> List[LabeledUUID]:
        all_cat_ids = self._hl_training_config.input_output_schema.get_head_output_attribute_enum_ids(
            self.head_idx
        )
        all_cat_values = self._hl_training_config.input_output_schema.get_head_output_attribute_enum_values(
            self.head_idx
        )

        if self.categories is None:
            categories = self._hl_training_config.input_output_schema.get_head_output_attribute_enum_ids(
                self.head_idx
            )
        else:
            categories = self.categories

        idxs = [all_cat_ids.index(c) for c in categories]
        return [LabeledUUID.from_str(f"{all_cat_ids[i]}|{all_cat_values[i]}") for i in idxs]

    def get_category_attribute_id(self):
        if self.category_attribute_id is None:
            category_attribute_id = (
                self._hl_training_config.input_output_schema.get_head_output_attribute_ids(self.head_idx)[0]
            )
        else:
            category_attribute_id = self.category_attribute_id
        return category_attribute_id


class YoloV11Trainer(BaseTrainer):

    def __init__(
        self,
        training_run_dir: Path,
        highlighter_training_config: TrainingConfigType,
        trainer_type: TrainerType,
    ):
        super().__init__(training_run_dir, highlighter_training_config, trainer_type)
        self._cfg = self._get_config()

    def _get_hl_metrics(self, client: HLClient):

        task = self._cfg["task"]

        if self._cfg["task"] in ("detect", "segment"):
            _metrics = self._get_metrics_det_seg()
        elif task == "classify":
            _metrics = self._get_metrics_classify()
        else:
            raise SystemExit(f"Invalid yolo task '{task}'")

        metrics = find_or_create_evaluation_metric(
            client,
            _metrics,
        )
        return {m.name: m for m in metrics}

    def _get_metrics_det_seg(self):
        cats = self.get_categories()
        _metrics = []
        _metrics.extend(
            [
                EvaluationMetric(
                    research_plan_id=self.research_plan_id,
                    code=EvaluationMetricCodeEnum.mAP,
                    chart="Per Class Metrics",
                    description=f"Mean Avarage Precision ({cat.short_str()})",
                    iou=0.5,
                    name=f"mAP@IOU50({cat.short_str()})",
                    object_class_uuid=cat,
                )
                for cat in cats
            ]
        )
        _metrics.extend(
            [
                EvaluationMetric(
                    research_plan_id=self.research_plan_id,
                    code=EvaluationMetricCodeEnum.Other,
                    chart="Per Class Metrics",
                    description=f"Precision ({cat.short_str()})",
                    name=f"Precision({cat.short_str()})",
                    object_class_uuid=cat,
                )
                for cat in cats
            ]
        )
        _metrics.extend(
            [
                EvaluationMetric(
                    research_plan_id=self.research_plan_id,
                    code=EvaluationMetricCodeEnum.Other,
                    chart="Per Class Metrics",
                    description=f"Recall ({cat.short_str()})",
                    name=f"Recall({cat.short_str()})",
                    object_class_uuid=cat,
                )
                for cat in cats
            ]
        )

        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.mAP,
                chart="Aggregate Metrics",
                description="Mean Avarage Precision Over All Classes",
                iou=0.5,
                name="mAP@IOU50",
            )
        )
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Aggregate Metrics",
                description="Precision Over All Classes",
                name="Precision",
            )
        )
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Aggregate Metrics",
                description="Recall Over All Classes",
                name="Recall",
            )
        )
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Model Size",
                description="Size of the model, 0:Nano|1:Small|2:Medium|3:Large|4:XLarge",
                name="Model Size",
            )
        )
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Ideal Confidence Threshold",
                description="The Confidence Threshold that maximizes the F1Score",
                name="Ideal Confidence Threshold",
            )
        )
        return _metrics

    def _get_metrics_classify(self):
        _metrics = []
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Aggregate Metrics",
                description="Top One Accuracy",
                name="Accuracy Top1",
            )
        )
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Aggregate Metrics",
                description="Top Five Accuracy",
                name="Accuracy Top5",
            )
        )
        _metrics.append(
            EvaluationMetric(
                research_plan_id=self.research_plan_id,
                code=EvaluationMetricCodeEnum.Other,
                chart="Model Size",
                description="Size of the model, 0:Nano|1:Small|2:Medium|3:Large|4:XLarge",
                name="Model Size",
            )
        )
        return _metrics

    def _get_config(self) -> Dict:
        if (self._training_run_dir / "cfg.yaml").exists():
            cfg = ultralytics.utils.YAML.load(self._training_run_dir / "cfg.yaml")
        else:
            cfg = self._get_default_config()
        return cfg

    def _get_default_config(self):
        overrides_lookup = {
            TrainerType.YOLO_DET: {
                "model": "yolov8m.pt",
                "task": "detect",
            },
            TrainerType.YOLO_SEG: {
                "model": "yolov8m-seg.pt",
                # Ensures overlapping masks are merged, which is critical for accurate
                # segmentation in datasets with overlapping objects (default is True, but
                # explicitly set for clarity).
                "overlap_mask": True,
                # Controls mask resolution; 4 is the default and balances detail
                # with computational efficiency, suitable for most segmentation tasks.
                "mask_ratio": 4,
                "task": "segment",
            },
            TrainerType.YOLO_CLS: {
                "model": "yolov8m-cls.pt",
                # Adds regularization to prevent overfitting, which is more common
                # in classification tasks with large datasets; 0.1 is a modest starting point.
                "dropout": 0.1,
                # Classification often works with smaller images than detection/segmentation;
                # 224 is a common size (e.g., ImageNet), balancing detail and speed.
                "imgsz": 224,
                "task": "classify",
            },
        }

        overrides = overrides_lookup[self._trainer_type]

        default_cfg = dict(ultralytics.cfg.get_cfg())
        default_cfg.update(overrides)
        default_cfg["project"] = "runs"
        default_cfg["opset"] = 14
        default_cfg["format"] = "onnx"
        default_cfg["dynamic"] = False
        return default_cfg

    def generate_boilerplate(self):
        with (self._training_run_dir / "cfg.yaml").open("w") as f:
            yaml.dump(self._cfg, f)

    @property
    def config_path(self):
        return self._training_run_dir / "cfg.yaml"

    def _make_classify_artefact(self, onnx_filepath) -> Path:
        crop_args = self.get_crop_args()
        if isinstance(crop_args, CropArgs):
            crop_args_dict = crop_args.model_dump()
        elif crop_args is None:
            crop_args_dict = None
        else:
            raise ValueError(f"Crop args must be None or an instance of `CropArgs` got: {crop_args}")
        d = dict(
            file_url=str(Path(onnx_filepath.absolute())),
            type="OnnxOpset14",
            inference_config=dict(
                type="classifier",
                code="BoxClassifier",
                machine_agent_type_id="d4787671-3839-4af9-9b34-a686faafbfae",
                parameters=dict(
                    output_format="yolov8_cls",
                    cropper=crop_args_dict,
                ),
            ),
            training_config=self._cfg,
        )

        artefact_path = onnx_filepath.parent / "artefact.yaml"
        with artefact_path.open("w") as f:
            yaml.dump(d, f)

        return artefact_path

    def _make_detect_segment_artefact(self, onnx_filepath) -> Path:
        output_format = "yolov8_seg" if self._cfg["task"] == "segment" else "yolov8_det"
        d = dict(
            file_url=str(Path(onnx_filepath.absolute())),
            type="OnnxOpset14",
            inference_config=dict(
                type="detector",
                code="Detector",
                machine_agent_type_id="29653174-8f45-440d-b75a-4ed0aa5fa6ff",
                parameters=dict(
                    output_format=output_format,
                ),
            ),
            training_config=self._cfg,
        )

        artefact_path = onnx_filepath.parent / "artefact.yaml"
        with artefact_path.open("w") as f:
            yaml.dump(d, f)

        return artefact_path

    def export_to_onnx(self, trained_model) -> Path:
        return Path(trained_model.export(format="onnx", batch=1, dynamic=False, device=0))

    def make_artefact(self, onnx_file_path: Path) -> Path:
        # Disable ultralyitcs' auto install of packages
        ultralytics.utils.checks.AUTOINSTALL = False

        _task = self._cfg["task"]
        if _task == "classify":
            return self._make_classify_artefact(onnx_file_path)
        elif _task in ("detect", "segment"):
            return self._make_detect_segment_artefact(onnx_file_path)
        else:
            raise ValueError(f"Invalid yolo task '{_task}', expected one of (classify|detect|segment)")

    def train(self) -> Any:
        model = ultralytics.YOLO(self._cfg["model"])

        ultralytics.settings.update({"datasets_dir": str(self._training_run_dir.absolute())})

        data_cfg_path = (self._training_run_dir / "datasets" / "data.yaml").absolute()
        with data_cfg_path.open("r") as f:
            data_cfg = yaml.safe_load(f)

        self._cfg["data"] = str(data_cfg_path)
        self._cfg["single_cls"] = data_cfg["nc"] == 1
        self._cfg["classes"] = list(data_cfg["names"].keys())

        if self._cfg["task"] == "classify":
            self._cfg["data"] = str(data_cfg_path.parent)
        else:
            self._cfg["data"] = str(data_cfg_path)

        model.train(**self._cfg)
        return model

    def _export(self, checkpoint, cfg_overrides={}):

        self._cfg["model"] = checkpoint
        self._cfg.update(cfg_overrides)
        model = Path(self._cfg["model"])
        artefact_path = self.make_artefact(model)

        return artefact_path.absolute()

    def get_crop_args(self) -> Optional[CropArgs]:
        if self._cfg["task"] == "classify":
            crop_args = self.crop_args
        else:
            crop_args = None
        return crop_args

    @property
    def training_data_dir(self) -> Path:
        return self._training_run_dir / "datasets"

    def generate_trainer_specific_dataset(self, hl_dataset):

        if not (self.training_data_dir / "data.yaml").exists():
            # Optionally filter dataset, see filter_dataset's doc str
            filtered_hl_ds = self.filter_dataset(hl_dataset)

            # Download required images
            image_cache_dir = self._training_run_dir / "images"
            multithread_graphql_file_download(
                HLClient.get_client(),
                filtered_hl_ds.data_files_df.data_file_id.values,
                image_cache_dir,
            )

            ddf = filtered_hl_ds.data_files_df
            if any([Path(f).suffix.lower() == ".mp4" for f in ddf.filename.unique()]):
                print("Detected video dataset, interpolating data from keyframes")
                filtered_hl_ds = filtered_hl_ds.interpolate_from_key_frames(
                    frame_save_dir=image_cache_dir,
                    source_video_dir=image_cache_dir,
                )

            # Write dataset in yolo format
            writer = YoloWriter(
                output_dir=self.training_data_dir,
                image_cache_dir=image_cache_dir,
                category_attribute_id=self.get_category_attribute_id(),
                categories=self.get_categories(),
                task=self._cfg["task"],
                crop_args=self.get_crop_args(),
            )
            writer.write(filtered_hl_ds)

    def evaluate(
        self, checkpoint: Path, object_classes: List[str], cfg_path: Optional[Path] = None
    ) -> Dict[str, EvaluationMetricResult]:
        """Evaluate a YOLOv11 model and generate structured evaluation metrics.

        Evaluates the model using ultralytics validation and creates evaluation metric
        result objects for upload to Highlighter. Handles both classification and
        detection/segmentation tasks with appropriate metrics for each.

        Args:
            checkpoint: Path to model checkpoint (can be .pt, .onnx, or other supported formats)
            object_classes: List of object class names for the model
            cfg_path: Optional path to configuration file (uses self._cfg if None)

        Returns:
            List[EvaluationMetricResult]: Evaluation metric results ready for upload

        Side Effects:
            Saves evaluation results to 'eval_metric_results.json' in checkpoint directory
        """
        eval_metric_results: Dict[str, EvaluationMetricResult] = {}
        if cfg_path is None:
            cfg: Dict = self._cfg
        else:
            cfg: Dict = ultralytics.utils.YAML.load(cfg_path)

        assert cfg["data"] is not None
        client = HLClient.get_client()

        model = ultralytics.YOLO(str(checkpoint), task=cfg["task"])
        results = model.val(**cfg)

        if cfg["task"] in ("segment", "detect"):
            eval_metric_results = self._create_eval_results_det_or_seg(results, cfg, client)
        elif cfg["task"] == "classify":
            eval_metric_results = self._create_eval_results_cls(results, cfg, client)

        with (checkpoint.parent / "eval_metric_results.json").open("w") as f:
            json.dump(
                {k: e.model_dump() for k, e in eval_metric_results.items()},
                f,
                indent=2,
                cls=json_tools.HLJSONEncoder,
            )

        return eval_metric_results

    def _create_eval_results_cls(
        self, results, cfg: Dict, client: HLClient
    ) -> Dict[str, EvaluationMetricResult]:
        """Create evaluation metric results for classification tasks.

        Extracts classification-specific metrics including model size, top-1 accuracy,
        and top-5 accuracy from ultralytics validation results.

        Args:
            results: Ultralytics validation results object
            cfg: Configuration dictionary containing model information
            client: HLClient for metric lookup

        Returns:
            List[EvaluationMetricResult]: Classification evaluation metrics
        """
        eval_metric_results: Dict[str, EvaluationMetricResult] = {}
        _hl_metrics = self._get_hl_metrics(client)

        model_size_char = Path(cfg["model"]).stem.replace("-cls", "")[-1]
        if model_size_char in "nsmlx":
            model_size_int = "nsmlx".index(model_size_char)
            eval_metric_results["Model Size"] = _hl_metrics["Model Size"].result(
                model_size_int, self.training_run_id
            )
        else:
            model_str = cfg["model"]
            raise SystemExit(f"Unvalid model_size_char '{model_size_char}' from '{model_str}'")
        acc_top1 = results.results_dict["metrics/accuracy_top1"]
        acc_top5 = results.results_dict["metrics/accuracy_top5"]
        eval_metric_results["Accuracy Top1"] = _hl_metrics["Accuracy Top1"].result(
            acc_top1, self.training_run_id
        )
        eval_metric_results["Accuracy Top5"] = _hl_metrics["Accuracy Top5"].result(
            acc_top5, self.training_run_id
        )
        return eval_metric_results

    def _create_eval_results_det_or_seg(
        self, results, cfg: Dict, client: HLClient
    ) -> Dict[str, EvaluationMetricResult]:
        """Create evaluation metric results for detection and segmentation tasks.

        Extracts detection/segmentation-specific metrics including precision, recall,
        mAP@IoU50, model size, ideal confidence threshold, and per-class mAP values
        from ultralytics validation results.

        Args:
            results: Ultralytics validation results object
            cfg: Configuration dictionary containing model information
            client: HLClient for metric lookup

        Returns:
            List[EvaluationMetricResult]: Detection/segmentation evaluation metrics

        Note:
            Uses corrected ultralytics result attributes (e.g., 'metrics/precision(B)')
            rather than deprecated mean_results() method for better accuracy.
        """
        eval_metric_results: Dict[str, EvaluationMetricResult] = {}
        _hl_metrics = self._get_hl_metrics(client)

        eval_metric_results["Precision"] = _hl_metrics["Precision"].result(
            results.results_dict["metrics/precision(B)"], self.training_run_id
        )
        eval_metric_results["Recall"] = _hl_metrics["Recall"].result(
            results.results_dict["metrics/recall(B)"], self.training_run_id
        )
        eval_metric_results["mAP@IOU50"] = _hl_metrics["mAP@IOU50"].result(
            results.results_dict["metrics/mAP50(B)"], self.training_run_id
        )

        model_size_char = Path(cfg["model"]).stem.replace("-det", "").replace("-seg", "")[-1]
        if model_size_char in "nsmlx":
            model_size_int = "nsmlx".index(model_size_char)
            eval_metric_results["Model Size"] = _hl_metrics["Model Size"].result(
                model_size_int, self.training_run_id
            )
        else:
            model_str = cfg["model"]
            raise SystemExit(f"Unvalid model_size_char '{model_size_char}' from '{model_str}'")

        f1_conf_curve_idx = results.curves.index("F1-Confidence(B)")

        if len(results.curves_results[f1_conf_curve_idx][1].shape) == 2:
            best_f1_idx = np.argmax(results.curves_results[f1_conf_curve_idx][1].mean(axis=0))
        else:
            best_f1_idx = np.argmax(results.curves_results[f1_conf_curve_idx][1])
        best_f1_thr = results.curves_results[f1_conf_curve_idx][0][best_f1_idx]
        eval_metric_results["Ideal Confidence Threshold"] = _hl_metrics["Ideal Confidence Threshold"].result(
            best_f1_thr, self.training_run_id
        )

        cats = self.get_categories()
        CLS_PRECISION_IOU50 = 2
        for cls_idx, cat in enumerate(cats):
            class_name = cat.short_str()
            metric_name = f"mAP@IOU50({class_name})"
            eval_metric_results[metric_name] = _hl_metrics[metric_name].result(
                results.class_result(cls_idx)[CLS_PRECISION_IOU50], self.training_run_id
            )

        return eval_metric_results
