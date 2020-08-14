# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import party
from . import orden_trabajo
from . import armario
# from . import herramientas
# from . import configuracion

def register():
    Pool.register(
        party.Party,
        party.Area,
        party.Zona,
        party.Grupo,
        party.ZonaArmario,
        orden_trabajo.OrdenTrabajo,
        orden_trabajo.OrdenTrabajoCerradas,
        orden_trabajo.AsignacioOrdenTrabajo,
        orden_trabajo.WisardCargarOrdenTrabajoStart,
        armario.OciCentralTelecom,
        armario.OciArmario,
        armario.OciTerminal,
        # oreden_trabajo.OrdenDeTrabajo,
        # herramientas.OrdenDeTrabajo,
        # configuracion.ConfigurationSequence,
        # configuracion.ConfigurationRecorridoSequence,
        module='oci', type_='model')
    Pool.register(
        orden_trabajo.WisardCargarOrdenTrabajo,
        orden_trabajo.WisardCerrarOrdenTrabajo,
        #     party.PartyReplace,
    #     party.PartyErase,
        module='oci', type_='wizard')
