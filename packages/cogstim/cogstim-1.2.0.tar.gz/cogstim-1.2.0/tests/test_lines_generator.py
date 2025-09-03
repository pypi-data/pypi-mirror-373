import tempfile
from pathlib import Path

from cogstim.lines import StripePatternGenerator


def test_stripe_pattern_generator_single_set():
    """StripePatternGenerator should create the expected number of images for a minimal config."""

    with tempfile.TemporaryDirectory() as tmpdir:
        cfg = {
            "output_dir": tmpdir,
            "img_sets": 1,  # one repetition
            "angles": [0],  # single angle
            "min_stripe_num": 2,
            "max_stripe_num": 2,  # fixed stripe count
            "img_size": 128,  # smaller image for quick tests
            "tag": "",
            "min_thickness": 5,
            "max_thickness": 6,  # ensure low < high for randint
            "min_spacing": 2,
            "max_attempts": 100,
            "background_colour": "#000000",
        }

        generator = StripePatternGenerator(cfg)
        generator.create_images()

        # Expected file path pattern: output_dir/<angle>/img_<stripes>_<set_idx>.png
        angle_dir = Path(tmpdir) / "0"
        images = list(angle_dir.glob("*.png"))

        # total_images = img_sets * len(angles) * (#stripe_counts)
        assert len(images) == 1, "Exactly one image should be generated for this configuration." 