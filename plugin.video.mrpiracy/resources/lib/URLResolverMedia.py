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

import json, re, xbmc, urllib, xbmcgui, os, sys, pprint
from t0mm0.common.net import Net
from bs4 import BeautifulSoup
import jsunpacker
import AADecoder


class OpenLoad():

	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.id = str(self.getId())
		self.messageOk = xbmcgui.Dialog().ok
		self.site = 'https://openload.co'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7'}


	def getId(self):
		#return self.url.split('/')[-1]
		return re.compile('https\:\/\/openload\.co\/embed\/(.+?)\/').findall(self.url)[0]

	def decodeOpenLoad(self, html):
		aastring = re.search(r"<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)</script", html, re.DOTALL | re.IGNORECASE).group(1)
		aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
		aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))", "8")
		aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))", "7")
		aastring = aastring.replace("((o^_^o) +(o^_^o))", "6")
		aastring = aastring.replace("((ﾟｰﾟ) + (ﾟΘﾟ))", "5")
		aastring = aastring.replace("(ﾟｰﾟ)", "4")
		aastring = aastring.replace("((o^_^o) - (ﾟΘﾟ))", "2")
		aastring = aastring.replace("(o^_^o)", "3")
		aastring = aastring.replace("(ﾟΘﾟ)", "1")
		aastring = aastring.replace("(+!+[])", "1")
		aastring = aastring.replace("(c^_^o)", "0")
		aastring = aastring.replace("(0+0)", "0")
		aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]", "\\")
		aastring = aastring.replace("(3 +3 +0)", "6")
		aastring = aastring.replace("(3 - 1 +0)", "2")
		aastring = aastring.replace("(!+[]+!+[])", "2")
		aastring = aastring.replace("(-~-~2)", "4")
		aastring = aastring.replace("(-~-~1)", "3")
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n %s <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n" % aastring)

		decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
		decodestring = "\\+"+ decodestring
		decodestring = decodestring.replace("+","")
		decodestring = decodestring.replace(" ","")

		decodestring = self.decode(decodestring)
		decodestring = decodestring.replace("\\/","/")
		print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n %s <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n" % decodestring)
		videourl = re.compile("window.vr='([^']+)'").findall(decodestring)
		print("videp",videourl)
		if len(videourl)>0:
			linkvideo = videourl[0]
		else:
			linkvideo=''
		return linkvideo

	def decode(self, encoded):
		for octc in (c for c in re.findall(r'\\(\d{2,3})', encoded)):
			encoded = encoded.replace(r'\%s' % octc, chr(int(octc, 8)))
		return encoded.decode('utf8')

	def getMediaUrl(self):

		content = self.net.http_GET(self.url, headers=self.headers).content

		videoUrl = self.decodeOpenLoad(str(content.encode('utf-8')))

		print videoUrl

		return videoUrl

		"""soup = BeautifulSoup(content)

		scriptResults = soup.find_all('script')
		
		video_url1 = ''

		for script in scriptResults:
			aadecoded = AADecoder.AADecoder(str(script.encode('utf-8')))
			if aadecoded.is_aaencoded():
				video_url = aadecoded.decode()

		print video_url1

		aascript = re.compile('<script type="text\/javascript">(.+?)<\/script>').findall(content)

		dataJs = ''

		mat = re.finditer('(eval\(function.*?)</script>', str(aascript[1].encode('utf-8')), re.DOTALL)

		print "AQUI AQUI AQUI AQUI AQUI AQUI AQUI"

		print mat

		for pack in re.finditer('(eval\(function.*?)</script>', str(aascript[1].encode('utf-8')), re.DOTALL):
			dataJs = jsunpacker.unpack(pack.group(1))

		print dataJs

		print "====================================>"
		print str(aascript[1].encode('utf-8'))
		string = AADecoder.AADecoder(str(aascript[1].encode('utf-8'))).decode()
		video_url = string.replace('window.vr ="','',1).replace('";window.vt ="video/mp4" ;','',1)

		print video_url
		return video_url"""

	def getMediaUrlOld(self):

		try:
			ticket = 'https://api.openload.co/1/file/dlticket?file=%s' % self.id
			result = self.net.http_GET(ticket).content
			jsonResult = json.loads(result)

			if jsonResult['status'] == 200:
				fileUrl = 'https://api.openload.co/1/file/dl?file=%s&ticket=%s' % (self.id, jsonResult['result']['ticket'])
				captcha = jsonResult['result']['captcha_url']

				print "CAPTCHA: "
				print self.id
				captcha.replace('\/', '/')
				print captcha

				if captcha:
					captchaResponse = self.getCaptcha(captcha.replace('\/', '/'))

					if captchaResponse:
						fileUrl += '&captcha_response=%s' % urllib.quote(captchaResponse)

				xbmc.sleep(jsonResult['result']['wait_time'] * 1000)

				result = self.net.http_GET(fileUrl).content
				jsonResult = json.loads(result)

				if jsonResult['status'] == 200:
					return jsonResult['result']['url'] + '?mime=true'  #really?? :facepalm:
				else:
					self.messageOk('MrPiracy.xyz', "FILE: "+jsonResult['msg'])

			else:

				self.messageOk('MrPiracy.xyz', "TICKET: "+jsonResult['msg'])
				return False
		except:
			self.messageOk('MrPiracy.xyz', 'Ocorreu um erro a obter o link. Escolha outro servidor.')

	def getCaptcha(self, image):
		try:
			image = xbmcgui.ControlImage(450, 0, 300, 130, image)
			dialog = xbmcgui.WindowDialog()
			dialog.addControl(image)
			dialog.show()
			xbmc.sleep(3000)

			letters = xbmc.Keyboard('', 'Escreva as letras na imagem', False)
			letters.doModal()

			if(letters.isConfirmed()):
				result = letters.getText()
				if result == '':
					self.messageOk('MrPiracy.xyz', 'Tens de colocar o texto da imagem para aceder ao video.')
				else:
					return result
			else:
				self.messageOk('MrPiracy.xyz', 'Erro no Captcha')
		finally:
			dialog.close()

	def getSubtitle(self):
		pageOpenLoad = self.net.http_GET(self.url, headers=self.headers).content
		subtitle = re.compile('<track kind="captions" src="(.+?)" srclang="pt" label="Portuguese" default>').findall(pageOpenLoad)[0]
		#return self.site + subtitle
		return subtitle


class VideoMega():

	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.id = str(self.getId())
		self.messageOk = xbmcgui.Dialog().ok
		self.site = 'https://videomega.tv'
		self.headers = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
		self.headersComplete = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25', 'Referer': self.getNewHost()}

	def getId(self):
		return re.compile('http\:\/\/videomega\.tv\/view\.php\?ref=(.+?)&width=700&height=430').findall(self.url)[0]

	def getNewHost(self):
		return 'http://videomega.tv/cdn.php?ref=%s' % (self.id)

	def getMediaUrl(self):
		sourceCode = self.net.http_GET(self.getNewHost(), headers=self.headersComplete).content
		match = re.search('<source\s+src="([^"]+)"', sourceCode)

		if match:
			return match.group(1) + '|User-Agent=%s' % (self.headers)
		else:
			self.messageOk('MrPiracy.xyz', 'Video nao encontrado.')

class Vidzi():
	def __init__(self, url):
		self.url = url
		self.net = Net()
		self.id = str(self.getId())
		self.messageOk = xbmcgui.Dialog().ok
		self.site = 'https://videomega.tv'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:43.0) Gecko/20100101 Firefox/43.0', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}
		self.subtitle = ''

	def getId(self):
		return re.compile('http\:\/\/vidzi.tv\/embed-(.+?)-').findall(self.url)[0]
	
	def getNewHost(self):
		return 'http://vidzi.tv/embed-%s.html' % (self.id)

	def getMediaUrl(self):
		sourceCode = self.net.http_GET(self.getNewHost(), headers=self.headers).content

		if '404 Not Found' in sourceCode:
			self.messageOk('MrPiracy.xyz', 'Ficheiro nao encontrado ou removido. EScolha outro servidor.')

		match = re.search('file\s*:\s*"([^"]+)', sourceCode)
		if match:
			return match.group(1) + '|Referer=http://vidzi.tv/nplayer/jwpayer.flash.swf'
		else:
			for pack in re.finditer('(eval\(function.*?)</script>', sourceCode, re.DOTALL):
				dataJs = jsunpacker.unpack(pack.group(1)) # Unpacker for Dean Edward's p.a.c.k.e.r | THKS

				print dataJs
				#pprint.pprint(dataJs)

				stream = re.search('file\s*:\s*"([^"]+)', dataJs)
				"""
				subtitle = re.compile('tracks:\[\{file:"(.+?)\.srt"').findall(dataJs)[0]
				subtitle += ".srt"
				self.subtitle = subtitle"""
				self.subtitle = "Nao tem legenda!"
				if stream:
					return stream.group(1)

		self.messageOk('MrPiracy.xyz', 'Video nao encontrado. Escolha outro servidor')


	def getSubtitle(self):
		return self.subtitle



