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

logger = logging.getLogger(__name__)


class Materiales(ModelView, ModelSQL):
    'Materiales'
    __name__ = 'oci.materiales'
    _order = 'name'

    name = fields.Many2One('oci.orden.trabajo.cerradas.wfx', 'OT', ondelete='CASCADE')
    insumo = fields.Many2One('product.product', 'Insumo', required=True)
    cantidad = fields.Integer('Cantidad', required=True)
    nro_serie = fields.Char('Nro Serie')
    fecha = fields.Function(fields.Date('Fecha'), 'get_fecha_ot', searcher='search_fecha_ot')

    def get_fecha_ot(self, name):
        if self.name:
            return self.name.fecha
        return None

    @classmethod
    def search_fecha_ot(cls, name, clause):
        res = []
        value = clause[2]
        res.append(('name.fecha', clause[1], value))
        return res

    @classmethod
    def order_fecha(cls, tables):
        pool = Pool()
        WFX = pool.get('oci.orden.trabajo.cerradas.wfx')
        material, _ = tables[None]
        if 'name' not in tables:
            wfx = WFX.__table__()
            tables['name'] = {
                None: (wfx, material.name == wfx.id),
                }
        else:
            wfx = tables['template']
        return WFX.fecha.convert_order('fecha',
            tables['name'], WFX)


