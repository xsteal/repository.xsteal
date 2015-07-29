#!/usr/bin/python

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc
from bs4 import BeautifulSoup

addon_id    = xbmcaddon.Addon().getAddonInfo("id")
selfAddon	= xbmcaddon.Addon(addon_id)
addonfolder	= selfAddon.getAddonInfo('path')
getSetting	= xbmcaddon.Addon().getSetting
artfolder	= addonfolder + '/resources/img/'
fanart 		= addonfolder + 'fundo.png'

site = 'http://tuga.io/'
sitekids = 'http://kids.tuga.io/'

def categorias():
	if getSetting("pref_site") == 'Geral' or getSetting("pref_site") == 'Ambos':
		addDir('Filmes', site, 1, artfolder+'filmes.png', 0)
		addDir('Series', site, 2, artfolder+'series.png', 0)
		addDir('Pesquisa', site, 6, artfolder+'pesquisa.png', 0)
		addDir('', '', '', artfolder+'nada.png', 0)
	if getSetting("pref_site") == 'Kids' or getSetting("pref_site") == 'Ambos':
		addDir('Filmes KIDS', sitekids, 1, artfolder+'filmes_kids.png', 0)
		addDir('Pesquisa KIDS', sitekids, 6, artfolder+'pesquisa_kids.png', 0)
	xbmc.executebuiltin("Container.SetViewMode(50)")

def getFilmes(url, pagina):

	siteAux = ''

	if 'kids.' in url: siteAux = sitekids
	else: siteAux = site
	
	mensagemprogresso = xbmcgui.DialogProgress()
	mensagemprogresso.create('Tuga.io', 'A abrir lista de filmes','Por favor aguarde...')

	i=1
	mensagemprogresso.update(i)

	codigo_fonte_listaFilmes=abrir_url(url+'filmes')
	match_filmes=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(codigo_fonte_listaFilmes)

	tamanhoArray = len(match_filmes)+0.0

	for link,imagem,nome,ano,imdb in match_filmes:
		percentagem = int((i/tamanhoArray)*100)
		link = link[1:]
		codigo_fonte=abrir_url(siteAux+link)
		#match=re.compile('jwplayer\(\'player_get_hard\'\).setup\(\{\n                            file: \'(.+?)\',\n                            aspectratio: \'.+?\',\n                            width: \'.+?\',\n                            height: \'.+?\',\n                            skin: \'.+?\',\n                            primary: ".+?",\n                            androidhls:.+?,\n                            logo : \{\n                                file: ".+?",\n                                link: ".+?",\n                                hide: .+?\n                            \},\n                            tracks:\n                                    \[\n                                        \{\n                                            file: "(.+?)",\n                                            default: ".+?"\n                                        \}\n                                    \],\n                            captions: \{\n                                backgroundOpacity: .+?                            \}\n\n                        \}\);').findall(codigo_fonte)
		getStream=re.compile('file: \'(.+?)\'').findall(codigo_fonte) 
		getLegenda=re.compile('file: \"(.+?)\"').findall(codigo_fonte)
		stream = ''
		legenda = ''
		mensagemprogresso.update(percentagem, "", nome, "")
		for streamAux in getStream: stream = streamAux
		for legendaAux in getLegenda: legenda = legendaAux 
		addVideo(nome + ' ('+ano+')', stream, 3, siteAux+imagem, siteAux+legenda)
		if mensagemprogresso.iscanceled(): break
		i+=1
		
	if pagina==0:
		match_prox=re.compile('<a href=\"(.+?)\" class=\"r\">Pr').findall(codigo_fonte_listaFilmes)
		pagina+=1
		for proximo in match_prox:
			proximo = proximo[1:]
			addDir('Proximo >>', siteAux+proximo, 1, artfolder+'proximo.png', pagina)
		
	elif pagina>=1:
		match_prox_ant=re.compile('<a href=\".+?\" class="l"><i class="fa fa-arrow-left"></i> Anterior</a><a href="(.+?)" class="r">Pr').findall(codigo_fonte_listaFilmes)
		pagina+=1
		for proximo in match_prox_ant:
			proximo = proximo[1:]
			addDir('Proximo >>', siteAux+proximo, 1, artfolder+'proximo.png', pagina)
	
	mensagemprogresso.close()
	xbmc.executebuiltin("Container.SetViewMode(500)")

def getSeries(url, pagina):
	codigo_fonte_listaSeries = abrir_url(url+'series')
	match_series=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(codigo_fonte_listaSeries)
	for link,imagem,nome,ano,imdb in match_series:
		link = link[1:]
		addDir(nome + ' ('+ano+')', site+link, 4, site+imagem, pagina)

	if pagina==0:
		match_prox=re.compile('<a href=\"(.+?)\" class=\"r\">Pr').findall(codigo_fonte_listaSeries)
		pagina+=1
		for proximo in match_prox:
			proximo = proximo[1:]
			addDir('Proximo >>', site+proximo, 2, artfolder+'proximo.png', pagina)	
	elif pagina>=1:
		match_prox_ant=re.compile('<a href=\".+?\" class="l"><i class="fa fa-arrow-left"></i> Anterior</a><a href="(.+?)" class="r">Pr').findall(codigo_fonte_listaSeries)
		pagina+=1
		for proximo in match_prox_ant:
			proximo = proximo[1:]
			addDir('Proximo >>', site+proximo, 2, artfolder+'proximo.png', pagina)
	xbmc.executebuiltin("Container.SetViewMode(500)")

def getSeasons(url):
	codigo_fonte = abrir_url(url)
	temporadaN = 0
	soup = BeautifulSoup(codigo_fonte)
	
	for temporada in soup.findAll('h2'):
		addDirSeason(temporada.text, url, 5, artfolder+'/temporadas/temporada'+str(temporadaN+1)+'.png', 0, temporadaN)
		temporadaN+=1
	xbmc.executebuiltin("Container.SetViewMode(500)")


def getEpisodes(url, temporadaNumero):
	codigo_fonte = abrir_url(url)
	soup = BeautifulSoup(codigo_fonte)

	temporadas = soup.findAll('div', attrs={'class':'temporadas'})

	#for temporada in temporadas:
	match_episodios=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(temporadas[temporadaNumero]))
	for link,imagem,nome,ano,imdb in match_episodios:
		codigo_fonte=abrir_url(site+link)
		getStream=re.compile('file: \'(.+?)\'').findall(codigo_fonte) 
		getLegenda=re.compile('file: \"(.+?)\"').findall(codigo_fonte)
		stream = ''
		legenda = ''
		for streamAux in getStream: stream = streamAux
		for legendaAux in getLegenda: legenda = legendaAux 
		addVideo(nome, stream, 3, site+imagem, site+legenda)
	xbmc.executebuiltin("Container.SetViewMode(500)")

def pesquisa(url):
	siteAux = ''

	if 'kids.' in url: siteAux = sitekids
	else: siteAux = site

	url =  siteAux + 'procurar'

	teclado = xbmc.Keyboard('', 'O que quer pesquisar?')
	teclado.doModal()

	if(teclado.isConfirmed()):
		strPesquisa = teclado.getText()
		
		codigo_fonte_pesquisa = abrir_url_pesquisa(url, strPesquisa)
		soup = BeautifulSoup(codigo_fonte_pesquisa)
		filmes_series = soup.findAll('div', attrs={'class':'list'})

		if(filmes_series[0].find('ul').text != ''):
			addLink('Filmes:', '', artfolder+'filmes.png')
			match_filmes=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(filmes_series[0]))
			for link,imagem,nome,ano,imdb in match_filmes:
				link = link[1:]
				codigo_fonte=abrir_url(siteAux+link)
				getStream=re.compile('file: \'(.+?)\'').findall(codigo_fonte) 
				getLegenda=re.compile('file: \"(.+?)\"').findall(codigo_fonte)
				stream = ''
				legenda = ''
				for streamAux in getStream: stream = streamAux
				for legendaAux in getLegenda: legenda = legendaAux 
				addVideo(nome + ' ('+ano+')', stream, 3, siteAux+imagem, siteAux+legenda)

		addDir('', '', '', artfolder+'nada.png', 0)

		if(filmes_series[1].find('ul').text != ''):
			addLink('Series:', '', artfolder+'series.png')
			match_series=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(filmes_series[1]))
			for link,imagem,nome,ano,imdb in match_series:
				link = link[1:]
				addDir(nome + ' ('+ano+')', siteAux+link, 4, siteAux+imagem, pagina)
		xbmc.executebuiltin("Container.SetViewMode(500)")

###################################################################################
#                               FUNCOES JA FEITAS                                 #
###################################################################################

def abrir_url(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def abrir_url_pesquisa(url,pesquisa):
	data = urllib.urlencode({'procurar' : pesquisa})
	req = urllib2.Request(url,data)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def addDir(name,url,mode,iconimage,pagina):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
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
	liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def addVideo(name,url,mode,iconimage,legenda):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&legenda="+urllib.quote_plus(legenda)+"&iconimage="+urllib.quote_plus(iconimage)
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

def clean(text):
	command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
	regex = re.compile("|".join(map(re.escape, command.keys())))
	return regex.sub(lambda mo: command[mo.group(0)], text)

def player(name,url,iconimage,legenda):
	playlist = xbmc.PlayList(1)
	playlist.clear()
	listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	listitem.setInfo("Video", {"title":name})
	listitem.setProperty('mimetype', 'video/x-msvideo')
	listitem.setProperty('IsPlayable', 'true')
	playlist.add(url, listitem)
	xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	xbmcPlayer.play(playlist)
	xbmc.Player().setSubtitles(legenda)

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
try: mode=int(params["mode"])
except: pass
try: pagina=int(params["pagina"])
except: pass
try: iconimage=urllib.unquote_plus(params["iconimage"])
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
if mode==None or url==None or len(url)<1: categorias()
elif mode==1: getFilmes(url, pagina)
elif mode==2: getSeries(url, pagina)
elif mode==3: player(name, url, iconimage, legenda)
elif mode==4: getSeasons(url)
elif mode==5: getEpisodes(url, temporada)
elif mode==6: pesquisa(url)
xbmcplugin.endOfDirectory(int(sys.argv[1]))