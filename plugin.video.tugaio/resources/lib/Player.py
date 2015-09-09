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

#enen92 class (RatoTv) adapted for Tuga.io addon

class Player(xbmc.Player):
    def __init__(self, url, idFilme, pastaData, temporada, episodio, nome, ano, logo):
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

        if not xbmcvfs.exists(os.path.join(pastaData,'tracker')):
            xbmcvfs.mkdirs(os.path.join(pastaData,'tracker'))


        if self.temporada != 0 and self.episodio != 0:
            self.pastaVideo = os.path.join(self.pastaData,'tracker',str(self.idFilme)+'S'+str(self.temporada)+'x'+str(self.episodio)+'.tugaio')
        else:
            self.pastaVideo = os.path.join(self.pastaData,'tracker',str(self.idFilme)+'.tugaio')

       

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

            dialog = xbmcgui.Dialog().yesno('Tuga.io', u'Já começaste a ver antes.', 'Continuas a partir de %s?' % (tempoAux), '', 'Não', 'Sim')
            if dialog:
                self.seekTime(float(tempo))

        

    def onPlayBackStopped(self):
        print 'player Stop'
        self.playing = False
        tempo = int(self.tempo)
        print 'self.time/self.totalTime='+str(self.tempo/self.tempoTotal)
        if (self.tempo/self.tempoTotal > 0.90):

            self.adicionarVistoBiblioteca()

            try:
                xbmcvfs.delete(self.pastaVideo)
            except:
                print "Não apagou"
                pass

            
            

    def onPlayBackEnded(self):
        self.onPlayBackStopped()

    def adicionarVistoBiblioteca(self):
        pastaVisto=os.path.join(self.pastaData,'vistos')
        
        try: 
            os.makedirs(pastaVisto)
        except: 
            pass

        if int(self.temporada) != 0 and int(self.episodio) != 0:
            ficheiro = os.path.join(pastaVisto, str(self.idFilme)+'S'+str(self.temporada)+'x'+str(self.episodio)+'.tugaio')
        else:
            ficheiro = os.path.join(pastaVisto, str(self.idFilme)+'.tugaio')

        if not os.path.exists(ficheiro):
            f = open(ficheiro, 'w')
            f.write('')
            f.close()

            try:

                if int(self.temporada) != 0 and int(self.episodio) != 0:
                    print "\n\n\n\n\n ADICIONAR SERIE \n\n\n\n\n"
                    if xbmc.getCondVisibility('Library.HasContent(TVShows)'):
                        print "\n\n\n\n\n ADICIONAR SERIE DEPOIS \n\n\n\n\n"
                        dados = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "season", "operator": "is", "value": "%s"}, {"field": "episode", "operator": "is", "value": "%s"}]}, "properties": ["title", "plot", "votes", "rating", "writer", "firstaired", "playcount", "runtime", "director", "productioncode", "season", "episode", "originaltitle", "showtitle", "lastplayed", "fanart", "thumbnail", "file", "resume", "tvshowid", "dateadded", "uniqueid"]}, "id": 1}' % (self.temporada, self.episodio))
                        dados = unicode(dados, 'utf-8', erros='ignore')
                        dados = json.loads(dados)
                        dados = dados['result']['episodes']
                        dados = [i for i in dados if titulo in i['file']][0]
                        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetEpisodeDetails", "params": {"episodeid" : %s, "playcount" : 1 }, "id": 1 }' % str(dados['episodeid']))
                else:
                    print "\n\n\n\n\n ADICIONAR FILMES \n\n\n\n\n"
                    if xbmc.getCondVisibility('Library.HasContent(Movies)'):
                        print "\n\n\n\n\n ADICIONAR FILMES DEPOIS \n\n\n\n\n"
                        dados = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["file"]}, "id": 1}' % (self.ano, str(int(self.ano)+1), str(int(self.ano)-1)))
                        dados = unicode(dados, 'utf-8', errors='ignore')
                        dados = json.loads(dados)
                        dados = dados['result']['movies']
                        dados = [i for i in dados if titulo in i['file']][0]
                        xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(dados['movieid']))
            except:
                pass

            xbmc.executebuiltin("XBMC.Notification(Tuga.io,"+"Marcado como visto"+","+"6000"+","+ self.logo+")")
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
