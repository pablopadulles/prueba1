from trytond.model import (
    ModelView, ModelSQL, MatchMixin, DeactivableMixin, fields,
    sequence_ordered, Exclude)
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    StateReport, Button
from trytond.pool import Pool
import xlrd
from trytond.transaction import Transaction
from trytond.pyson import Eval, If, Bool, Not
from decimal import Decimal


class DesdeHastaFechas(ModelView):
    'ModelView Entre Fechas'
    __name__ = 'oci.desde.hasta.fechas'

    fecha1 = fields.Date('Fecha Desde', states={'required': True})
    fecha2 = fields.Date('Fecha Hasta', states={'required': True})

    @staticmethod
    def default_fecha1():
        Date = Pool().get('ir.date')
        return Date.today()


class WizardOTWFX(Wizard):
    'Wizard OT WFX'
    __name__ = 'oci.wizard.ot.wfx'

    start = StateView('oci.desde.hasta.fechas',
        'oci.oci_desde_hasta_fechas', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'print_', 'tryton-ok', default=True),
            ])

    print_ = StateReport('oci.report.ot.wfx')

    def do_print_(self, action):
        data = {
            'fecha1': self.start.fecha1,
            'fecha2': self.start.fecha2,
        }
        return action, data


class WizardCombustible(Wizard):
    'Wizard Combustible'
    __name__ = 'oci.wizard.combustible'

    start = StateView('oci.desde.hasta.fechas',
        'oci.oci_desde_hasta_fechas', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'print_', 'tryton-ok', default=True),
            ])

    print_ = StateReport('oci.report.combustible')

    def do_print_(self, action):
        data = {
            'fecha1': self.start.fecha1,
            'fecha2': self.start.fecha2,
        }
        return action, data