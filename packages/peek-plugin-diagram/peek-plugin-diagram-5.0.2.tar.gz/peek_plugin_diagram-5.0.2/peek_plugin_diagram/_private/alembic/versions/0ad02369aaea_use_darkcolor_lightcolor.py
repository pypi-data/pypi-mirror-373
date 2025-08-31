"""use darkcolor lightcolor

Peek Plugin Database Migration Script

Revision ID: 0ad02369aaea
Revises: 0db3aedfee95
Create Date: 2022-10-20 15:56:02.384820

"""

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision = "0ad02369aaea"
down_revision = "0db3aedfee95"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

__metadata = MetaData(schema="pl_diagram")
__DeclarativeBase = declarative_base(metadata=__metadata)


class __DispColor(__DeclarativeBase):
    __tablename__ = "DispColor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    darkColor = Column(String)
    lightColor = Column(String)


def upgrade():
    op.alter_column(
        "DispColor",
        "color",
        schema="pl_diagram",
        nullable=True,
        new_column_name="darkColor",
    )

    op.add_column(
        "DispColor",
        sa.Column("lightColor", sa.String(), nullable=True),
        schema="pl_diagram",
    )
    op.execute(
        """
        UPDATE pl_diagram."DispColor"
        SET "darkColor" = null
        WHERE "darkColor" = 'None'
        """
    )

    session = Session(bind=op.get_bind())
    rows = (
        session.query(__DispColor)
        .filter(__DispColor.darkColor.isnot(None))
        .all()
    )

    for row in rows:
        row.lightColor = __invertColor(row.darkColor, "#fff")
    session.commit()


def downgrade():
    op.drop_column("DispColor", "lightColor", schema="pl_diagram")
    op.alter_column(
        "DispColor",
        "darkColor",
        nullable=True,
        new_column_name="color",
        schema="pl_diagram",
    )


import logging

logging.getLogger("colormath.color_conversions").setLevel(logging.INFO)
logging.getLogger("colormath.color_objects").setLevel(logging.INFO)
logging.getLogger("colormath.chromatic_adaptation").setLevel(logging.INFO)

from colormath import color_diff_matrix
from colormath.color_conversions import convert_color
from colormath.color_diff import _get_lab_color1_vector
from colormath.color_diff import _get_lab_color2_matrix
from colormath.color_objects import sRGBColor
from colormath.color_objects import LabColor
from tinycss2.color3 import RGBA
from tinycss2.color3 import parse_color

logger = logging.getLogger(__name__)


def __deltaECie2000(color1, color2, Kl=1, Kc=1, Kh=1):
    """
    Calculates the Delta E (CIE2000) of two colors.
    """
    color1_vector = _get_lab_color1_vector(color1)
    color2_matrix = _get_lab_color2_matrix(color2)
    delta_e = color_diff_matrix.delta_e_cie2000(
        color1_vector, color2_matrix, Kl=Kl, Kc=Kc, Kh=Kh
    )[0]
    # workaround to `numpy.asscalar()` deprecation
    return float(delta_e)


def __parseCSSColor(color: str) -> RGBA:
    assert color != "None", "There is a string 'None' in the source data"
    try:
        result = parse_color(color)

    except Exception as e:
        logger.error(f"Failure to parse colour '{color}' of type {type(color)}")
        raise

    if not result:
        raise Exception(
            f"Failure to parse colour '{color} of type" f" {type(color)}"
        )

    return result


def __rgbaToHexA(r: float, g: float, b: float, a: float) -> str:
    return "#{:02x}{:02x}{:02x}{:02x}".format(
        round(255 * r), round(255 * g), round(255 * b), round(255 * a)
    )


def __rgbaToHex(r: float, g: float, b: float) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        round(255 * r), round(255 * g), round(255 * b)
    )


def __rgbToLab(r: int, g: int, b: int) -> LabColor:
    rgb = sRGBColor(rgb_r=r, rgb_g=g, rgb_b=b)
    return convert_color(rgb, LabColor, target_illuminant="d65")


def __labToRgb(lighting, a, b) -> sRGBColor:
    lab = LabColor(lab_l=lighting, lab_a=a, lab_b=b)
    return convert_color(lab, sRGBColor, target_illuminant="d65")


def __calculateColorDifference(color1: LabColor, color2: LabColor) -> float:
    return __deltaECie2000(color1=color1, color2=color2)


def __doInvertColor(
    cssColor: str,
    backgroundCssColor: str,
    calibrate: bool = True,
    colorShift: float = 0.05,
) -> str:
    cssColor = __parseCSSColor(cssColor)
    labColor = __rgbToLab(cssColor.red, cssColor.green, cssColor.blue)

    backgroundCssColor = __parseCSSColor(backgroundCssColor)
    backgroundLabColor = __rgbToLab(
        backgroundCssColor.red,
        backgroundCssColor.green,
        backgroundCssColor.blue,
    )

    # ╔═══════════════╦════════════════════════════════════════╗
    # ║ Delta E Value ║               Perception               ║
    # ╠═══════════════╬════════════════════════════════════════╣
    # ║ <= 1.0        ║ Not perceptible by human eyes.         ║
    # ║ 1 - 2         ║ Perceptible through close observation. ║
    # ║ 2 - 10        ║ Perceptible at a glance.               ║
    # ║ 11 - 49       ║ Colors are more similar than opposite. ║
    # ║ 100           ║ Colors are exact opposite.             ║
    # ╚═══════════════╩════════════════════════════════════════╝
    colorDifference = __calculateColorDifference(labColor, backgroundLabColor)

    if colorDifference <= 0.5 or colorDifference >= 99.999:
        # invert lighting if color is too similar to background color
        invertedLabColor = LabColor(
            lab_l=100 - labColor.lab_l,  # invert the lighting
            lab_a=labColor.lab_a,
            lab_b=labColor.lab_b,
        )
    else:
        invertedLabColor = labColor

    if calibrate and colorDifference < 99.999:
        # when inverted color looks too similar to background color
        lightingShift = min(10, colorShift * invertedLabColor.lab_l)

        newLighting = invertedLabColor.lab_l

        if backgroundLabColor.lab_l > 50:
            # tone the color with bright background
            newLighting -= lightingShift
        else:
            # tint the color with dark background
            newLighting += lightingShift

        # boundary limits
        newLighting = min(newLighting, 100)
        newLighting = max(0, newLighting)

        invertedLabColor = LabColor(
            lab_l=newLighting,
            lab_a=invertedLabColor.lab_a,
            lab_b=invertedLabColor.lab_b,
        )

    invertedRgb = __labToRgb(
        invertedLabColor.lab_l, invertedLabColor.lab_a, invertedLabColor.lab_b
    )

    if cssColor.alpha == 1.0:
        return __rgbaToHex(
            invertedRgb.rgb_r, invertedRgb.rgb_g, invertedRgb.rgb_b
        )

    # return invertedRgb
    return __rgbaToHexA(
        invertedRgb.rgb_r,
        invertedRgb.rgb_g,
        invertedRgb.rgb_b,
        cssColor.alpha,  # take alpha from original input color
    )


def __invertColor(cssColor: str, backgroundCssColor: str) -> str:
    return __doInvertColor(
        cssColor=cssColor,
        backgroundCssColor=backgroundCssColor,
        calibrate=True,
        colorShift=0.05,
    )
