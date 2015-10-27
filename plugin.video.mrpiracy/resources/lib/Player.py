#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import xbmcgui
import xbmc
import xbmcvfs
import time
import urllib
import urllib2
import re
import sys 
import traceback
import json
from t0mm0.common.net import Net

__SITE__ = 'http://www.mrpiracy.xyz/'
__COOKIE_FILE__ = os.path.join(xbmc.translatePath('special://userdata/addon_data/plugin.video.mrpiracy/').decode('utf-8'), 'cookie.mrpiracy')
__HEADERS__ = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}


#enen92 class (RatoTv) adapted for MrPiracy.xyz addon

class Player(xbmc.Player):
    def __init__(self, url, idFilme, pastaData, temporada, episodio, nome, ano, logo, serieNome):
        xbmc.Player.__init__(self)
        self.url=url
        self.temporada=temporada
        self.episodio=episodio
        self.playing = True
        self.tempo = 0
        self.tempoTotal = 0
        self.idFilme = idFilme
        self.pastaData = xbmc.translatePath(pastaData)
        self.nome = nome
        self.ano = ano
        self.logo = logo
        self.serieNome = serieNome

        if not xbmcvfs.exists(os.path.join(pastaData,'tracker')):
            xbmcvfs.mkdirs(os.path.join(pastaData,'tracker'))


        if self.temporada != 0 and self.episodio != 0:
            self.pastaVideo = os.path.join(self.pastaData,'tracker',str(self.idFilme)+'S'+str(self.temporada)+'x'+str(self.episodio)+'.mrpiracy')
            self.content = 'episode'
        else:
            self.pastaVideo = os.path.join(self.pastaData,'tracker',str(self.idFilme)+'.mrpiracy')
            self.content = 'movie'

       

    def onPlayBackStarted(self):
        print '=======> player Start'
        self.tempoTotal = self.getTotalTime()
        print '==========> total time'+str(self.tempoTotal)

        if xbmcvfs.exists(self.pastaVideo):
            print "Ja existe um ficheiro do filme"

            f = open(self.pastaVideo, "r")
            tempo = f.read()
            tempoAux = ''
            minutos,segundos = divmod(float(tempo), 60)
            if minutos > 60:
                horas,minutos = divmod(minutos, 60)
                tempoAux = "%02d:%02d:%02d" % (horas, minutos, segundos)
            else:
                tempoAux = "%02d:%02d" % (minutos, segundos)

            dialog = xbmcgui.Dialog().yesno('MrPiracy.xyz', u'Já começaste a ver antes.', 'Continuas a partir de %s?' % (tempoAux), '', 'Não', 'Sim')
            if dialog:
                self.seekTime(float(tempo))

        

    def onPlayBackStopped(self):
        print 'player Stop'
        self.playing = False
        tempo = int(self.tempo)
        print 'self.time/self.totalTime='+str(self.tempo/self.tempoTotal)
        if (self.tempo/self.tempoTotal > 0.90):

            self.adicionarVistoBiblioteca()
            self.adicionarVistoSite()

            try:
                xbmcvfs.delete(self.pastaVideo)
            except:
                print "Não apagou"
                pass

    def adicionarVistoSite(self):

        net = Net()
        net.set_cookies(__COOKIE_FILE__)

        codigo_fonte = net.http_GET(self.url, headers=__HEADERS__).content

        if self.content == 'movie':
            visto = re.compile('<a id="watched" href="(.+?)" class="watched ">Marcar como visto<span class="watch"><\/span><\/a>').findall(codigo_fonte)[0]
        elif self.content == 'episode':
            visto = re.compile('<div class="episode-actions">\s+<a href="(.+?)" class="marcar">Marcar como visto<\/a><a').findall(codigo_fonte)[0]

        print "VISTO"
        print visto

        if visto != '':
            marcar = net.http_GET(__SITE__+visto, headers=__HEADERS__).content

        


    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def adicionarVistoBiblioteca(self):
        pastaVisto=os.path.join(self.pastaData,'vistos')
        
        try: 
            os.makedirs(pastaVisto)
        except: 
            pass

        if int(self.temporada) != 0 and int(self.episodio) != 0:
            ficheiro = os.path.join(pastaVisto, str(self.idFilme)+'S'+str(self.temporada)+'x'+str(self.episodio)+'.mrpiracy')
        else:
            ficheiro = os.path.join(pastaVisto, str(self.idFilme)+'.mrpiracy')

        if not os.path.exists(ficheiro):
            f = open(ficheiro, 'w')
            f.write('')
            f.close()

            try:

                if int(self.temporada) != 0 and int(self.episodio) != 0:
                
                    #if xbmc.getCondVisibility('Library.HasContent(TVShows)'):
                    print "Check if tvshow episode exists in library when marking as watched\n\n"
                    titulo = re.sub('[^-a-zA-Z0-9_.()\\\/ ]+', '',  self.nome)
                    dados = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["imdbnumber", "title", "year"]}, "id": 1}' % (self.temporada, self.episodio))
                    dados = unicode(dados, 'utf-8', erros='ignore')
                    dados = json.loads(dados)
                    dados = dados['result']['episodes']
                    dados = [i for i in dados if titulo in i['file']][0]
                    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(dados['episodeid']))
                    
                    """metaget = metahandlers.MetaData(preparezip=False)
                    metaget.get_meta('tvshow', self.serieNome, imdb_id=self.idFilme)
                    metaget.get_episode_meta(self.serieNome, self.idFilme, self.temporada, self.episodio)
                    metaget.change_watched(self.content, '', self.idFilme, season=self.temporada, episode=self.episodio, year='', watched=7)"""
                else:

                    #if xbmc.getCondVisibility('Library.HasContent(Movies)'):
                    print "Check if movie exists in library when marking as watched\n\n" 
                    titulo = re.sub('[^-a-zA-Z0-9_.()\\\/ ]+', '',  self.nome)
                
                    dados = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["imdbnumber", "originaltitle", "year"]}, "id": 1}' % (self.ano, str(int(self.ano)+1), str(int(self.ano)-1)))
                    dados = unicode(dados, 'utf-8', errors='ignore')
                    dados = json.loads(dados)
                    print dados
                    dados = dados['result']['movies']
                    print dados
                    dados = [i for i in dados if self.idFilme in i['file']][0]
                    xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(dados['movieid']))

                    """metaget = metahandlers.MetaData(preparezip=False)
                    metaget.get_meta('movie', self.nome ,year=self.ano)
                    metaget.change_watched(self.content, '', self.idFilme, season='', episode='', year='', watched=7)"""
            except:
                pass

            xbmc.executebuiltin("XBMC.Notification(MrPiracy.xyz,"+"Marcado como visto"+","+"6000"+","+ self.logo+")")
            xbmc.executebuiltin("XBMC.Container.Refresh")

        else:
            print "Já foi colocado antes"

    def trackerTempo(self):
        try:
            self.tempo = self.getTime()
            f = open(self.pastaVideo, mode="w")
            f.write(str(self.tempo))
            f.close()
        except:
            traceback.print_exc()
            print "Não gravou o conteudo em %s" % self.pastaVideo
