import re
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC
from copy import copy
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject
import os
import tempfile

from io import StringIO, BytesIO
import gzip

class CDDownloader(QObject):
    """
    Class to download word definitions and media files - audio and picture (if exist) 
    from Cambridge Dictionary.
    Elemtent fields: word_title, word_gram, word_pro_uk, word_pro_us, word_uk_media, word_us_media, word_image, meanings
    """

    def __init__(self):
        super(CDDownloader, self).__init__()
        self.icon_url = 'https://dictionary.cambridge.org/'
        self.url = \
            'https://dictionary.cambridge.org/dictionary/english/'
        #self.url_sound = self.icon_url
        self.extras = dict(
            Source=u"Cambridge Dictionary")
        self.base_url = 'https://dictionary.cambridge.org/'
        self.user_url = ''
        self.word = ''
        self.language = 'en'
        self.word_data = []
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'

    def get_word_defs(self):

        if not self.language.lower().startswith('en'):
            return
        word = self.word.replace("'", "-")
        if not word and not self.user_url:
            return
        
        # self.maybe_get_icon()
        # Do our parsing with BeautifulSoup

        # self.ws = word_soup
        
        if self.user_url:
            req = urllib.request.Request(self.user_url)
        else:
            req = urllib.request.Request(self.url + urllib.parse.quote(word.encode('utf-8')))
        req.add_header("User-Agent",self.user_agent) 
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3')
        req.add_header('Accept-Language', 'en-US')
        req.add_header('Accept-Encoding', 'gzip, deflate, br')

        try:
            response = urllib.request.urlopen(req)
        except e:
            return
        if response.info().get('Content-Encoding') == 'gzip':
            response_zip = response.read()
            buf = BytesIO(response_zip)
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            html_doc = data.decode()
        else:
            html_doc = response.read()

        word_soup = BeautifulSoup(html_doc, "html.parser")

        # Searching for array of word bodiesdownload_files
        #html_tag_entry = word_soup.find(name='div', attrs={'class': 'entry-body'})
        # print(response.getcode())

        #if not html_tag_entry:
        #    return

        for tag_cald4 in word_soup.find_all(name='div', attrs={'class': 'pr dictionary','data-id':'cald4', 'data-id':'cbed'}):
            for tag_entry in tag_cald4.find_all(name='div', attrs={'class': 'pr entry-body__el'}):
                l1_word = {}
                # Word title
                cur_tag = tag_entry.find(name='div', attrs={'class': 'di-title'})
                if cur_tag:
                    l1_word["word_title"] = self.prettify_string(cur_tag.text)
                else:
                    l1_word["word_title"] = self.prettify_string(cur_tag.text)
                # Word's grammatical part
                cur_tag = tag_entry.find(name='div', attrs={'class': 'posgram dpos-g hdib lmr-5'})
                if cur_tag:
                    l1_word["word_gram"] = self.prettify_string(cur_tag.text)
                # UK IPA
                cur_tag = tag_entry.find("span", class_=re.compile("uk\sdpron-i\s"))
                if not cur_tag:
                    cur_tag = tag_entry.find("span", attrs={'class':'uk dpron-i'})
                if cur_tag:
                    ipa = cur_tag.find(name='span',attrs={'class':'ipa dipa lpr-2 lpl-1'})
                    if ipa:
                        ipa_text = self.prettify_string(ipa.text)
                    else:
                        ipa_text = ''
                    l1_word["word_pro_uk"] = 'UK '+ ipa_text
                    media_file_tag = cur_tag.find("source", attrs={'type':'audio/mpeg'})
                    if media_file_tag:
                        l1_word["word_uk_media"] = self.get_tempfile_from_url(self.base_url.rstrip('/')+media_file_tag['src'])
                    else:
                        l1_word["word_uk_media"] = ''
                else:
                    l1_word["word_pro_uk"] = ''
                # US IPA
                cur_tag = tag_entry.find("span", class_=re.compile("us\sdpron-i\s"))
                if not cur_tag:
                    cur_tag = tag_entry.find("span", attrs={'class':'us dpron-i'})
                if cur_tag:
                    ipa = cur_tag.find(name='span',attrs={'class':'ipa dipa lpr-2 lpl-1'})
                    if ipa:
                        ipa_text = self.prettify_string(ipa.text)
                    else:
                        ipa_text = ''
                    l1_word["word_pro_us"] = 'US '+ ipa_text
                    media_file_tag = cur_tag.find("source", attrs={'type':'audio/mpeg'})
                    if media_file_tag:
                        l1_word["word_us_media"] = self.get_tempfile_from_url(self.base_url.rstrip('/')+media_file_tag['src'])
                    else:
                        l1_word["word_us_media"] = ''
                else:
                    l1_word["word_pro_us"] = ''
                # Image
                tag_picture = tag_entry.find(name='amp-img',attrs={'class':'dimg_i'})
                if tag_picture:
                    l1_word['word_image'] = self.base_url.rstrip('/') + tag_picture.attrs['src']
                else:
                    l1_word['word_image'] = ''
                l2_word = {}
                suffix = 1
                #Looping through word general definition - like 'draw verb (PICTURE)'
                for html_l2_tag in tag_entry.find_all(name='div', attrs={'class': 'pos-body'}):
                    # Looping through words specific definitions - l2_meaning (def & examples)
                    for html_pos_body in html_l2_tag.find_all(attrs={'class': 'pr dsense','class': 'pr dsense '}):
                        tag_l2_word_key = html_pos_body.find(attrs={'class': 'dsense_h'})
                        if not tag_l2_word_key:
                            continue
                        general_m = self.prettify_string(tag_l2_word_key.get_text())
                        l2_word[general_m] = None
                        l2_meaning_key = {}
                        l2_meaning_examples = []
                        l2_meaning = {}
                        for html_meaning in html_pos_body.find_all(name="div", attrs={'class':'def-block ddef_block','class':'def-block ddef_block '}):
                            tag_l2_meaning = html_meaning.find("div", attrs={'class':'ddef_h'})
                            if not tag_l2_meaning:
                                continue
                            specific_m = self.prettify_string(tag_l2_meaning.text)
                            l2_meaning[specific_m] = None
                            # A meaning
                            #l2_meanings['to make a picture of something or someone with a pencil or pen:'] = ['Jonathan can draw very well.',
                            #                                                                                  'Draw a line at the bottom of the page.']
                            examples = []
                            for tag_examples in html_meaning.find_all(name='div', attrs={'class': 'examp dexamp'}):
                                    examples.append(self.prettify_string(tag_examples.text))
                            l2_meaning[specific_m] = examples
                        l2_word[general_m] = l2_meaning
                       
                    for html_pos_body in html_l2_tag.find_all(name='div', attrs={'class': 'pr','class': 'dsense','class':'dsense-noh'}):
                        
                        general_m = 'UNDEFINED' + str(suffix)
                        l2_word[general_m] = None
                        l2_meaning_key = {}
                        l2_meaning_examples = []
                        l2_meaning = {}
                        for html_meaning in html_pos_body.find_all(name="div", attrs={'class':'def-block','class':'ddef_block'}):
                            tag_l2_meaning = html_meaning.find("div", attrs={'class':'ddef_h'})
                            if not tag_l2_meaning:
                                continue
                            specific_m = self.prettify_string(tag_l2_meaning.text)
                            l2_meaning[specific_m] = None
                            # A meaning
                            #l2_meanings['to make a picture of something or someone with a pencil or pen:'] = ['Jonathan can draw very well.',
                            #                                                                                  'Draw a line at the bottom of the page.']
                            examples = []
                            for tag_examples in html_meaning.find_all(name='div', attrs={'class': 'examp dexamp'}):
                                    examples.append(self.prettify_string(tag_examples.text))
                            l2_meaning[specific_m] = examples
                        l2_word[general_m] = l2_meaning
                        suffix += 1

                l1_word["meanings"] = l2_word
                self.word_data.append(l1_word)

            if not self.word and self.user_url:
                self.word = self.user_url.split('/')[-1]

    def get_tempfile_from_url(self, url_in):
        """
        Download raw data from url and put into a tempfile

        Wrapper helper function aronud self.get_data_from_url().
        """
        if not url_in:
            return None
        data = self.get_data_from_url(url_in)
        self.file_extension = '.'+url_in.split('.')[-1]
        # We put the data into RAM first so that we don’t have to
        # clean up the temp file when the get does not work. (Bad
        # get_data raises all kinds of exceptions that fly through
        # here.)
        tfile = tempfile.NamedTemporaryFile(
            delete=False, prefix=u'anki_audio_', suffix=self.file_extension)
        tfile.write(data)
        tfile.close()
        return tfile.name

    def get_data_from_url(self, url_in):
        """
        Return raw data loaded from an URL.

        Helper function. Put in an URL and it sets the agent, sends
        the requests, checks that we got error code 200 and returns
        the raw data only when everything is OK.
        """
        request = urllib.request.Request(url_in)
        request.add_header('User-agent', self.user_agent)
        response = urllib.request.urlopen(request)
        if 200 != response.code:
            raise ValueError(str(response.code) + ': ' + response.msg)
        return response.read()

    def prettify_string(self, in_str):
        if not in_str:
            return ''
        in_str = re.sub(r' +',' ',in_str)
        in_str = re.sub(r'\n','',in_str)
        return in_str.strip()

    def clean_up(self):
        for word in self.word_data:
            tmp = word['word_us_media']
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except:
                    pass
        self.user_url = ''
        self.word = ''
        self.word_data = []

    def get_file_entry(self,file,base_name):
        file_entry = {}
        file_entry['base_name']       = base_name
        file_entry['file_extension']  = os.path.splitext(file)[1][1:].strip() 
        file_entry['file_path']       = os.path.abspath(file)
        return file_entry

    def get_all_words_in_user_lists(self):
        #config = get_config()
        #if config is None:
        #    return None
        #if config['cookie'] is None:
        #       return None

        #req = urllib.request.Request(WORDLIST_URL)
        req = urllib.request.Request('https://dictionary.cambridge.org/plus/wordlist')

        #req.add_header("User-Agent",USER_AGENT) 
        req.add_header('Accept-Language', 'en-US')
        #req.add_header('Cookie', config['cookie'])
        req.add_header('Cookie', 'amp-access=amp-sSL5PWF4cDaHSINafMzEUQ; _ga=GA1.3.1644716223.1578470821; _hjid=acc4a0d6-3857-4df7-940c-83951fa6e3c9; _fbp=fb.1.1578470822113.1993653726; gig_bootstrap_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=ver2; _gig_llp=googleplus; _gig_llu=Alexey; username=Alexey+Morar; logged=logged; __cfduid=d04b46ae2d0fa5f14bbf3fc5952a11e0d1578471182; preferredDictionaries=\\\"english,english-russian,british-grammar,english-polish\\\"; beta-redesign=active; glt_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=st2.s.AcbHnI-N5w.yXp9l2H6ONV30QCjaHcydO4GfeUEV8OQNEqn0mxUoWCvAExCc8dXE1iG7rYf7dGD3MoEiIVVmV7wNygerInGw1K8hUTkL8dA3xz73K0zTwc._0srqtoBkktgH2hlRSY1cul1DYMn1ykUtVCP3Whz6zY8tJoI7mvq-LfsXsq5LObq1P8BJ0o3xpJBNI1GJDP9og.sc3%7CUUID%3D08796647443945aa83ff72063b318baa; remember-me=Z29vZ2xlcGx1cy0xMDk3MjYwMzY5NDU2MjAxNTU3MzE6MTU4MTA2MDg3ODYwNzoxZTcyZTI5YmY2ZTk3ZmFlMGRiZDY4NjkwYjhkMzRlNw; _gid=GA1.3.872495736.1580621332; XSRF-TOKEN=f11a82dd-f7d5-42d4-97c2-3a56788ac35c; JSESSIONID=85DEA5FF0EB95092F6A7397C5AE4275C-n1')

        try:
            response = urllib.request.urlopen(req)
        except e:
            return 
        
        html_doc = response.read()
        word_soup = BeautifulSoup(html_doc, "html.parser")
        user_word_lists = []
        tag_wl_personal = word_soup.find(name = 'ul', attrs={'class':'hul-u hax fs-18 wordlist-personal'})
        if tag_wl_personal:
            for tag_wl in tag_wl_personal.find_all(name = 'span', attrs={'class': 'hdib tb lml-15 hoh dipa to-e wl-name'}):
                tag_href = tag_wl.find(name = 'a', attrs={'target': '_top'})
                if tag_href:
                    user_word_list.append(tag_href.text)
                
        for word_list in user_word_lists:
            req = urllib.request.Request(word_list)

            #req.add_header("User-Agent",USER_AGENT) 
            req.add_header('Accept-Language', 'en-US')
            #req.add_header('Cookie', config['cookie'])
            req.add_header('Cookie', 'amp-access=amp-sSL5PWF4cDaHSINafMzEUQ; _ga=GA1.3.1644716223.1578470821; _hjid=acc4a0d6-3857-4df7-940c-83951fa6e3c9; _fbp=fb.1.1578470822113.1993653726; gig_bootstrap_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=ver2; _gig_llp=googleplus; _gig_llu=Alexey; username=Alexey+Morar; logged=logged; __cfduid=d04b46ae2d0fa5f14bbf3fc5952a11e0d1578471182; preferredDictionaries=\\\"english,english-russian,british-grammar,english-polish\\\"; beta-redesign=active; glt_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=st2.s.AcbHnI-N5w.yXp9l2H6ONV30QCjaHcydO4GfeUEV8OQNEqn0mxUoWCvAExCc8dXE1iG7rYf7dGD3MoEiIVVmV7wNygerInGw1K8hUTkL8dA3xz73K0zTwc._0srqtoBkktgH2hlRSY1cul1DYMn1ykUtVCP3Whz6zY8tJoI7mvq-LfsXsq5LObq1P8BJ0o3xpJBNI1GJDP9og.sc3%7CUUID%3D08796647443945aa83ff72063b318baa; remember-me=Z29vZ2xlcGx1cy0xMDk3MjYwMzY5NDU2MjAxNTU3MzE6MTU4MTA2MDg3ODYwNzoxZTcyZTI5YmY2ZTk3ZmFlMGRiZDY4NjkwYjhkMzRlNw; _gid=GA1.3.872495736.1580621332; XSRF-TOKEN=f11a82dd-f7d5-42d4-97c2-3a56788ac35c; JSESSIONID=85DEA5FF0EB95092F6A7397C5AE4275C-n1')

            try:
                response = urllib.request.urlopen(req)
            except e:
                return 
        
            html_doc = response.read()
            word_soup = BeautifulSoup(html_doc, "html.parser")

            for tag_word in word_soup.find_all(name = 'li', attrs={'class':'wordlistentry-row'}):
                print(tag_word.text)
        


# This code for debugging purposes

ad = CDDownloader()
ad.word = 'ad-hominem'
ad.language = 'en'

ad.get_all_words_in_user_lists()
#print(str(ad.word_data))

