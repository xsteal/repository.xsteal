#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2015 xsteal
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json,threading,xbmcvfs,cookielib,pprint
from bs4 import BeautifulSoup
from resources.lib import Downloader #Enen92 class
from resources.lib import Player
from t0mm0.common.net import Net
from resources.lib import URLResolverMedia



__ADDON_ID__   = xbmcaddon.Addon().getAddonInfo("id")
__ADDON__   = xbmcaddon.Addon(__ADDON_ID__)
__ADDON_FOLDER__    = __ADDON__.getAddonInfo('path')
__SETTING__ = xbmcaddon.Addon().getSetting
__ART_FOLDER__  = os.path.join(__ADDON_FOLDER__,'resources','img')
__FANART__      = os.path.join(__ADDON_FOLDER__,'fanart.jpg')

__PASTA_FILMES__ = xbmc.translatePath(__ADDON__.getSetting('bibliotecaFilmes'))
__PASTA_SERIES__ = xbmc.translatePath(__ADDON__.getSetting('bibliotecaSeries'))

__SKIN__ = 'v1'
__SITE__ = 'http://kodi.mrpiracy.xyz/'

__ALERTA__ = xbmcgui.Dialog().ok

__COOKIE_FILE__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.mrpiracy/'), 'cookie.mrpiracy')
__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'} #ISO-8859-1,


def menu():
    check_login = login()
    if check_login:
        addDir('Filmes', __SITE__+'kodi_filmes.php', 1, os.path.join(__ART_FOLDER__, __SKIN__, 'filmes.png'), 1)
        addDir('Series', __SITE__+'kodi_series.php', 1, os.path.join(__ART_FOLDER__, __SKIN__, 'series.png'), 1)
        addDir('Pesquisa', __SITE__, 6, os.path.join(__ART_FOLDER__, __SKIN__, 'procurar.png'), 1)
        addDir('', '', '', os.path.join(__ART_FOLDER__,'nada.png'), 0)
        addDir('Filmes por Ano', __SITE__+'kodi_filmes.php', 9, os.path.join(__ART_FOLDER__, __SKIN__, 'ano.png'), 1)
        addDir('Filmes por Genero', __SITE__+'kodi_filmes.php', 8, os.path.join(__ART_FOLDER__, __SKIN__, 'generos.png'), 1)
        addDir('Series por Ano', __SITE__+'kodi_series.php', 9, os.path.join(__ART_FOLDER__, __SKIN__, 'ano.png'), 1)
        addDir('Series por Genero', __SITE__+'kodi_series.php', 8, os.path.join(__ART_FOLDER__, __SKIN__, 'generos.png'), 1)
        addDir('A Minha Conta', 'url', 10, os.path.join(__ART_FOLDER__, __SKIN__, 'definicoes.png'), 0)
        addDir('Definições', 'url', 1000, os.path.join(__ART_FOLDER__, __SKIN__, 'definicoes.png'), 0)

        vista_menu()
    else:
        addDir('Alterar Definições', 'url', 1000, os.path.join(__ART_FOLDER__, __SKIN__, 'definicoes.png'), 0)
        addDir('Entrar novamente', 'url', None, os.path.join(__ART_FOLDER__, __SKIN__, 'retroceder.png'), 0)
        vista_menu()

def minhaConta():
    addDir('Favoritos', __SITE__+'favoritos.php', 11, os.path.join(__ART_FOLDER__, __SKIN__, 'favoritos.png'), 1)
    addDir('Agendados', __SITE__+'vermaistarde.php', 11, os.path.join(__ART_FOLDER__, __SKIN__, 'agendados.png'), 1)
    addDir('Últimos Filmes Vistos', __SITE__+'vistos.php', 11, os.path.join(__ART_FOLDER__, __SKIN__, 'ultimos.png'), 1)

    vista_menu()



def login():
    if __ADDON__.getSetting("email") == '' or __ADDON__.getSetting('password') == '':
        __ALERTA__('MrPiracy.xyz', 'Precisa de definir o seu email e password')
        return False
    else:
        try:

            net = Net()

            dados = {'email': __ADDON__.getSetting("email"), 'password': __ADDON__.getSetting("password"), 'lembrar_senha': 'lembrar'}
            
            codigo_fonte = net.http_POST(__SITE__+'login_bd.php',form_data=dados,headers=__HEADERS__).content.encode('utf-8')

            match = re.compile('class="myAccount">(.+?)<\/a>').findall(codigo_fonte)

           

        except:
            resultado = False
            __ALERTA__('MrPiracy.xyz', 'Não foi possível abrir a página. Por favor tente novamente')
            match = ''
            return resultado

        if match == []:
            match = re.compile('class="myAccount">(.+?)<\/a>').findall(codigo_fonte)

            if match == []:
                resultado = False
                __ALERTA__('MrPiracy.xyz', 'Email e/ou Password incorretos')
                return resultado
            else:
                resultado = True
                xbmc.executebuiltin("XBMC.Notification(MrPiracy.xyz, Sessão iniciada: "+__ADDON__.getSetting("email") +", '10000', "+__ADDON_FOLDER__+"/icon.png)")
                return resultado
        else:
            net.save_cookies(__COOKIE_FILE__)
            resultado = True
            xbmc.executebuiltin("XBMC.Notification(MrPiracy.xyz, Sessão iniciada: "+__ADDON__.getSetting("email") +", '10000', "+__ADDON_FOLDER__+"/icon.png)")
            return resultado

def getList(url, pagina):
    tipo = ''
    categoria = ''

    net = Net()
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    if 'kodi_filmes.php' in url:
        tipo = 'kodi_filmes'
    elif 'kodi_series.php' in url:
        tipo = 'kodi_series'
        
    if 'categoria=' in url:
        categoria = re.compile('categoria=(.+[0-9])').findall(url)[0]

    if tipo == 'kodi_filmes':
        #filmes pt
        #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
        #filmes pt com \n no plot
        #->match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte)
        #filmes com \n no plot
        #->match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte)
        #filmes normais
        #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
        
        #sem plot
        #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+').findall(codigo_fonte)
        #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+').findall(codigo_fonte)

        #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: inherit\;line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+)<\/span>').findall(codigo_fonte)
        match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: inherit\;line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+)<\/span>').findall(codigo_fonte)
        #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: inherit\;line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+)<\/span>').findall(codigo_fonte)
        match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: inherit\;line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+)<\/span>').findall(codigo_fonte)

    elif tipo == 'kodi_series':
        #series pt
        #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
        #series pt com \n no plot
        #->match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall('codigo_fonte')
        #series com \n no plot
        #->match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte)
        #series normais
        #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)

        #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+').findall(codigo_fonte)
        #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+').findall(codigo_fonte)
        
        match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
        #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Criador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte)

    #pprint.pprint(match)

    
    if tipo == 'kodi_filmes':

        for imagem, nome1, link, nome3, genero, ano, nomeOriginal, realizador, elenco, plot in match:
            try:
                
                infoLabels = {'Title': nomeOriginal.encode('utf8'), 'Year': ano, 'Genre': genero.encode('utf8'), 'Plot': plot }

                addVideo(nomeOriginal+' ('+ano+')', __SITE__+"kodi_"+link, 3, imagem, 'filme', 0, 0, infoLabels, imagem)
            except:
                pass
    else:
        for imagem, nome1, nome2, link, nome3, genero, ano, nomeOriginal, realizador, elenco, plot in match:
            try:
                infoLabels = {'Title':nomeOriginal.encode('utf8'), 'Aired':ano, 'Plot': plot}
                addDir(nomeOriginal+ ' ('+ano+')', __SITE__+"kodi_"+link, 4, imagem, pagina, 'serie', infoLabels, imagem)
            except:
                pass
            
    if categoria == '':
        addDir('Proximo', __SITE__+tipo+'.php?pagina='+str(int(pagina)+1), 1, os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'), int(pagina)+1)
    else:
        addDir('Proximo', __SITE__+tipo+'.php?pagina='+str(int(pagina)+1)+'&categoria='+categoria, 1, os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'), int(pagina)+1)

    vista_filmesSeries()

    
def getSeasons(url):
    net = Net()
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    #match = re.compile('<div class="season"><a href="(.+?)".+?>(.+?)<\/a><\/div>').findall(codigo_fonte)
    match = re.compile('<div class="season"><a href="(.+?)">(.+?)<\/a><\/div>').findall(codigo_fonte)
    match += re.compile('<div class="season"><a href="(.+?)" >(.+?)<\/a><\/div>').findall(codigo_fonte)


    for link, temporada in match:

        if '" class="slctd' in link:
            link = re.compile('(.+?)" class="slctd').findall(link)[0]

        addDirSeason("[B]Temporada[/B] "+temporada, __SITE__+"kodi_"+link, 5, os.path.join(__ART_FOLDER__, __SKIN__, 'temporadas', 'temporada'+temporada+'.png'), 1, temporada)

    vista_temporadas()

def getEpisodes(url):

    net = Net()
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    #match = re.compile('<div id="(.+?)" class="item">\s+<div class="thumb(.+?)">\s+<a href="(.+?)">\s+<img style="(.+?)" src="(.+?)" onError="this.onerror=null;this.src=\'(.+?)\';" alt="(.+?)">\s+<div class="thumb-shadow"><\/div>\s+<div class="visto" style="background-size: 110px;"><\/div>\s+<div class="thumb-effect"><\/div>\s+<div class="episode-number">(.+?)<\/div>').findall(codigo_fonte)
    #match = re.compile('<div id="(.+?)" class="item">\s+<div class="thumb(.+?)">\s+<a href="(.+?)">\s+<img style="(.+?)" src="(.+?)" onError="this.onerror=null;this.src=\'(.+?)\';" alt="(.+?)">\s+<div class="thumb-shadow"><\/div>\s+<div class="thumb-effect"><\/div>\s+<div class="episode-number">(.+?)<\/div>').findall(codigo_fonte)
    match = re.compile('<div id="(.+?)" class="item">\s+<div class="thumb(.+?)?">\s+<a name=\'.+?\' href="(.+?)">\s+<img style="(.+?)" src="(.+?)" onError="this\.onerror=null;this\.src=\'(.+?)\';"\s+alt="(.+?)?">\s+<div class="thumb-shadow" alt="(.+?)?"><\/div>\s+<div class="thumb-effect" alt="(.+?)?"><\/div>\s+<div class="episode-number">(.+?)<\/div>').findall(codigo_fonte)

    temporadaNumero = re.compile('<div\s+class="season"><a\s+href="(.+?)"\s+class="slctd">(.+?)<\/a>').findall(codigo_fonte)[0][1]
    actors = re.compile('<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>').findall(codigo_fonte)[0]
    try:
        plot = re.compile(u'Descrição:<\/span>(.+\s.+)<\/span>\s+<\/div>').findall(codigo_fonte)[0]
    except:
        plot = "-"

    criador = re.compile('<span class="director-caption">Criador: <\/span>\s+<span class="director">\s+(.+?)<\/span>').findall(codigo_fonte)[0]
    serieTitulo = re.compile('<span class="original-name">- "(.+?)"<\/span>').findall(codigo_fonte)[0]


    for lixo, lixo1, link, lixo2, imagem, imagemExterna, nome, nome1, nome2, episodioNumero in match:
        imdb = re.compile('imdb=(.+?)&').findall(link)[0]
        infoLabels = {'Title':nome, 'Actors':actors, 'Plot':plot, 'Season':temporadaNumero, 'Episode':episodioNumero, 'Writer': criador, "Code":imdb }
        
        if 'e' in episodioNumero:
            episodioNumeroReal = re.compile('(.+)e').findall(episodioNumero)[0]
        else:
            episodioNumeroReal = episodioNumero

        addVideo('[B]Episodio '+episodioNumero+'[/B] | '+nome, __SITE__+"kodi_"+link, 3, __SITE__+imagem, 'episodio', temporadaNumero, episodioNumeroReal, infoLabels, imagemExterna, serieTitulo)

    """arrow = re.compile('<div id="slide-right-arrow" class="right-arrow"><a href=\'(.+?)\'><\/a><\/div>').findall(codigo_fonte)

    if arrow != []:
        for more in arrow:
            getEpisodes(__SITE__+more)

    """

    vista_episodios()

def getStreamLegenda(match, siteBase, codigo_fonte):
    
    stream = ''
    legenda = ''

    net = Net()

    
    dialog = xbmcgui.Dialog()
    servidor = ''

    if match != []:

        servidores = re.compile('document\.getElementById\(\"banner-box box-header servidores\"\)\.innerHTML = \'(.+?)\'\;').findall(codigo_fonte)


        #pprint.pprint(servidores)

        
        #if len(match) == 1:
        servidor = dialog.select(u'Escolha o servidor', ['OpenLoad', 'VidZi', 'Antigo OpenLoad'])
        """elif len(match) == 2:
            servidor = dialog.select(u'Escolha o servidor', ['Servidor #1', 'Servidor #2', 'Servidor #3'])
        elif len(match) == 3:
            servidor = dialog.select(u'Escolha o servidor', ['Servidor #1', 'Servidor #2', 'Servidor #3'])
        elif len(match) == 4:
            servidor = dialog.select(u'Escolha o servidor', ['Servidor #1', 'Servidor #2', 'Servidor #3', 'Servidor #4', 'Servidor #5'])"""

        if servidor == 0:
            linkOpenload = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(codigo_fonte)[0]
            stream = URLResolverMedia.OpenLoad(linkOpenload).getMediaUrl()      
            legenda = URLResolverMedia.OpenLoad(linkOpenload).getSubtitle()
            
        elif servidor == 3:
            linkVideoMega = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(servidores[1])[0]
            stream = URLResolverMedia.VideoMega(linkVideoMega).getMediaUrl()
            linkOpenload = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(codigo_fonte)[0]
            legenda = URLResolverMedia.OpenLoad(linkOpenload).getSubtitle()
            
        elif servidor == 1:
            linkVidzi = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(servidores[2])[0]
            vidzi = URLResolverMedia.Vidzi(linkVidzi)
            stream = vidzi.getMediaUrl()
            #legenda = vidzi.getSubtitle()
            linkOpenload = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(codigo_fonte)[0]
            legenda = URLResolverMedia.OpenLoad(linkOpenload).getSubtitle()
        
        elif servidor == 2:
            linkOpenload = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(codigo_fonte)[0]
            stream = URLResolverMedia.OpenLoad(linkOpenload).getMediaUrlOld()      
            legenda = URLResolverMedia.OpenLoad(linkOpenload).getSubtitle()

    else:

        if 'serie' in siteBase:
            linkOpenload = re.compile('<iframe src="(.+?)" scrolling="no"').findall(codigo_fonte)[0]
        else:
            linkOpenload = re.compile('<iframe id="reprodutor" src="(.+?)" scrolling="no"').findall(codigo_fonte)[0]
        
        servidor = dialog.select(u'Escolha o servidor', ['OpenLoad', 'Antigo OpenLoad'])

        if servidor == 0:
            stream = URLResolverMedia.OpenLoad(linkOpenload).getMediaUrl()      
            legenda = URLResolverMedia.OpenLoad(linkOpenload).getSubtitle()
        elif servidor == 1:
            stream = URLResolverMedia.OpenLoad(linkOpenload).getMediaUrlOld()      
            legenda = URLResolverMedia.OpenLoad(linkOpenload).getSubtitle()
           


    return stream, legenda

def pesquisa():
    
    net = Net()
    net.set_cookies(__COOKIE_FILE__)

    dialog = xbmcgui.Dialog()
    server = dialog.select(u'Onde quer pesquisar?', ['Filmes', 'Series'])

    if server == 0:
        site = __SITE__+'kodi_procurarf.php'
    elif server == 1:
        site = __SITE__+'kodi_procurars.php'

    teclado = xbmc.Keyboard('', 'O que quer pesquisar?')
    teclado.doModal()

    if teclado.isConfirmed():
        strPesquisa = teclado.getText()
        dados = {'searchBox': strPesquisa}
        codigo_fonte = net.http_POST(site, form_data=dados, headers=__HEADERS__).content

        if server == 1:
            #series pt com \n no plot
            #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info" style="width\: 80\%\;">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Escritor:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte)
            #series pt
            #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Escritor:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
            #series com \n no plot
            #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info" style="width\: 80\%\;">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Escritor:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte)
            #series normais
            #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Escritor:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)

            match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info" style="width\: 80\%\;">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Escritor:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>').findall(codigo_fonte)
        elif server == 0:
            #filmes pt
            #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="movie-actions" style="display: none;">\s+<a id="watched" href="javascript\: movieUserAction\(\'movies\', 7339, \'watched\'\)\;" class="">Marcar como visto<span class="watch"><\/span><\/a><br>\s+<a id="cliped" href="javascript\: movieUserAction\(\'movies\', 7339, \'cliped\'\)\;" class="">Agendar para ver mais tarde<span class="clip"><\/span><\/a><br>\s+<a id="faved" href="javascript\: movieUserAction\(\'movies\', 7339, \'faved\'\)\;" class="">Adicionar este filme aos favoritos<span class="fave"><\/span><\/a>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
            #filmes pt com \n no plot
            #match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<div class="portugues"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info" style="width\: 80\%\;">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info" style="width\: initial\;">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+\s+.+)<\/span>').findall(codigo_fonte.encode('utf8'))
            #filmes com \n no plot
            #(<script>(.+\s+)+?<\/script>)?\s+<div class="movie-actions">\s+<div id=".+?"><a id="watched" style=".+?" onclick=".+?" class="watched ">.+?<span class=".+?"><\/span><\/a><\/div>\s+<div id=".+?"><a id="cliped" style=".+?" onclick=".+?" class="cliped ">.+?<span class="clip"><\/span><\/a><\/div>\s+<div id=".+?"><a id="faved" style="cursor:pointer" onclick=".+?" class="faved ">.+?<span class="fave"><\/span><\/a><\/div> <\/div>\s+
            #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info" style="width\: 80\%\;">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info" style="width\: initial\;">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)
            #filmes normais
            #match += re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<\/div>\s+<div class="movie-actions" style="display: none;">\s+<a id="watched" href="javascript\: movieUserAction\(\'movies\', 7339, \'watched\'\)\;" class="">Marcar como visto<span class="watch"><\/span><\/a><br>\s+<a id="cliped" href="javascript\: movieUserAction\(\'movies\', 7339, \'cliped\'\)\;" class="">Agendar para ver mais tarde<span class="clip"><\/span><\/a><br>\s+<a id="faved" href="javascript\: movieUserAction\(\'movies\', 7339, \'faved\'\)\;" class="">Adicionar este filme aos favoritos<span class="fave"><\/span><\/a>\s+<\/div>\s+<div class="clear"><\/div>\s+<br><div class="clear"><\/div>\s+<span id="movie-synopsis" class="movie-synopsis">(.+?)<\/span>').findall(codigo_fonte)

            match = re.compile('<img src="(.+?)" alt="(.+?)">\s+<div class="thumb-effect" title="(.+?)"><\/div>\s+<\/a>\s+<\/div>\s+<\/div>\s+<div class="movie-info" style="width\: 80\%\;">\s+<a href="(.+?)" class="movie-name">(.+?)<\/a>\s+<div class="clear"><\/div>\s+<div class="movie-detailed-info" style="width\: initial\;">\s+<div class="detailed-aux" style="height\: 20px\; line-height\: 20px\;">\s+<span class="genre">(.+?)<\/span>\s+<span class="year">\s+<span>\(<\/span>(.+?)<span>\)<\/span><\/span>\s+<span class="original-name">\s+-\s+"(.+?)"<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Realizador:\s+<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>\s+<div class="detailed-aux">\s+<span class="director-caption">Elenco:<\/span>\s+<span class="director">(.+?)<\/span>\s+<\/div>').findall(codigo_fonte)


        pprint.pprint(match)

        if match != []:

            for imagem, nome1, nome2, link, nome3, genero, ano, nomeOriginal, realizador, elenco in match:
                if server == 0:
                    try:
                        infoLabels = {'Title': nomeOriginal, 'Year': ano, 'Genre': genero, 'Plot': '-' }
                        addVideo(nomeOriginal+' ('+ano+')', __SITE__+"kodi_"+link, 3, imagem, 'filme', 0, 0, infoLabels, imagem)
                    except:
                        pass
                elif server == 1:
                    try:
                        infoLabels = {'Title':nomeOriginal, 'Aired':ano, 'Plot': '-'}
                        addDir(nomeOriginal+ ' ('+ano+')', __SITE__+"kodi_"+link, 4, imagem, pagina, 'serie', infoLabels, imagem)
                    except:
                        pass
        else:
            addDir('Voltar', 'url', None, os.path.join(__ART_FOLDER__, __SKIN__, 'retroceder.png'), 0)  

    vista_filmesSeries()        

def download(url,name):

    legendasOn = False

    if 'serie.php' in url:
        siteBase = 'serie.php'
    elif 'filme.php' in url:
        siteBase = 'filme.php'

    net = Net()
    net.set_cookies(__COOKIE_FILE__)
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    match = re.compile('<a class="btn" href="(.+?)"><img src="(.+?)"><\/a>').findall(codigo_fonte)

    stream, legenda = getStreamLegenda(match, siteBase, codigo_fonte)


    folder = xbmc.translatePath(__ADDON__.getSetting('pastaDownloads'))
    
    streamAux = clean(stream.split('/')[-1])
    extensaoStream = clean(streamAux.split('.')[1])
    name = name+'.'+extensaoStream


    if legenda != '':
        legendaAux = clean(legenda.split('/')[-1])
        extensaoLegenda = clean(legendaAux.split('.')[1])
        nomeLegenda = name+'.'+extensaoLegenda
        legendasOn = True

    Downloader.Downloader().download( os.path.join(folder,name), stream, name)

    if legendasOn:
        download_legendas(legenda, os.path.join(folder,nomeLegenda))

def download_legendas(url,path):
    contents = abrir_url(url)
    if contents:
        fh = open(path, 'w')
        fh.write(contents)
        fh.close()
    return

def getGeneros(url):
    net = Net()
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    #match = re.compile('<div id="item1" class="item">\s+<label for="genre1" id="genre1Label"><a style="font-family: Tahoma; color: #8D8D8D;font-size: 11px;padding-left: 5px;float: left;width: 142px;font-weight: normal;text-decoration: initial;" href="(.+?)">(.+?)<\/a><\/label>\s+<\/div>').findall(codigo_fonte)
    match = re.compile('<label for="genre1" id="genre1Label"><a style="font-family: Tahoma; color: #8D8D8D;font-size: 11px;padding-left: 5px;float: left;width: 142px;font-weight: normal;text-decoration: initial;" href="(.+?)">(.+?)<\/a><\/label>').findall(codigo_fonte)
    match += re.compile('<label for="genre1" id="genre1Label"><a style="font-family: Tahoma; color: #8D8D8D;font-size: 11px;padding-left: 5px;float: left;width: 142px;text-decoration: initial;" href="(.+?)">(.+?)<\/a><\/label>').findall(codigo_fonte)

    

    for link, nome in match:
        if 'kodi_filmes.php' in url:
            addDir(nome.encode('utf8'), __SITE__+"kodi_"+link, 1, os.path.join(__ART_FOLDER__, __SKIN__, 'generos.png'), 1)
        else:
            addDir(nome.encode('utf8'), url+link, 1, os.path.join(__ART_FOLDER__, __SKIN__, 'generos.png'), 1)

def getYears(url):
    net = Net()
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    match = re.compile('<label for="(.+?)" id="(.+?)"><a style=\'font-family: Tahoma; color: #8D8D8D;\' class="active" href="(.+?)">(.+?)<\/a><\/label>').findall(codigo_fonte)
    #match += re.compile('<div id="(.+?)" class="item">\s+<label for="(.+?)" id="(.+?)"><a style=\'font-family: Tahoma; color: #8D8D8D;\' class="active" href="(.+?)">(.+?)<\/a><\/label>\s+<\/div>').findall(codigo_fonte)
    
    for lixo1, lixo2, link, nome in match:
        addDir(nome.encode('utf-8'), url+link, 1, os.path.join(__ART_FOLDER__, __SKIN__, 'generos.png'), 1)

def getListOfMyAccount(url, pagina):
    net = Net()
    net.set_cookies(__COOKIE_FILE__)
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    match = re.compile('<div id="5" class="item">\s+<a href="(.+?)">\s+<img src="(.+?)" alt="(.+?)" title="(.+?)">').findall(codigo_fonte)

    if 'favoritos.php' in url:
        tipo = 'favoritos'
    elif 'vermaistarde.php' in url:
        tipo = 'vermaistarde'
    elif 'vistos.php' in url:
        tipo = 'vistos'

    for link, imagem, nome, nome1 in match:
        if 'filme.php' in link:
            infoLabels = {'Title': nome.encode('utf8') }
            addVideo(nome.encode('utf8'), __SITE__+"kodi_"+link, 3, imagem, 'filme', 0, 0, infoLabels, imagem)
        elif 'serie.php' in link:
            infoLabels = {'Title': nome.encode('utf8')}
            addDir(nome.encode('utf8'), __SITE__+"kodi_"+link, 4, imagem, pagina, 'serie', infoLabels, imagem)
            
    addDir('Proximo', __SITE__+'kodi_'+tipo+'.php?pagina='+str(int(pagina)+1), 11, os.path.join(__ART_FOLDER__, __SKIN__, 'proximo.png'), int(pagina)+1)

    vista_filmesSeries()


###################################################################################
#                              DEFININCOES                                        #
###################################################################################

def abrirDefinincoes():
    __ADDON__.openSettings()
    addDir('Entrar novamente','url',None,os.path.join(__ART_FOLDER__, __SKIN__,'retroceder.png'), 0)
    vista_menu()
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def vista_menu():
    opcao = __ADDON__.getSetting('menuView')
    if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51")

def vista_filmesSeries():
    opcao = __ADDON__.getSetting('filmesSeriesView')
    if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
    elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(501)")
    elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
    elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
    elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
    elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")
    

def vista_temporadas():
    opcao = __ADDON__.getSetting('temporadasView')
    if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def vista_episodios():
    opcao = __ADDON__.getSetting('episodiosView')
    if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
    elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
    elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")    

###################################################################################
#                               FUNCOES JA FEITAS                                 #
###################################################################################


def abrir_url(url,pesquisa=False):

    header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Connection': 'keep-alive'}

    if pesquisa:
        data = urllib.urlencode({'searchBox' : pesquisa})
        req = urllib2.Request(url,data, headers=header)
    else:
        req = urllib2.Request(url, headers=header)
    
    response = urllib2.urlopen(req)
    link=response.read()
    return link

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage,pagina,tipo=False,infoLabels=False,poster=False):
    if infoLabels: infoLabelsAux = infoLabels
    else: infoLabelsAux = {'Title': name}

    if poster: posterAux = poster
    else: posterAux = iconimage

    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True

    fanart = __FANART__

    if tipo == 'filme': 
        fanart = posterAux
        xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    elif tipo == 'serie':
        fanart = posterAux
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif tipo == 'episodio':
        fanart = posterAux
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    else: 
        xbmcplugin.setContent(int(sys.argv[1]), 'Movies')


    liz=xbmcgui.ListItem(name, iconImage=posterAux, thumbnailImage=posterAux)
    liz.setProperty('fanart_image', fanart)
    liz.setInfo( type="Video", infoLabels=infoLabelsAux )

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addFolder(name,url,mode,iconimage,folder):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', iconimage)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
    return ok

def addDirSeason(name,url,mode,iconimage,pagina,temporada):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&temporada="+str(temporada)
    ok=True
    xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', __FANART__)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addVideo(name,url,mode,iconimage,tipo,temporada,episodio,infoLabels,poster,serieNome=''):
    

    if tipo == 'filme': 
        xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
    elif tipo == 'serie':
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif tipo == 'episodio':
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')


    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&temporada="+str(temporada)+"&episodio="+str(episodio)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&serieNome="+urllib.quote_plus(serieNome)
    ok=True
    #contextMenuItems = []
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setProperty('fanart_image', poster)
    liz.setInfo( type="Video", infoLabels=infoLabels )
    #contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=7&name=%s&url=%s&iconimage=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage))))
    #liz.addContextMenuItems(contextMenuItems, replaceItems=False)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok

def clean(text):
    command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
    regex = re.compile("|".join(map(re.escape, command.keys())))
    return regex.sub(lambda mo: command[mo.group(0)], text)

def player(name,url,iconimage,temporada,episodio,serieNome=''):

    pastaData = ''
    
    if temporada == 0 and episodio == 0:
        pastaData = __PASTA_FILMES__
        idIMDb = re.compile('imdb=(.+)').findall(url)[0]
        ano = str(re.compile('\((.+?)\)').findall(name)[0])
        siteBase = 'filme.php'
    else:
        pastaData = __PASTA_SERIES__
        ano = 2000
        idIMDb = re.compile('imdb=(.+?)&').findall(url)[0]
        siteBase = 'serie.php'

    mensagemprogresso = xbmcgui.DialogProgress()
    mensagemprogresso.create('MrPiracy.xyz', u'Abrir emissão','Por favor aguarde...')

    mensagemprogresso.update(25, "", u'Obter video e legenda', "")

    net = Net()
    net.set_cookies(__COOKIE_FILE__)
    codigo_fonte = net.http_GET(url, headers=__HEADERS__).content

    match = re.compile('<a id="(.+?)" class="btn(.+?)?" onclick=".+?"><img src="(.+?)"><\/a>').findall(codigo_fonte)

    stream, legenda = getStreamLegenda(match, siteBase, codigo_fonte)

    print "STREAM    &&&     LEGENDA"
    print stream
    print legenda

    mensagemprogresso.update(50, "", u'Prepara-te, vai começar!', "")
    
    playlist = xbmc.PlayList(1)
    playlist.clear()
    listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    listitem.setInfo("Video", {"title":name})
    listitem.setProperty('mimetype', 'video/x-msvideo')
    listitem.setProperty('IsPlayable', 'true')

    playlist.add(stream, listitem)
    
    xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
    
    mensagemprogresso.update(75, "", u'Boa Sessão!!!', "")
    print "url: "+url+" idIMDb: "+idIMDb+" pastaData: "+pastaData+"\n temporada: "+str(temporada)+" episodio: "+str(episodio)+" \nnome: "+name+" ano:"+str(ano)+"\nstream: "+stream+" legenda: "+legenda 

    if stream == False:
        __ALERTA__('MrPiracy.xyz', 'O servidor escolhido não disponível, escolha outro ou tente novamente mais tarde.')
    else:
        player = Player.Player(url=url, idFilme=idIMDb, pastaData=pastaData, temporada=temporada, episodio=episodio, nome=name, ano=ano, logo=os.path.join(__ADDON_FOLDER__,'icon.png'), serieNome=serieNome)
        mensagemprogresso.close()
        player.play(playlist)
        player.setSubtitles(legenda)

        while player.playing:
            xbmc.sleep(5000)
            player.trackerTempo()


########################################################################################################
#                                               GET PARAMS                                                 #
############################################################################################################

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
    return param


params=get_params()
url=None
name=None
mode=None
iconimage=None
link=None
legenda=None
pagina=None
temporada=None
episodio=None

try: url=urllib.unquote_plus(params["url"])
except: pass
try: link=urllib.unquote_plus(params["link"])
except: pass
try: legenda=urllib.unquote_plus(params["legenda"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: temporada=int(params["temporada"])
except: pass
try: episodio=int(params["episodio"])
except: pass
try: mode=int(params["mode"])
except: pass
try: pagina=int(params["pagina"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
except: pass
try : serieNome=urllib.unquote_plus(params["serieNome"])
except: pass


print "Mode: "+str(mode)
print "URL: "+str(url)
print "LINK. "+str(link)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)
print "PAGINA: "+str(pagina)

###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################
if mode==None or url==None or len(url)<1: menu()
elif mode==1: getList(url, pagina)
elif mode==2: getSeries(url, pagina)
elif mode==3: player(name, url, iconimage, temporada, episodio, serieNome)
elif mode==4: getSeasons(url)
elif mode==5: getEpisodes(url)
elif mode==6: pesquisa()
elif mode==7: download(url, name)
elif mode==8: getGeneros(url)
elif mode==9: getYears(url)
elif mode==10: minhaConta()
elif mode==11: getListOfMyAccount(url, pagina)
elif mode==666: comunicado()
elif mode==1000: abrirDefinincoes()
xbmcplugin.endOfDirectory(int(sys.argv[1]))