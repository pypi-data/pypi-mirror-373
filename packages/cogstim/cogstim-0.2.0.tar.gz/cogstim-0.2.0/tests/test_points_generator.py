from cogstim.ans_dots import PointsGenerator, GENERAL_CONFIG
from pathlib import Path


def test_points_generator_creates_images(tmp_path):
    cfg = GENERAL_CONFIG | {
        "NUM_IMAGES": 1,
        "IMG_DIR": str(tmp_path),
        "EASY": True,
        "ONE_COLOUR": True,
        "version_tag": "",
        "min_point_num": 1,
        "max_point_num": 2,
    }

    gen = PointsGenerator(cfg)
    gen.generate_images()

    images = list(Path(cfg["IMG_DIR"]).rglob("*.png"))
    assert len(images) > 0 