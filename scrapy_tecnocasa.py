""""
OBJETIVO:
    - Extraer informacion sobre los productos en la pagina de Tecnocasa
    - Aprender a realizar extracciones verticales y horizontales utilizando reglas mediante la libreria scrapy.

CREADO POR DAVID DE VEGA MARTIN  PARA LA PEC 1 DE LA ASIGNATURA  TIPOLOGIA Y CICLO DE VIDA DE PRODUCTOS

SCRIPT DESARROLLADO  PARA  LA PRE-ENTREGA INICIAL COMO DESARROLLO

ULTIMA EDICION = 5 DE NOVIEMBRE DE 2021

"""

# 0 .- IMPORTACION  DE LAS LIBRERIAS NECESARIAS.

from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from bs4 import BeautifulSoup

# 1 .- DEFINICION DEL ELEMENTO A EXTRAER:

class Articulo(Item):
    aProvincia = Field()
    bCiudad = Field()
    cDireccion = Field()
    dCP = Field()
    ePrecio = Field()
    fTipologia = Field()
    gSuperficie = Field()
    hDormitorios = Field()
    iSubtipo = Field()
    jAnho_Const = Field()
    lCategoria = Field()

# 2.- DEFINICION DEL SPIDER PARA LA EXTRACCION

class TecnocasaCrawler(CrawlSpider):

    name = 'Tecnocasa'
    # FIJAMOS PARAMETROS NAVEGADOR PARA FACILITAR SCRAPING SIN SER DETECTADOS.
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 400
        # Numero maximo de paginas en las cuales voy a descargar items. Scrapy se cierra cuando alcanza este numero
    }


    allowed_domains = ['tecnocasa.es']

    # DEFINICION DE LA URL SEMILLA CON LA QUE VAMOS A EXTRAER LA PETICION
    start_urls = ['https://www.tecnocasa.es/anuncios/inmuebles/castilla-y-leon/salamanca/salamanca.html']

                  # ['https://www.tecnocasa.es/anuncios/inmuebles/comunidad-de-madrid/madrid/madrid.html']

                  # ['https://www.tecnocasa.es/anuncios/inmuebles/castilla-y-leon/salamanca/salamanca.html']

    # PARAMETRO PARA FIJAR TIEMPO ENTRE SOLICITUDES DE DESCARGA
    download_delay = 4

    # DEFINICION DE REGLAS PARA LA EXTRACCION

    rules = (
        Rule(  # REGLA #1 => HORIZONTALIDAD POR PAGINACION
            LinkExtractor(
                allow=r'/pag-'
                # Patron en donde se utiliza "/pag-", expresion que puede tomar el valor de cualquier combinacion de numeros
            ), follow=True),
        Rule(  # REGLA #2 => VERTICALIDAD AL DETALLE DE LOS PRODUCTOS
            LinkExtractor(
                allow=r'/venta/'
            ), follow=True, callback='parse_items'),
    # Al entrar al detalle de los productos, se llama al callback con la respuesta al requerimiento
    )


    # FUNCIONES PARA EL PRE-PROCESADO DE LOS RESULTADOS:

    def quitarSimboloEuro(self, texto):
        nuevoTexto = texto.replace('€', '')
        nuevoTexto = \
            nuevoTexto.replace('\n', '').replace('\r', '').replace('\t', '').replace(':', '').strip()
        return nuevoTexto

    def quitarTabulaciones(self, texto):
        nuevoTexto = \
            texto.replace('\n', '').replace('\r', '').replace('\t', '').replace(':', '').replace(',',';').strip()
        return nuevoTexto

    def quitarSuperficie(self,texto):
        nuevoTexto =\
            texto.replace('\n', '').replace('\r', '').replace('\t', '').replace(':', '').replace(',',' ;').replace( 'm2','').replace( 'construidos','').strip()
        return nuevoTexto

    # FUNCION PARA EL PARSEO DE LAS PAGINA
    # LA EXTRACCION DE ELEMENTOS DE EFECTUA VIA XPATH
    # EL PREPROCESADO SE EFECTUA CON LAS FUNCIONES DE PREPROCESADO DEFINIDAS EN EL BLOQUE ANTERIOR
    # Y LA FUNCION MAPCOMPOSE DE LA LIBRERIA SCRAPY

    def parse_items(self, response):
        item = ItemLoader(Articulo(), response)

        # Utilizo Map Compose y funcionaes para pre-procesamiento.

        item.add_xpath('aProvincia', '//div[@class="col-md-6 col-sm-12 col-xs-12"][1]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))
        item.add_xpath('bCiudad', '//div[@class="col-md-6 col-sm-12 col-xs-12"][2]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))
        item.add_xpath('cDireccion', '//div[@class="col-md-6 col-sm-12 col-xs-12"][3]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))
        item.add_xpath('dCP', '//div[@class="col-md-6 col-sm-12 col-xs-12"][4]/text()[normalize-space()]',
                       MapCompose(self.quitarSimboloEuro))
        item.add_xpath('ePrecio', '//div[@class="col-md-6 col-sm-12 col-xs-12"][5]/text()[normalize-space()]',
                       MapCompose(self.quitarSimboloEuro))
        item.add_xpath('fTipologia', '//div[@class="col-md-6 col-sm-12 col-xs-12"][6]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))
        item.add_xpath('gSuperficie', '//div[@class="col-md-6 col-sm-12 col-xs-12"][7]/text()[normalize-space()]',
                       MapCompose(self.quitarSuperficie))
        item.add_xpath('hDormitorios', '//div[@class="col-md-6 col-sm-12 col-xs-12"][8]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))
        item.add_xpath('iSubtipo', '//div[@class="col-md-6 col-sm-12 col-xs-12"][9]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))
        item.add_xpath('jAnho_Const', '//div[@class="col-md-6 col-sm-12 col-xs-12"][10]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))

        item.add_xpath('lCategoria', '//div[@class="col-md-6 col-sm-12 col-xs-12"][11]/text()[normalize-space()]',
                       MapCompose(self.quitarTabulaciones))

        yield item.load_item()





# ###########
# EJECUCION #
# ###########
# Este script se ha diseñado para ejecutarlo directamente en  consola y envia los resultados ya preprocesados
# directamente al archivo csv que le especificamos

# Adjuntamos el comando a ejecutar.

#  scrapy runspider scrapy_tecnocasa.py -t csv -o scrapy_tecnocasa01.csv

