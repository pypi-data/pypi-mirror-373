import shutil
from pathlib import Path
from typing import Dict, Optional, Union
from uuid import UUID
from warnings import warn

from shapely import geometry as gm
from tqdm import tqdm

from ....client.io import _pil_open_image_path
from ....core import PIXEL_LOCATION_ATTRIBUTE_UUID
from ...cropping import CropArgs, crop_rect_from_poly
from ...interfaces import IWriter

PathLike = Union[str, Path]


def _create_full_data_file_folder_dataset(
    dataset, use_entity_id_as_class, attribute_of_interest, root_dir, data_file_dir, use_symlinks
):
    im_df = dataset.data_files_df.set_index("data_file_id")

    if use_entity_id_as_class:
        grp = dataset.annotations_df.groupby("entity_id")
    else:
        adf = dataset.annotations_df
        grp = adf[adf.attribute_id == attribute_of_interest].groupby("value")

    def make_class_folder(grp):
        # Create folder for each unique class
        folder_name = grp.name
        folder_path = root_dir / folder_name

        # Populate folder with data_files
        data_file_ids = grp["data_file_id"].unique()
        for data_file_id in data_file_ids:
            data_file_filename = im_df.loc[data_file_id, "filename"]
            data_file_path = data_file_dir / data_file_filename

            ext = Path(data_file_filename).suffix.lower()
            dest_path = folder_path / f"{data_file_id}{ext}"
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if use_symlinks:
                dest_path.symlink_to(data_file_path)
            else:
                source = str(data_file_path)
                dest = str(dest_path)
                shutil.copy(source, dest)

    grp.apply(make_class_folder)


def _create_crop_folder_dataset(
    dataset,
    attribute_of_interest,
    data_file_dir,
    root_dir,
    crop_args: Optional[CropArgs],
):
    adf = dataset.annotations_df
    idf = dataset.data_files_df
    id_to_fileame = idf.set_index("data_file_id").to_dict()["filename"]
    adf["filename"] = adf.data_file_id.map(id_to_fileame)

    adf = adf[adf.attribute_id.isin([attribute_of_interest, str(PIXEL_LOCATION_ATTRIBUTE_UUID)])]

    def make_crop(grp, orig_file_name, pil_data_file, root_dir):
        pix_loc_record: Dict = {}
        attr_record: Dict = {}
        for attr in grp.to_dict("records"):
            if attr["attribute_id"] == str(PIXEL_LOCATION_ATTRIBUTE_UUID):
                pix_loc_record = attr
            else:
                attr_record = attr

        if "value" not in pix_loc_record:
            warn(f"value not found for pixel location record '{grp.to_dict()}', skipping.")
            return None

        if "value" not in attr_record:
            warn(f"value not found for attr record '{grp.to_dict()}', skipping.")
            return None

        poly: Union[gm.Polygon, gm.MultiPolygon] = pix_loc_record["value"]
        if not isinstance(poly, (gm.Polygon, gm.MultiPolygon)):
            warn(f"pixel location is not a Polygon {poly}, skipping")
            return None

        try:
            bbox = [(int(x), int(y)) for x, y in poly.envelope.exterior.coords]
        except AttributeError:
            warn(f"invalid Polygon {poly}, skipping")
            return None

        l = min([x for x, _ in bbox])
        t = min([y for _, y in bbox])
        r = max([x for x, _ in bbox])
        b = max([y for _, y in bbox])

        save_path = (
            root_dir
            / attr_record["value"]
            / f"{orig_file_name.stem}-{l}-{t}-{r}-{b}{orig_file_name.suffix.lower()}"
        )

        if not save_path.exists():
            crop = crop_rect_from_poly(pil_data_file, poly, crop_args)

            save_path.parent.mkdir(exist_ok=True, parents=True)
            try:
                crop.save(save_path)
            except ValueError:
                warn(f"empty crop, skipping. {crop.size}")

    def make_crops(grp, data_file_dir=data_file_dir, root_dir=root_dir):
        data_file_path = str(data_file_dir / grp.name)

        try:
            pil_image = _pil_open_image_path(data_file_path)
        except OSError as e:
            warn(f"{e}: '{data_file_path}', skipping.")
            return None

        grp.groupby("entity_id").apply(lambda row: make_crop(row, Path(grp.name), pil_image, root_dir))

    tqdm.pandas(desc="Generating crops")
    adf.groupby("filename").progress_apply(make_crops)


class TorchImageFolderWriter(IWriter):
    format_name = "torch-image-folder"

    def __init__(
        self,
        data_file_dir: PathLike,
        root_dir: PathLike,
        attribute_of_interest: Optional[Union[str, UUID]] = None,
        use_entity_id_as_class: bool = False,
        use_symlinks: bool = True,
        crop_args: Optional[Union[CropArgs, Dict]] = None,
    ):
        """
        If no attribute_of_interest is passed will default to treating each
        entity as a unique class.

        Args:
            dataset: A Dataset object

            data_file_dir: location of source data_files

            root_dir: output root directory where class data_file directories will
            be created. If this dir does not exist it will be created
            attribute_of_interest: If set will create directories for each item
            in:
                `dataset.annotations_df[dataset.annotations_df.attribute_id == attribute_of_interest].value.unique()`

            use_entity_id_as_class: If set will create directories for each item
            in:
                `dataset.annotations_df.entity_id.unique()`

            use_symlinks: Only applicable if `crop_pixel_location=True`, will
            create symlinks to source data_files rather than copying

            crop_args:
                crop_rotated_rect: (Bool Default=False)
                    False: Crop the minimum rectangle containing the
                    pixel_location. The rectangle has vertical and horozontal
                    sides.

                    True: Crop the minimum rotated rectangle
                    contaning the polygon. This rectange has parallel sides
                    but is rotated. A cv2.warpPerspective transform is applied
                    to  the rotated rectangel to produce the crop.

                scale: (Optional) If set scale is applied to the rectangle before
                padding. Scaling is about the origin. This is useful in the case
                where the original source data_file has been resized on disk so the
                accompanying polygon must be scaled to match. It is NOT for
                enlarging the rectange to include more of the background, to
                do that use pad.

                pad: (Optional) If set will pad the rectangle before cropping

                warped_wh: (Optional) (Applies only for crop_rotated_rect=True)
                If set will transform the resize the resulting crop to the
                desired width and height. If not set, the resulting crop with have
                the same width and height as the original rotated rectangle
        """
        self.data_file_dir = Path(data_file_dir)
        self.root_dir = Path(root_dir)

        if ((attribute_of_interest is not None) and use_entity_id_as_class) or (
            (attribute_of_interest is None) and not use_entity_id_as_class
        ):
            raise ValueError("Must use ONE of 'attribute_of_interest' OR 'use_entity_id_as_class")

        if isinstance(attribute_of_interest, UUID):
            self.attribute_of_interest = str(attribute_of_interest)
        else:
            self.attribute_of_interest = attribute_of_interest

        self.attribute_of_interest = attribute_of_interest
        self.use_entity_id_as_class = use_entity_id_as_class
        self.use_symlinks = use_symlinks

        if isinstance(crop_args, dict):
            self.crop_args = CropArgs(**crop_args)
        elif isinstance(crop_args, CropArgs):
            self.crop_args = crop_args
        elif crop_args is None:
            self.crop_args = None
        else:
            raise ValueError(
                f"invalid parameter 'crop_args' expected a CropArgs object or None, got {crop_args}"
            )

    def write(self, dataset):
        self.root_dir.mkdir(exist_ok=True, parents=True)

        if self.crop_args is None:
            _create_full_data_file_folder_dataset(
                dataset,
                self.use_entity_id_as_class,
                self.attribute_of_interest,
                self.root_dir,
                self.data_file_dir,
                self.use_symlinks,
            )
        else:
            _create_crop_folder_dataset(
                dataset, self.attribute_of_interest, self.data_file_dir, self.root_dir, self.crop_args
            )
