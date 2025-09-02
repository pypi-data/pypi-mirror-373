from iso639 import Lang
from datetime import datetime


def lang_to_iso639_1(lang: str, unk_code: str = "unk") -> str:
    """ Converts language into ISO-639-1 standard.
    Input can be any language code in a valid ISO-639
    standard or even a full name of the language,
    e.g. "Estonian".

    Parameters
    -----------
    lang: str
        Language code in any valid ISO-639 standard.

    unk_code: str
        Code to return incase of invalid/unsupported
        input language.

    Returns
    -------
    Language code in ISO-639-1 standard.
    """
    try:
        lg = Lang(lang)
        iso_639_1_lang = lg.pt1
    except:
        iso_639_1_lang = unk_code
    return iso_639_1_lang


def lang_to_iso639_2(lang: str, unk_code: str = "unk") -> str:
    """ Converts language into ISO-639-2 standard.
    Input can be any language code in a valid ISO-639
    standard or even a full name of the language,
    e.g. "Estonian".

    Parameters
    -----------
    lang: str
        Language code in any valid ISO-639 standard.

    unk_code: str
        Code to return incase of invalid/unsupported
        input language.

    Returns
    -------
    Language code in ISO-639-2 standard.
    """
    try:
        lg = Lang(lang)
        # NB! uses bibliographic identifier (e.g. "de" -> "ger")
        # opposed to terminological identifier ("de" -> "deu").
        # This can be changed by replaving lg.pt2b -> lg.pt2t
        iso_639_2_lang = lg.pt2b
    except:
        iso_639_2_lang = unk_code
    return iso_639_2_lang


def lang_to_iso639_3(lang: str, unk_code: str = "unk") -> str:
    """ Converts language into ISO-639-3 standard.
    Input can be any language code in a valid ISO-639
    standard or even a full name of the language,
    e.g. "Estonian".

    Parameters
    -----------
    lang: str
        Language code in any valid ISO-639 standard.
        unk_code: str

    Code to return incase of invalid/unsupported
        input language.

    Returns
    -------
    str
        Language code in ISO-639-3 standard.
    """
    try:
        lg = Lang(lang)
        iso_639_3_lang = lg.pt3
    except:
        iso_639_3_lang = unk_code
    return iso_639_3_lang


def ratio_to_percentage(ratio: float) -> str:
    """ Converts ratio to corresponding percentage.

    Parameters
    -----------
    ratio: float
        Float in range [0,1]

    Returns
    --------
    str
        Percentage corresponding to the float.

    """
    percentage = f"{int(ratio*100)}%"
    return percentage

def format_date(original_date: str) -> str:
    """ Converts date from format %Y-%m-%d into format %d.%m.%Y, e.g:
    2025-02-12 -> 12.02.2025.

    Parameters
    -----------
    original_date: str
        Original date in format %Y-%m-%d

    Returns
    ----------
    str:
        Date in format %d.%m.%Y
    """
    try:
        date_obj = datetime.strptime(original_date, "%Y-%m-%d")
        #new_date = date_obj.strftime("%d.%m.%Y") # Would have been more precise :(
        new_date = date_obj.strftime("%Y")

    except:
        new_date = original_date
    return new_date
