#!/usr/bin/python
# -*- coding: utf-8 -*-

#Agredecimentos ao Mafarricos

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os,json,threading,xbmcvfs
from bs4 import BeautifulSoup
from resources.lib import Downloader #Enen92 class
from resources.lib import TVDB
from resources.lib import MovieDB
from resources.lib import Player


addon_id    = xbmcaddon.Addon().getAddonInfo("id")
selfAddon	= xbmcaddon.Addon(addon_id)
addonfolder	= selfAddon.getAddonInfo('path')
getSetting	= xbmcaddon.Addon().getSetting
artfolder	= os.path.join(addonfolder,'resources','img')
fanart 		= os.path.join(addonfolder,'fundo.png')

pastaFilmes = xbmc.translatePath(selfAddon.getSetting('bibliotecaFilmes'))
pastaSeries = xbmc.translatePath(selfAddon.getSetting('bibliotecaSeries'))

skin = 'v2'

tv = TVDB.TVDB('D2E52B80062E3EE0', 'pt')
#movie = MovieDB.MovieDB('3421e679385f33e2438463e286e5c918', 'pt')

site = 'http://tuga.io/'
sitekids = 'http://kids.tuga.io/'

def getLiguaMetaDados():
	lang = ''
	lingua = selfAddon.getSetting('linguaMetaDados')
	if lingua == '0': lang = 'pt'
	elif lingua == '1': lang = 'en'

	print "LINGUA: ========>"
	print lang


	return lang

def categorias():
	addDir('[COLOR red][B]COMUNICADO[/B][/COLOR]', site, 666, os.path.join(artfolder, 'nada.jpg'), 0)
	addDir('', '', '', os.path.join(artfolder,'nada.png'), 0)

	if getSetting("pref_site") == 'Geral' or getSetting("pref_site") == 'Ambos':
		addDir('Filmes', site+'filmes', 1, os.path.join(artfolder,skin,'filmes.png'), 0)
		addDir('Series', site+'series', 2, os.path.join(artfolder,skin,'series.png'), 0)
		addDir('Pesquisa', site, 6, os.path.join(artfolder,skin,'pesquisa.png'), 0)
		if "confluence" in xbmc.getSkinDir(): addDir('', '', '', os.path.join(artfolder,'nada.png'), 0)
	if getSetting("pref_site") == 'Kids' or getSetting("pref_site") == 'Ambos':
		addDir('Filmes KIDS', sitekids+'filmes', 1, os.path.join(artfolder,skin,'kids.png'), 0)
		addDir('Pesquisa KIDS', sitekids, 6, os.path.join(artfolder,skin,'pesquisakids.png'), 0)
		if "confluence" in xbmc.getSkinDir(): addDir('', '', '', os.path.join(artfolder,'nada.png'), 0)
	addDir('Filmes por Genero', site, 8, os.path.join(artfolder,skin,'filmegeneros.png'), 0)
	addDir('Series por Genero', site, 9, os.path.join(artfolder,skin,'seriesgeneros.png'), 0)
	addDir('Filmes IMDB Rating', site+'filmes?orderby=1', 1, os.path.join(artfolder,skin,'filmesimdb.png'), 0)
	addDir('Series IMDB Rating', site+'series?orderby=1', 2, os.path.join(artfolder,skin,'seriesimdb.png'), 0)
	if "confluence" in xbmc.getSkinDir(): addDir('', '', '', os.path.join(artfolder,skin,'nada.png'), 0)
	addDir('Definicoes', site, 1000, os.path.join(artfolder,skin,'definicoes.png'), 0)

	vista_menu()

def login(site):
	username = getSetting("username")
	password = getSetting("password")

	codigo_fonte = abrir_url(site)
	match = re.compile('data-sitekey="(.+?)"').findall(codigo_fonte)[0]

	codigo_fonte = abrir_url('http://www.google.com/recaptcha/api/challenge?k='+match)
	recaptcha = re.compile('challenge : \'(.+?)\'').findall(codigo_fonte)[0]

	data = urllib.urlencode({'username': username, 'password': password, 'g-recaptcha-response': recaptcha})
	req = urllib2.Request(site,data)
	req.add_header('User-Agent', 'Mozilla/5.0')
	response = urllib2.urlopen(req)



	link=response.read()
	response.close()
	print link

def getFilmes(url, pagina):

	siteAux = ''

	if 'kids.' in url: siteAux = sitekids
	else: siteAux = site
	
	mensagemprogresso = xbmcgui.DialogProgress()
	mensagemprogresso.create('Tuga.io', 'A abrir lista de filmes','Por favor aguarde...')

	i=1
	mensagemprogresso.update(i)

	codigo_fonte_listaFilmes=abrir_url(url)
	match_filmes=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(codigo_fonte_listaFilmes)

	tamanhoArray = len(match_filmes)+0.0

	for link,imagem,nome,ano,imdb in match_filmes:
		percentagem = int((i/tamanhoArray)*100)
		link = link[1:]
		
		
		idIMDb = link.split('/')[-1]
		
		"""mediaInfo = getInfoIMDB(idIMDb)
		nome = mediaInfo['Title'].encode('utf8')
		ano = mediaInfo['Year'].encode('utf8')
		infoLabels = {'Title':name, 'Year': ano, 'Genre':mediaInfo['Genre'], 'Plot':mediaInfo['Plot']}
		poster = mediaInfo['Poster']
		"""

		infoLabels = {'Title': name, 'Year': ano}
		poster = site+imagem
		#match=re.compile('jwplayer\(\'player_get_hard\'\).setup\(\{\n                            file: \'(.+?)\',\n                            aspectratio: \'.+?\',\n                            width: \'.+?\',\n                            height: \'.+?\',\n                            skin: \'.+?\',\n                            primary: ".+?",\n                            androidhls:.+?,\n                            logo : \{\n                                file: ".+?",\n                                link: ".+?",\n                                hide: .+?\n                            \},\n                            tracks:\n                                    \[\n                                        \{\n                                            file: "(.+?)",\n                                            default: ".+?"\n                                        \}\n                                    \],\n                            captions: \{\n                                backgroundOpacity: .+?                            \}\n\n                        \}\);').findall(codigo_fonte)
		mensagemprogresso.update(percentagem, "", nome, "")
		addVideo(nome + ' ('+ano+')', siteAux+link, 3, siteAux+imagem, 'filme', 0, 0, infoLabels, poster)
		if mensagemprogresso.iscanceled(): break
		i+=1
		
	if pagina==0:
		match_prox=re.compile('<a href=\"(.+?)\" class=\"r\">Pr').findall(codigo_fonte_listaFilmes)
		pagina+=1
		for proximo in match_prox:
			proximo = proximo[1:]
			addDir('Proximo >>', siteAux+proximo, 1, os.path.join(artfolder,skin,'proximo.png'), pagina)
		
	elif pagina>=1:
		match_prox_ant=re.compile('<a href=\".+?\" class="l"><i class="fa fa-arrow-left"></i> Anterior</a><a href="(.+?)" class="r">Pr').findall(codigo_fonte_listaFilmes)
		pagina+=1
		for proximo in match_prox_ant:
			proximo = proximo[1:]
			addDir('Proximo >>', siteAux+proximo, 1, os.path.join(artfolder,skin,'proximo.png'), pagina)
	
	mensagemprogresso.close()
	
	vista_filmesSeries()

def getSeries(url, pagina):
	codigo_fonte_listaSeries = abrir_url(url)
	match_series=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(codigo_fonte_listaSeries)
	for link,imagem,nome,ano,imdb in match_series:
		link = link[1:]
		
		idIMDb = link.split('/')[-1]
		
		#mediaInfo = json.loads(tv.getSerieInfo(idIMDb))

		#infoLabels = {'Title':nome, 'Aired':mediaInfo['aired'], 'Plot':mediaInfo['plot']}
		infoLabels = {'Title':nome}
		addDir(nome+ ' ('+ano+')', site+link, 4, site+imagem, pagina, 'serie', infoLabels, site+imagem)

	if pagina==0:
		match_prox=re.compile('<a href=\"(.+?)\" class=\"r\">Pr').findall(codigo_fonte_listaSeries)
		pagina+=1
		for proximo in match_prox:
			proximo = proximo[1:]
			addDir('Proximo >>', site+proximo, 2, os.path.join(artfolder,skin,'proximo.png'), pagina)	
	elif pagina>=1:
		match_prox_ant=re.compile('<a href=\".+?\" class="l"><i class="fa fa-arrow-left"></i> Anterior</a><a href="(.+?)" class="r">Pr').findall(codigo_fonte_listaSeries)
		pagina+=1
		for proximo in match_prox_ant:
			proximo = proximo[1:]
			addDir('Proximo >>', site+proximo, 2, os.path.join(artfolder,skin,'proximo.png'), pagina)
	
	vista_filmesSeries()

def getSeasons(url):
	codigo_fonte = abrir_url(url)
	temporadaN = 0
	
	match = re.compile('(?s)(.*)\n<footer').findall(codigo_fonte)

	soup = BeautifulSoup(match[0])
	idIMDb = url.split('/')[-1]

	titulo = re.compile('<div class="title"><span class="t">(.+?)<\/span>').findall(codigo_fonte)[0]
	
	for temporada in soup.findAll('h2'):
		addDirSeason(temporada.text, url, 5, os.path.join(artfolder,skin,'temporadas','temporada'+str(temporadaN+1)+'.png'), 0, temporadaN, idIMDb)
		temporadaN+=1
	
	vista_temporadas()


def getEpisodes(url, temporadaNumero, idIMDb):
	codigo_fonte = abrir_url(url)

	match = re.compile('(?s)(.*)\n<footer').findall(codigo_fonte)

	soup = BeautifulSoup(match[0])
	#soup = BeautifulSoup(codigo_fonte)
	
	temporadas = soup.findAll('div', attrs={'class':'temporadas'})

	i = 0
	match_episodios=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(temporadas[temporadaNumero]))
	for link,imagem,nomeOriginal,ano,imdb in match_episodios:

		episodioNumero = nomeOriginal.split('.')[1]
		episodioNomeSplit = episodioNumero.split('|')
		episodioNumero = episodioNomeSplit[0]
		
		nomeOriginal = episodioNomeSplit[-1]

		codigoIMDb = link.split('/')[-1]
		
		if int(episodioNumero) == 0:
			i+=1

		episodioNumero = str(int(episodioNumero)+i)
		#mediaInfo = json.loads(tv.getSeasonEpisodio(idIMDb,(temporadaNumero+1),episodioNumero))
		#nome = 'Ep. '+str(episodioNumero)+' - '+mediaInfo['name'].encode('utf8')
		#ano = mediaInfo['aired'].encode('utf8')
		#infoLabels = {'Title':nome, 'Aired': mediaInfo['aired'], 'Actors':mediaInfo['actors'], 'Plot':mediaInfo['plot'], 'Season':mediaInfo['season'], 'Episode':mediaInfo['episode'], 'Writer': mediaInfo['writer'], 'Director':mediaInfo["director"], "Code":codigoIMDb }
		nome = '[B]'+str(temporadaNumero+1)+'x'+episodioNumero+'[/B] '+nomeOriginal
		infoLabels = {'Title':nome}
		poster = site+imagem

		addVideo(nome, site+link, 3, site+imagem, 'episodio', temporadaNumero+1, episodioNumero, infoLabels, poster)
	
	vista_episodios()

def pesquisa(url):
	siteAux = ''

	if 'kids.' in url: 
		siteAux = sitekids
		artFilmes = os.path.join(artfolder,skin,'kids.png')
	else: 
		siteAux = site
		artFilmes = os.path.join(artfolder,skin,'filmes.png')

	url =  siteAux + 'procurar'

	teclado = xbmc.Keyboard('', 'O que quer pesquisar?')
	teclado.doModal()

	if(teclado.isConfirmed()):
		strPesquisa = teclado.getText()
		
		codigo_fonte_pesquisa = abrir_url(url, strPesquisa)
		
		match = re.compile('(?s)(.*)\n<footer').findall(codigo_fonte_pesquisa)
		
		soup = BeautifulSoup(match[0])
		#soup = BeautifulSoup(codigo_fonte_pesquisa)
		filmes_series = soup.findAll('div', attrs={'class':'list'})

		if(str(filmes_series[0].find('ul').text) != ''):
			addLink('Filmes:', '', artFilmes)
			match_filmes=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(filmes_series[0]))
			for link,imagem,nome,ano,imdb in match_filmes:
				link = link[1:]

				idIMDb = link.split('/')[-1]
				"""mediaInfo = getInfoIMDB(idIMDb)
				nome = mediaInfo['Title'].encode('utf8')
				ano = mediaInfo['Year'].encode('utf8')
				infoLabels = {'Title':name, 'Year': ano, 'Genre':mediaInfo['Genre'], 'Plot':mediaInfo['Plot']}
				poster = mediaInfo['Poster']
				"""

				infoLabels = {'Title': name, 'Year': ano}
				poster = site+imagem
				
				addVideo(nome + ' ('+ano+')', siteAux+link, 3, siteAux+imagem,'filme', 0, 0, infoLabels, poster)

			addDir('', '', '', os.path.join(artfolder,'novo','nada.png'), 0)

		if(str(filmes_series[1].find('ul').text) != ''):
			addLink('Series:', '', os.path.join(artfolder,skin,'series.png'))
			match_series=re.compile('<li>\n<a href="(.+?)">\n<div class="thumb">\n<div class="img" style="background-image: url\(\'(.+?)\'\);"></div>\n</div>\n<div class="info">\n<div class="title">(.+?)</div>\n<div class="infos">\n<div class="year">(.+?)</div>\n<div class="imdb">(.+?)</div>\n</div>\n</div>\n</a>\n</li>\n').findall(str(filmes_series[1]))
			for link,imagem,nome,ano,imdb in match_series:
				link = link[1:]
				idIMDb = link.split('/')[-1]

				#mediaInfo = json.loads(tv.getSerieInfo(idIMDb))
				#print mediaInfo
				#infoLabels = {'Title':name, 'Released':mediaInfo['aired'], 'Plot':mediaInfo['plot']}

				infoLabels = {'Title':name}

				#poster = mediaInfo['poster']
				poster = site+imagem
				addDir(nome + ' ('+ano+')', siteAux+link, 4, siteAux+imagem,'serie', infoLabels, poster)

		vista_filmesSeries()

def download(url,name):

	legendasOn = False

	#dialog = xbmcgui.Dialog()
	#servidor = dialog.select(u'Escolha o servidor para Download', ['Servidor #1', 'Servidor #2', 'Servidor #3'])
	
	stream, legenda = getStreamLegenda(url)
	splitStream = stream.split('/')

	nomeStream = stream.split('/')[-1]

	tamanho = len(splitStream)

	"""if servidor == 0:
		stream = 'http://az786600.vo.msecnd.net/'
		if tamanho == 5:
			stream += splitStream[3]+'/'
		stream += nomeStream
	elif servidor == 1:
		stream = 'http://cdn3.tuga.io/'
		if tamanho == 5:
			stream += splitStream[3]+'/'
		stream += nomeStream
	elif servidor == 2:
		stream = 'http://cdn.tuga.su/'
		if tamanho == 5:
			stream += splitStream[3]+'/'
		stream += nomeStream"""

	folder = xbmc.translatePath(selfAddon.getSetting('pastaDownloads'))

	urlAux = clean(stream.split('/')[-1])
	extensaoMedia = clean(urlAux.split('.')[-1])
	nomeMedia = name+'.'+extensaoMedia
	

	if legenda != '':
		legendaAux = clean(legenda.split('/')[-1])
		extensaoLegenda = clean(legendaAux.split('.')[1])
		nomeLegenda = name+'.'+extensaoLegenda
		legendasOn = True

	Downloader.Downloader().download( os.path.join(folder,nomeMedia), stream, name)

	if legendasOn:
		download_legendas(legenda, os.path.join(folder,nomeLegenda))

def download_legendas(url,path):
	contents = abrir_url(url)
	if contents:
		fh = open(path, 'w')
		fh.write(contents)
		fh.close()
	return

def getStreamLegenda(url):
	siteAux = ''
	legendasOn = True
	if 'kids.' in url: 
		siteAux = sitekids
		legendasOn = False
	else: 
		siteAux = site

	codigo_fonte = abrir_url(url)

	getStream=re.compile('file: \"http(.+?)\"').findall(codigo_fonte) 
	getLegenda=re.compile('file: \"\/subtitles(.+?)\"').findall(codigo_fonte)
	stream = ''
	legenda = ''
		
	for streamAux in getStream: stream = "http"+streamAux
	if legendasOn:
		for legendaAux in getLegenda: legenda = siteAux+'subtitles'+legendaAux

	return stream, legenda

def getInfoIMDB(idIMDb):
	url = 'http://www.omdbapi.com/?i='+idIMDb+'&plot=short'
	data = json.loads(abrir_url(url))
	return data

def getGeneros(url, tipo):
	siteAux = ''
	mode = 1
	arte = ''

	if tipo == 'filmes':
		siteAux = url+'filmes'
		mode = 1
		arte = os.path.join(artfolder,skin,'filmes.png')
	elif tipo == 'series':
		siteAux = url+'series'
		mode = 2
		arte = os.path.join(artfolder,skin,'series.png')


	codigo_fonte=abrir_url(siteAux)
	match = re.compile('(?s)(.*)\n<footer').findall(codigo_fonte)

	soup = BeautifulSoup(match[0])
	#soup = BeautifulSoup(codigo_fonte)
	generos = soup.find('select', attrs={'name':'genre'})

	listaGeneros = re.compile('<option value="(.+?)">(.+?)</option>').findall(str(generos))
	for value, text in listaGeneros:
		addDir(text, siteAux+'?genre='+value, mode, arte, 0)


###################################################################################
#                              DEFININCOES		                                  #
###################################################################################

def addBiblioteca(nome, url, tipo, temporada=False, episodio=False):
	updatelibrary=True

	if tipo == 'filme': 
		if not xbmcvfs.exists(pastaFilmes): xbmcvfs.mkdir(pastaFilmes)
	elif tipo == 'serie': 
		if not xbmcvfs.exists(pastaSeries): xbmcvfs.mkdir(pastaSeries)

	if type == 'filme': 
		try: file_folder = os.path.join(pastaFilmes,nome)
		except: pass
	elif type == 'serie':
		file_folder1 = os.path.join(pastaSeries,nome)
		if not xbmcvfs.exists(file_folder1): tryFTPfolder(file_folder1)
		file_folder = os.path.join(pastaSeries, nome+'/','S'+temporada)
		title =  nome + ' S'+temporada+'E'+episodio

	strm_contents = 'plugin://plugin.video.tugaio/?url='+url+'&mode=3&name='+urllib.quote_plus(nome)
	savefile(urllib.quote_plus(title)+'.strm',strm_contents,file_folder)
	if updatelibrary: xbmc.executebuiltin("XBMC.UpdateLibrary(video)")
	return True

def comunicado():
	texto = "Boa tarde,\nVenho vos anunciar que o addon Tuga.io vai ser descontinuado. A razão que me levou a fazer isto tem a haver com vários factos que vou enumerar de seguida.\n\n1º - Falta de tempo e paciência. Poderia ser só uma condicionante ou o tempo ou a paciência mas os dois juntos é difícil. A condicionante paciência vem do facto de sempre que atualizo, os mesmos criadores do site Tuga.io tentavam dificultar a vida a quem tenta dar visibilidade ao seu projeto. Lançaram o projeto para os utilizadores da internet terem acesso livre aos diversos conteúdos de filmes e séries, colocando regras que seria grátis para todos e de forma fácil. Implementaram o registo de utilizadores a indicarem que o mesmo não seria necessário para visualizar o conteúdo. No dia 01 de Outubro de 2015 os diversos utilizadores do projeto receberam uma notícia que os registos estavam fechados que era necessário conta para ver os conteúdos. Mudaram as regras, está no direito deles mas para também combater um addon que lhe dava visibilidade.\n2º - Bloqueios constantes. Nos últimos meses vocês verificavam que o addon deixava de funcionar de um momento para o outro. Tive a difícil tarefa de tentar perceber o bloqueio e contornar-lo para que vocês, utilizadores do addon, pudessem utilizar.\nO addon poderá continuar, quem quiser pode pegar no código já desenvolvido por mim e lançar novas atualizações, terei todo o gosto em ajudar quem quiser continuar o mesmo. Posso ajudar desde a interpretação de código já feito, como a implementação de novas funcionalidades. Tinha algumas ideias para o addon, que quem pegar nele direi e ajudarei na implementação, ideias que já tinham sido começado a ser implementadas mas não estavam a 100%.\nEu como desenvolvedor, não irei parar e tenho ideias para lançar no meu repositório, poderá ser um lançamento demorado mas que até ao final do ano, eu espero lançar. A ideia principal não será para a visualização de filmes nem séries, mas será um ideia que muitos de vocês que gostam de futebol poderão usar. E adianto também que não é um addon para ver o futebol mas é para ser acompanhado o futebol pelo Kodi.\nAgradeço a todos que usaram este addon durante meses, dos elogios e das sugestões que foram, ou não implementadas, mas não estavam esquecidas.\nAgradeço ao Carlos Correia e ao Enen pela ajuda e dicas no desenvolvimento do mesmo. E ao João Ferreira pelas imagens feitas e disponibilizadas para o addon.\nAos interessados na continuação do addon, poderão contactar via MP ou podem enviar um email para xsteal.projetos@gmail.com.\nObrigado a todos."
	print texto
	xbmcgui.Dialog().ok("Tuga.io", texto)
	addDir('Entrar novamente','url',None,os.path.join(artfolder,skin,'retroceder.png'),True)
	vista_menu()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def abrirDefinincoes():
	selfAddon.openSettings()
	addDir('Entrar novamente','url',None,os.path.join(artfolder,skin,'retroceder.png'),True)
	vista_menu()
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def vista_menu():
	opcao = selfAddon.getSetting('menuView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51")

def vista_filmesSeries():
	opcao = selfAddon.getSetting('filmesSeriesView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
	elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(501)")
	elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
	elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
	elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
	elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")
	

def vista_temporadas():
	opcao = selfAddon.getSetting('temporadasView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def vista_episodios():
	opcao = selfAddon.getSetting('episodiosView')
	if opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
	elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
	elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")    

###################################################################################
#                               FUNCOES JA FEITAS                                 #
###################################################################################

#ABELHAS ADDON
def tryFTPfolder(file_folder):
	if 'ftp://' in file_folder:
		try:
			from ftplib import FTP		
			ftparg = re.compile('ftp://(.+?):(.+?)@(.+?):?(\d+)?/(.+/?)').findall(file_folder)
			ftp = FTP(ftparg[0][2],ftparg[0][0],ftparg[0][1])
			try: ftp.cwd(ftparg[0][4])
			except: ftp.mkd(ftparg[0][4])
			ftp.quit()
		except: print 'Nao conseguiu criar %s' % file_folder
	else: xbmcvfs.mkdir(file_folder)

def abrir_url(url,pesquisa=False):
	#header = {'User-Agent': 'Mozilla/5.0'}
	
	header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'}

	if pesquisa:
		data = urllib.urlencode({'procurar' : pesquisa})
		req = urllib2.Request(url,data, headers=header)
	else:
		req = urllib2.Request(url, headers=header)
	
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

def addDir(name,url,mode,iconimage,pagina,tipo=False,infoLabels=False,poster=False):
	if infoLabels: infoLabelsAux = infoLabels
	else: infoLabelsAux = {'Title': name}

	if poster: posterAux = poster
	else: posterAux = iconimage

	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True

	if tipo == 'filme':	
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	elif tipo == 'serie':
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	elif tipo == 'episodio':
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
	else: 
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')

	liz=xbmcgui.ListItem(name, iconImage=posterAux, thumbnailImage=posterAux)
	liz.setProperty('fanart_image', posterAux)
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

def addDirSeason(name,url,mode,iconimage,pagina,temporada,idIMDbSerie,infoLabels=False,poster=False):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&pagina="+str(pagina)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&temporada="+str(temporada)+"&idIMDbSerie="+urllib.quote_plus(idIMDbSerie)
	ok=True
	xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	liz=xbmcgui.ListItem(name, iconImage="fanart.jpg", thumbnailImage=iconimage)
	liz.setProperty('fanart_image', iconimage)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
	return ok

def addVideo(name,url,mode,iconimage,tipo,temporada,episodio,infoLabels=False,poster=False):
	if infoLabels: infoLabelsAux = infoLabels
	else: infoLabelsAux = {'Title': name}

	if poster: posterAux = poster
	else: posterAux = iconimage

	if tipo == 'filme':	
		xbmcplugin.setContent(int(sys.argv[1]), 'Movies')
	elif tipo == 'serie':
		xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	elif tipo == 'episodio':
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')


	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&temporada="+str(temporada)+"&episodio="+str(episodio)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
	ok=True
	contextMenuItems = []
	liz=xbmcgui.ListItem(name, iconImage=posterAux, thumbnailImage=posterAux)
	liz.setProperty('fanart_image', posterAux)
	liz.setInfo( type="Video", infoLabels=infoLabelsAux )
	contextMenuItems.append(('Download', 'XBMC.RunPlugin(%s?mode=7&name=%s&url=%s&iconimage=%s)'%(sys.argv[0],urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(iconimage))))
	liz.addContextMenuItems(contextMenuItems, replaceItems=False)
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
	return ok

def clean(text):
	command={'&#8220;':'"','&#8221;':'"', '&#8211;':'-','&amp;':'&','&#8217;':"'",'&#8216;':"'"}
	regex = re.compile("|".join(map(re.escape, command.keys())))
	return regex.sub(lambda mo: command[mo.group(0)], text)

def player(name,url,iconimage,temporada,episodio):

	mensagemprogresso = xbmcgui.DialogProgress()
	mensagemprogresso.create('Tuga.io', u'Abrir emissão','Por favor aguarde...')



	#dialog = xbmcgui.Dialog()
	#servidor = dialog.select(u'Escolha o servidor', ['Servidor #1', 'Servidor #2', 'Servidor #3'])
	mensagemprogresso.update(25, "", u'Obter video e legenda', "")
	stream, legenda = getStreamLegenda(url)

	splitStream = stream.split('/')

	nomeStream = stream.split('/')[-1]

	tamanho = len(splitStream)

	"""if servidor == 0:
		stream = 'http://az786600.vo.msecnd.net/'
		if tamanho == 5:
			stream += splitStream[3]+'/'
		stream += nomeStream
	elif servidor == 1:
		stream = 'http://cdn3.tuga.io/'
		if tamanho == 5:
			stream += splitStream[3]+'/'
		stream += nomeStream
	elif servidor == 2:
		stream = 'http://cdn.tuga.su/'
		if tamanho == 5:
			stream += splitStream[3]+'/'
		stream += nomeStream"""

	

	mensagemprogresso.update(50, "", u'Prepara-te, vai começar!', "")
	
	playlist = xbmc.PlayList(1)
	playlist.clear()
	listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	listitem.setInfo("Video", {"title":name})
	listitem.setProperty('mimetype', 'video/x-msvideo')
	listitem.setProperty('IsPlayable', 'true')

	playlist.add(stream, listitem)

	idIMDb = url.split('/')[-1]
	if temporada == 0 and episodio == 0:
		ano = str(re.compile('\((.+?)\)').findall(name)[0])
	else:
		ano = 2000

	pastaData = ''
	
	if temporada == 0 and episodio == 0:
		pastaData = selfAddon.getSetting('bibliotecaFilmes')
		name = re.compile('(.+?) \(.+?\)').findall(name)[0]
	else:
		pastaData = selfAddon.getSetting('bibliotecaSeries')
		name = re.compile('(.+?)\| (.+)').findall(name)[0][1]

	
	mensagemprogresso.update(75, "", u'Boa Sessão!!!', "")
	print "url: "+url+" idIMDb: "+idIMDb+" pastaData: "+pastaData+"\n temporada: "+str(temporada)+" episodio: "+str(episodio)+" \nnome: "+name+" ano:"+str(ano)
	

	player = Player.Player(url=url, idFilme=idIMDb, pastaData=pastaData, temporada=temporada, episodio=episodio, nome=name, ano=ano, logo=os.path.join(addonfolder,'icon.png'))
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
idIMDbSerie=None
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
try: idIMDbSerie=urllib.unquote_plus(params["idIMDbSerie"])
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
elif mode==3: player(name, url, iconimage, temporada, episodio)
elif mode==4: getSeasons(url)
elif mode==5: getEpisodes(url, temporada, idIMDbSerie)
elif mode==6: pesquisa(url)
elif mode==7: download(url, name)
elif mode==8: getGeneros(url, 'filmes')
elif mode==9: getGeneros(url, 'series')
elif mode==666: comunicado()
elif mode==1000: abrirDefinincoes()
xbmcplugin.endOfDirectory(int(sys.argv[1]))