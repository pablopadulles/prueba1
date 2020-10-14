from stdnum import get_cc_module
import stdnum.exceptions
import logging
from sql import Null, Column, Literal
from sql.functions import CharLength, Substring, Position
from datetime import datetime, timedelta
from trytond.i18n import gettext
from trytond.model import (ModelView, ModelSQL, MultiValueMixin, ValueMixin,
    DeactivableMixin, fields, Unique, sequence_ordered, Workflow)
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval, Bool, Not
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond import backend
from trytond.tools.multivalue import migrate_property
from trytond.tools import lstrip_wildcard
import xlrd
from .exceptions import (
    InvalidIdentifierCode, VIESUnavailable, SimilarityWarning, EraseError)

logger = logging.getLogger(__name__)

class Vehiculo(ModelView, ModelSQL):
    'Vehiculo'
    __name__ = 'oci.vehiculo'
    _order = 'name'

    active = fields.Boolean('Active')
    name = fields.Char('Pantente', required=True)
    km = fields.Integer('Kilometros')
    monto = fields.Function(fields.Numeric('Monto Total'), 'get_monto')
    monto_mensual = fields.Function(fields.Numeric('Monto Mensual'), 'get_monto_mensual')
    modelo = fields.Char('Modelo', required=True)
    marca = fields.Char('Marca', required=True)
    bonos = fields.One2Many('oci.bono', 'name', 'Bonos', readonly=True)

    def get_monto(self, name):
        monto = 0
        for bono in self.bonos:
            monto += bono.monto
        return monto

    def get_monto_mensual(self, name):
        monto = 0
        Date = Pool().get('ir.date')
        today = Date.today()
        today2 = today.replace(day=1)
        bonos = Bono.search([('fecha', '>', today2)])
        for bono in bonos:
            monto = bono.monto
        return monto

    def get_combustible(self, fecha1, fecha2):
        bonos = Bono.search([('fecha', '>=', fecha1),
                             ('fecha', '<=', fecha2),
                             ('name', '=', self.id)])
        return bonos

    def get_monto_entre_fechas(self, fecha1, fecha2):
        bonos = Bono.search([('fecha', '>=', fecha1),
                             ('fecha', '<=', fecha2),
                             ('name', '=', self.id)])
        monto = 0
        for bono in bonos:
            monto += bono.monto
        return monto

    @staticmethod
    def default_active():
        return True


class Bono(Workflow, ModelView, ModelSQL):
    'Bonos'
    __name__ = 'oci.bono'

    name = fields.Many2One('oci.vehiculo', 'vehiculo', required=True,
            states={'readonly': Not(Eval('state').in_(['rendido', 'borrador']))})
    user1 = fields.Many2One('res.user', 'Genera Bono', readonly=True)
    user2 = fields.Many2One('res.user', 'Recibe Rendido', readonly=True)
    party = fields.Many2One('party.party', 'Chofer', domain=[('perfil', '=', 'chofer')],
            states={'readonly': Eval('state').in_(['rendido', 'pendiente'])}, required=True)
    km1 = fields.Numeric('Km actuales')
    km2 = fields.Numeric('Km actualizados', help='Actualiza el kilometraje del vehiculo',
            states={'readonly': Not(Eval('state').in_(['rendido', 'borrador']))})
    monto = fields.Numeric('Monto', required=True,
            states={'readonly': Eval('state').in_(['rendido', 'pendiente'])})
    fecha = fields.Date('Fecha', required=True, states={'readonly': Eval('state').in_(['rendido', 'pendiente'])})
    code = fields.Char('Codigo', readonly=True)
    type = fields.Selection([
            (None, ''),
            ('nafta', 'Nafta'),
            ('gasoil', 'Gasoil')],
            'Combustible', required=True,
            states={'readonly': Eval('state').in_(['rendido', 'pendiente'])})
    state = fields.Selection([
            ('borrador', 'Borrador'),
            ('pendiente', 'Pendiente'),
            ('rendido', 'Rendido')],
            'Estado', readonly=True)

    @classmethod
    def __setup__(cls):
        super(Bono, cls).__setup__()
        cls._transitions |= set((
            ('borrador', 'pendiente'),
            ('pendiente', 'rendido'),
            ))
        cls._order = [
            ('fecha', 'ASC'),
            ]
        cls._buttons.update({
            'rendir': {
                'invisible': ~Eval('state').in_(['pendiente'])
            },
            'pendiente': {
                'invisible': Eval('state').in_(['rendido'])
            },
        })

    @classmethod
    @ModelView.button_action('oci.imprimir_bono')
    @Workflow.transition('pendiente')
    def pendiente(cls, bonos):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('rendido')
    def rendir(cls, bonos):
        user = Transaction().user
        if not user:
            user = Transaction().context.get('user')
        for bono in bonos:
            bono.user2 = user
            if bono.km2:
                bono.name.km = bono.km2
                bono.name.save()
            bono.save()
        pass

    @classmethod
    def create(cls, vlist):
        vlist = [x.copy() for x in vlist]
        for values in vlist:
            if not values.get('code'):
                values['code'] = cls._new_code()
        return super(Bono, cls).create(vlist)

    @classmethod
    def _new_code(cls, **pattern):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Configuration = pool.get('oci.configuration')
        config = Configuration(1)
        sequence = config.get_multivalue('bono_sequence', **pattern)
        if sequence:
            return Sequence.get_id(sequence.id)

    @staticmethod
    def default_state():
        return 'borrador'

    @staticmethod
    def default_active():
        return True

    @staticmethod
    def default_fecha():
        Date = Pool().get('ir.date')
        return Date.today()

    @staticmethod
    def default_user1():
        user = Transaction().user
        if not user:
            user = Transaction().context.get('user')
        return user

    @fields.depends('name')
    def on_change_with_km1(self, name=None):
        if self.name:
            return self.name.km
        else:
            return 0

