from PIL import Image
from cogstim.dots_core import NumberPoints
from cogstim.helpers import COLOUR_MAP


def _make_number_points(init_size: int = 512):
    img = Image.new("RGB", (init_size, init_size), color=COLOUR_MAP["black"])
    return NumberPoints(
        img=img,
        init_size=init_size,
        colour_1=COLOUR_MAP["yellow"],
        colour_2=COLOUR_MAP["blue"],
        min_point_radius=5,
        max_point_radius=8,
        attempts_limit=500,
    )


def test_design_points_no_overlap():
    """Created points should not overlap with each other."""
    generator = _make_number_points()
    points = generator.design_n_points(5, "colour_1")

    assert len(points) == 5

    # Verify no overlaps
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            assert generator._check_points_not_overlapping(points[i][0], points[j][0])


def test_equalize_areas():
    """equalize_areas() should make the yellow and blue point areas roughly equal."""
    generator = _make_number_points()
    # Manually craft two distant points to guarantee no overlaps during equalisation
    point_yellow = ((100, 100, 10), "colour_1")
    point_blue = ((400, 400, 30), "colour_2")
    point_array = [point_yellow, point_blue]

    equalized = generator.equalize_areas(point_array)

    yellow_area = generator.compute_area(equalized, "colour_1")
    blue_area = generator.compute_area(equalized, "colour_2")

    # Areas should now be (almost) equal
    rel_diff = abs(yellow_area - blue_area) / max(yellow_area, blue_area)
    assert rel_diff < generator.area_tolerance

    # Still no overlap
    assert generator._check_points_not_overlapping(equalized[0][0], equalized[1][0])
