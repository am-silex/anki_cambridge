# system libs
import re
from urllib.error import *
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen
from abc import ABC
from copy import copy
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject
from http.cookies import SimpleCookie
import os
import sys
from os.path import dirname, join
import tempfile
from io import StringIO, BytesIO
import gzip
import queue
import copy
import json


# project libs
from .utils import *

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
        self.wordlist_entry = None
        self.words_queue = queue.Queue()
        #Definitions
        self.cambridge_plus_url = 'https://dictionary.cambridge.org/plus/'
        self.cambridge_plus_api_url = 'https://dictionary.cambridge.org/plus/api/'
        self.config = get_config()
        self.req = None

        if self.config is None:
            raise Exception("Config file error")
        if self.config['cookie'] is None:
            raise Exception("Config doesn't have cookie")

    def get_word_defs(self):
        
        if not self.language.lower().startswith('en'):
            return
        word = self.word.replace("'", "-")
        if not word and not self.user_url:
            return
        
        self.word_data.clear()
        # self.maybe_get_icon()
        # Do our parsing with BeautifulSoup

        if self.user_url:
            self.req = Request(self.user_url)
        else:
            self.req = Request(self.url + quote(word.encode('utf-8')))
    
        self._fill_request_headers()

        try:
            response = urlopen(self.req)
        except HTTPError as e:
                QMessageBox.warning(mw,'URL error',e.reason.strip())
                return
        except URLError as e:
                QMessageBox.warning(mw,'URL error',e.reason.strip())
                return
        html_doc = response.read()

        word_soup = BeautifulSoup(html_doc, "html.parser")

        stop_further_parsing = False

        for tag_cald4 in word_soup.find_all(name='div', attrs={'class': 'pr dictionary','data-id':['cald4','cbed','cacd','cald4-us']}):
            for tag_entry in tag_cald4.find_all(name='div', attrs={'class': ['pr entry-body__el','pr idiom-block','entry-body__el clrd js-share-holder']}):
                word_to_add = word_entry()
                tag_dict = tag_cald4.find(name='div',attrs={'class':'cid'})
                word_to_add.word_dictionary_id = tag_dict['id']
                word_to_add.word_dictionary = self.get_dict_name(word_to_add.word_dictionary_id)
                #Different types of entries
                #pr entry-body__el - ordinary entry
                #pr idiom-block - idiomatic expressions
                #entry-body__el clrd js-share-holder phrasal verbs
                l1_word = {}
                # Word title
                cur_tag = tag_entry.find(name='div', attrs={'class': 'di-title'})
                if cur_tag:
                    word_to_add.word_title = self._prettify_string(cur_tag.text)
                else:
                    return
                # Word's grammatical part
                cur_tag = tag_entry.find(name='div', attrs={'class': 'posgram dpos-g hdib lmr-5'})
                if cur_tag:
                    word_to_add.word_part_of_speech = self._prettify_string(cur_tag.text)
                else:
                    l1_word["word_gram"] = ''
                # UK IPA
                cur_tag = tag_entry.find("span", class_=re.compile("uk\sdpron-i\s"))
                if not cur_tag:
                    cur_tag = tag_entry.find("span", attrs={'class':'uk dpron-i'})
                if cur_tag:
                    ipa = cur_tag.find(name='span',attrs={'class':'ipa dipa lpr-2 lpl-1'})
                    if ipa:
                        ipa_text = self._prettify_string(ipa.text)
                    else:
                        ipa_text = ''
                    word_to_add.word_pro_uk = 'UK ' + ipa_text
                    media_file_tag = cur_tag.find("source", attrs={'type':'audio/mpeg'})
                    if media_file_tag:
                        if media_file_tag['src'] in self.word_media:
                            word_to_add.word_uk_media = self.word_media[media_file_tag['src']]
                        else:
                            word_to_add.word_uk_media = self.get_tempfile_from_url(self.base_url.rstrip('/') + media_file_tag['src'])
                            self.word_media[media_file_tag['src']] = word_to_add.word_uk_media
                # US IPA
                cur_tag = tag_entry.find("span", class_=re.compile("us\sdpron-i\s"))
                if not cur_tag:
                    cur_tag = tag_entry.find("span", attrs={'class':'us dpron-i'})
                if cur_tag:
                    ipa = cur_tag.find(name='span',attrs={'class':'ipa dipa lpr-2 lpl-1'})
                    if ipa:
                        ipa_text = self._prettify_string(ipa.text)
                    else:
                        ipa_text = ''
                    l1_word["word_pro_us"] = 'US ' + ipa_text
                    word_to_add.word_pro_us = 'US ' + ipa_text
                    media_file_tag = cur_tag.find("source", attrs={'type':'audio/mpeg'})
                    if media_file_tag:
                        if media_file_tag['src'] in self.word_media:
                            word_to_add.word_us_media = self.word_media[media_file_tag['src']]
                        else:
                            word_to_add.word_us_media = self.get_tempfile_from_url(self.base_url.rstrip('/') + media_file_tag['src'])
                            self.word_media[media_file_tag['src']] = word_to_add.word_uk_media
               
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
                        general_m = self._prettify_string(tag_l2_word_key.get_text())
                        word_to_add.word_general = general_m 
                        l2_word[general_m] = None
                        l2_meaning_key = {}
                        l2_meaning_examples = []
                        l2_meaning = {}
                        for html_meaning in html_pos_body.find_all(name="div", attrs={'class':['def-block ddef_block','def-block ddef_block ']}):
                            tag_l2_meaning = html_meaning.find("div", attrs={'class':'ddef_h'})
                            if not tag_l2_meaning:
                                continue
                            # Image
                            tag_picture = html_meaning.find(name='amp-img',attrs={'class':'dimg_i'})
                            if tag_picture:
                                if tag_picture.attrs['src'] in self.word_media:
                                    word_to_add.word_image = self.word_media[tag_picture.attrs['src']]
                                else:
                                    word_to_add.word_image = self.get_tempfile_from_url(self.base_url.rstrip('/') + tag_picture.attrs['src'])
                                    self.word_media[tag_picture.attrs['src']] = word_to_add.word_image
                            word_to_add.senseId = html_meaning.attrs['data-wl-senseid']
                            tag_l2_specific_gram = tag_l2_meaning.find("span", attrs={'class':'gram dgram'})
                            word_to_add.word_specific_gram = self._prettify_string(tag_l2_specific_gram.text if tag_l2_specific_gram else '')
                            tag_usage = tag_l2_meaning.find("span", attrs={'class':'usage dusage'})
                            if tag_usage:
                                word_to_add.usage = self._prettify_string(tag_usage.text)
                            tag_l2_specific = tag_l2_meaning.find("div", attrs={'class':'def ddef_d db'})
                            word_to_add.word_specific = self._prettify_string(tag_l2_specific.text if tag_l2_specific else '')
                            specific_m = self._prettify_string(tag_l2_meaning.text)
                            l2_meaning[specific_m] = None
                            examples = []
                            for tag_examples in html_meaning.find_all(name='div', attrs={'class': 'examp dexamp'}):
                                    examples.append(self._prettify_string(tag_examples.text))
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
                            # Image
                            tag_picture = html_meaning.find(name='amp-img',attrs={'class':'dimg_i'})
                            if tag_picture:
                                if tag_picture.attrs['src'] in self.word_media:
                                    word_to_add.word_image = self.word_media[tag_picture.attrs['src']]
                                else:
                                    word_to_add.word_image = self.get_tempfile_from_url(self.base_url.rstrip('/') + tag_picture.attrs['src'])
                                    self.word_media[tag_picture.attrs['src']] = word_to_add.word_image
                            specific_m = self._prettify_string(tag_l2_meaning.text)
                            word_to_add.senseId = html_meaning.attrs['data-wl-senseid']
                            tag_l2_specific_gram = tag_l2_meaning.find("span", attrs={'class':'gram dgram'})
                            word_to_add.word_specific_gram = self._prettify_string(tag_l2_specific_gram.text if tag_l2_specific_gram else '')
                            tag_usage = tag_l2_meaning.find("span", attrs={'class':'usage dusage'})
                            if tag_usage:
                                word_to_add.usage = self._prettify_string(tag_usage.text)
                            tag_l2_specific = tag_l2_meaning.find("div", attrs={'class':'def ddef_d db'})
                            word_to_add.word_specific = self._prettify_string(tag_l2_specific.text if tag_l2_specific else '')
                            l2_meaning[specific_m] = None
                            examples = []
                            for tag_examples in html_meaning.find_all(name='div', attrs={'class': 'examp dexamp'}):
                                    examples.append(self._prettify_string(tag_examples.text))
                            l2_meaning[specific_m] = examples
                            word_to_add.word_examples = examples
                            self.word_data.append(word_to_add)
                            word_to_add = copy.deepcopy(word_to_copy)
                        l2_word[general_m] = l2_meaning
                        suffix += 1

                l1_word["meanings"] = l2_word

            if not self.word and self.user_url:
                self.word = self.user_url.split('/')[-1]

        self.word_data.sort(key=lambda x:x.word_dictionary_id)

    def get_tempfile_from_url(self, url_in):
        """
        Download raw data from url and put into a tempfile

        Wrapper helper function aronud self.get_data_from_url().
        """
        if not url_in:
            return None
        data = self.get_data_from_url(url_in)
        if data == None:
            return None

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
        self.req = Request(url_in)
        self._fill_request_headers()
        try:
            response = urlopen(self.req)
        except URLError as e:
            return None
        
        if 200 != response.code:
            raise ValueError(str(response.code) + ': ' + response.msg)
        return response.read()

    def clean_up(self):
        self.user_url = ''
        self.word = ''
        self.word_data.clear()
        self.word_media = {}        
        self.wordlist.clear()
        self.word_id = ''
        self.wordlist_entry = None

    def get_file_entry(self,file,base_name):
        file_entry = {}
        file_entry['base_name'] = base_name
        file_entry['file_extension'] = os.path.splitext(file)[1][1:].strip() 
        file_entry['file_path'] = os.path.abspath(file)
        return file_entry

    def fetch_wordlist_entries(self, wordlist_id):

        for n in range(1,100):
            
            # https://dictionary.cambridge.org/plus/wordlist/21215803/entries/100/
        
            url_for_request = urljoin(self.base_url,'plus/wordlist/')
            url_for_request = urljoin(url_for_request,str(wordlist_id) + '/entries/')
            url_for_request = urljoin(url_for_request,str(n) + '/')        

            self.req = Request(url_for_request)
            self._fill_request_headers()
            self.req.add_header('Accept', 'application/json')            
            self.req.add_header('Cookie', self.config['cookie'])            

            response = urlopen(self.req)
            word_list_json = json.loads(response.read())
            if not word_list_json:
               break
            
            for word_in_response in word_list_json:
                wl_entry = wordlist_entry()
                wl_entry.wordlist_id = word_in_response['wordlistId']
                wl_entry.word_id = word_in_response['id']
                wl_entry.senseId = word_in_response['senseId']
                wl_entry.word_url = word_in_response['entryUrl']
                wl_entry.definition = word_in_response['definition']
                wl_entry.soundUKMp3 = word_in_response['soundUKMp3']
                wl_entry.soundUSMp3 = word_in_response['soundUSMp3']
                wl_entry.dictCode = word_in_response['dictCode']
                wl_entry.headword = word_in_response['headword']
                self.wordlist.append(wl_entry)
                #{
                #"id": 26061590,
                #"entryId": "walk-on-part",
                #"headword": "walk-on part",
                #"senseId": "ID_00035581_01",
                #"dictCode": "English",
                #"definition": "A walk-on part in a play is a very small part
                #in which the actor is on the stage for a short time and speaks
                #very few or no words.",
                #"translation": "",
                #"pos": "noun",
                #"soundUK": "/CUK01223",
                #"soundUS": "/CUS02231",
                #"soundUKMp3":
                #"https://dictionary.cambridge.org/media/english/uk_pron/c/cuk/cuk01/cuk01223.mp3",
                #"soundUKOgg":
                #"https://dictionary.cambridge.org/media/english/uk_pron_ogg/c/cuk/cuk01/cuk01223.ogg",
                #"soundUSMp3":
                #"https://dictionary.cambridge.org/media/english/us_pron/c/cus/cus02/cus02231.mp3",
                #"soundUSOgg":
                #"https://dictionary.cambridge.org/media/english/us_pron_ogg/c/cus/cus02/cus02231.ogg",
                #"wordlistId": 21215803,
                #"entryUrl":
                #"https://dictionary.cambridge.org/dictionary/english/walk-on-part"
                #},
      
    def delete_word_from_wordlist(self, wl_entry):

        self.req = Request(self.cambridge_plus_api_url + 'deleteWordlistEntry')
        self._fill_request_headers()
        self.req.add_header('Content-Type','application/json')

        self.req.add_header('Cookie', self.config['cookie'])
        data = json.dumps({'id': wl_entry.word_id, 'wordlistId': wl_entry.wordlist_id})
        data = data.encode('ascii')
        r = urlopen(self.req, data)

    def get_dict_name(self,dict_id):

        dicts = {
            'dataset_cald4':'Cambridge Advanced Learner''s Dictionary & Thesaurus',
            'dataset_cbed':'Cambridge Business English Dictionary',
            'dataset_cacd':'Cambridge American English Dictionary'}
        if dict_id in dicts:
            return dicts[dict_id]
        else:
            return ''

    def find_word_by_definition(self, definition):
        for wd_entry in self.word_data:
            if wd_entry.word_specific == definition:
                return self.word_data.pop()
        return None

    def find_word_by_wl_entry(self, wl_entry):
        wd_entries = list(filter(lambda wd_entry: wd_entry.senseId == wl_entry.senseId, self.word_data))
        if len(wd_entries) == 1:
            return wd_entries[0]

    def _prettify_string(self, in_str):
        if not in_str:
            return ''
        in_str = re.sub(r' +',' ',in_str).strip()
        in_str = re.sub(r'\n','',in_str).strip()
        in_str = re.sub(r':$','',in_str).strip()    
        return in_str.strip()

    def _fill_request_headers(self):
        self.req.add_header("Host","dictionary.cambridge.org")
        self.req.add_header('Accept-Language', 'en-US')
        self.req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36')        


class wordlist_entry():
    """
    This class represent a single entry from Cambridge Wordlist.
    """

    def __init__(self,word=None, ref=None, l2_meaning=None, dataWordID=None, wordlist_id=None):
        self.wordlist_id = wordlist_id
        self.senseId = ''
        self.word = word
        self.word_url = ref
        self.word_l2_meaning = l2_meaning
        self.word_id = dataWordID
        self.definition = l2_meaning
        self.dictCode = ''
        self.soundUKMp3 = ''
        self.soundUSMp3 = ''
  
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
        self.usage = ''
        self.senseId = ''



#def self._prettify_string(self,in_str):
#    if not in_str:
#        return ''
#    in_str = re.sub(r' +',' ',in_str).strip()
#    in_str = re.sub(r'\n','',in_str).strip()
#    in_str = re.sub(r':','',in_str).strip()    
#    return in_str.strip()

# This code for debugging purposes
#ad = CDDownloader()
#ad.language = 'en'
#ad.user_url = 'https://dictionary.cambridge.org/dictionary/english/pit'
#ad.get_word_defs()
#ad = None


## This code for testing with WebDriver
#ad = CDDownloader()
#ad.language = 'en'
##ad.user_url = 'https://dictionary.cambridge.org/dictionary/english/tear-up'
##ad.get_all_words_in_list('https://dictionary.cambridge.org/plus/wordlist/21215803_cald')
#ad.fetch_wordlist_entries('21215803')
#ad = None