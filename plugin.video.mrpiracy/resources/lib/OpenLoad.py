#-*- coding: utf-8 -*-
#
# Djeman
#
# Join all classes i need to decode string for OpenLoad. All credits to creator of this classes - xsteal
#

import re, urllib2, string


class cParser():

    def parseSingleResult(self, sHtmlContent, sPattern):     
        aMatches = re.compile(sPattern).findall(sHtmlContent)
        
        if (len(aMatches) == 1):
            #aMatches[0] = self.__replaceSpecialCharacters(aMatches[0])
            return True, aMatches[0]
        
        return False, aMatches

    def __replaceSpecialCharacters(self, sString):
        return sString.replace('\\/','/').replace('&amp;','&').replace('\xc9','E').replace('&#8211;', '-').replace('&#038;', '&').replace('&rsquo;','\'').replace('\r','').replace('\n','').replace('\t','').replace('&#039;',"'")

    def parse(self, sHtmlContent, sPattern, iMinFoundValue = 1):
        #sHtmlContent = self.__replaceSpecialCharacters(sHtmlContent)
        aMatches = re.compile(sPattern, re.IGNORECASE).findall(sHtmlContent)
        if (len(aMatches) >= iMinFoundValue):                
            return True, aMatches
        return False, aMatches

    def replace(self, sPattern, sReplaceString, sValue):
        return re.sub(sPattern, sReplaceString, sValue)

    def escape(self, sValue):
        return re.escape(sValue)

    def getNumberFromString(self, sValue):
        sPattern = "\d+"
        aMatches = re.findall(sPattern, sValue)
        if (len(aMatches) > 0):
            return aMatches[0]
        return 0

class cPacker():
    def detect(self, source):
        """Detects whether `source` is P.A.C.K.E.R. coded."""
        return source.replace(' ', '').startswith('eval(function(p,a,c,k,e,')

    def unpack(self, source):
        """Unpacks P.A.C.K.E.R. packed js code."""
        payload, symtab, radix, count = self._filterargs(source)

        if count != len(symtab):
            raise self.UnpackingError('Malformed p.a.c.k.e.r. symtab.')

        try:
            
            unbase = Unbaser(radix)
        except TypeError:
            raise self.UnpackingError('Unknown p.a.c.k.e.r. encoding.')

        def lookup(match):
            """Look up symbols in the synthetic symtab."""
            word  = match.group(0)
            return symtab[unbase(word)] or word

        source = re.sub(r'\b\w+\b', lookup, payload)
        return self._replacestrings(source)

    def _cleanstr(self, str):
        str = str.strip()
        if str.find("function") == 0:
            pattern = (r"=\"([^\"]+).*}\s*\((\d+)\)")
            args = re.search(pattern, str, re.DOTALL)
            if args:
                a = args.groups()
                def openload_re(match):
                    c = match.group(0)
                    b = ord(c) + int(a[1])
                    return chr(ord(c) if (90 if c <= "Z" else 122) >= b else b - 26)

                str = re.sub(r"[a-zA-Z]", openload_re, a[0]);
                str = urllib2.unquote(str)

        elif str.find("decodeURIComponent") == 0:
            str = re.sub(r"(^decodeURIComponent\s*\(\s*('|\"))|(('|\")\s*\)$)", "", str);
            str = urllib2.unquote(str)
        elif str.find("\"") == 0:
            str = re.sub(r"(^\")|(\"$)|(\".*?\")", "", str);
        elif str.find("'") == 0:
            str = re.sub(r"(^')|('$)|('.*?')", "", str);

        return str

    def _filterargs(self, source):
        """Juice from a source file the four args needed by decoder."""

        juicer = (r"}\s*\(\s*(.*?)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*\((.*?)\).split\((.*?)\)")
        args = re.search(juicer, source, re.DOTALL)
        if args:
            a = args.groups()
            try:
                return self._cleanstr(a[0]), self._cleanstr(a[3]).split(self._cleanstr(a[4])), int(a[1]), int(a[2])
            except ValueError:
                raise self.UnpackingError('Corrupted p.a.c.k.e.r. data.')

        juicer = (r"}\('(.*)', *(\d+), *(\d+), *'(.*)'\.split\('(.*?)'\)")
        args = re.search(juicer, source, re.DOTALL)
        if args:
            a = args.groups()
            try:
                return a[0], a[3].split(a[4]), int(a[1]), int(a[2])
            except ValueError:
                raise self.UnpackingError('Corrupted p.a.c.k.e.r. data.')

        # could not find a satisfying regex
        raise self.UnpackingError('Could not make sense of p.a.c.k.e.r data (unexpected code structure)')



    def _replacestrings(self, source):
        """Strip string lookup table (list) and replace values in source."""
        match = re.search(r'var *(_\w+)\=\["(.*?)"\];', source, re.DOTALL)

        if match:
            varname, strings = match.groups()
            startpoint = len(match.group(0))
            lookup = strings.split('","')
            variable = '%s[%%d]' % varname
            for index, value in enumerate(lookup):
                source = source.replace(variable % index, '"%s"' % value)
            return source[startpoint:]
        return source
        
    def UnpackingError(Exception):
    #Badly packed source or general error.#
        print Exception
        pass



class Unbaser(object):
    """Functor for a given base. Will efficiently convert
    strings to natural numbers."""
    ALPHABET  = {
        36 : '0123456789abcdefghijklmnopqrstuvwxyz',
        52 : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOP',
        54 : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQR',
        62 : '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        95 : (' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
              '[\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
    }

    def __init__(self, base):
        self.base = base


        # If base can be handled by int() builtin, let it do it for us
        if 2 <= base <= 36:
            self.unbase = lambda string: int(string, base)
        else:
            # Build conversion dictionary cache
            try:
                self.dictionary = dict((cipher, index) for
                    index, cipher in enumerate(self.ALPHABET[base]))
            except KeyError:
                raise TypeError('Unsupported base encoding.')

            self.unbase = self._dictunbaser

    def __call__(self, string):
        return self.unbase(string)

    def _dictunbaser(self, string):
        """Decodes a  value to an integer."""
        ret = 0
        for index, cipher in enumerate(string[::-1]):
            ret += (self.base ** index) * self.dictionary[cipher]
        return ret


class AADecoder(object):

    def __init__(self, aa_encoded_data):
        self.encoded_str = aa_encoded_data
        
        self.b = ["(c^_^o)", "(ﾟΘﾟ)", "((o^_^o) - (ﾟΘﾟ))", "(o^_^o)", 
            "(ﾟｰﾟ)", "((ﾟｰﾟ) + (ﾟΘﾟ))", "((o^_^o) +(o^_^o))", "((ﾟｰﾟ) + (o^_^o))", 
            "((ﾟｰﾟ) + (ﾟｰﾟ))", "((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "(ﾟДﾟ) .ﾟωﾟﾉ", "(ﾟДﾟ) .ﾟΘﾟﾉ", 
            "(ﾟДﾟ) ['c']", "(ﾟДﾟ) .ﾟｰﾟﾉ", "(ﾟДﾟ) .ﾟДﾟﾉ", "(ﾟДﾟ) [ﾟΘﾟ]"]
        

    def is_aaencoded(self):
        idx = self.encoded_str.find("ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3; c=(ﾟΘﾟ) =(ﾟｰﾟ)-(ﾟｰﾟ); ")
        if idx == -1:
            return False

        if self.encoded_str.find("(ﾟДﾟ)[ﾟoﾟ]) (ﾟΘﾟ)) ('_');", idx) == -1:
            return False

        return True;

    def base_repr(self, number, base=2, padding=0):
        digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if base > len(digits):
            base = len(digits)
        
        num = abs(number)
        res = []
        while num:
            res.append(digits[num % base])
            num //= base
        if padding:
            res.append('0' * padding)
        if number < 0:
            res.append('-')
        return ''.join(reversed(res or '0'))

    def decode_char(self, enc_char, radix):
        end_char = "+ "
        str_char = ""
        while enc_char != '':
            found = False
            for i in range(len(self.b)):
                if enc_char.find(self.b[i]) == 0:
                    str_char += self.base_repr(i, radix)
                    enc_char = enc_char[len(self.b[i]):]
                    found = True
                    break
                
            if found == False:
                result = re.search("\((.+?)\)\+ ", enc_char, re.DOTALL)
                if result == None:
                    return ""
                else:
                    enc_char = enc_char[len(result.group(1))+2:]
                    value = self.decode_digit(result.group(1), radix)
                    if value == "":
                        return ""
                    else:
                        str_char += value
            
            enc_char = enc_char[len(end_char):]
        
        return str_char
        
    def decode_digit(self, enc_int, radix):
        # mode 0=+, 1=-
        mode = 0
        value = 0
        
        while enc_int != '':
            found = False
            for i in range(len(self.b)):
                if enc_int.find(self.b[i]) == 0:
                    if mode == 0:
                        value += i
                    else:
                        value -= i
                    enc_int = enc_int[len(self.b[i]):]
                    found = True
                    break
                
            if found == False:
                return ""
            
            enc_int = re.sub('^\s+|\s+$', '', enc_int)
            if enc_int.find("+") == 0:
                mode = 0
            else:
                mode = 1
            
            enc_int = enc_int[1:]
            enc_int = re.sub('^\s+|\s+$', '', enc_int)
        
        return self.base_repr(value, radix)

    
    def decode(self):
        self.encoded_str = re.sub('^\s+|\s+$', '', self.encoded_str)

        # get data
        pattern = (r"\(ﾟДﾟ\)\[ﾟoﾟ\]\+ (.+?)\(ﾟДﾟ\)\[ﾟoﾟ\]\)")
        result = re.search(pattern, self.encoded_str, re.DOTALL)
        if result == None:
            print "AADecoder: data not found"
            return False

        data = result.group(1)

        # hex decode string
        begin_char = "(ﾟДﾟ)[ﾟεﾟ]+"
        alt_char = "(oﾟｰﾟo)+ "

        out = ''
        while data != '':
            # Check new char
            if data.find(begin_char) != 0:
                print "AADecoder: data not found"
                return False

            data = data[len(begin_char):]
            
            # Find encoded char
            enc_char = ""
            if data.find(begin_char) == -1:
                enc_char = data
                data = ""
            else:
                enc_char = data[:data.find(begin_char)]
                data = data[len(enc_char):]

            radix = 8
            # Detect radix 16 for utf8 char
            if enc_char.find(alt_char) == 0:
                enc_char = enc_char[len(alt_char):]
                radix = 16

            str_char = self.decode_char(enc_char, radix)
            if str_char == "":
                print "no match : " + data + "\nout = " + out + "\n"
                return False
            
            out += chr(int(str_char, radix))

        if out == "":
            print "no match : " + data
            return False

        return out


class JJDecoder(object):

    def __init__(self, jj_encoded_data):
        self.encoded_str = jj_encoded_data

        
    def clean(self):
        return re.sub('^\s+|\s+$', '', self.encoded_str)

        
    def checkPalindrome(self, Str):
        startpos = -1
        endpos = -1
        gv, gvl = -1, -1

        index = Str.find('"\'\\"+\'+",')

        if index == 0:
            startpos = Str.find('$$+"\\""+') + 8
            endpos = Str.find('"\\"")())()')
            gv = Str[Str.find('"\'\\"+\'+",')+9:Str.find('=~[]')]
            gvl = len(gv)
        else:
            gv = Str[0:Str.find('=')]
            gvl = len(gv)
            startpos = Str.find('"\\""+') + 5
            endpos = Str.find('"\\"")())()')

        return (startpos, endpos, gv, gvl)

        
    def decode(self):
        
        self.encoded_str = self.clean()
        startpos, endpos, gv, gvl = self.checkPalindrome(self.encoded_str)

        if startpos == endpos:
            raise Exception('No data!')

        data = self.encoded_str[startpos:endpos]

        b = ['___+', '__$+', '_$_+', '_$$+', '$__+', '$_$+', '$$_+', '$$$+', '$___+', '$__$+', '$_$_+', '$_$$+', '$$__+', '$$_$+', '$$$_+', '$$$$+']

        str_l = '(![]+"")[' + gv + '._$_]+'
        str_o   = gv + '._$+'
        str_t = gv + '.__+'
        str_u = gv + '._+'
        
        str_hex = gv + '.'

        str_s = '"'
        gvsig = gv + '.'

        str_quote = '\\\\\\"'
        str_slash = '\\\\\\\\'

        str_lower = '\\\\"+'
        str_upper = '\\\\"+' + gv + '._+'

        str_end = '"+'

        out = ''
        while data != '':
            # l o t u
            if data.find(str_l) == 0:
                data = data[len(str_l):]
                out += 'l'
                continue
            elif data.find(str_o) == 0:
                data = data[len(str_o):]
                out += 'o'
                continue
            elif data.find(str_t) == 0:
                data = data[len(str_t):]
                out += 't'
                continue
            elif data.find(str_u) == 0:
                data = data[len(str_u):]
                out += 'u'
                continue

            # 0123456789abcdef
            if data.find(str_hex) == 0:
                data = data[len(str_hex):]
                
                for i in range(len(b)):
                    if data.find(b[i]) == 0:
                        data = data[len(b[i]):]
                        out += '%x' % i
                        break
                continue

            # start of s block
            if data.find(str_s) == 0:
                data = data[len(str_s):]

                # check if "R
                if data.find(str_upper) == 0: # r4 n >= 128
                    data = data[len(str_upper):] # skip sig
                    ch_str = ''
                    for i in range(2): # shouldn't be more than 2 hex chars
                        # gv + "."+b[ c ]
                        if data.find(gvsig) == 0:
                            data = data[len(gvsig):]
                            for k in range(len(b)): # for every entry in b
                                if data.find(b[k]) == 0:
                                    data = data[len(b[k]):]
                                    ch_str = '%x' % k
                                    break
                        else:
                            break

                    out += chr(int(ch_str, 16))
                    continue

                elif data.find(str_lower) == 0: # r3 check if "R // n < 128
                    data = data[len(str_lower):] # skip sig
                    
                    ch_str = ''
                    ch_lotux = ''
                    temp = ''
                    b_checkR1 = 0
                    for j in range(3): # shouldn't be more than 3 octal chars
                        if j > 1: # lotu check
                            if data.find(str_l) == 0:
                                data = data[len(str_l):]
                                ch_lotux = 'l'
                                break
                            elif data.find(str_o) == 0:
                                data = data[len(str_o):]
                                ch_lotux = 'o'
                                break
                            elif data.find(str_t) == 0:
                                data = data[len(str_t):]
                                ch_lotux = 't'
                                break
                            elif data.find(str_u) == 0:
                                data = data[len(str_u):]
                                ch_lotux = 'u'
                                break

                        # gv + "."+b[ c ]
                        if data.find(gvsig) == 0:
                            temp = data[len(gvsig):]
                            for k in range(8): # for every entry in b octal
                                if temp.find(b[k]) == 0:
                                    if int(ch_str + str(k), 8) > 128:
                                        b_checkR1 = 1
                                        break

                                    ch_str += str(k)
                                    data = data[len(gvsig):] # skip gvsig
                                    data = data[len(b[k]):]
                                    break

                            if b_checkR1 == 1:
                                if data.find(str_hex) == 0: # 0123456789abcdef
                                    data = data[len(str_hex):]
                                    # check every element of hex decode string for a match
                                    for i in range(len(b)):
                                        if data.find(b[i]) == 0:
                                            data = data[len(b[i]):]
                                            ch_lotux = '%x' % i
                                            break
                                    break
                        else:
                            break

                    out += chr(int(ch_str,8)) + ch_lotux
                    continue

                else: # "S ----> "SR or "S+
                    # if there is, loop s until R 0r +
                    # if there is no matching s block, throw error
                    
                    match = 0;
                    n = None

                    # searching for matching pure s block
                    while True:
                        n = ord(data[0])
                        if data.find(str_quote) == 0:
                            data = data[len(str_quote):]
                            out += '"'
                            match += 1
                            continue
                        elif data.find(str_slash) == 0:
                            data = data[len(str_slash):]
                            out += '\\'
                            match += 1
                            continue
                        elif data.find(str_end) == 0: # reached end off S block ? +
                            if match == 0:
                                raise '+ no match S block: ' + data
                            data = data[len(str_end):]
                            break # step out of the while loop
                        elif data.find(str_upper) == 0: # r4 reached end off S block ? - check if "R n >= 128
                            if match == 0:
                                raise 'no match S block n>128: ' + data
                            data = data[len(str_upper):] # skip sig
                            
                            ch_str = ''
                            ch_lotux = ''

                            for j in range(10): # shouldn't be more than 10 hex chars
                                if j > 1: # lotu check
                                    if data.find(str_l) == 0:
                                        data = data[len(str_l):]
                                        ch_lotux = 'l'
                                        break
                                    elif data.find(str_o) == 0:
                                        data = data[len(str_o):]
                                        ch_lotux = 'o'
                                        break
                                    elif data.find(str_t) == 0:
                                        data = data[len(str_t):]
                                        ch_lotux = 't'
                                        break
                                    elif data.find(str_u) == 0:
                                        data = data[len(str_u):]
                                        ch_lotux = 'u'
                                        break

                                # gv + "."+b[ c ]
                                if data.find(gvsig) == 0:
                                    data = data[len(gvsig):] # skip gvsig
                                    for k in range(len(b)): # for every entry in b
                                        if data.find(b[k]) == 0:
                                            data = data[len(b[k]):]
                                            ch_str += '%x' % k
                                            break
                                else:
                                    break # done
                            out += chr(int(ch_str, 16))
                            break # step out of the while loop
                        elif data.find(str_lower) == 0: # r3 check if "R // n < 128
                            if match == 0:
                                raise 'no match S block n<128: ' + data

                            data = data[len(str_lower):] # skip sig

                            ch_str = ''
                            ch_lotux = ''
                            temp = ''
                            b_checkR1 = 0

                            for j in range(3): # shouldn't be more than 3 octal chars
                                if j > 1: # lotu check
                                    if data.find(str_l) == 0:
                                        data = data[len(str_l):]
                                        ch_lotux = 'l'
                                        break
                                    elif data.find(str_o) == 0:
                                        data = data[len(str_o):]
                                        ch_lotux = 'o'
                                        break
                                    elif data.find(str_t) == 0:
                                        data = data[len(str_t):]
                                        ch_lotux = 't'
                                        break
                                    elif data.find(str_u) == 0:
                                        data = data[len(str_u):]
                                        ch_lotux = 'u'
                                        break

                                # gv + "."+b[ c ]
                                if data.find(gvsig) == 0:
                                    temp = data[len(gvsig):]
                                    for k in range(8): # for every entry in b octal
                                        if temp.find(b[k]) == 0:
                                            if int(ch_str + str(k), 8) > 128:
                                                b_checkR1 = 1
                                                break

                                            ch_str += str(k)
                                            data = data[len(gvsig):] # skip gvsig
                                            data = data[len(b[k]):]
                                            break

                                    if b_checkR1 == 1:
                                        if data.find(str_hex) == 0: # 0123456789abcdef
                                            data = data[len(str_hex):]
                                            # check every element of hex decode string for a match
                                            for i in range(len(b)):
                                                if data.find(b[i]) == 0:
                                                    data = data[len(b[i]):]
                                                    ch_lotux = '%x' % i
                                                    break
                                else:
                                    break
                            out += chr(int(ch_str, 8)) + ch_lotux
                            break # step out of the while loop
                        elif (0x21 <= n and n <= 0x2f) or (0x3A <= n and n <= 0x40) or ( 0x5b <= n and n <= 0x60 ) or ( 0x7b <= n and n <= 0x7f ):
                            out += data[0]
                            data = data[1:]
                            match += 1
                    continue
            print 'No match : ' + data
            break
        return out
