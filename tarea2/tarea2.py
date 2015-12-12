from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from putils import PGDatos
from api_client.sqldata import SQLData

"""
    El GridField añade soporte para redes de datos que no están en línea editable
"""
class GridField(object):

    def __init__(self, fldheader="", fldtype="", fldalign="", flddisabled=False, fldwidth=100, flddata=''):
        self.fldHeader = fldheader
        self.fldType = fldtype
        self.fldAlign = fldalign
        self.fldDisabled = flddisabled
        self.fldWidth = fldwidth
        self.fldData = flddata
        self.fldCol = -1


class GridFields(object):
    __fields = []
    __key = -1
    __columns = 0

    @property
    def columns(self):
        return self.__columns

    @property
    def key(self):
        return self.__key

    def add(self, field):
        if field.fldCol == -1:
            field.fldCol = self.__columns
        if field.fldType == "key":
            self.__key = self.__columns
        self.__fields.append(field)
        self.__columns += 1

    def getkey(self):
        return self.__fields[self.__key]

    def getfield(self, col):
        return self.__fields[col]


class GridProyecto(FloatLayout):
    """
        Esta funcion inicia la clase derivada de GridLayout para el manejo de grids
    """
    gHeader = GridLayout
    gBody = GridLayout
    rHeight = NumericProperty(30)
    columnas = NumericProperty()
    filas = NumericProperty()
    # colHeaders = ListProperty()
    # rowTypes = ListProperty()
    # rowAlign = ListProperty()
    # colDisabled = ListProperty()
    # colSizes = ListProperty()
    gfields = GridFields()
    __datasource = SQLData
    __rows = PGDatos()

    @property
    def datasource(self):
        return self.__rows

    @datasource.setter
    def datasource(self, value):
        self.__datasource = value
        for rowdic in self.__datasource.getapidata():
            datarow = []
            for col in range(self.gfields.columns):
                datarow.append(rowdic[self.gfields.getfield(col).fldData])
            self.addgridrow(datarow)

    def addcolumna(self, colheader, rowtype="txt", rowalign="center", colsize=200, coldisable=False, datafield=''):
        """
            Esta funcion agrega una columna al grid
        """
        # self.colHeaders.append(colheader)
        # self.rowTypes.append(rowtype)
        # self.rowAlign.append(rowalign)
        # self.colDisabled.append(coldisable)
        # self.colSizes.append(colsize)
        self.gfields.add(GridField(fldheader=colheader, fldtype=rowtype, fldalign=rowalign, flddisabled=coldisable,
                                   fldwidth=colsize, flddata=datafield))
        self.columnas = self.gfields.columns
#        self.gfields.columns += 1

    def addheaders(self):
        """
            Esta funcion crea las celdas que se utilizaran para el encabezado de los grids
        """
        gHdr = self.gHeader
        self.filas += 1
        for col in range(self.columnas):
            hdr = GridHeader()
            hdr.id = "hdr_col{0}".format(col)
            hdr.width = self.gfields.getfield(col).fldWidth
            hdr.padding = [5, 5]
            hdr.text = '[color=ffffff][b][size=16]{0}[/size][/b][/color]'.format(self.gfields.getfield(col).fldHeader)
            hdr.halign = 'center'
            hdr.valign = 'middle'
            hdr.markup = True
#            hdr.text_size = hdr.size
            gHdr.add_widget(hdr)

    def addgridrow(self, rowdata):
        """
            Aqui se agregan todas las celdas de cada fila de un grid de datos
        """
        gBdy = self.gBody
        gBdy.bind(minimum_height=gBdy.setter('height'), minimum_width=gBdy.setter('width'))
        self.filas += 1
        for col in range(self.columnas):
            if self.gfields.getfield(col).fldType == "txt" or self.gfields.getfield(col).fldType == "key":
                gBdy.add_widget(self.getcelllabel(self.filas, col, rowdata[col], self.gfields.getfield(col).fldAlign,
                                                  self.gfields.getfield(col).fldDisabled,
                                                  self.gfields.getfield(col).fldWidth,
                                                  self.gfields.getfield(col).fldType))
            else:
                gBdy.add_widget(self.getcellchk(self.filas, col, rowdata[col], self.gfields.getfield(col).fldDisabled,
                                                self.gfields.getfield(col).fldWidth,
                                                self.gfields.getfield(col).fldType))
        self.__rows.addrow(rowdata[self.gfields.key], rowdata[:self.gfields.key] + rowdata[(self.gfields.key + 1):])

    def getcellchk(self, fila, columna, Activo, Disabled = False, Size=200, Tipo="chk"):
        """
            Aqui se devuelve una celda completa para manejo de checkbox
        """
        cell = GridCCell()
        cell.id = "{0}_row{1}_col{2}".format(Tipo, fila, columna)
        cell.width = Size
        cell.active = Activo
        cell.disabled = Disabled
        cell.background_checkbox_disabled_down = 'atlas://data/images/defaulttheme/checkbox_on'
        cell.text_size = cell.size
        if Tipo == "bor":
            cell.bind(active=self.borradoclick)
        return cell

    def getcelllabel(self, fila, columna, Texto, Halign='left', Disabled = False, Size=200, Tipo="txt", Valign='middle'):
        """
            Esta funcion es para devolver una celda completa para manejo de etiquetas
        """
        cell = GridCell()
        cell.id = "{0}_row{0}_col{1}".format(Tipo, fila, columna)
        if Tipo == "key":
            cell.key = str(Texto)
        cell.width = Size
        cell.padding = [5,5]
        cell.text = '[color=000000]{0}[/color]'.format(Texto)
        cell.halign = Halign
        cell.valign = Valign
        cell.disabled = Disabled
        cell.markup = True
        cell.text_size = cell.size
        return cell

    def borradoclick(self, cell, value):
        """
            Esta funcion marca las celdas para el borrado
        """
        cell.borrado = cell.active
        count = 1
        for cella in cell.walk_reverse(loopback=False):
            if cella.id[4:7] == 'row':
                cella.borrado = cell.active
                count += 1
            if count >= self.columnas:
                break

    def delGridRow(self, range = "All"):
        """
            Esta funcion para elimina las celdas de un grid
        """
        childs = self.gBody.parent.children
        for ch in childs:
            for c in reversed(ch.children):
                if range == "All" or c.borrado:
                    if range != "All" and c.id == "key":
                        self._rows.delrow(c.key)
                        self.gBody.remove_widget(c)


class GridHeader(Label):
    """
        Aqui se inicia la clase derivada de BoxLayout como base del encabezado de los grids
    """
    height = NumericProperty(40)
    bgcolor = ListProperty([0.4, 0.4, 0.4])


class GridCell(Label):
    """
        Aqui se inicia la clase derivada de BoxLayout como base de las celdas de datos del grid
    """
    key = StringProperty("")
    borrado = BooleanProperty(False)
    height = NumericProperty(30)
    bgcolor = ListProperty([0.7, 0.7, 0.7])


class GridCCell(CheckBox):
    """
        Aqui se inicia la clase derivada de BoxLayout como base de las celdas de datos del grid
    """
    key = StringProperty("")
    borrado = BooleanProperty(False)
    height = NumericProperty(30)
    bgcolor = ListProperty([0.7, 0.7, 0.7])


def convertorgb(color):
    """
        Esta funcion convierte de codigo de colores de Hex a RGB decimal
    """
    __tmplist = []
    if len(color) == 6:
        __tmplist.append(float(int(color[0:2], 16)) / 255.0)
        __tmplist.append(float(int(color[2:4], 16)) / 255.0)
        __tmplist.append(float(int(color[4:6], 16)) / 255.0)
        return __tmplist
    else:
        return [0, 0, 0]


class LabelPopup(Label):
    """
        Este es el objeto de texto principal de la aplicacion, permite modificar el color de fondo, color de texto
        y agregar bordes
    """
    __texto = StringProperty('')
    __textocolor = StringProperty('FFFFFF')
    __bordercolor = ListProperty([])
    __backcolor = ListProperty([])

    def __init__(self, **kwargs):
        """
            Esta funcion Sobreescribe el constructor de objeto Label
        """

        if 'texto' in kwargs:
            self.texto = kwargs['texto']
        if 'textocolor' in kwargs:
            self.textocolor = kwargs['textocolor']

        self.line = ObjectProperty(None)
        self.linecolor = ObjectProperty(None)
        self.fondo = ObjectProperty(None)
        self.fondocolor = ObjectProperty(None)
        Label.__init__(self, **kwargs)

    @property
    def texto(self):
        """
            Esta propiedad de texto contiene el texto del objeto
        """
        return self.__texto

    @texto.setter
    def texto(self, value):
        self.text = '[color={0}]{1}[/color]'.format(self.__textocolor, value)
        self.markup = True
        self.__texto = value

    @property
    def textocolor(self):
        """
            La propiedad textocolor contiene el color del texto en formato RGB Hex
        """
        return self.__textocolor

    @textocolor.setter
    def textocolor(self, value):
        self.text = '[color={0}]{1}[/color]'.format(value, self.__texto)
        self.markup = True
        self.__textocolor = value

    @property
    def bordercolor(self):
        """
            La propiedad bordercolor contiene el color del borde en formato RGB Dec list
        """
        return self.__bordercolor

    @bordercolor.setter
    def bordercolor(self, value):
        with self.canvas.after:
            self.linecolor = Color(value)
            self.line = Line(rectangle=[self.x, self.y, self.width-1, self.height-6], width=2)
        self.__bordercolor = value

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    @property
    def backcolor(self):
        """
            La propiedad backcolor contiene el color del fondo en formato RGB Dec List
        """
        return self.__backcolor

    @backcolor.setter
    def backcolor(self, value):
        with self.canvas.before:
            self.fondocolor = Color(value)
            self.fondo = Rectangle(pos=[self.x, self.y], size=[self.width-1, self.height-6])
        self.__backcolor = value

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        """
            Esta funcion actualiza el borde y el fondo de el objeto cada vez que cambie de tamano o lugar
        """
        if len(self.bordercolor) > 0:
            self.linecolor.rgb = self.bordercolor
            self.line.rectangle = [self.x, self.y, self.width-1, self.height-6]
        if len(self.backcolor) > 0:
            self.fondocolor.rgb = self.backcolor
            self.fondo.pos = self.pos
            self.fondo.size = [self.width-1, self.height-6]


    def textocolorrgb(self, value):
        """
            Esta funcion sirve convertir colores RGB de Hex a Dec List
        """
        return convertorgb(value)


class LabelSPopup(LabelPopup):
    """
        Este objeto es derivado de LabelPopup
    """
    pass


class PopupParcial(Popup):
    """
        Este objeto cambia el fondo de los Popup en la aplicacion
    """
    pass


class PopupContent(FloatLayout):
    """
        Este objeto contiene los Popup de la Aplicacion, agrega una imagen en conjunto de un Label con
        su fondo y bordes
    """
    mensaje = ObjectProperty(None)
    texto = StringProperty('')
    textocolor = StringProperty('FFFFFF')
    backcolor = ListProperty([])

    def __init__(self, **kwargs):
        """
            Sobreescribe constructor de la clase para agregar funcionalidad en caso de configurar algunas
            propiedades
        """
        if 'texto' in kwargs:
            self.texto = kwargs['texto']
        if 'textocolor' in kwargs:
            self.textocolor = kwargs['textocolor']
        if 'backcolor' in kwargs:
            self.backcolor = kwargs['backcolor']

        FloatLayout.__init__(self, **kwargs)
        self.mensaje.texto = self.texto
        self.mensaje.textocolor = self.textocolor
        self.mensaje.bordercolor = self.mensaje.textocolorrgb(self.textocolor)
        self.mensaje.backcolor = self.backcolor

def showmessagebox(Titulo, Mensaje, Tipo=1):
    """
        Esta funcion despliega un Popup Window para mensajes de la aplicacion
    """
    label = ObjectProperty(None)
    if Tipo == 0:
        label = LabelPopup(texto=Mensaje)
    if Tipo == 1:
        label = PopupContent(texto=Mensaje, textocolor='006600', backcolor=[.6, 1, .6])
    if Tipo == 2:
        label = PopupContent(texto=Mensaje, textocolor='660000', backcolor=[1, .6, .6])
    popup = PopupParcial(title=Titulo, content=label, auto_dismiss=True, size_hint=(.9, .3))
    popup.open()


class LabelProyecto(LabelPopup):
    """
        Texto derivado de LabelPopup para el uso del resto de la aplicacion
    """
    bgcolor = ListProperty([0, 0, 0])


class ButtonDropDown(Button):
    """
        Este objeto es para el uso del dropdown, agrega funcionalidad de datos
    """
    data = ListProperty()

    def __init__(self, data , **kw):
        """
            Sobreescribe constructor para agregar propiedad data
        """
        self.data = data
        super(ButtonDropDown, self).__init__(**kw)


class DropParcial(Button):
    """
        Esto modifica un boton para agregar funciones de dropdown y manejo de datos
    """
    __datasource = ListProperty()
    origen = StringProperty('')
    sector = StringProperty('')
    options = ListProperty()

    @property
    def datasource(self):
        """
            La propiedad datasource obtiene datos de la fuente de datos y los agrega al dropdown utilizando
            botones
        """
        return self.__datasource

    @datasource.setter
    def datasource(self, value):
        for row in value:
            self.options.append(ButtonDropDown(data=row, text=str(row[1]), size_hint_y=None, height=self.height))
        self.__datasource = value

    def __init__(self, **kw):
        """
            Sobreescribe constructor y agrega un dropdown al boton principal
        """
        ddn = self.drop_down = DropDown()
        ddn.bind(on_select=self.on_select)
        super(DropParcial, self).__init__(**kw)

    def on_options(self, instance, value):
        """
            Esto se activa al agregar opciones al dropdown
        """
        ddn = self.drop_down
        ddn.clear_widgets()
        for widg in value:
            widg.bind(on_release=lambda btn: ddn.select(btn.data))
            ddn.add_widget(widg)

    def on_select(self, *args):
        """
            Esto se activa al seleccionar una opcion en el dropdown
        """
        self.text = args[1][1]
        self.origen = args[1][2]
        self.sector = args[1][3]

    def on_touch_up(self, touch):
        """
            Esto despliega el dropdown al presionar el boton principal
        """
        if touch.grab_current == self:
            self.drop_down.open(self)
        return super(DropParcial, self).on_touch_up(touch)
