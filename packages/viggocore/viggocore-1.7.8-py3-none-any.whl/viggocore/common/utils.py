import json
import math

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import os
from typing import Optional, Union, Any
import uuid

DATE_FMT = '%Y-%m-%d'
DATETIME_FMT = '%Y-%m-%dT%H:%M:%S.%fZ'


# ----------
# Date functions
# ----------
def convert_date_from_str(value: Optional[str]) -> Optional[datetime]:
    date_time = None
    if value is not None:
        try:
            if len(value.strip()) == 10:
                date_time = datetime.strptime(value, DATE_FMT)
            elif len(value.strip()) == 24:
                date_time = datetime.strptime(value, DATETIME_FMT)
        except Exception:
            pass
    return date_time


def convert_date_to_str(date_value: Union[date, datetime]) -> str:
    if type(date_value) is date:
        return date_value.strftime(DATE_FMT)
    elif type(date_value) is datetime:
        return date_value.strftime(DATETIME_FMT)
    else:
        raise Exception('{} is not date or datetime'.format(date_value))
# ----------


# ----------
# Decimal functions
# ----------
def to_decimal(num):
    try:
        return Decimal(str(num))
    except Exception:
        return Decimal('0.0')


def to_decimal_n(num, n):
    try:
        num_str = '{:.' + str(n) + 'f}'
        num_str = num_str.format(num)
        return Decimal(num_str)
    except Exception:
        return Decimal('0.0')


def is_decimal(num):
    response = False
    if (to_decimal(num) - int(num)) > to_decimal('0.0'):
        response = True
    return response


def convert_decimal(value: Decimal) -> Union[float, int]:
    if isinstance(value, Decimal):
        if not value.is_finite():
            return str(value)
        if str(value).find('.') > -1:
            return float(value.real)
        else:
            return int(value)
    else:
        raise Exception('{} is not Decimal'.format(value))


def float_to_string(n: float):
    if 'e-' in str(n):
        values = str(n).split('e-')
        a = values[0].replace('.', '')
        b = int(values[1])
        return '0.' + ('0' * (b - 1)) + a
    else:
        return str(n)


def round_abnt(valor, n: int = 2):
    valor = float(valor)
    negativo = valor < 0

    delta = 0.00001
    pow_aux = pow(10, n)
    pow_value = abs(valor) / 10
    int_value = math.trunc(pow_value)
    frac_value = float('0.' + float_to_string(pow_value).split('.')[1])
    pow_value = (
        (frac_value * 10 * pow_aux / pow(10.0, -9)) + 0.5) * pow(10.0, -9)
    int_calc = math.trunc(pow_value)
    frac_calc = float('0.' + float_to_string(pow_value).split('.')[1])
    frac_calc = math.trunc(frac_calc * 100)

    if (frac_calc > 50):
        int_calc += 1
    elif (frac_calc == 50):
        valor_temp = int_calc / 10
        last_number = round(
            (float('0.' + float_to_string(valor_temp).split('.')[1])) * 10)
        if (last_number % 2) == 1:
            int_calc += 1
        else:
            valor_temp = pow_value * 10
            rest_part = float('0.' + float_to_string(valor_temp).split('.')[1])
            if rest_part > delta:
                int_calc += 1
    resultado = ((int_value * 10) + Decimal(str(int_calc / pow_aux)))
    if negativo:
        resultado *= -1
    return float(resultado)
# ----------


class ViggocoreEncoder(json.JSONEncoder):

    def default(self, value: Any) -> Any:
        try:
            if isinstance(value, Decimal):
                return convert_decimal(value)
            if isinstance(value, date):
                return convert_date_to_str(value)
            if isinstance(value, Enum):
                return value.name

            # default  str
            return str(value)
        except Exception:
            return super().default(value)


def to_json(value: Any) -> str:
    return json.dumps(value, cls=ViggocoreEncoder)


def random_uuid() -> str:
    return uuid.uuid4().hex


def remove_file(filename):
    try:
        os.remove(filename)
    except Exception:
        return False
    return True


def is_empty_or_blank(texto):
    if texto is None:
        return True
    return not str(texto).strip()


def _get_base_folder():
    DEFAULT_FOLDER = '/files'
    env_folder = os.environ.get('VIGGOCORE_FILE_DIR', DEFAULT_FOLDER)
    if not os.path.isabs(env_folder):
        env_folder = os.path.join(os.getcwd(), env_folder)
    return env_folder


def get_upload_folder():
    base_folder = _get_base_folder()
    folder = os.path.join(base_folder, 'FileTemp')
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder
