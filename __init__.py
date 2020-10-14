# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import party
from . import orden_trabajo
from . import armario
# from . import herramientas
from . import configuracion
from . import materiales
from . import wizard
from . import report
from . import veiculos


def register():
    Pool.register(
        party.Party,
        party.Area,
        party.Zona,
        party.Grupo,
        party.ZonaArmario,
        party.Categoria,
        party.Tarea,
        orden_trabajo.OrdenTrabajo,
        orden_trabajo.OrdenTrabajoCerradas,
        orden_trabajo.AsignacioOrdenTrabajo,
        orden_trabajo.WisardCargarOrdenTrabajoStart,
        orden_trabajo.OrdenTrabajoCerradasWFX,
        orden_trabajo.Tarea,
        orden_trabajo.LocalizacionTarea,
        armario.OciCentralTelecom,
        armario.OciArmario,
        armario.OciTerminal,
        materiales.Materiales,
        configuracion.Configuration,
        configuracion.ConfigurationOTSequence,
        configuracion.ConfigurationBonoSequence,
        wizard.DesdeHastaFechas,
        veiculos.Veiculo,
        veiculos.Bono,
        # oreden_trabajo.OrdenDeTrabajo,
        # herramientas.OrdenDeTrabajo,
        # configuracion.ConfigurationSequence,
        # configuracion.ConfigurationRecorridoSequence,
        module='oci', type_='model')
    Pool.register(
        orden_trabajo.WisardCargarOrdenTrabajo,
        orden_trabajo.WisardCerrarOrdenTrabajo,
        wizard.WizardOTWFX,
        wizard.WizardCombustible,
        #     party.PartyReplace,
    #     party.PartyErase,
        module='oci', type_='wizard')
    Pool.register(
        report.ReportOTWFX,
        report.ReportBono,
        report.ReportCombustible,
        module='oci', type_='report')
