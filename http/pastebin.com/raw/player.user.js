// ==UserScript==
// @name         MrPiracy Player
// @author       MrPiracy
// @namespace    http://mrpiracy.club/
// @homepage     http://mrpiracy.club/
// @description  Necessário para a reprodução de alguns servidores
// @match        https://mrpiracy.club/*
// @match        http://mrpiracy.club/*
// @icon         http://mrpiracy.club/images/apple-touch-icon-120x120.png
// @icon64       http://mrpiracy.club/images/apple-touch-icon-57x57.png
// @version      1
// @grant        GM_xmlhttpRequest
// @updateURL    http://mrpiracy.club/js/static/player.meta.js
// @downloadURL  http://mrpiracy.club/js/static/player.user.js
// @connect *
// @run-at       document-body
// ==/UserScript==


function exec(fn) {
    var script = document.createElement('script');
    script.setAttribute("type", "application/javascript");
    script.textContent = '(' + fn + ')();';
    document.body.appendChild(script);
    document.body.removeChild(script);
}

function getVideo() {
    var dados = document.getElementById("videoValues");
    if(dados === null) {
        return;
    }

    var dadosConteudo = JSON.parse(dados.innerHTML);

    var data = '';
    if(dadosConteudo.data !== '') {
        data = dadosConteudo.data;
    }
    var streams = [];
    GM_xmlhttpRequest({
        method: dadosConteudo.metodo,
        url: dadosConteudo.link,
        headers: {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language":"en-us,en;q=0.5",
            "Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
            "Connection":"keep-alive",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36"
           },
        data: data,
        onload: function(response) {

            postApi(dadosConteudo.acesso, dadosConteudo.legenda, dadosConteudo.imdb, response.responseText);

        }
    });

    dados.parentNode.removeChild(dados);
}

function postApi(link, legenda, imdb, dataPost) {
    GM_xmlhttpRequest({
        method: "POST",
        url: link,
        data: "imdb="+encodeURIComponent(btoa(encodeURIComponent(imdb)))+"&legenda="+encodeURIComponent(btoa(encodeURIComponent(legenda)))+"&conteudo="+encodeURIComponent(btoa(encodeURIComponent(dataPost))),
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        onload: function(response) {
            var playerText = document.createElement('div');
            playerText.setAttribute('id', 'coiso');
            playerText.setAttribute('hidden', 'true');
            playerText.innerHTML = response.responseText;
            document.body.appendChild(playerText);

            exec(function() {
                userscriptCallback();
            });
        }
    });
}

function injectTest() {
    var tag = document.createElement('div');
    tag.setAttribute('id', 'forceScript');
     tag.setAttribute('hidden', 'true');
    document.body.appendChild(tag);
}

injectTest();
setInterval(getVideo, 100);
