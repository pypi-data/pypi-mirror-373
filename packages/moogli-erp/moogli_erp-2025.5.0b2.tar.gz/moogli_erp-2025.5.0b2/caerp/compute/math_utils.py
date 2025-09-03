"""
    Math utilities used for computing
"""

import typing
import logging
import math
from decimal import (
    Decimal,
    ROUND_HALF_UP,
    ROUND_DOWN,
)


PRECISION_LEVEL = 2
# Nombre de chiffres après la virgule pour le calcul de la TVA inversée
# Le bofip dit 3
REVERSE_TVA_QUOTIENT_PRECISION = 5


class NullValue:
    pass


null_value = NullValue()


logger = logging.getLogger(__name__)


def floor_to_precision(
    value: typing.Union[int, float, Decimal],
    round_floor=False,
    precision=2,
    dialect_precision=5,
) -> int:
    """
    floor a value in its int representation:
        >>> floor_to_precision(296999)
        297000

        >>> floor_to_precision(296999, round_floor=True)
        296000

        amounts are of the form : value * 10 ** dialect_precision it allows to
        store dialect_precision numbers after comma for intermediary amounts
        for totals we want precision numbers

    :param int value: The value to floor
    :param bool round_floor: Should be rounded down ?
    :param int precision: How much significant numbers we want ?
    :param int dialect_precision: The number of zeros that are concerning the
    floatting part of our value
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))

    dividor = 10 ** (dialect_precision - precision)

    value = value / Decimal(dividor)
    return floor(value, round_floor) * dividor


def floor(value, round_floor=False):
    """
    floor a float value
    :param value: float value to be rounded
    :param bool round_floor: Should the data be floor rounded ?
    :return: an integer

    >>> floor(296.9999999)
    297
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return int(dec_round(value, 0, round_floor))


def dec_round(dec, precision, round_floor=False):
    """
    Return a decimal object rounded to precision

    :param int precision: the number of decimals we want after the comma
    :param bool round_floor: Should the data be floor rounded ?
    """
    if round_floor:
        method = ROUND_DOWN
    else:
        method = ROUND_HALF_UP
    # On construit un nombre qui a le même nombre de 0 après la virgule que
    # ce que l'on veut en définitive
    precision_reference_tmpl = "%%.%df" % precision
    precision_reference = precision_reference_tmpl % 1
    precision = Decimal(precision_reference)
    return dec.quantize(precision, method)


def round(float_, precision, round_floor=False):
    """
    Return a float object rounded to precision
    :param float float_: the object to round
    :param int precision: the number of decimals we want after the comma
    :param bool round_floor: Should the data be floor rounded ?
    """
    dec = Decimal(float_)
    return float(dec_round(dec, precision, round_floor))


def amount(value, precision=2):
    """
    Convert a float value as an integer amount to store it in a database
    :param value: float value to convert
    :param precision: number of dot translation to make

    >>> amount(195.65)
    19565
    """
    converter = math.pow(10, precision)
    result = floor(value * converter)
    return result


def integer_to_amount(value, precision=2, default=null_value) -> float:
    """
    Convert an integer value to a float with precision numbers after comma
    """
    try:
        flat_point = Decimal(str(math.pow(10, -precision)))
        val = Decimal(str(value)) * flat_point
        result = float(Decimal(str(val)).quantize(flat_point, ROUND_HALF_UP))
    except Exception as exc:
        if default != null_value:
            result = default
        else:
            logger.exception(
                "Pass a default parameter to integer_to_amount "
                "if you don't want the exception to be raised"
            )
            raise exc
    return result


def percentage(value, _percent) -> int:
    """
    Return the value of the "percent" percent of the original "value"
    Truncate the result.

    >>> percentage(100.1, 50)
    50
    """
    return int(float(value) * (float(_percent) / 100.0))


def percent(part, total, default=null_value, precision=2) -> float:
    """
    Return the percentage of total represented by part
    if default is provided, the ZeroDivisionError is handled
    """
    if default is not null_value and total == 0:
        return default
    value = part * 100.0 / total
    return float(dec_round(Decimal(str(value)), precision))


def convert_to_int(
    value: typing.Any, default: typing.Optional[typing.Any] = null_value
) -> typing.Optional[int]:
    """Convert a value to an integer

    :param value: The value to convert
    :param default: if provided will be returned if the conversion fails

    :raises ValueError:
    :raises TypeError:

    Usage

        >>> convert_to_int("15")
        15
        >>> convert_to_int("not an int", 15)
        15
    """
    try:
        val = int(value)
    except (ValueError, TypeError) as err:
        if default is not null_value:
            val = default
        else:
            raise err
    return val


def str_to_int(value: typing.Any, default=null_value) -> typing.Optional[int]:
    """
    convert a string to an integer cleaning all non numeric information

    Usage

        >>> str_to_int("abc12,56")
        1256
    """
    if isinstance(value, str):
        value = "".join(i for i in value if i.isdigit())

    return convert_to_int(value, default=default)


def convert_to_float(value: typing.Any, default: typing.Any = null_value) -> float:
    """
    Try to convert the given value object to a float

        >>> convert_to_float("15.25")
        15.25
    """
    try:
        val = float(value)
    except (ValueError, TypeError) as err:
        if default is not null_value:
            val = default
        else:
            raise err
    return val


def str_to_float(value: typing.Any, default: typing.Any = null_value) -> float:
    """
    Convert a string to a float cleaning all non numeric information

    .. code-block:: python

        >>> str_to_float("15dede,25")
        15.25
    """
    if isinstance(value, str):
        value = value.replace(",", ".")
        value = "".join(i for i in value if i.isdigit() or i == "." or i == "-")
    return convert_to_float(value, default=default)


# TVA related functions
def compute_genuine_ht_from_ttc(ttc: int, tva_rate: int) -> int:
    """Compute the HT from TTC using the genuine calculation method (division_mode)"""
    tva_rate_dividor = tva_rate + 100 * 100.0
    return floor(ttc * 10000 / tva_rate_dividor)


def compute_floored_ht_from_ttc(ttc: int, tva_rate: int) -> int:
    """Compute the HT from TTC using the approximative method (multiplication_mode)"""
    # Representation in the integer representation
    # e.g 833 pour TVA 20%
    quotient_translator = 10**REVERSE_TVA_QUOTIENT_PRECISION

    tva_rate_multiplicator = (
        math.floor(10000 * quotient_translator * (1 / ((100 * 100) + tva_rate)))
        / quotient_translator
    )

    return floor(ttc * tva_rate_multiplicator)


def compute_ht_from_ttc_in_int(
    ttc: int, tva_rate: int, division_mode: bool = False
) -> int:
    """Compute HT from TTC using the appropriate calculation mode (see below function)"""
    # Ref #2317 : negative tva are used to differenciate 0% tvas
    tva_rate = max(int(tva_rate), 0)
    value = compute_genuine_ht_from_ttc(ttc, tva_rate)
    if division_mode:
        return value
    else:
        # On check si on peut retrouver le même ttc en sens inverse
        computed_ttc = compute_tva(value, tva_rate) + value
        if computed_ttc != ttc:
            value = compute_floored_ht_from_ttc(ttc, tva_rate)
    return value


def compute_ht_from_ttc(ttc, tva_rate, float_format=True, division_mode=False):
    """
    Compute ht from ttc

    This function has two modes :

    - multiplication (default) : use legal coefficients (lower math precision,
      rounding in favor of TVA) is based on legal basis rather than math
      precision.
      https://bofip.impots.gouv.fr/bofip/1380-PGP.html/identifiant=BOI-TVA-LIQ-10-20140919

    - division : use division, better math precision, at risk of less
      reproductable computation and rounding errors. Use it when you want to
      try reversing a computation that have already been done the other way
      (HT→TTC) (may not work 100% of cases though).

    Results should be used at line level, not at total level, or
    inconsistencies may arise.

    Eg (pseudo-code):
      - VALID: total_ht =  sum([compute_ht_from_ttc(line.ttc) for line in
        lines])
      - INVALID: total_ht =  compute_ht_from_ttc(sum([line.ttc for line in
        lines]))

    :param float ttc: ttc value in float format (by default)
    :param integer tva_rate: the tva rate value in integer format (tva_rate *
    100)
    :param bool float_format: Is ttc in the float format (real ttc value)
    :param division_mode: Use the division mode

    :returns: the value in integer format or in float format regarding
    float_format
    """
    # First we translate the float value to an integer representation
    if float_format:
        ttc = amount(ttc, precision=5)

    result = compute_ht_from_ttc_in_int(ttc, tva_rate, division_mode)

    # We translate the result back to a float value
    if float_format:
        result = integer_to_amount(result, precision=5)

    return result


def compute_tva_from_ttc(
    ttc: typing.Union[float, int],
    tva_rate: int,
    float_format: bool = True,
) -> typing.Union[float, int]:
    """
    This function is based on legal basis rather than math precision
    https://bofip.impots.gouv.fr/bofip/1380-PGP.html/identifiant=BOI-TVA-LIQ-10-20140919


    Results should be used at line level, not at total level, or errors will
    appear and may cumulate :

    Eg (pseudo-code):
      - VALID: total_tva =  sum([compute_tva_from_ttc(line.ttc) for line in
        lines])
      - INVALID: total_tva =  compute_tva_from_ttc(sum([line.ttc for line in
        lines]))


    :param ttc: ttc value in float format (by default)
    :param tva_rate: the tva rate value in integer format (tva_rate * 100)
    :param float_format: Is ttc in the float format (real ttc value)

    :returns: the value in integer format or in float format regarding
      float_format
    """
    if float_format:
        ttc = amount(ttc, precision=5)

    ht = compute_ht_from_ttc(ttc, tva_rate, float_format=False)
    tva = ttc - ht

    if float_format:
        tva = integer_to_amount(tva, precision=5)
    return tva


def compute_tva(ht, tva_rate):
    """
    Compute the tva for the given ht
    """
    return float(ht) * (max(int(tva_rate), 0) / 10000.0)


def translate_integer_precision(value, from_precision=5, to_precision=2):
    """
    Translate an integer value from precision 5 to precision 2

    e.g : >>> translate_integer_precision(150111)
          ... 150
    """
    return amount(integer_to_amount(value, from_precision), to_precision)
