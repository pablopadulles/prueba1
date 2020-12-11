from stdnum import get_cc_module
import stdnum.exceptions
from sql import Null, Column, Literal
from sql.functions import CharLength, Substring, Position
from sql.operators import Equal

from trytond.i18n import gettext
from trytond.model import (ModelView, ModelSQL, MultiValueMixin, ValueMixin,
    DeactivableMixin, fields, Unique, sequence_ordered, Exclude)

from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval, Bool, Not
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond import backend
from trytond.tools.multivalue import migrate_property
from trytond.tools import lstrip_wildcard
from .exceptions import (
    Invalidlocation, EraseError)


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    lastname = fields.Char('Apellido', states={'required': Bool(Eval('perfil', False))})
    cod_tec = fields.Char('Cod/Tec', states={'required': Bool(Eval('perfil').in_(['tec']))})
    password_hash = fields.Char('Password Hash')
    password = fields.Function(fields.Char(
            "Password"),
        getter='get_password', setter='set_password')
    dni = fields.Char('DNI', states={'required': Bool(Eval('perfil', False))})
    cel_teco = fields.Char('Celular Teco')
    cel = fields.Char('Celular')
    legajo = fields.Char('Legajo', states={'required': Bool(Eval('perfil', False))})
    fecha_ingreso = fields.Date('Fecha Ingreso')
    fecha_baja = fields.Date('Fecha Baja', states={'readonly': True})
    perfil = fields.Selection([
        (None, ''),
        ('tec', 'Tecnico'),
        ('sup', 'Supervisor'),
        ('adm', 'Adminitrativo'),
        ('chofer', 'Chofer'),
        ], 'Perfil')
    categoria = fields.Many2One('oci.categoria', 'Categoria')
    tarea = fields.Many2One('oci.tarea', 'Tarea')
    grupo = fields.Many2One('oci.grupo', 'Grupo')
    exSupervisor = fields.Boolean('ExSupervisor')
    ivr = fields.Char('IVR')

    @classmethod
    def __setup__(cls):
        super(Party, cls).__setup__()
        cls.name.states.update({
                'required': True,
                })
        t = cls.__table__()
        # cls._sql_constraints = [
        #     ('cod_tec_uniq', Unique(t, t.dni),
        #         'El Cod/Tec debe ser unico e irrepetible.'),]

    @classmethod
    def search_rec_name(cls, name, clause):
        partys = cls.search([('ivr',) + tuple(clause[1:])], order=[])
        partys += cls.search([('lastname',) + tuple(clause[1:])], order=[])
        partys += cls.search([('name',) + tuple(clause[1:])], order=[])
        partys += cls.search([('legajo',) + tuple(clause[1:])], order=[])
        return [('id', 'in', [party.id for party in partys])]

    def get_password(self, name):
        return 'x' * 10

    def get_rec_name(self, name):
        res = ''
        if self.legajo:
            res += '[' + self.legajo + '] '
        if self.name:
            res += self.name
        if self.lastname:
            res += ', ' + self.lastname

        return res

    @staticmethod
    def order_legajo(tables):
        table, _ = tables[None]
        return [CharLength(table.legajo), table.legajo]

    @classmethod
    def set_password(cls, users, name, value):
        if value == 'x' * 10:
            return

        to_write = []
        for user in users:
            to_write.extend([[user], {
                        'password_hash': value,
                        }])
        cls.write(*to_write)

    @classmethod
    def validate(cls, partys):
        super(Party, cls).validate(partys)
        cls.check_identificadores(partys)

    @classmethod
    def check_identificadores(cls, partys):
        for party in partys:
            if party.location:
                if len((cls.search([('location', '=', party.location)]))):
                    raise Invalidlocation(
                        gettext('oci.msg_invalid_location'))

    @classmethod
    def check_location(cls, partys):
        for party in partys:
            if party.perfil in ['tec', 'chofer']:
                if len((cls.search([('dni', '=', party.dni)]))) > 1:
                    raise EraseError(
                        gettext('oci.msg_dni'))
                if len((cls.search([('cod_tec', '=', party.cod_tec)]))) > 1:
                    raise EraseError(
                        gettext('oci.msg_cod_tec'))


class Tarea(ModelView, ModelSQL):
    'Tarea'
    __name__ = 'oci.tarea'

    name = fields.Char('Nombre de la tarea', required=True)


class Categoria(ModelView, ModelSQL):
    'Categoria'
    __name__ = 'oci.categoria'

    name = fields.Char('Nombre de la categoria', required=True)


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
