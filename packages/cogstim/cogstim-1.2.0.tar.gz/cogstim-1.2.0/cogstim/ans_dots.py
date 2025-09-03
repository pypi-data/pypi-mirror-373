import os
from PIL import Image
from cogstim.dots_core import NumberPoints, PointLayoutError
from tqdm import tqdm
import logging

from cogstim.helpers import COLOUR_MAP, SIZES

logging.basicConfig(level=logging.INFO)


GENERAL_CONFIG = {
    "colour_1": "yellow",
    "colour_2": "blue",
    "attempts_limit": 2000,
    "background_colour": "black",
    "min_point_radius": SIZES["min_point_radius"],
    "max_point_radius": SIZES["max_point_radius"],
}


EASY_RATIOS = [1 / 5, 1 / 4, 1 / 3, 2 / 5, 1 / 2, 3 / 5, 2 / 3, 3 / 4]
HARD_RATIOS = [
    4 / 5,
    5 / 6,
    7 / 8,
    8 / 9,
    9 / 10,
    10 / 11,
    11 / 12,
]


class TerminalPointLayoutError(ValueError):
    pass


class PointsGenerator:
    def __init__(self, config):
        self.config = config
        # Expect NUM_IMAGES key specifying how many tagged repetitions per phase
        self.num_images = config["NUM_IMAGES"]
        self.setup_directories()
        self.ratios = EASY_RATIOS if self.config["EASY"] else EASY_RATIOS + HARD_RATIOS

    def setup_directories(self):
        os.makedirs(self.config["IMG_DIR"], exist_ok=True)
        os.makedirs(
            os.path.join(self.config["IMG_DIR"], self.config["colour_1"]), exist_ok=True
        )
        if not self.config["ONE_COLOUR"]:
            os.makedirs(
                os.path.join(self.config["IMG_DIR"], self.config["colour_2"]), exist_ok=True
            )

    def create_image(self, n1, n2, equalized):
        img = Image.new(
            "RGB",
            (SIZES["init_size"], SIZES["init_size"]),
            color=self.config["background_colour"],
        )
        # Map configured colours to drawer colours. In one-colour mode, only pass colour_1.
        colour_2 = None if self.config["ONE_COLOUR"] else COLOUR_MAP[self.config["colour_2"]]

        number_points = NumberPoints(
            img,
            SIZES["init_size"],
            colour_1=COLOUR_MAP[self.config["colour_1"]],
            colour_2=colour_2,
            min_point_radius=self.config["min_point_radius"],
            max_point_radius=self.config["max_point_radius"],
            attempts_limit=self.config["attempts_limit"],
        )
        point_array = number_points.design_n_points(n1, "colour_1")
        point_array = number_points.design_n_points(
            n2, "colour_2", point_array=point_array
        )
        if equalized and not self.config["ONE_COLOUR"]:
            point_array = number_points.equalize_areas(point_array)
        return number_points.draw_points(point_array)

    def create_and_save(self, n1, n2, equalized, tag=""):
        eq = "_equalized" if equalized else ""
        v_tag = f"_{self.config['version_tag']}" if self.config.get("version_tag") else ""
        name = f"img_{n1}_{n2}_{tag}{eq}{v_tag}.png"

        attempts = 0
        while attempts < self.config["attempts_limit"]:
            try:
                self.create_and_save_once(name, n1, n2, equalized)
                break
            except PointLayoutError as e:
                logging.debug(f"Failed to create image {name} because '{e}' Retrying.")
                attempts += 1

                if attempts == self.config["attempts_limit"]:
                    raise TerminalPointLayoutError(
                        f"""Failed to create image {name} after {attempts} attempts. 
                        Your points are probably too big, or there are too many. 
                        Stopping."""
                    )

    def create_and_save_once(self, name, n1, n2, equalized):
        img = self.create_image(n1, n2, equalized)
        img.save(
            os.path.join(
                self.config["IMG_DIR"],
                self.config["colour_1"] if n1 > n2 else self.config["colour_2"],
                name,
            )
        )

    def get_positions(self):
        min_p = self.config["min_point_num"]
        max_p = self.config["max_point_num"]

        if self.config["ONE_COLOUR"]:
            # For one-colour mode, we only need a single count per image
            return [(a, 0) for a in range(min_p, max_p + 1)]

        positions = []
        # Note that we don't need the last value of 'a', since 'b' will always be greater.
        for a in range(min_p, max_p):
            # Given 'a', we need to find 'b' in the tuple (a, b) such that b/a is in the ratios list.
            for ratio in self.ratios:
                b = a / ratio

                # We keep this tuple if b is an integer and within the allowed range.
                if b == round(b) and b <= max_p:
                    positions.append((a, int(b)))

        return positions

    def generate_images(self):
        positions = self.get_positions()
        multiplier = 1 if self.config["ONE_COLOUR"] else 4
        total_images = self.num_images * len(positions) * multiplier
        logging.info(
            f"Generating {total_images} images: {self.num_images} sets x {len(positions)} combinations x {multiplier} variants in '{self.config['IMG_DIR']}'."
        )
        for i in tqdm(range(self.num_images)):
            for pair in positions:
                if self.config["ONE_COLOUR"]:
                    # One-colour mode: use first value as the count, ignore second
                    self.create_and_save(pair[0], 0, equalized=False, tag=i)
                else:
                    # Two-colour mode: both orders, equalized and non-equalized
                    self.create_and_save(pair[0], pair[1], equalized=False, tag=i)
                    self.create_and_save(pair[1], pair[0], equalized=False, tag=i)
                    self.create_and_save(pair[0], pair[1], equalized=True, tag=i)
                    self.create_and_save(pair[1], pair[0], equalized=True, tag=i)
