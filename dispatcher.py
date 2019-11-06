from .Cambridge import CambDownloader

def get_word_definitions_from_link(self, link = ''):
    if not link:
        raise RuntimeError("Link is not provided")

    cd = CambDownloader(true)
    cd.user_url = link
    return cd.get_word_data()
    

