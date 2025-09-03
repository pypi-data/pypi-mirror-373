from cogstim.shapes import ShapesGenerator
from cogstim.helpers import COLOUR_MAP
import tempfile


def test_draw_shape_circle():
    with tempfile.TemporaryDirectory() as tmpdir:
        sg = ShapesGenerator(
            shapes=["circle"],
            colours=["yellow"],
            task_type="two_shapes",
            img_dir=tmpdir,
            train_num=1,
            test_num=0,
            jitter=False,
            min_surface=10000,
            max_surface=10001,
            background_colour="black",
        )
        img, dist, angle = sg.draw_shape("circle", 10000, COLOUR_MAP["yellow"], jitter=False)

        # Basic sanity checks
        assert img.size == (512, 512)
        assert 0 <= dist <= 124  # within max jitter range used in code
        assert 0 <= angle <= 360
