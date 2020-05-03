# system libs
import re
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC
from copy import copy
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  
from http.cookies import SimpleCookie
import os
import sys
from os.path import dirname, join
import tempfile
from io import StringIO, BytesIO
import gzip
import queue
import copy


# project libs
#from .utils import *

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
        self.extras = dict(Source=u"Cambridge Dictionary")
        self.base_url = 'https://dictionary.cambridge.org/'
        self.user_url = ''
        self.word = ''
        self.language = 'en'
        self.word_data = []
        self.word_media = {}
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
        self.wordlist_id = ''
        self.word_id = ''
        self.wordlist = []
        self.words_queue = queue.Queue()

    def get_word_defs(self,only_this_meaning=None):

        if not self.language.lower().startswith('en'):
            return
        word = self.word.replace("'", "-")
        if not word and not self.user_url:
            return
        
        self.word_data = []
        self.word_media = []
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
        except HTTPError as e:
                QMessageBox.warning(mw,'URL error',e.reason.strip())
        except URLError as e:
                QMessageBox.warning(mw,'URL error',e.reason.strip())
        if response.info().get('Content-Encoding') == 'gzip':
            response_zip = response.read()
            buf = BytesIO(response_zip)
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            html_doc = data.decode()
        else:
            html_doc = response.read()

        word_soup = BeautifulSoup(html_doc, "html.parser")

        stop_further_parsing = False

        for tag_cald4 in word_soup.find_all(name='div', attrs={'class': 'pr dictionary','data-id':['cald4','cbed','cacd']}):
            for tag_entry in tag_cald4.find_all(name='div', attrs={'class': ['pr entry-body__el','pr idiom-block','entry-body__el clrd js-share-holder']}):
                word_to_add = word_entry()
                tag_dict = tag_cald4.find(name='div',attrs={'class':'cid'})
                word_to_add.word_dictionary_id = tag_dict['id']
                word_to_add.word_dictionary = self.get_dict_name(word_to_add.word_dictionary_id)
                #Different types of entries
                #pr entry-body__el                      - ordinary entry
                #pr idiom-block                         - idiomatic expressions
                #entry-body__el clrd js-share-holder     phrasal verbs
                l1_word = {}
                # Word title
                cur_tag = tag_entry.find(name='div', attrs={'class': 'di-title'})
                if cur_tag:
                    l1_word["word_title"] = prettify_string(cur_tag.text)
                    word_to_add.word_title = prettify_string(cur_tag.text)
                else:
                    return
                    #l1_word["word_title"] = prettify_string(cur_tag.text)
                # Word's grammatical part
                cur_tag = tag_entry.find(name='div', attrs={'class': 'posgram dpos-g hdib lmr-5'})
                if cur_tag:
                    l1_word["word_gram"] = prettify_string(cur_tag.text)
                    word_to_add.word_part_of_speech = prettify_string(cur_tag.text)
                else:
                    l1_word["word_gram"] = ''
                # UK IPA
                cur_tag = tag_entry.find("span", class_=re.compile("uk\sdpron-i\s"))
                if not cur_tag:
                    cur_tag = tag_entry.find("span", attrs={'class':'uk dpron-i'})
                if cur_tag:
                    ipa = cur_tag.find(name='span',attrs={'class':'ipa dipa lpr-2 lpl-1'})
                    if ipa:
                        ipa_text = prettify_string(ipa.text)
                    else:
                        ipa_text = ''
                    l1_word["word_pro_uk"] = 'UK ' + ipa_text
                    word_to_add.word_pro_uk = 'UK ' + ipa_text
                    media_file_tag = cur_tag.find("source", attrs={'type':'audio/mpeg'})
                    if media_file_tag:
                        if media_file_tag['src'] in self.word_media:
                            word_to_add.word_uk_media = self.word_media[media_file_tag['src']]
                        else:
                            l1_word["word_uk_media"] = self.get_tempfile_from_url(self.base_url.rstrip('/') + media_file_tag['src'])
                            word_to_add.word_uk_media = self.get_tempfile_from_url(self.base_url.rstrip('/') + media_file_tag['src'])
                            self.word_media[media_file_tag['src'] ] = word_to_add.word_uk_media
                    else:
                        l1_word["word_uk_media"] = ''
                else:
                    l1_word["word_pro_uk"] = ''
                    l1_word["word_uk_media"] = ''
                # US IPA
                cur_tag = tag_entry.find("span", class_=re.compile("us\sdpron-i\s"))
                if not cur_tag:
                    cur_tag = tag_entry.find("span", attrs={'class':'us dpron-i'})
                if cur_tag:
                    ipa = cur_tag.find(name='span',attrs={'class':'ipa dipa lpr-2 lpl-1'})
                    if ipa:
                        ipa_text = prettify_string(ipa.text)
                    else:
                        ipa_text = ''
                    l1_word["word_pro_us"] = 'US ' + ipa_text
                    word_to_add.word_pro_us = 'US ' + ipa_text
                    media_file_tag = cur_tag.find("source", attrs={'type':'audio/mpeg'})
                    if media_file_tag:
                        if media_file_tag['src'] in self.word_media:
                            word_to_add.word_us_media = self.word_media[media_file_tag['src']]
                        else:
                            l1_word["word_us_media"] = self.get_tempfile_from_url(self.base_url.rstrip('/') + media_file_tag['src'])
                            word_to_add.word_us_media = self.get_tempfile_from_url(self.base_url.rstrip('/') + media_file_tag['src'])
                            self.word_media[media_file_tag['src'] ] = word_to_add.word_uk_media
                    else:
                        l1_word["word_us_media"] = ''
                else:
                    l1_word["word_pro_us"] = ''
                    l1_word["word_us_media"] = ''
                # Image
                tag_picture = tag_entry.find(name='amp-img',attrs={'class':'dimg_i'})
                if tag_picture:
                    if tag_picture.attrs['src'] in self.word_media:
                        word_to_add.word_image = self.word_media[tag_picture.attrs['src']]
                    else:
                        l1_word['word_image'] = self.get_tempfile_from_url(self.base_url.rstrip('/') + tag_picture.attrs['src'])
                        word_to_add.word_image = self.get_tempfile_from_url(self.base_url.rstrip('/') + tag_picture.attrs['src'])
                        self.word_media[tag_picture.attrs['src']] = word_to_add.word_image
                else:
                    l1_word['word_image'] = ''
                l2_word = {}
                suffix = 1
                word_to_copy = copy.deepcopy(word_to_add)
                #Looping through word general definition - like 'draw verb
                #(PICTURE)'
                for html_l2_tag in tag_entry.find_all(name=['div','span'], attrs={'class': ['pos-body','idiom-body didiom-body','pv-body dpv-body']}):
                    # Looping through words specific definitions - l2_meaning
                    # (def & examples)
                    for html_pos_body in html_l2_tag.find_all(attrs={'class': ['pr dsense','pr dsense ','sense-body dsense_b']}):                        
                        tag_l2_word_key = html_pos_body.find(attrs={'class': 'dsense_h'})
                        if not tag_l2_word_key:
                            continue
                        general_m = prettify_string(tag_l2_word_key.get_text())
                        word_to_add.word_general = general_m 
                        l2_word[general_m] = None
                        l2_meaning_key = {}
                        l2_meaning_examples = []
                        l2_meaning = {}
                        for html_meaning in html_pos_body.find_all(name="div", attrs={'class':['def-block ddef_block','def-block ddef_block ']}):
                            tag_l2_meaning = html_meaning.find("div", attrs={'class':'ddef_h'})
                            if not tag_l2_meaning:
                                continue
                            tag_l2_specific_gram = tag_l2_meaning.find("span", attrs={'class':'gram dgram'})
                            word_to_add.word_specific_gram = prettify_string(tag_l2_specific_gram.text if tag_l2_specific_gram else '')
                            tag_l2_specific = tag_l2_meaning.find("div", attrs={'class':'def ddef_d db'})
                            word_to_add.word_specific = prettify_string(tag_l2_specific.text if tag_l2_specific else '')

                            specific_m = prettify_string(tag_l2_meaning.text)
                            l2_meaning[specific_m] = None
                            examples = []
                            for tag_examples in html_meaning.find_all(name='div', attrs={'class': 'examp dexamp'}):
                                    examples.append(prettify_string(tag_examples.text))
                            l2_meaning[specific_m] = examples
                            word_to_add.word_examples = examples
                            self.word_data.append(word_to_add)
                            word_to_add = copy.deepcopy(word_to_copy)
                        l2_word[general_m] = l2_meaning
                       
                    for html_pos_body in html_l2_tag.find_all(name='div', attrs={'class': 'pr','class': 'dsense','class':'dsense-noh'}):
                        general_m = 'UNDEFINED' + str(suffix)
                        word_to_add.word_general = ''
                        l2_word[general_m] = None
                        l2_meaning_key = {}
                        l2_meaning_examples = []
                        l2_meaning = {}
                        for html_meaning in html_pos_body.find_all(name="div", attrs={'class':'def-block','class':'ddef_block'}):
                            tag_l2_meaning = html_meaning.find("div", attrs={'class':'ddef_h'})
                            if not tag_l2_meaning:
                                continue
                            specific_m = prettify_string(tag_l2_meaning.text)

                            tag_l2_specific_gram = tag_l2_meaning.find("span", attrs={'class':'gram dgram'})
                            word_to_add.word_specific_gram = prettify_string(tag_l2_specific_gram.text if tag_l2_specific_gram else '')
                            tag_l2_specific = tag_l2_meaning.find("div", attrs={'class':'def ddef_d db'})
                            word_to_add.word_specific = prettify_string(tag_l2_specific.text if tag_l2_specific else '')

                            l2_meaning[specific_m] = None
                            examples = []
                            for tag_examples in html_meaning.find_all(name='div', attrs={'class': 'examp dexamp'}):
                                    examples.append(prettify_string(tag_examples.text))
                            l2_meaning[specific_m] = examples
                            word_to_add.word_examples = examples
                            self.word_data.append(word_to_add)
                            word_to_add = copy.deepcopy(word_to_copy)
                        l2_word[general_m] = l2_meaning
                        suffix += 1

                l1_word["meanings"] = l2_word
                #self.word_data.append(l1_word)

            if not self.word and self.user_url:
                self.word = self.user_url.split('/')[-1]

        self.word_data.sort(key=lambda x:x.word_dictionary_id)
        #if only_this_meaning != None:
        #    only_l2_word = [] 
        #    found = False
        #    for l1_word in self.word_data:
        #        if found: break
        #        for l2_word_key in l1_word['meanings']:
        #            if found: break
        #            for meaning_key in l1_word['meanings'][l2_word_key]:
        #                #QMessageBox.information(mw,'Auth',meaning_key)
        #                #QMessageBox.information(mw,'Auth',only_this_meaning)
        #                if meaning_key == only_this_meaning:
        #                    only_l2_word = {meaning_key:l1_word['meanings'][l2_word_key][meaning_key]}
        #                    only_meaning = {l2_word_key:only_l2_word}
        #                    only_l1_word = {}
        #                    only_l1_word['meanings'] = only_meaning
        #                    only_l1_word['word_title']  = l1_word['word_title']
        #                    only_l1_word['word_gram']  = l1_word['word_gram']
        #                    only_l1_word['word_pro_uk']  = l1_word['word_pro_uk']
        #                    only_l1_word['word_pro_us']  = l1_word['word_pro_us']
        #                    only_l1_word['word_uk_media']  = l1_word['word_uk_media']
        #                    only_l1_word['word_us_media']  = l1_word['word_us_media']
        #                    only_l1_word['word_image']  = l1_word['word_image']
        #                    only_word_data = []
        #                    only_word_data.append(only_l1_word)
        #                    self.word_data = only_word_data
        #                    found = True
        #                    break

    def get_tempfile_from_url(self, url_in):
        """
        Download raw data from url and put into a tempfile

        Wrapper helper function aronud self.get_data_from_url().
        """
        if not url_in:
            return None
        data = self.get_data_from_url(url_in)
        self.file_extension = '.' + url_in.split('.')[-1]
        # We put the data into RAM first so that we don’t have to
        # clean up the temp file when the get does not work.  (Bad
        # get_data raises all kinds of exceptions that fly through
        # here.)
        tfile = tempfile.NamedTemporaryFile(delete=False, prefix=u'anki_audio_', suffix=self.file_extension)
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
        try:
            response = urllib.request.urlopen(request)
        except URLError as e:
            QMessageBox.warning(mw,'URL error',e.reason.strip())
        
        if 200 != response.code:
            raise ValueError(str(response.code) + ': ' + response.msg)
        return response.read()

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
        self.word_media = {}
        self.word_id = ''
        while self.words_queue.not_empty:
            self.words_queue.get()

    def get_file_entry(self,file,base_name):
        file_entry = {}
        file_entry['base_name'] = base_name
        file_entry['file_extension'] = os.path.splitext(file)[1][1:].strip() 
        file_entry['file_path'] = os.path.abspath(file)
        return file_entry

    def get_all_words_in_list(self, wordlist_link):
        
        config = get_config()
        if config is None:
            return None
        if config['cookie'] is None:
            return None

        #config = {'cookie':'_ga=GA1.3.524435349.1588174459; _fbp=fb.1.1588174461106.1230392959; amp-access=amp-Qrmz-u2Xb_Y3cMl2Q3bfng; preferredDictionaries="english-russian,english,british-grammar,english-polish"; gig_canary=false; gig_canary_ver=10883-5-26471970; gig_bootstrap_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=_gigya_ver3; glt_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=st2.s.AcbHV1W6Uw.RbXpvOop7O50iQKJRETZjNI5HBNexcnW9PpKxJLbfkvRQH9KsxsPKPSBDq0u8uVwFrP1gWTJatV716R7MaYeED9XMoP_FtRl7538RguQK8o.MBBFBrIX2fepHP9KC_0tfgwm0vKlwb7YKTFdidwHl-MeCgIO_23-S1YCvjFlNQqduKyVOCBOoJ_jeiPZaf7HHg.sc3%7CUUID%3D08796647443945aa83ff72063b318baa; glt_3_1Rly-IzDTFvKO75hiQQbkpInsqcVx6RBnqVUozkm1OVH_QRzS-xI3Cwj7qq7hWv5=st2.s.AcbHV1W6Uw.RbXpvOop7O50iQKJRETZjNI5HBNexcnW9PpKxJLbfkvRQH9KsxsPKPSBDq0u8uVwFrP1gWTJatV716R7MaYeED9XMoP_FtRl7538RguQK8o.MBBFBrIX2fepHP9KC_0tfgwm0vKlwb7YKTFdidwHl-MeCgIO_23-S1YCvjFlNQqduKyVOCBOoJ_jeiPZaf7HHg.sc3%7CUUID%3D08796647443945aa83ff72063b318baa; _gig_llp=googleplus; _gig_llu=Alexey; username=Alexey+Morar; logged=logged; remember-me=Z29vZ2xlcGx1cy0xMDk3MjYwMzY5NDU2MjAxNTU3MzE6MTU4OTUyODY3MTE1ODplOWY2NzFlMWYwYTMzNTJkM2JlZGUwNmExNjk3M2E4YQ; beta-redesign=active; _gid=GA1.3.1075438070.1588319079; XSRF-TOKEN=1036d3f0-5421-411a-a861-c2e46af66e38; JSESSIONID=970C4AF288089261DF9D1F8F74AE2DF8-n1'}

        #all_words_in_list = []
        req = urllib.request.Request(wordlist_link)

        #req.add_header("User-Agent",USER_AGENT)
        req.add_header('Accept-Language', 'en-US')
        req.add_header('Cookie', config['cookie'])

        try:
            chrome_options = Options()  
            chrome_options.add_argument("--headless") 
            driver = webdriver.Chrome(join(join(dirname(__file__),'lib'),'chromedriver') , chrome_options=chrome_options)            
            driver.get(self.base_url)
            cookies = SimpleCookie()
            cookies.load(config['cookie'])
            for k,v in cookies.items():
                driver.add_cookie({'name' : k, 'value' : v._value})
            driver.get(wordlist_link)
            html_doc = driver.page_source
            # response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            QMessageBox.warning(mw,'HTTP error',e.reason.strip())
            return 
        
        #html_doc = response.read()
        
        word_soup = BeautifulSoup(html_doc, "html.parser")
        tag_wordlist_id = word_soup.find(name = 'button', attrs={'class':'bt hfr fs14 lp0 lb0 lmt-5 js-plus-wordlist-deleteall'})
        if tag_wordlist_id:
            self.wordlist_id = tag_wordlist_id['data-wordlist-id']
        else:
            return

        tag_all_wl = word_soup.find_all(name = 'li', attrs={'class':'wordlistentry-row'})
        for tag_wl_entry in tag_all_wl:
            word_html_text = tag_wl_entry.find(attrs={'class':'phrase haxa lmr-10'}).get_text()
            word = word_html_text # prettify_string(tag_wl_entry)
            ref = tag_wl_entry.find(name = 'a', attrs={'class':'tb'})['href']
            word_l2_meaning = prettify_string(tag_wl_entry.find(name = 'div', attrs={'class':'def fs16 fs18-s fs19-m lmb-10'}).get_text())
            dataWordID = tag_wl_entry['data-word-id']
            wl_entry = wordlist_entry(word,ref,word_l2_meaning,dataWordID)
            self.wordlist.append(wl_entry)
        driver.quit()
            
    def clear_wordlist(self):
        self.wordlist.clear()

    def delete_word_from_wordlist(self):
        if self.wordlist_id and self.word_id:
            config = get_config()
            if config is None:
                return None
            if config['cookie'] is None:
                return None

            req = urllib.request.Request(CAMBRIDGE_API_BASE+'deleteWordlistEntry')
            req.add_header('Content-Type','application/json')

            req.add_header('Accept-Language', 'en-US')
            req.add_header('Cookie', config['cookie'])
            data = json.dumps({'id': self.word_id, 'wordlistId': self.wordlist_id})
            data = data.encode('ascii')
            try:
                r = urllib.request.urlopen(req, data)
            except HTTPError as e:
                QMessageBox.warning(mw,'URL error',e.reason.strip())
            except URLError as e:
                QMessageBox.warning(mw,'URL error',e.reason.strip())

    def get_dict_name(self,dict_id):

        dicts = {
            'dataset_cald4':'Cambridge Cambridge Advanced Learner''s Dictionary & Thesaurus',
            'dataset_cbed':'Cambridge Business English Dictionary',
            'dataset_cacd':'Cambridge American English Dictionary'}
        if dict_id in dicts:
            return dicts[dict_id]
        else:
            return ''

class wordlist_entry():
    """
    This class represent a single entry from Cambridge Wordlist.
    """

    def __init__(self,word = None, ref = None, l2_meaning = None, dataWordID = None):
        self.word = word
        self.word_url = ref
        self.word_l2_meaning = l2_meaning
        self.word_id = dataWordID
  
class word_entry():
    # word_title, word_gram, word_pro_uk, word_pro_us, word_uk_media, word_us_media, word_image, meanings
    def __init__(self):
        self.word_dictionary_id = ''
        self.word_dictionary = ''
        self.word_title = ''
        self.word_part_of_speech = ''        
        self.word_pro_uk = ''
        self.word_pro_us = ''
        self.word_uk_media = ''
        self.word_us_media = ''
        self.word_image = ''
        self.word_general = ''
        self.word_specific = ''
        self.word_specific_gram = ''
        self.word_examples = []


def prettify_string(in_str):
    if not in_str:
        return ''
    in_str = re.sub(r' +',' ',in_str).strip()
    in_str = re.sub(r'\n','',in_str).strip()
    in_str = re.sub(r':','',in_str).strip()    
    return in_str.strip()

# This code for debugging purposes
#ad = CDDownloader()
##ad.word = 'ad-hominem'
#ad.language = 'en'
#ad.user_url = 'https://dictionary.cambridge.org/dictionary/english/slump'
#ad.get_word_defs()
#ad = None


## This code for testing with WebDriver
#ad = CDDownloader()
#ad.language = 'en'
#ad.user_url = 'https://dictionary.cambridge.org/dictionary/english/tear-up'
#ad.get_all_words_in_list('https://dictionary.cambridge.org/plus/wordlist/21215803_cald')