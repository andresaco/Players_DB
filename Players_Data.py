from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import requests
import html5lib
from bs4 import BeautifulSoup as bs

import os
from pprint import pprint as pp

from collections import OrderedDict as OrdDict
import time


# Paginas a investigar
#  https://www.laliga.es/
#  https://es.besoccer.com/
#  https://www.fifaindex.com


class Conexion_by_browser(object):

    def __init__(self):
        self.ruta = os.getcwd()
        self.rutaDrivers = self.ruta + '/Drivers/geckodriver'
        self.rutaDrivers = self.ruta + '/Drivers/chromedriver'
        self.browser = webdriver
        self.Chrome()

    def Firefox(self):
        self.browser = self.browser.Firefox(executable_path=self.rutaDrivers)
        return self.browser

    def Chrome(self):
        print('Estableciendo conexion y abriendo el navegador... \n')
        self.options = self.browser.ChromeOptions()
        self.options.add_argument("headless")
        self.browser = self.browser.Chrome(executable_path=self.rutaDrivers, chrome_options=self.options)
        self.browser.maximize_window()

        return self.browser

    def Navegar_web(self,page,format='html'):
        print ('Conectando con ....  -->   ' + page + '\n')
        self.browser.get(page)
        # self.browser.close()
        if format == 'html':
            self.html = self.browser.page_source
            return bs(self.html,"html.parser")
        elif format == 'web':
            return self.browser

class Conexion_to_server(object):

    def __init__(self):
        print ('Estableciendo conexion con el servidor...\n')


    def Parseo_web(self,page):
        print('Conectando con ....  -->' + page +'\n')
        self.s = requests.Session()
        self.html = self.s.get(page).text
        self.s.close()

        return bs(self.html,"html.parser")




class Plantillas(Conexion_by_browser,Conexion_to_server):

    def __init__(self):
        self.url_plantillas = 'https://www.laliga.es/laliga-santander'
        self.url_skills = 'https://www.fifaindex.com'
        ##### By Server
        self.html = self.Parseo_web(self.url_plantillas)
        ##### By Browser
        Conexion_by_browser.__init__(self)
        # self.html = self.Navegar_web(self.url_plantillas)

        ### Atributos y variables
        self.equipos={}


    def page_skills(self,Name_full,Name_short,team):

        self.nombre = Name_full.replace(' ','+')
        self.url_player = 'https://www.fifaindex.com/players/?name=' + self.nombre
        self.html = self.Parseo_web(self.url_player)
        self._pos_jug_table = self.html.find_all('table', attrs={'class': 'table table-striped table-players'})[0]
        self._pos_jug_table = self._pos_jug_table.find_all('tbody')

        self.NoResults = 'There are no results'
        if len(self._pos_jug_table) == 1 and self.NoResults in self._pos_jug_table[0].text:
            self.nombre = Name_short.replace(' ', '+')
            self.url_player = 'https://www.fifaindex.com/players/?name=' + self.nombre
            self.html = self.Parseo_web(self.url_player)
            self._pos_jug_table = self.html.find_all('table', attrs={'class': 'table table-striped table-players'})[0]
            self._pos_jug_table = self._pos_jug_table.find_all('tbody')

        if len(self._pos_jug_table)==1 and self.NoResults not in self._pos_jug_table[0].text:
            self._jug = self._pos_jug_table[0].find_all('tr')[0]
            self._url_player = self._jug.find_all('td', attrs={'data-title': 'Name'})[0]
            self.url_player = self._url_player.find_all('a')[0].get('href')
        else:
            for _jug in self._pos_jug_table[0].find_all('tr'):
                self._team =_jug.find_all('td',attrs={'data-title':'Team'})[0]
                self.team = self._team.find_all('img')[0].get('title')
                if team == self.team:
                    self._url_player = _jug.find_all('td',attrs={'data-title':'Name'})[0]
                    self.url_player = self._url_player.find_all('a')[0].get('href')
                    pp(self.url_player)
                    break


        self.html = self.Parseo_web(self.url_skills + self.url_player)

        return self.html


    def get_equipos(self):

        ## Accedemos a la pagina de la LFP y obtenemos los equipos con sus correspondientes
        ## links para acceder a cada una de las plantillas
        self.tabla_teams = self.html.find_all('div', attrs={'id':'equipos'})[0].find_all('div')

        for elem in self.tabla_teams:
            for team in elem:
                self.equipos[team.text] = {'link': team.get('href'),'Jugadores':{}}


    def exe(self):
        self.get_equipos()

        for team in self.equipos:
            self.enlace = self.equipos.get(team).get('link')
            self.html = self.Parseo_web(self.enlace)
            ### Accedemos a las cajas ('box') de los jugadores.
            self._box = self.html.find_all('div',attrs={'id':'plantilla'})[0].find_all('a',attrs={'class':'box-jugador'})

            for jug in self._box:
                ########## Parseamos la pagina del jugador
                self.jug_enlace = jug.get('href')
                # self.jug_enlace = 'https://www.laliga.es/jugador/messi'
                # self.html = self.Parseo_web(self.jug_enlace)
                self.html = self.Navegar_web(self.jug_enlace)
                self.jug_perfil = self.html.find_all('div',attrs={'id':'datos-perfil'})[0].find_all('div')

                ##### Obtenemos los datos generales del jugador
                self.Datos_jugador = {}
                for param in self.jug_perfil:
                    self.Datos_jugador[param.get('id')] = param.text



                self.informacion_jug = self.html.find_all('div',attrs={'class':'box-dato'})

                for info in self.informacion_jug[:-1]:
                    if not info.find_all('div', attrs={'class','nombre'}):
                        self._dato = info.find_all('h2', attrs={'class','nombre'})[0].text
                    else:
                        self._dato = info.find_all('div', attrs={'class', 'nombre'})[0].text
                    self._valor = info.find_all('div', attrs={'class','dato'})[0].text

                    self.Datos_jugador[self._dato] = self._valor

                self.Nombre_short = self.html.find_all('h1', attrs={'id': 'nickname'})[0].text
                self.Datos_jugador['nick'] = self.Nombre_short
                self.Nombre_full  = self.Datos_jugador.get('nombre')



                ##### Estadisticas del jugador
                self.Estadisticas_jugador={}

                # sacamos las cabeceras de las tablas
                self._box_est = self.html.find_all('section',attrs={'id':'box-estadisticas-jugador'})[0]
                self._cabeceras = self._box_est.find_all('nav',attrs={'class':'cabecera-seccion-2 submenu'})[0].find_all('ul')
                self._cabeceras_url = [cab.get('href') for cab in self._cabeceras[0].find_all('a')]
                self._cabeceras_text = [cab.text.strip() for cab in self._cabeceras[0].find_all('a')]

                #
                # pp(self._cabeceras_text)

                for cab_text,cab_url in zip(self._cabeceras_text,self._cabeceras_url):
                    self.html = self.Parseo_web(cab_url)
                    self._box_est = self.html.find_all('section', attrs={'id': 'box-estadisticas-jugador'})[0]

                    self._tablas = self._box_est.find_all('table')
                    # pp(len(self._tablas))

                    self.data = {}
                    for tabla in self._tablas:
                        # pp(tabla)
                        self._params_init = tabla.find_all('tr')

                        self._params=[]
                        for row in self._params_init:
                            if not row.get('class'):
                                self._params.append(row)
                                continue
                            if row.get('class')[0].find('mostrar_movil') == -1:
                                self._params.append(row)

                        self._caract = self._params[0]
                        self._vals = self._params[1:]


                        self.caracts = [caract.get('title') for caract in self._caract.find_all('th') ][1:]


                        for row in self._vals:
                            self._v = [ vals.text for vals in row]
                            self.data[self._v[0]]=self._v[1:]

                        self.Estadisticas_jugador[cab_text] = {'Params':self.caracts, 'Values':self.data}


                        # pp(self.Estadisticas_jugador)
                        # break


                ##### Caracteristicas del jugador
                self.Caracteristicas_jugador = {}

                # self.html = self.Navegar_web(self.url_skills,'web')
                # self._player_name = self.html.find_element_by_id('id_name')
                # self._player_name.send_keys(self.Nombre_short)
                # self.Search_boton = '/html/body/main/div/div[2]/div[1]/form/div[13]/div/button[2]'
                # self.boton = self.html.find_element_by_xpath(self.Search_boton).click()
                # self.html = bs(self.html.page_source,"html.parser")



                # Buscamos al jugador en las opciones que dan

                self.html = self.page_skills(self.Nombre_full,self.Nombre_short,team)







                # pp(self.html)






                ##############
                self.equipos[team]['Jugadores'][self.Nombre_full] = \
                    {'Info_general': self.Datos_jugador,
                     'Estadisticas': self.Estadisticas_jugador,
                     'Caracteristicas' : self.Caracteristicas_jugador}
                ##############
                # pp(self.equipos)

                break






                ######




                # pp(self.equipos)








            break






        # print (self.equipos)









if __name__ == "__main__":

    html = Plantillas().exe()
    # print (html)

