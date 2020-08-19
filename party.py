from stdnum import get_cc_module
import stdnum.exceptions
from sql import Null, Column, Literal
from sql.functions import CharLength, Substring, Position

from trytond.i18n import gettext
from trytond.model import (ModelView, ModelSQL, MultiValueMixin, ValueMixin,
    DeactivableMixin, fields, Unique, sequence_ordered)
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval, Bool, Not
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond import backend
from trytond.tools.multivalue import migrate_property
from trytond.tools import lstrip_wildcard
from .exceptions import (
    InvalidIdentifierCode, VIESUnavailable, SimilarityWarning, EraseError)


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    lastname = fields.Char('Apellido', states={'required': Bool(Eval('perfil', False))})
    dni = fields.Char('DNI')
    legajo = fields.Char('Legajo', states={'required': Bool(Eval('perfil', False))})
    fecha_ingreso = fields.Date('Fecha Ingreso')
    fecha_baja = fields.Date('Fecha Baja', states={'readonly': True})
    perfil = fields.Selection([
        (None, ''),
        ('tec', 'Tecnico'),
        ('sup', 'Supervisor'),
        ('adm', 'Adminitrativo'),
        ], 'Perfil')
    area = fields.Many2One('oci.area', 'Area')
    zona = fields.Many2One('oci.zona', 'Zona')
    grupo = fields.Many2One('oci.grupo', 'Grupo')
    exSupervisor = fields.Boolean('ExSupervisor')
    ivr = fields.Char('IVR')

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
        cls.name.states.update({
                'required': True,
                })


class Area(ModelView, ModelSQL):
    'Area de trabajo'
    __name__ = 'oci.area'

    name = fields.Char('Nombre del Area', required=True)


class Zona(ModelView, ModelSQL):
    'Zona de trabajo'
    __name__ = 'oci.zona'

    name = fields.Char('Nombre', required=True)
    armarios = fields.Many2Many('oci.zona-oci.armario', 'zona', 'armario', 'Armarios')


class Grupo(ModelView, ModelSQL):
    'Grupo de trabajo'
    __name__ = 'oci.grupo'

    name = fields.Char('Nombre', required=True)

class ZonaArmario(ModelSQL):
    'Zona - Armario'
    __name__ = 'oci.zona-oci.armario'
    _table = 'oci_zona_armario_rel'

    zona = fields.Many2One('oci.zona', 'Zona')
    armario = fields.Many2One('oci.armario', 'Armario')
