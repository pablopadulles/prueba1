from trytond.report import Report
from trytond.pool import Pool
from trytond.transaction import Transaction
from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import urllib



class ReportCombustible(Report):
    'Report OT WFX'
    __name__ = 'oci.report.combustible'

    @classmethod
    def _get_records(cls, data):
        res = []
        Veiculos = Pool().get('oci.veiculo')
        veiculos = Veiculos.search([])
        return veiculos

        # t = time(8, 0,0)
        # t2 = time(23, 0,0)
        # clause = [
        #     ('bool_sector_in', '=', 'True'),
        #     ('clasificacion_tarea', 'in', ['cor', 'int', 'cpr', 'nr']),
        #     ('fecha', '>=', datetime.combine(data['desde'],t)),
        #     ('fecha', '<=', datetime.combine(data['hasta'],t2)),
        #     ('state', '=', data['state']),
        #     ]
        #
        # return Incidencias.search(clause,
        #         order=[('fecha', 'ASC')])

    @classmethod
    def get_context(cls, records, data):
        report_context = super(ReportCombustible, cls).get_context(records, data)
        report_context['veiculos'] = cls._get_records(data)
        return report_context


class ReportBono(Report):
    'Report OT WFX'
    __name__ = 'oci.bono.print'


class ReportOTWFX(Report):
    'Report OT WFX'
    __name__ = 'oci.report.ot.wfx'

    @classmethod
    def _get_records(cls, data):
        res = []
        return res

        # t = time(8, 0,0)
        # t2 = time(23, 0,0)
        # clause = [
        #     ('bool_sector_in', '=', 'True'),
        #     ('clasificacion_tarea', 'in', ['cor', 'int', 'cpr', 'nr']),
        #     ('fecha', '>=', datetime.combine(data['desde'],t)),
        #     ('fecha', '<=', datetime.combine(data['hasta'],t2)),
        #     ('state', '=', data['state']),
        #     ]
        #
        # return Incidencias.search(clause,
        #         order=[('fecha', 'ASC')])

    @classmethod
    def get_context(cls, records, data):
        report_context = super(ReportOTWFX, cls).get_context(records, data)
        report_context['datos'] = cls._get_records(data)
        return report_context
