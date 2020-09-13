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

CAMPOS = [
    ('numero', 'integer'),
    ('codigo', 'char'),
    ('descripccion_codigo', 'char'),
    ('fecha_ingreso_sol', 'datetime'),
    ('fecha_inicio_cita', 'datetime'),
    ('fecha_fin_cita', 'datetime'),
    ('abonado', 'char'),
    ('ebos', 'char'),
    ('prioridad', 'integer'),
    ('descripccion_prioridad', 'char'),
    ('unidad_negocio', 'char'),
    ('codigo_origen', 'char'),
    ('codigo_sac', 'char'),
    ('tipo_solicitud', 'char'),
    ('central', 'char'),
    ('armario', 'char'),
    ('terminal', 'char'),
    ('area', 'char'),
    ('estado_ot', 'char'),
    ('codigo_tecnico', 'char'),
    ('categoria_linea', 'char'),
    ('oficina_gestionaria', 'char'),
    ('tecnologia', 'char'),
    ('servicio_reclamado', 'char'),
    ('problema_nivel1', 'char'),
    ('problema_nivel2', 'char'),
    ('problema_nivel3', 'char'),
    ('problema_nivel4', 'char'),
    ('historico_fecha_cierre', 'datetime'),
    ('historico_cierre', 'char'),
    ('historico_comentario_cierre', 'char'),
    ('historico_descripcion_intervenciones', 'char'),
    ('historico_localizacion_intervenciones', 'char'),
    ('historico_causa_intervenciones', 'char'),
    ('facilidades', 'char'),
    ('coordenada_rg', 'char'),
    ('ip_adsl', 'char'),
    ('coordenada_adsl_elementored', 'char'),
    ('fecha_ultima_prueba_actor', 'datetime'),
    ('resultado_ultima_prueba_actor', 'char'),
    ('categoria_terminal', 'char'),
    ('nro_ticket', 'char'),
    ('contacto_nombre', 'char'),
    ('contacto_telefono', 'char'),
    ('horario_contacto', 'char'),
    ('localidad_descripcion', 'char'),
    ('cod_categoria_cliente', 'char'),
    ('nro_cliente', 'char'),
    ('comentario_cita', 'char'),
    ('modelo_instalacion', 'char'),
    ('fecha_intalacion_temporaria', 'datetime'),
    ('tipo_linea', 'char'),
    ('tipo_aparato', 'char'),
    ('horizontal', 'char'),
    ('horizontal_adsl', 'char'),
    ('topologia', 'char'),
    ('nro_adicional', 'char'),
    ('cavina_apto_nuevo', 'char'),
    ('aparatos', 'char'),
    ('cod_aparato1', 'char'),
    ('descripccion_aparato1', 'char'),
    ('fecha_aparato1', 'datetime'),
    ('cod_aparato2', 'char'),
    ('descripccion_aparato2', 'char'),
    ('fecha_aparato2', 'datetime'),
    ('cod_aparato3', 'char'),
    ('descripccion_aparato3', 'char'),
    ('fecha_aparato3', 'datetime'),
    ('cod_aparato4', 'char'),
    ('descripccion_aparato4', 'char'),
    ('fecha_aparato4', 'datetime'),
    ('cod_aparato5', 'char'),
    ('descripccion_aparato5', 'char'),
    ('fecha_aparato5', 'datetime'),
    ('armario_categoria', 'char'),
    ('armario_comentario', 'char'),
    ('armario_nombre_calle', 'char'),
    ('armario_altura', 'char'),
    ('armario_nombre_edificio', 'char'),
    ('armario_manzana', 'char'),
    ('terminal_categoria', 'char'),
    ('terminal_comentario', 'char'),
    ('terminal_nombre_calle', 'char'),
    ('terminal_altura', 'char'),
    ('terminal_manzana', 'char'),
    ('terminal_nombre_edificio', 'char'),
    ('categoria_cliente', 'char'),
    ('nombre_cliente', 'char'),
    ('domicilio_cliente_calle', 'char'),
    ('domicilio_cliente_altura', 'char'),
    ('domicilio_cliente_piso', 'char'),
    ('domicilio_cliente_dpto', 'char'),
    ('domicilio_cliente_localidad', 'char'),
    ('domicilio_cliente_cod_postal', 'char'),
    ('domicilio_cliente_comentario', 'char'),
    ('domicilio_facturacion_calle', 'char'),
    ('domicilio_facturacion_altura', 'char'),
    ('domicilio_facturacion_piso', 'char'),
    ('domicilio_facturacion_dpto', 'char'),
    ('domicilio_facturacion_cod_postal', 'char'),
    ('domicilio_facturacion_localidad', 'char'),
    ('domicilio_facturacion_comentario', 'char'),
    ('domicilio_instalacion_calle', 'char'),
    ('domicilio_instalacion_altura', 'char'),
    ('domicilio_instalacion_piso', 'char'),
    ('domicilio_instalacion_dpto', 'char'),
    ('domicilio_instalacion_localidad', 'char'),
    ('domicilio_instalacion_cod_postal', 'char'),
    ('servicios_sup', 'char'),
    ('cod_servicio_supl1', 'char'),
    ('descripcion_servicio_supl1', 'char'),
    ('fecha_servicio_supl1', 'datetime'),
    ('cod_servicio_supl2', 'char'),
    ('descripcion_servicio_supl2', 'char'),
    ('fecha_servicio_supl2', 'datetime'),
    ('cod_servicio_supl3', 'char'),
    ('descripcion_servicio_supl3', 'char'),
    ('fecha_servicio_supl3', 'datetime'),
    ('cod_servicio_supl4', 'char'),
    ('descripcion_servicio_supl4', 'char'),
    ('fecha_servicio_supl4', 'datetime'),
    ('cod_servicio_supl5', 'char'),
    ('descripcion_servicio_supl5', 'char'),
    ('fecha_servicio_supl5', 'datetime'),
    ('descripccion_tecnologia', 'char'),
    ('dslam_elementored', 'char'),
    ('modelo_instalacion2', 'char'),
    ('nro_cuit', 'char'),
    ('observaciones', 'char'),
    ('profesion', 'char'),
    ('reg_comercio_folio', 'char'),
    ('reg_comercio_libro', 'char'),
    ('reg_comercio_tomo', 'char'),
    ('condicion_iva', 'char'),
    ('figura_en_guia', 'char'),
    ('simcard', 'char'),
    ('fecha_asignacion', 'datetime'),
    ('dslam_vuelco', 'char'),
    ('predecesor', 'char'),
    ('pr_par', 'char'),
    ('pr_coordenada', 'char'),
    ('pr_cable', 'char')]


class OrdenTrabajo(ModelView, ModelSQL):
    'OrdenTrabajo'
    __name__ = 'oci.orden.trabajo'


    ot_oci = fields.Many2One('oci.asignacion.orden.trabajo', 'Orden Trabajo OCI')
    type = fields.Selection([
            ('telecom', 'Telecom'),
            ('oci', 'Oci')], 'Tipos')
    state = fields.Selection([
            ('pendiente', 'Pendiente'),
            ('asignado', 'Asignado'),
            ('cerrado', 'Cerrado')], 'Estado')
    # campos del excel
    numero = fields.Integer('Nro Orden Trabajo')
    codigo = fields.Char('Código de Trabajo')
    descripccion_codigo = fields.Char('Descripcion Cod. Trabajo')
    fecha_ingreso_sol = fields.DateTime('Fecha Ingreso Sol/Rec')
    fecha_inicio_cita = fields.DateTime('Fecha Inicio Cita')
    fecha_fin_cita = fields.DateTime('Fecha Fin Cita')
    abonado = fields.Char('Abonado')
    ebos = fields.Char('EBOS')
    #prioridad = fields.Integer('Prioridad')
    prioridad = fields.Integer('Prioridad')
    descripccion_prioridad = fields.Char('Descripcion Prioridad')
    unidad_negocio = fields.Char('Unidad Negocio')
    codigo_origen = fields.Char('Codigo Origen')
    codigo_sac = fields.Char('Codigo SAC')
    tipo_solicitud = fields.Char('Tipo Solicitud')
    central = fields.Char('Central')
    armario = fields.Char('Armario')
    terminal = fields.Char('Terminal')
    area = fields.Char('Area')
    estado_ot = fields.Char('Estado OT')
    codigo_tecnico = fields.Char('Codigo Técnico')
    categoria_linea = fields.Char('Categoria Linea')
    oficina_gestionaria = fields.Char('Oficina Gestionaria')
    tecnologia = fields.Char('Tecnologia')
    servicio_reclamado = fields.Char('Servicio Reclamda')
    problema_nivel1 = fields.Char('Problema Nivel 1')
    problema_nivel2 = fields.Char('Problema Nivel 2')
    problema_nivel3 = fields.Char('Problema Nivel 3')
    problema_nivel4 = fields.Char('Problema Nivel 4')
    historico_fecha_cierre = fields.DateTime('Historico Fecha Cierre')
    historico_cierre = fields.Char('Historico Cierre')
    historico_comentario_cierre = fields.Char('Historico Comentario Cierre')
    historico_descripcion_intervenciones = fields.Char('Historico Descripcion Intervenciones')
    historico_localizacion_intervenciones = fields.Char('Historico Localizacion Intervenciones')
    historico_causa_intervenciones = fields.Char('Historico Causa Intervenciones')
    facilidades = fields.Char('Facilidades')
    coordenada_rg = fields.Char('Coordenada RG')
    ip_adsl = fields.Char('IP ADSL')
    coordenada_adsl_elementored = fields.Char('Coordenada ADSL Elementored')
    fecha_ultima_prueba_actor = fields.DateTime('Fecha Ultima Prueba Actor')
    resultado_ultima_prueba_actor = fields.Char('Resultado Ultima Prueba Actor')
    categoria_terminal = fields.Char('Categoria Terminal')
    nro_ticket = fields.Char('Nro Tiket')
    contacto_nombre = fields.Char('Contacto Nombre')
    contacto_telefono = fields.Char('Contacto Telefono')
    horario_contacto = fields.Char('Horario Contacto')
    localidad_descripcion = fields.Char('Localidad Descripcion')
    cod_categoria_cliente = fields.Char('Codigo Categoria Cliente')
    nro_cliente = fields.Char('Nro Cliente')
    comentario_cita = fields.Char('Comentario Cita')
    modelo_instalacion = fields.Char('Modelo Instalacion')
    fecha_intalacion_temporaria = fields.DateTime('Fecha Instalacion Temporaria')
    tipo_linea = fields.Char('Tipo Linea')
    tipo_aparato = fields.Char('Tipo Aparato')
    horizontal = fields.Char('Horizontal')
    horizontal_adsl = fields.Char('Horizontal ADSL')
    topologia = fields.Char('Topologia')
    nro_adicional = fields.Char('Nro Adicional')
    cavina_apto_nuevo = fields.Char('Cavina Apto Nuevo')
    aparatos = fields.Char('Aparatos')
    cod_aparato1 = fields.Char('Cod Aparato 1')
    descripccion_aparato1 = fields.Char('Descripcion Aparato 1')
    fecha_aparato1 = fields.DateTime('Fecha Aparato 1')
    cod_aparato2 = fields.Char('Cod Aparato 2')
    descripccion_aparato2 = fields.Char('Descripcion Aparato 2')
    fecha_aparato2 = fields.DateTime('Fecha Aparato 2')
    cod_aparato3 = fields.Char('Cod Aparato 3')
    descripccion_aparato3 = fields.Char('Descripcion Aparato 3')
    fecha_aparato3 = fields.DateTime('Fecha Aparato 3')
    cod_aparato4 = fields.Char('Cod Aparato 4')
    descripccion_aparato4 = fields.Char('Descripcion Aparato 4')
    fecha_aparato4 = fields.DateTime('Fecha Aparato 4')
    cod_aparato5 = fields.Char('Cod Aparato 5')
    descripccion_aparato5 = fields.Char('Descripcion Aparato 5')
    fecha_aparato5 = fields.DateTime('Fecha Aparato 5')
    armario_categoria = fields.Char('Armario Categoria')
    armario_comentario = fields.Char('Armario Comentario')
    armario_nombre_calle = fields.Char('Armario Nombre Calle')
    armario_altura = fields.Char('Armario Altura')
    armario_nombre_edificio = fields.Char('Armario Nombre Edificio')
    armario_manzana = fields.Char('Armario Manzana')
    terminal_categoria = fields.Char('Terminal Categoria')
    terminal_comentario = fields.Char('Terminal Comentario')
    terminal_nombre_calle = fields.Char('Terminal Nombre Calle')
    terminal_altura = fields.Char('Terminal Altura')
    terminal_manzana = fields.Char('Terminal Manzana')
    terminal_nombre_edificio = fields.Char('Terminal Categoria')
    categoria_cliente = fields.Char('Categoria Cliente')
    nombre_cliente = fields.Char('Nombre Cliente')
    domicilio_cliente_calle = fields.Char('Domicilio Cliente Calle')
    domicilio_cliente_altura = fields.Char('Domicilio Cliente Altura')
    domicilio_cliente_piso = fields.Char('Domicilio Cliente Piso')
    domicilio_cliente_dpto = fields.Char('Domicilio Cliente DPTO')
    domicilio_cliente_localidad = fields.Char('Domicilio Cliente Localidad')
    domicilio_cliente_cod_postal = fields.Char('Domicilio Cliente Cod-Postal')
    domicilio_cliente_comentario = fields.Char('Domicilio Cliente Comentario')
    domicilio_facturacion_calle = fields.Char('Domicilio Facturacion Calle')
    domicilio_facturacion_altura = fields.Char('Domicilio Facturacion Altura')
    domicilio_facturacion_piso = fields.Char('Domicilio Facturacion Piso')
    domicilio_facturacion_dpto = fields.Char('Domicilio Facturacion DPTO')
    domicilio_facturacion_cod_postal = fields.Char('Domicilio Facturacion Cod-Postal')
    domicilio_facturacion_localidad = fields.Char('Domicilio Facturacion Localidad')
    domicilio_facturacion_comentario = fields.Char('Domicilio Facturacion Comentario')
    domicilio_instalacion_calle = fields.Char('Domicilio Instalacion Calle')
    domicilio_instalacion_altura = fields.Char('Domicilio Instalacion Altura')
    domicilio_instalacion_piso = fields.Char('Domicilio Instalacion Piso')
    domicilio_instalacion_dpto = fields.Char('Domicilio Instalacion DPTO')
    domicilio_instalacion_localidad = fields.Char('Domicilio Instalacion Localidad')
    domicilio_instalacion_cod_postal = fields.Char('Domicilio Instalacion Cod-Postal')
    servicios_sup = fields.Char('Servicios Sup')
    cod_servicio_supl1 = fields.Char('Codigo Servicio Suplementario 1')
    descripcion_servicio_supl1 = fields.Char('Descripcion Servicio Suplementario 1')
    fecha_servicio_supl1 = fields.DateTime('Fecha Servicio Suplementario 1')
    cod_servicio_supl2 = fields.Char('Codigo Servicio Suplementario 2')
    descripcion_servicio_supl2 = fields.Char('Descripcion Servicio Suplementario 2')
    fecha_servicio_supl2 = fields.DateTime('Fecha Servicio Suplementario 2')
    cod_servicio_supl3 = fields.Char('Codigo Servicio Suplementario 3')
    descripcion_servicio_supl3 = fields.Char('Descripcion Servicio Suplementario 3')
    fecha_servicio_supl3 = fields.DateTime('Fecha Servicio Suplementario 3')
    cod_servicio_supl4 = fields.Char('Codigo Servicio Suplementario 4')
    descripcion_servicio_supl4 = fields.Char('Descripcion Servicio Suplementario 4')
    fecha_servicio_supl4 = fields.DateTime('Fecha Servicio Suplementario 4')
    cod_servicio_supl5 = fields.Char('Codigo Servicio Suplementario 5')
    descripcion_servicio_supl5 = fields.Char('Descripcion Servicio Suplementario 5')
    fecha_servicio_supl5 = fields.DateTime('Fecha Servicio Suplementario 5')
    descripccion_tecnologia = fields.Char('Descripcion Tecnologia')
    dslam_elementored = fields.Char('DSLAM ELEMENTORED')
    modelo_instalacion2 = fields.Char('Modelo Instalacion')
    nro_cuit = fields.Char('Nro Cuit')
    observaciones = fields.Char('Observaciones')
    profesion = fields.Char('Profesion')
    reg_comercio_folio = fields.Char('Reg Comercio Folio')
    reg_comercio_libro = fields.Char('Reg Comercio Libro')
    reg_comercio_tomo = fields.Char('Reg Comercio Tomo')
    condicion_iva = fields.Char('Condicion IVA')
    figura_en_guia = fields.Char('Figura en Guia')
    simcard = fields.Char('SIMCARD')
    fecha_asignacion = fields.DateTime('Fecha Asignacion')
    dslam_vuelco = fields.Char('DSLAM Vuelco')
    predecesor = fields.Char('Predecesor')
    pr_par = fields.Char('PR PAR')
    pr_coordenada = fields.Char('PR Coordenada')
    pr_cable = fields.Char('PR Cable')

    def get_rec_name(self, name):
        return self.numero

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('numero', '=', int(clause[2].split('%')[1]))]


class WisardCargarOrdenTrabajoStart(ModelView):
    'Wisard Cargar Orden de Trabajo Start'
    __name__ = 'wizard.cargar.orden.trabajo.start'

    type = fields.Selection([
            ('telecom', 'Telecom'),
            ('oci', 'Oci')], 'Tipos')
    state = fields.Selection([
            ('pendiente', 'Pendiente'),
            ('cerrado', 'Cerrado')], 'Estado')
    archivo = fields.Binary('Archivo')


class WisardCargarOrdenTrabajo(Wizard):
    'Wisard Cargar Orden de Trabajo'
    __name__ = 'oci.wizard.cargar.orden.trabajo'

    start = StateView('wizard.cargar.orden.trabajo.start',
        'oci.cargar_orden_trabajo_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'update', 'tryton-ok', default=True),
            ])
    update = StateTransition()

    def transition_update(self):
        file = xlrd.open_workbook(file_contents=self.start.archivo)
        d1 = datetime.now()
        if len(file.sheets()) >= 1:
            h_cuerpo = file.sheet_by_index(0)
            for i in range(2, h_cuerpo.nrows):
                linea = h_cuerpo.row_values(i)
                # txt.write(t.parceador(t.type.lines, linea))
                self.crearLineaOrdenTrabajo(linea)
        d2 = datetime.now()
        self.analizarDatos()
        print(d2 - d1)
        return 'end'

    def crearLineaOrdenTrabajo(self, linea):
        OrdenTrabajo = Pool().get('oci.orden.trabajo')
        dic = {'state': 'pendiente',
               'type': 'telecom'}

        for campo in range(0, len(CAMPOS)):
            if CAMPOS[campo][1] == 'integer':
                dic[CAMPOS[campo][0]] = int(linea[campo]) if linea[campo] else None
            elif CAMPOS[campo][1] == 'char':
                dic[CAMPOS[campo][0]] = str(linea[campo]).strip() if linea[campo] else None
            elif CAMPOS[campo][1] == 'datetime':
                if linea[campo]:
                    temp = datetime(1899, 12, 30)
                    delta = timedelta(days=float(linea[campo]))
                    dic[CAMPOS[campo][0]] = temp + delta
                else:
                    dic[CAMPOS[campo][0]] = None

        try:
            # if dic['abonado']:
            #     search = [
            #         ('abonado', '=', dic['abonado']),
            #         ('state', '=', 'pendiente')
            #     ]
            # else:
            search = [
                ('numero', '=', dic['numero']),
                ('state', '=', 'pendiente')
            ]

            ot = OrdenTrabajo.search(search)
            if ot:
                OrdenTrabajo.write(ot, dic)
            else:
                OrdenTrabajo.create([dic])
        except:
            print(linea[0])

    def analizarDatos(self):
        #central
        cursor0 = Transaction().connection.cursor()
        st0 = "select central \
                from oci_orden_trabajo \
                group by 1"
        cursor0.execute(st0)
        for data in cursor0.fetchall():
            Central = Pool().get('oci.central.telecom')
            central = Central.search([('name', '=', str(data[0]))])
            if not central:
                central, = Central.create([{'name': str(data[0])}])
            else:
                central = central[0]
            #ARMARIOS
            cursor1 = Transaction().connection.cursor()
            st1 = "select armario, armario_nombre_calle, armario_altura, armario_nombre_edificio, armario_manzana, central \
                    from oci_orden_trabajo \
                    where state = 'pendiente' \
                    and armario_nombre_calle != 'null' \
                    and  central = '%s'\
                    group by 1,2,3,4,5,6 \
                    order by 1"%(central.name)
            cursor1.execute(st1)
            for data1 in cursor1.fetchall():
                Armario = Pool().get('oci.armario')
                armario = Armario.search([('name', '=', data1[0]), ('central', '=', central.id)])
                if not armario:
                    armario, = Armario.create([{
                        'name': str(data1[0]),
                        'calle': str(data1[1]),
                        'altura': str(data1[2]),
                        'nombre_edificio': str(data1[3]),
                        'manzana': str(data1[4]),
                        'central': central.id,
                    }])
                else:
                    armario = armario[0]

                #TERMINALES
                cursor2 = Transaction().connection.cursor()
                st2 = "select terminal, terminal_nombre_calle, terminal_altura, terminal_nombre_edificio, terminal_manzana \
                        from oci_orden_trabajo \
                        where state = 'pendiente' \
                        and armario = '%s' \
                        group by 1,2,3,4,5 \
                        order by 1"%(armario.name)
                cursor2.execute(st2)
                terminales = []
                for data2 in cursor2.fetchall():
                    Terminal = Pool().get('oci.terminal')
                    terminal = Terminal.search([('name', '=', data2[0]), ('armario', '=', armario.id)])
                    if not terminal:
                        terminales.append({
                            'name': str(data2[0]),
                            'calle': str(data2[1]),
                            'altura': str(data2[2]),
                            'nombre_edificio': str(data2[3]),
                            'manzana': str(data2[4]),
                            'armario': armario.id,
                        })
                Terminal.create(terminales)


class AsignacioOrdenTrabajo(Workflow, ModelView, ModelSQL):
    'Asignacion Orden Trabajo'
    __name__ = 'oci.asignacion.orden.trabajo'

    name = fields.Char('Numero', readonly=True)
    tecnico = fields.Many2One('party.party', 'Tecnico', domain=[
            ('perfil', '=', 'tec'),
            ])
    ott_function = fields.Function(fields.Many2Many('oci.orden.trabajo', None, None, 'OT',
            states={'invisible': True}),
            'on_change_with_ott_function')
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('close', 'Cerrada'),
        ('open', 'Avierta')], 'Estado', readonly=True)
    ott = fields.One2Many('oci.orden.trabajo', 'ot_oci', 'OT', add_remove=[
            ('id', 'in', Eval('ott_function'))],
            states={'readonly': Not(Bool(Eval('state').in_(['draft'])))})

    @classmethod
    def __setup__(cls):
        super(AsignacioOrdenTrabajo, cls).__setup__()
        cls._order.insert(0, ('id', 'ASC'))
        cls._transitions |= set((
            ('draft', 'open'),
            ('open', 'close'),
            ))
        cls._buttons.update({
                'crear': {
                    'invisible': Eval('state').in_(['open'])
                    },
                })


    @staticmethod
    def default_state():
        return 'draft'

    @fields.depends('tecnico')
    def on_change_with_ott_function(self, name=None):
        if not self.tecnico:
            return []
        armarios = []
        central = []
        for armario in self.tecnico.zona.armarios:
            armarios.append(armario.name)
            central.append(armario.central.name)
        OrdenTrabajo = Pool().get('oci.orden.trabajo')
        ots = OrdenTrabajo.search([('armario', 'in', armarios),
                                   ('central', 'in', central),
                                   ('state', '=', 'pendiente')])

        ots = [ot.id for ot in ots]
        return ots

    @classmethod
    @Workflow.transition('open')
    def crear(cls, ot):
        for values in ot:
            if not values.name:
                values.name = cls._new_code()
            for ot in values.ott:
                ot.state = 'asignado'
            values.save()

    @classmethod
    def _new_code(cls, **pattern):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Configuration = pool.get('oci.configuration')
        config = Configuration(1)
        sequence = config.get_multivalue('ot_sequence', **pattern)
        if sequence:
            return Sequence.get_id(sequence.id)


class OrdenTrabajoCerradas(ModelView, ModelSQL):
    'Cierre de las Ordenes de Trabajo'
    __name__ = 'oci.orden.trabajo.cerradas'

    name = fields.Many2One('oci.orden.trabajo', 'Orden de Trabajo')
    grupo_operativo = fields.Char('Grupo Operativo')
    codigo_trabajo = fields.Char('Codigo de Trabajo')
    nro_solicitud_tiket = fields.Char('Codigo de Trabajo')
    nro_abonado_ot = fields.Char('Nro Abonado OT')
    fecha_cierre_ot = fields.DateTime('Fecha de Cierre OT')
    cod_cierre = fields.Char('Codigo Cierre')
    cod_localizacion = fields.Char('Codigo Localizacion')
    cod_causa = fields.Char('Codigo Causa')
    cod_nueva_falta = fields.Char('Codigo Nueva Falta')
    loc_nueva_falta = fields.Char('Localizacion Nueva Falta')
    tecnico_cierre = fields.Char('Tecnico Cierre')
    tecnico_cierre_nombre = fields.Char('Tecnico Cierre Nombre')
    comentario_tarea = fields.Char('Comentario Tarea')
    disp_cierre = fields.Char('Disp Cierre')
    materiales = fields.Char('Materiales')
    nro_cierre_apto = fields.Char('Nro Cierre APTO')
    grupo = fields.Char('Grupo')
    area_ot = fields.Char('Area OT')
    central = fields.Char('Central')
    zona = fields.Char('Zona')
    terminal = fields.Char('Terminal')
    oficina_gestion = fields.Char('Oficina Gestion')
    categoria_linea = fields.Char('Categoria Linea')
    fecha_creacion_not = fields.DateTime('Fecha Creacion NOT')
    fecha_hora_asignacion = fields.DateTime('Fecha y Hora Asignacion')
    fecha_hora_despacho = fields.DateTime('Fecha y Hora Despacho')
    fecha_creacion_tkt = fields.DateTime('Fecha Creacion TKT')


CAMPOS_CIERRE = [
    ('name', 'id'),
    ('grupo_operativo', 'char'),
    ('codigo_trabajo', 'char'),
    ('nro_solicitud_tiket', 'char'),
    ('nro_abonado_ot', 'char'),
    ('fecha_cierre_ot', 'datetime'),
    ('cod_cierre', 'char'),
    ('cod_localizacion', 'char'),
    ('cod_causa', 'char'),
    ('cod_nueva_falta', 'char'),
    ('loc_nueva_falta', 'char'),
    ('tecnico_cierre', 'char'),
    ('tecnico_cierre_nombre', 'char'),
    ('comentario_tarea', 'char'),
    ('disp_cierre', 'char'),
    ('materiales', 'char'),
    ('nro_cierre_apto', 'char'),
    ('grupo', 'char'),
    ('area_ot', 'char'),
    ('central', 'char'),
    ('zona', 'char'),
    ('terminal', 'char'),
    ('oficina_gestion', 'char'),
    ('categoria_linea', 'char'),
    ('fecha_creacion_not', 'datetime'),
    ('fecha_hora_asignacion', 'datetime'),
    ('fecha_hora_despacho', 'datetime'),
    ('fecha_creacion_tkt', 'datetime')]


class WisardCerrarOrdenTrabajo(Wizard):
    'Wisard Cerrar Orden de Trabajo'
    __name__ = 'oci.wizard.cerrar.orden.trabajo'

    start = StateView('wizard.cargar.orden.trabajo.start',
        'oci.cargar_orden_trabajo_start', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'update', 'tryton-ok', default=True),
            ])
    update = StateTransition()

    def transition_update(self):
        file = xlrd.open_workbook(file_contents=self.start.archivo)
        # d1 = datetime.now()
        if len(file.sheets()) >= 1:
            h_cuerpo = file.sheet_by_index(0)
            for i in range(2, h_cuerpo.nrows):
                linea = h_cuerpo.row_values(i)
                # txt.write(t.parceador(t.type.lines, linea))
                self.crearLineaOrdenTrabajo(linea)
        # d2 = datetime.now()
        # self.analizarDatos()
        # print(d2 - d1)
        return 'end'

    def crearLineaOrdenTrabajo(self, linea):
        OrdenTrabajoCerradas = Pool().get('oci.orden.trabajo.cerradas')
        OrdenTrabajo = Pool().get('oci.orden.trabajo')
        dic = {}

        for campo in range(0, len(CAMPOS_CIERRE)):
            if CAMPOS_CIERRE[campo][1] == 'id':
                ots = OrdenTrabajo.search([('numero', '=', int(linea[campo+1]))])
                if ots:
                    dic[CAMPOS_CIERRE[campo][0]] = ots[0].id
                    ots[0].state = 'cerrado'
                    ots[0].save()
                else:
                    continue
            if CAMPOS_CIERRE[campo][1] == 'char':
                dic[CAMPOS_CIERRE[campo][0]] = str(linea[campo+1]).strip() if linea[campo+1] else None
            elif CAMPOS_CIERRE[campo][1] == 'datetime':
                if linea[campo]:
                    if type(linea[campo]) == str:
                        dt_s = linea[campo+1]
                        dt = datetime.strptime(dt_s, '%d/%m/%Y %H:%M:%S')
                        dic[CAMPOS_CIERRE[campo][0]] = dt
                    else:
                        temp = datetime(1899, 12, 30)
                        delta = timedelta(days=float(linea[campo+1]))
                        dic[CAMPOS_CIERRE[campo][0]] = temp + delta
                else:
                    dic[CAMPOS_CIERRE[campo][0]] = None

        try:
            OrdenTrabajoCerradas.create([dic])
        except:
            logger.error('%s', str(linea), exc_info=True)


class OrdenTrabajoCerradasWFX(ModelView, ModelSQL):
    'Cierre de las Ordenes de Trabajo WFX'
    __name__ = 'oci.orden.trabajo.cerradas.wfx'
    _rec_name = 'nro_abonado'

    fecha = fields.Date('Fecha')
    nro_abonado = fields.Char('Nro Abonado')
    nro_ot = fields.Char('Orden Trabajo')
    tecnico = fields.Many2One('party.party', 'Tecnico', domain=[
            ('perfil', '=', 'tec'),
        ])
    central = fields.Many2One('oci.central.telecom', 'Zona')
    armario = fields.Many2One('oci.armario', 'Armario', domain=[
            ('central', '=', Eval('central')),
        ])
    cod_tec = fields.Char('Cod/Tec')
    celular = fields.Char('Celular')
    alta = fields.Boolean('Alta')
    tarea = fields.Many2One('oci.tarea', 'Tarea')
    loc = fields.Many2One('oci.tarea', 'Tarea', domain=[
            ('tarea', '=', Eval('tarea')),
        ])
    sin_visita = fields.Boolean('Sin Visitar')
    observaciones = fields.Text('Observaciones')
    materiales = fields.One2Many('oci.materiales', 'orden_trabajo', 'Materiales')

    @fields.depends('tecnico', 'cod_tec', 'celular')
    def on_change_tecnico(self):
        if not self.tecnico:
           return
        self.cod_tec = self.tecnico.cod_tec
        self.celular = self.cel_teco

    @fields.depends('nro_ot')
    def on_change_nro_ot(self):
        if not self.nro_ot:
           return
        self.nro_ot = 'LETRAS' + self.nro_ot.rjust(6, '0')

    @staticmethod
    def default_fecha():
        Date = Pool().get('ir.date')
        return Date.today()


class Tarea(ModelView, ModelSQL):
    'Tareas para los cierres'
    __name__ = 'oci.tarea'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Codigo')
    loc = fields.One2Many('oci.tarea.loc', 'tarea', 'Tarea')


class LocalizacionTarea(ModelView, ModelSQL):
    'Localizacion de la tarea'
    __name__ = 'oci.tarea.loc'

    name = fields.Char('Nombre', required=True)
    code = fields.Char('Codigo')
    tarea = fields.Many2One('oci.tarea', 'Tarea', required=True)
