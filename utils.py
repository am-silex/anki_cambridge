import os
from random import randint
import json
import socket
import ssl

from aqt import mw
from anki import notes

from . import styles
from ._names import *
from .mediafile_utils import *

from PyQt5.QtWidgets import QMessageBox


fields = ['Word','Examples','Definition','Audio','Picture','Pronunciation','Grammar','Meaning','SynonymAntonym']

def fill_note(word_entry, note):

    config = get_config()
    pronunciation_uk = config['pronunciation_uk'] if 'pronunciation_uk' in config else True
    pronunciation_us = config['pronunciation_us'] if 'pronunciation_us' in config else True

    note['Word']            = word_entry.word_title
    note['Examples']        = "<br> ".join(word_entry.word_examples)
    note['Definition']      = word_entry.word_specific
    note['Pronunciation']   = ""
    if pronunciation_uk:
        note['Pronunciation'] += word_entry.word_pro_uk + ' ' 
    if pronunciation_us:
        note['Pronunciation'] += word_entry.word_pro_us
    note['Grammar']         = word_entry.word_part_of_speech
    note['Meaning']         = word_entry.word_general
    audio_field = ''
    if word_entry.word_uk_media and pronunciation_uk:
        try:
            f_entry = get_file_entry(word_entry.word_uk_media,note['Word'])
            audio_field = audio_field + '[sound:' + unmunge_to_mediafile(f_entry)+'] '
        except :
            pass
    try:
        if word_entry.word_us_media and pronunciation_us:
            f_entry = get_file_entry(word_entry.word_us_media,note['Word'])
            audio_field = audio_field + '[sound:' + unmunge_to_mediafile(f_entry)+'] '
    except :
        pass        
    
    note['Audio'] = audio_field
    #Fetching picture
    #picture_name = word.get('Picture').split('/')[-1] if word.get('Picture') else ''
    picture_field = ''
    f_picture = word_entry.word_image
    if f_picture:
        f_entry = get_file_entry(f_picture,note['Word'])
        picture_field = '<img src="' + unmunge_to_mediafile(f_entry) + '">'
    note['Picture'] = picture_field
    return note

def add_word(word, model):
    # TODO: Use picture_name and sound_name to check
    #  if update is needed and don't download media if not
    collection = mw.col
    note = notes.Note(collection, model)
    note = fill_note(word, note)
    
    # TODO: Rewrite to use is_duplicate()
            #word_value = word.get('wordValue') if word.get('wordValue') else 'NO_WORD_VALUE'
            #dupes = collection.findDupes("en", word_value)
            ## a hack to support words with apostrophes
            #note_dupes1 = collection.findNotes("en:'%s'" % word_value)
            #note_dupes2 = collection.findNotes('en:"%s"' % word_value)
            #note_dupes = note_dupes1 + note_dupes2
    collection.addNote(note)
   
def add_word_to_collection(word_entry, collection):

    model = prepare_model(mw.col, fields, styles.model_css)
    note = notes.Note(collection, model)
    note = fill_note(word_entry, note)
    
    collection.addNote(note)


    #if not dupes and not note_dupes:
    #    collection.addNote(note)
    ## TODO: Update notes if translation or tags (user wordsets) changed
    #elif (note['picture_name'] or note['sound_name']) and note_dupes:
    #    # update existing notes with new pictures and sounds in case
    #    # they have been changed in LinguaLeo's UI
    #    for nid in note_dupes:
    #        note_in_db = notes.Note(collection, id=nid)
    #        # a dirty hack below until a new field in the model is introduced
    #        # put a space before or after a *sound* field of an existing note if you want it to be updated
    #        # if a note has no picture or sound, it will be updated anyway
    #        # TODO: Check if hack is still needed, remove if not
    #        sound_name = note_in_db['sound_name']
    #        sound_name = sound_name.replace("&nbsp;", " ")
    #        note_needs_update = sound_name != sound_name.strip()
    #        if note['picture_name'] and (note_needs_update or not note_in_db['picture_name'].strip()):
    #            note_in_db['picture_name'] = note['picture_name']
    #        if note['sound_name'] and (note_needs_update or not note_in_db['sound_name'].strip()):
    #            note_in_db['sound_name'] = note['sound_name']
    #        note_in_db.flush()
    ## TODO: Check if it is possible to update Anki's media collection to remove old (unused) media

def create_templates(collection):
    template_Recognition = collection.models.newTemplate('Recognition')
    template_Recognition['qfmt'] = styles.std_word
    template_Recognition['afmt'] = styles.std_word_def_sound
    template_Recall = collection.models.newTemplate('Recall')
    template_Recall['qfmt'] = styles.std_def
    template_Recall['afmt'] = styles.std_def_word_sound
    template_Sound = collection.models.newTemplate('Sound')
    template_Sound['qfmt'] = styles.std_sound
    template_Sound['afmt'] = styles.std_sound_word_def
    return (template_Recognition, template_Recall, template_Sound)

def create_new_model(collection, fields, model_css):
    model = collection.models.new(CAMBRIDGE_MODEL)
    #Seems like tag key is depricated
    #model['tags'].append("Cambridge")
    #model['css'] = model_css
    for field in fields:
        collection.models.addField(model, collection.models.newField(field))
    template_Recognition, template_Recall, template_Sound = create_templates(collection)
    collection.models.addTemplate(model, template_Recognition)
    collection.models.addTemplate(model, template_Recall)
    collection.models.addTemplate(model, template_Sound)
    model['id'] = randint(100000, 1000000)  # Essential for upgrade detection
    collection.models.update(model)
    return model

def is_model_exist(collection, fields):
    name_exist = CAMBRIDGE_MODEL in collection.models.allNames()
    if name_exist:
        fields_ok = collection.models.fieldNames(collection.models.byName(
                                                CAMBRIDGE_MODEL)) == fields
    else:
        fields_ok = False
    return name_exist and fields_ok

def prepare_model(collection, fields, model_css):
    """
    Returns a model for our future notes.
    Creates a deck to keep them.
    """
    if is_model_exist(collection, fields):
        model = collection.models.byName(CAMBRIDGE_MODEL)
    else:
        model = create_new_model(collection, fields, model_css)
    # TODO: Move Deck name to config?
    # Create a deck "Cambridge" and write id to deck_id
    model['did'] = collection.decks.id('Cambridge')
    collection.models.setCurrent(model)
    collection.models.save(model)
    return model

def get_cambridge_model(collection):
    """
    Get model named defined in STANDARD_MODEL_WITH_AUDIO literal
    """
    return collection.models.byName(CAMBRIDGE_MODEL)

def is_valid_ascii(url):
    """
    Check an url if it is a valid ascii string
    After the LinguaLeo update some images
    have broken links with cyrillic characters
    """
    if url == '':
        return True
    try:
        url.encode('ascii')
    except:
        return False
    return True

def get_module_name():

    return __name__.split(".")[0]

def get_addon_dir():
    root = mw.pm.addonFolder()
    addon_dir = os.path.join(root, get_module_name())
    return addon_dir

def get_cookies_path():
    """
    Returns a full path to cookies.txt in the user_files folder
    :return:
    """
    # user_files folder in the current addon's dir
    uf_dir = os.path.join(get_addon_dir(), 'user_files')
    # Create a folder if doesn't exist
    if not os.path.exists(uf_dir):
        try:
            os.makedirs(uf_dir)
        except:
            # TODO: Improve error handling
            return None
    return os.path.join(uf_dir, 'cookies.txt')

def get_config():
    # Load config from config.json file
    #if getattr(getattr(mw, "addonManager", None), "getConfig", None):
    #    config = mw.addonManager.getConfig(get_module_name())
    #else:
        try:
            config_file = os.path.join(get_addon_dir(), 'config.json')
            with open(config_file, 'r') as f:
                config = json.loads(f.read())
        except IOError:
            try:
                config = {'cookie':'', 'pronunciation_uk': True, 'pronunciation_us': True}
                config_file = os.path.join(get_addon_dir(), 'config.json')
                with open(config_file, 'w') as f:
                    json.dump(config, f, sort_keys=True, indent=2)
                f.close()
                with open(config_file, 'r') as f:
                    config = json.loads(f.read())
            except:
                config = None
        return config
    
def update_config(config):
    #if getattr(getattr(mw, "addonManager", None), "writeConfig", None):
    #    mw.addonManager.writeConfig(get_module_name(), config)
    #else:
    try:
        config_file = os.path.join(get_addon_dir(), 'config.json')
        with open(config_file, 'w') as f:
            json.dump(config, f, sort_keys=True, indent=2)
    except:
        # TODO: Improve error handling
        #pass
        raise SystemError
    
def get_config_dict():
    config = {}
    config['cookie'] = ''
    config['pronunciation_uk'] = True
    config['pronunciation_us'] = True
    return config

def find_note_with_url_pictures(AddonDialog):
    query = "Picture:*https*"
    foundCardsIDs = mw.col.findNotes(query)
    AddonDialog.progress.setMaximum(len(foundCardsIDs))
    n = 0
    for f_noteID in foundCardsIDs:
        f_note = mw.col.getNote(f_noteID)
        f_picture = mw.cddownloader.get_tempfile_from_url(f_note['Picture'])
        picture_name = f_note['Word'].split('/')[-1] if f_note['Word'] else ''
        f_entry = get_file_entry(f_picture,picture_name)
        picture_field = '<img src="' + unmunge_to_mediafile(f_entry) + '">'
        f_note['Picture'] = picture_field 
        f_note.flush()
        n =+ 1
        AddonDialog.progress.setValue(n)




