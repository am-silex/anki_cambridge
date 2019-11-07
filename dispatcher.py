from .Cambridge import CambDownloader

def get_word_definitions_from_link(link):
    if not link:
        QM
        raise RuntimeError("Link is not provided")

    cd = CambDownloader(true)
    cd.user_url = link
    return cd.get_word_data()
    

