#coding:utf-8

"""
 EXPLICACION FUNCIONAMIENTO DEL SCRIPT:
 =======================================

 ESTE SCRIPT PARSEA LA PAGINA DE TECNOCASA MEDIANTE UNA EXTRACCION VERTICAL Y HORIZONTAL DE DATOS A UN NIVEL.

 EXTRACCION VERTICAL :
 ---------------------

 SE EFECTUA EXTRAYENDO LOS LINK DE LOS ARTICULOS/PROPIEDADES QUE ENCONTRAMOS EN EL LISTADO
 PRINCIPAL, CONCRETAMENTE  EN ELEMENTOS CON XPATH a[@class="immobileLink"] EXTRAEREMOS DICHOS ELEMENTOS, LOS ALMACENAMOS
 Y POSTERIORMENTE LOS ITERAREMOS PARA EXTRAER LA PAGINA CORRESPONDIENTE COMPLETA.

 UNA VEZ ACCEDEMOS A LA PROPIEDAD FINAL QUE DESEAMOS, EXTRAEREMOS LA INFORMACION DEL CONTENEDOR DIV EN EL QUE SE
 RECOGEN TODAS SUS CARACTERISTICAS Y VIA XPATH LAS EXTRAEMOS , ALMACENAMOS Y PREPROCESAMOS.


 EXTRACCION HORIZONTAL (PAGINACION):
 -----------------------------------
 UNA VEZ EFECTUADO EL SCRAPING VERTICAL DE LA PAGINA, TENEMOS QUE PASAR A LA SIGUIENTE.

 EN ESTA PAGINA WEB NO HAY BOTON "SIGUIENTE" POR LO QUE NO PODEMOS HACER CLICK EN EL MISMO.
 PARA AVANZAR PAGINA HE DESARROLLADO UN MECANISMO DIFERENTE.

 EN LA PARTE SUPERIOR IZQUIERDA DEL LISTADO DE INMUEBLES TENEMOS UNA LEYENDA QUE NOS INFORMA DEL NUMERO DE PROPIEDADES
 PARA EL AREA DESIGNADA, LA CUAL SE ENCUENTRA EN EL ARBOL HTML EN UN STRING.

 MEDIANTE UNA RUTA XPATH LA EXTRAEMOS DEL STRING  Y POSTERIORMENTE LOS DIGITOS QUE LO FORMAN.

 CADA PAGINA SE COMPONE DE 12 ANUNCIOS, ASI QUE EL TOTAL DE INMUEBLES SE DIVIDE ENTRE EL NUMERO DE ANUNCIOS Y OBTENEMOS.
 EL NUMERO DE PAGINAS A PARSEAR , PARA NO TENER PROBLEMAS CON EL REDONDEO LO AUMENTAREMOS EN UNA UNIDAD.

 EFECTUADO ESTO BUSCAMOS EL PATRON DE PAGINACION QUE EMPLEA LA PAGINA. OBSERVAMOS QUE ES LA PAGINA PRINCIPAL,
 AÑADIENDO '/PAG' MAS NUMERO DE PAGINA.

 MEDIANTE UN BUCLE GENERAREMOS TODAS LAS PAGINAS QUE DEBERA RECORRER EL SCRIPT AUTOMATICAMENTE, YA QUE INSISTIMOS,
 NO PODEMOS EMPLEAR EL BOTON CLICK SIGUIENTE.
 (NO ES LA SOLUCION OPTIMA PERO ES LA UNICA QUE SE HA PODIDO DESARROLLAREN EL TIEMPO ASIGNADO,
 TENIENDO EN CUENTA QUE ESTE SCRIPT ES MEJORA O UNA AMPLIACION DE LA PRE-ENTREGA).

 EL SCRIPT COMPRENDE DOS GRANDES BUCLES, EL EXTERNO DEDICADO A RECORRER HORIZONTALMENTE LA PAGINA , ESTO ES LA
 PAGINACION.

 EN SU INTEROR ENCONTRAREMOS, EL BUCLE INTERNO QUE ES EL QUE EFECTUA LA EXTRACCION VERTICAL,
 EL PRE-PROCESAMIENTO Y EL CONTROL POR CONSOLA DE TODO EL PROCESO DE DESCARGA.

 FINALMENTE MEDIANTE UN DICCIONARIO CARGAMOS TODOS LOS ELEMENTOS DE CADA REGISTRO EN UNA LISTA, LA CUAL
 VA RELLENANDO UN DATAFRAME DE PANDA.

 FINALMENTE ESTE DATAFRAME SE CONVIERTE EN UN ARCHIVO CSV.

CREADO POR DAVID DE VEGA MARTIN  PARA LA PEC 1 DE LA ASIGNATURA  TIPOLOGIA Y CICLO DE VIDA DE PRODUCTOS

SCRIPT DESARROLLADO  TRAS LA PRE-ENTREGA INICIAL COMO DESARROLLO

ULTIMA EDICION = 5 DE NOVIEMBRE DE 2021


"""


# 0.- CARGAMOS LAS LIBRERIAS NECESARIAS
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pandas as pd

# 0.- DEFINIMOS EL USER AGENT EN SELENIUM EMPLEANDO LA CLASE OPTIONS.
# ESTABLECEMOS URL SEMILLA.

opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/"
                  "71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36")

driver = webdriver.Chrome('C:/webdriver/chromedriver.exe', options=opts)

driver = webdriver.Chrome()

driver.get("https://www.tecnocasa.es/anuncios/piso/andalucia/malaga.html")

# 1.- EXTRACCION DEL NUMERO DE PAGINAS A PARSEAR.

total_inmuebles = \
    driver.find_element(By.XPATH,
                        '//div[@class="col-xs-12 col-sm-12 text-right"]/span[@class="pull-left raleway"]/div').text

for i in total_inmuebles.split():
    if i.isdigit():
        num_inmuebles =int(i)

max_page_num = (round(num_inmuebles /12))+1

print(" Numero de paginas a parsear:{}".format(max_page_num))


templist = [] # NOTA: CREAMOS LISTA QUE RECOGERA LOS REGISTROS ANTES DE AÑADIRLOS AL DF PANDA.



#  2.- BUCLE EXTERNO QUE CONTROLA LA PAGINACION

for i in range (1,max_page_num+1):
    if i==1:
        url = 'https://www.tecnocasa.es/anuncios/piso/andalucia/malaga.html'

    else:
        url = "https://www.tecnocasa.es/anuncios/piso/andalucia/malaga.html" +"/"+ "pag-"+ str(i)

        driver.get(url)

        # EXTRACCION DEL ARBOL HTML DE LOS LINK DE CADA UNA DE LAS PROPIEDADES A LA VENTA.

        links_productos = driver.find_elements(By.XPATH, '//a[@class="immobileLink"]')

        links_de_la_pagina = []

        for a_link in links_productos:
            links_de_la_pagina.append(a_link.get_attribute("href"))


        # BUCLE INTERNO PARA EXTRACCION VERTICAL DEL DETALLE DE CADA UNO DE LAS PROPIEDADES

        for link in links_de_la_pagina:
            try:

                # LA EXTRACCION SE EFECTUA VIA RUTA XPATH  DEL CONTENEDOR DIV QUE COMPONE LA FICHA DE LA PROPIEDAD
                # ALGUNOS ELEMENTOS APARECEN DUPLICADOS, ESTO ES PARA GARANTIZAR LA INTEGRIDAD DE LA INFORMACION.
                # ESTOS FORMULARIOS LOS COMPLETAN LOS FRANQUICIADOS Y LOS SUBEN A LA PAGINA PRINCIPAL DE LA EMPRESA
                # POR LO QUE EL FORMATO NO ES UNITARIO Y REQUERIRIA UN PREPROCESADO MAS COMPLEJO QUE EXCEDE LOS
                # PLANTEAMIENTOS DE ESTA PEC.
                # SE INCORPORA TODA LA INFORMACION POSIBLE, A FIN DE RECONSTRUIR ALREDEDOR DE UN 5-7 % DE REGISTROS
                # DEFICIENTES.

                driver.get(link)

                # <<<<<<<<<<<<<<<<<<<<<<<<<     EXTRACCION DETALLE DE PROPIEDADES     >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

                # DETALLE UBICACION INMUEBLE:

                ubicacion = driver.find_element(By.XPATH, '//h1').text
                provincia = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][1]').text
                ciudad = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][2]').text
                cp = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][3]').text

                # VALORACION INMUEBLE:

                precio = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][4]').text
                precio1 = driver.find_element(By.XPATH, '//span[@class="immobilePrezzo"]').text

                # SUPERFICIE Y DORMITORIOS.

                superficie = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][6]').text
                dormitorios= driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][7]').text

                # CLASIFICACION Y ANTIGUEDAD.

                subtipologia= driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][8]').text
                anho = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][9]').text
                categoria = driver.find_element(By.XPATH, '//div[@class="col-md-6 col-sm-12 col-xs-12"][10]').text

                # <<<<<<<<<<<<<<<<<<<<<<<<<   FIN EXTRACCION DETALLE DE PROPIEDADES     >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

                # <<<<<<<<<<<<<<<<<<<<<<<<<       PREPROCESADO  DE PROPIEDADES          >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

                ubicacion = (ubicacion.replace('\n', '').replace('\t', '').replace(':', '')
                             .replace(',',';').replace('Piso en venta en','').strip())

                provincia = (provincia.replace('\n', '').replace('\t', '').replace(':', '')
                             .replace('Provincia', '').strip())

                ciudad = (ciudad.replace('\n', '').replace('\t', '').replace(':', '')
                          .replace(',', ';').replace('Ciudad','').strip())

                cp = (cp.replace('\n', '').replace('\t', '').replace(':', '').replace(',', ';')
                      .replace('C.P.', '').strip())

                precio = (precio.replace('\n', '').replace('\t', '').replace('Precio','').replace('€','')
                          .replace(':', '').replace('C.P.','').strip())

                precio1 = (precio1.replace('\n', '').replace('\t', '').replace(':', '').replace('€','').strip())

                superficie = (superficie.replace('\n', '').replace('\t', '').replace(':', '').replace(',', ';')
                              .replace('Superficie', '').replace('construidos', '')
                              .replace('Tipologia Piso','').replace('m2', '').strip())

                dormitorios = (dormitorios.replace('\n', '').replace('\t', '').replace(':', '').replace(',',';')
                             .replace('Tipologia','').replace('Dormitorios','').replace('Superficie', '')
                             .replace('construidos', '').replace('m2', '').strip())

                subtipologia = (subtipologia.replace('\n', '').replace('\t', '').replace(':', '').replace(',',';')
                                .replace('Subtipología','').strip())

                anho = (anho.replace('\n', '').replace('\t', '').replace(':', '').replace(',',';')
                            .replace('Año de construcción','').replace('Subtipología','')
                            .replace('dormitorios','').replace('dormitorio','').strip())

                categoria = (categoria.replace('\n', '').replace('\t', '').replace(':', '').replace(',',';')
                             .replace('Categoría','').replace('Año de construcción','').strip())

                # <<<<<<<<<<<<<<<<<<<<<<<<<    FIN  PREPROCESADO  DE PROPIEDADES        >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

                # ALMACENAMIENTO DE LA EXTRACCION MEDIANTE DICCIONARIO QUE ALBERGA CADA REGISTRO/PROPIEDAD
                # LA TOTALIDAD DE LOS REGITROS FORMAN UN DATAFRAME PANDA QUE SE ALMACENA EN UN CSV

                # 1.- DICCIONARIO

                Table_dict = {"UBICACION": ubicacion, "PROVINCIA": provincia,"CIUDAD":ciudad,
                              "PRECIO": precio, "PRECIO1": precio1, "CP":cp,"SUPERFICIE": superficie,
                              "DORMITORIOS":dormitorios, "SUBTIPOLOGIA":subtipologia,
                              "AÑO CONST":anho, "CATEGORIA":categoria }

                # 2.- CARGA A DATAFRAME

                templist.append(Table_dict)
                df = pd.DataFrame(templist)

                # NOTA => CONTROL VISUAL POR CONSOLA DEL FLUJO DE EXTRACCION
                print("=======================")
                print("<<<      INICIO     >>>")
                print("=======================")
                print("\n")
                print(ubicacion)
                print(provincia)
                print(ciudad)
                print(precio)
                print(precio1)
                print(cp)
                print(superficie)
                print(dormitorios)
                print(subtipologia)
                print(anho)
                print(categoria)
                print("\n")
                print("<<<<      FIN     >>>>>>")
                print("\n\n")
            except Exception as e:
                print(e)

                # MECANISMO DE CONTROL = EN CASO DE ERROR EN LA EXTRACCION DE UN ARTICULO /PROPIEDAS, RETORNA
                # AUTOMATICAMENTE A LA PAGINA QUE SE ESTE PARSEANDO Y CONTINUA CON EL SIGUIENTE ELEMENTO.

                driver.back()

# ENVIO DEL DATAFRAME A UN ARCHIVO CSV Y CIERRE DEL SCRIPT.

df.to_csv('malaga.csv')

driver.close()

print (" <<<<<   <<<<<   PROCESO FINALIZADO.   >>>>>    >>>>>")









