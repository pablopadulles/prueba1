from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date
try:
    from urllib.parse import urlencode
except ImportError:
    from urlparse import urlparse
try:
    from urllib.parse import urlunparse
except ImportError:
    from urlparse import urlunparse
from collections import OrderedDict
from io import BytesIO

try:
    from PIL import Image
except ImportError:
    Image = None
from sql import Literal, Join, Table, Null
from sql.functions import Overlay, Position

from trytond.model import ModelView, ModelSingleton, ModelSQL, fields, Unique, Workflow, MultiValueMixin, ValueMixin
from trytond.wizard import Wizard, StateAction, StateView, Button
from trytond.transaction import Transaction
from trytond import backend
from trytond.pyson import Eval, Not, Bool, PYSONEncoder, Equal, And, Or, If
from trytond.pool import Pool, PoolMeta
from trytond.tools import grouped_slice, reduce_ids
from trytond.backend import name as backend_name

from uuid import uuid4
import string
import random
import pytz


ot_sequence = fields.Many2One(
        'ir.sequence', 'Nro Orden de Trabajo', required=True,
        domain=[
            ('code', '=', 'oci.asignacion.orden.trabajo'),
        ]
        )


# SEQUENCES
class Configuration(ModelSingleton, ModelSQL, ModelView, MultiValueMixin):
    'Configuration'
    __name__ = 'oci.configuration'

    ot_sequence = fields.MultiValue(ot_sequence)


class ConfigurationOTSequence(ModelSQL, ValueMixin):
    'Configuration Sequence'
    __name__ = 'oci.configuration.ot_sequence'

    ot_sequence = ot_sequence
    #_configuration_value_field = 'recorrido_sequence'

    @classmethod
    def check_xml_record(cls, records, values):
        return True
