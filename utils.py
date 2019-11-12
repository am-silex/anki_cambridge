import os
from random import randint
import json
import socket
import ssl

from aqt import mw
from anki import notes

from . import styles


fields = ['en', 'transcription',
          'ru', 'picture_name',
          'sound_name', 'context']

def add_word(word, model):
    # TODO: Use picture_name and sound_name to check
    #  if update is needed and don't download media if not
    collection = mw.col
    note = notes.Note(collection, model)
    note = fill_note(word, note)
    # TODO: Rewrite to use is_duplicate()
    word_value = word.get('wordValue') if word.get('wordValue') else 'NO_WORD_VALUE'
    dupes = collection.findDupes("en", word_value)
    # a hack to support words with apostrophes
    note_dupes1 = collection.findNotes("en:'%s'" % word_value)
    note_dupes2 = collection.findNotes('en:"%s"' % word_value)
    note_dupes = note_dupes1 + note_dupes2
    if not dupes and not note_dupes:
        collection.addNote(note)
    # TODO: Update notes if translation or tags (user wordsets) changed
    elif (note['picture_name'] or note['sound_name']) and note_dupes:
        # update existing notes with new pictures and sounds in case
        # they have been changed in LinguaLeo's UI
        for nid in note_dupes:
            note_in_db = notes.Note(collection, id=nid)
            # a dirty hack below until a new field in the model is introduced
            # put a space before or after a *sound* field of an existing note if you want it to be updated
            # if a note has no picture or sound, it will be updated anyway
            # TODO: Check if hack is still needed, remove if not
            sound_name = note_in_db['sound_name']
            sound_name = sound_name.replace("&nbsp;", " ")
            note_needs_update = sound_name != sound_name.strip()
            if note['picture_name'] and (note_needs_update or not note_in_db['picture_name'].strip()):
                note_in_db['picture_name'] = note['picture_name']
            if note['sound_name'] and (note_needs_update or not note_in_db['sound_name'].strip()):
                note_in_db['sound_name'] = note['sound_name']
            note_in_db.flush()
    # TODO: Check if it is possible to update Anki's media collection to remove old (unused) media

def create_templates(collection):
    template_eng = collection.models.newTemplate('en -> ru')
    template_eng['qfmt'] = styles.en_question
    template_eng['afmt'] = styles.en_answer
    template_ru = collection.models.newTemplate('ru -> en')
    template_ru['qfmt'] = styles.ru_question
    template_ru['afmt'] = styles.ru_answer
    return (template_eng, template_ru)


def create_new_model(collection, fields, model_css):
    model = collection.models.new("LinguaLeo_model")
    model['tags'].append("LinguaLeo")
    model['css'] = model_css
    for field in fields:
        collection.models.addField(model, collection.models.newField(field))
    template_eng, template_ru = create_templates(collection)
    collection.models.addTemplate(model, template_eng)
    collection.models.addTemplate(model, template_ru)
    model['id'] = randint(100000, 1000000)  # Essential for upgrade detection
    collection.models.update(model)
    return model


def is_model_exist(collection, fields):
    name_exist = 'Standard with audio fields' in collection.models.allNames()
    if name_exist:
        fields_ok = collection.models.fieldNames(collection.models.byName(
                                                'Standard with audio fields')) == fields
    else:
        fields_ok = False
    return name_exist and fields_ok


def prepare_model(collection, fields, model_css):
    """
    Returns a model for our future notes.
    Creates a deck to keep them.
    """
    if is_model_exist(collection, fields):
        model = collection.models.byName('LinguaLeo_model')
    else:
        model = create_new_model(collection, fields, model_css)
    # TODO: Move Deck name to config?
    # Create a deck "LinguaLeo" and write id to deck_id
    model['did'] = collection.decks.id('LinguaLeo')
    collection.models.setCurrent(model)
    collection.models.save(model)
    return model