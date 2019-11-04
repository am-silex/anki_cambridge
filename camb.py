import re
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC
from copy import copy
from bs4 import BeautifulSoup

from downloader import AudioDownloader
from field_data import FieldData
# from download_entry import DownloadEntry


class CambDownloader(AudioDownloader):
    """Download audio from Cambridge Dictionary."""

    def __init__(self):
        AudioDownloader.__init__(self)
        self.icon_url = 'https://dictionary.cambridge.org/'
        self.url = \
            'https://dictionary.cambridge.org/dictionary/english/'
        self.url_sound = self.icon_url
        self.extras = dict(
            Source=u"Cambridge Dictionary")
        self.base_url = 'https://dictionary.cambridge.org/'

    def get_word_data(self, field_data):

        self.word_data = []
        if not self.language.lower().startswith('en'):
            return
        if not field_data.word:
            return
        if field_data.split:
            return
        word = field_data.word.replace("'", "-")
        # self.maybe_get_icon()
        # Do our parsing with BeautifulSoup

        # self.ws = word_soup
        response = urllib.request.urlopen(self.url + urllib.parse.quote(word.encode('utf-8')))
        html_doc = response.read()
        word_soup = BeautifulSoup(html_doc, "html.parser")

        # Searching for array of word bodiesdownload_files
        html_tag_entry = word_soup.find(name='div', attrs={'class': 'entry-body'})
        # print(response.getcode())

        if not html_tag_entry:
            return

        word_def_list = []
        for tag_entry in html_tag_entry.find_all(name='div', attrs={'class': 'pr entry-body__el'}):
            word_def = {}
            # Word title
            cur_tag = tag_entry.find(name='div', attrs={'class': 'di-title'})
            if not cur_tag:
                continue
            word_def["word_title"] = cur_tag.text
            # Word's grammatical part
            cur_tag = tag_entry.find(name='div', attrs={'class': 'posgram dpos-g hdib lmr-5'})
            if not cur_tag:
                continue
            word_def["word_gram"] = cur_tag.text
            # UK IPA
            cur_tag = tag_entry.find("span", class_=re.compile("uk\sdpron-i"))
            if cur_tag:
                word_def["word_pro_uk"] = cur_tag.text
                media_file_tag = cur_tag.find("audio", class_='i-amphtml-fill-content')
                if media_file_tag:
                    word_def["word_uk_media"] = self.base_url + media_file_tag.text
            # US IPA
            cur_tag = tag_entry.find("span", class_=re.compile("us\sdpron-i"))
            if not cur_tag:
                word_def["word_pro_us"] = cur_tag.text
                media_file_tag = cur_tag.find("audio", class_='i-amphtml-fill-content')
                if media_file_tag:
                    word_def["word_us_media"] = self.base_url + media_file_tag.text
            # Looping through words meanings definitions
            for html_pos_body in tag_entry.find_all(name='div', attrs={'class': 'pos-body'}):
                cur_meaning = {}
                for html_meaning in html_pos_body.find_all("div", class_=re.compile("pr\sdsense")):
                    # A meaning

                    for html_expl in html_meaning.find_all(name='div', attrs={'class': 'def-block ddef_block'}):
                        cur_tag = html_expl.find(name='div', attrs={'class': 'ddef_h'})
                        if not cur_tag:
                            continue
                        use_list = []
                        for use_example in html_expl.find_all(name='div', attrs={'class': 'examp dexamp'}):
                            use_list.append(use_example.text)
                        cur_meaning[cur_tag.text] = use_list
                word_def["meanings"] = cur_meaning
                # print(html_meaning.text)
            word_def_list.append(word_def)

        self.word_data = word_def_list


ad = CambDownloader()
ad.word_data = {"draw"}
ad.language = 'en'
fd = FieldData("","","draw")

ad.get_word_data(fd)
print(ad.word_data)
