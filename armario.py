from stdnum import get_cc_module
import stdnum.exceptions
from sql import Null, Column, Literal
from sql.functions import CharLength, Substring, Position
from datetime import datetime, timedelta
from trytond.i18n import gettext
from trytond.model import (ModelView, ModelSQL, MultiValueMixin, ValueMixin,
    DeactivableMixin, fields, Unique, sequence_ordered, Workflow)
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.pyson import Eval, Bool
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond import backend
from trytond.tools.multivalue import migrate_property
from trytond.tools import lstrip_wildcard
import xlrd
#
# CATEGORIAS = [
#     (None, ''),
#     ('fr', 'FR'),
#     ('po', 'PO'),
#     ]


class OciCentralTelecom(ModelView, ModelSQL):
    'Oci Central/Zona'
    __name__ = 'oci.central.telecom'

    name = fields.Char('Nombre', readonly=False)


class OciArmario(ModelView, ModelSQL):
    'Oci Armario'
    __name__ = 'oci.armario'

    name = fields.Char('Nombre', readonly=False)
    # categorias = fields.One2Many('oci.armario.categoria', 'armario', 'Categorias')
    # comentario = fields.Char('Comentario')
    calle = fields.Char('Calle', readonly=False)
    altura = fields.Char('Altura', readonly=False)
    nombre_edificio = fields.Char('Nombre del Edificio', readonly=False)
    manzana = fields.Char('Manzana', readonly=False)
    central = fields.Many2One('oci.central.telecom', 'Central', readonly=False)


class OciTerminal(ModelView, ModelSQL):
    'Oci Terminal'
    __name__ = 'oci.terminal'

    name = fields.Char('Nombre', readonly=False)
    # categorias = fields.One2Many('oci.terminal.categoria', 'terminal', 'Categorias')
    # comentario = fields.Char('Comentario')
    calle = fields.Char('Calle', readonly=False)
    altura = fields.Char('Altura', readonly=False)
    nombre_edificio = fields.Char('Nombre del Edificio', readonly=False)
    manzana = fields.Char('Manzana', readonly=False)
    armario = fields.Many2One('oci.armario', 'Armario', readonly=False)


# class OciTerminalCategoria(ModelView, ModelSQL):
#     'Oci Terminal Categoria'
#     __name__ = 'oci.terminal.categoria'
#
#     name = fields.Char('Nombre')
#     terminal = fields.Many2One('oci.terminal', 'Terminal')
#
#
# class OciArmarioCategoria(ModelView, ModelSQL):
#     'Oci Armario Categoria'
#     __name__ = 'oci.armario.categoria'
#
#     name = fields.Char('Nombre')
#     armario = fields.Many2One('oci.terminal', 'Armario')
