import json
from typing import Dict, Any
import os

def load_spec(file_path: str) -> Dict[str, Any]:
    """
    Load the JSON spec file into a Python dict.
    
    :param file_path: Path to your spec.json
    :return: A dict mapping each URI to its structure-definition dict.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

SPEC_PATH = os.path.join(os.path.dirname(__file__), "spec.json")
structure_specs = load_spec(SPEC_PATH)

def get_substructures(key: str) -> Dict[str, Any]:
    """
    Return the 'substructures' dict for the given key.
    """
    struct = structure_specs.get(key)
    if struct is None:
        return {}
        raise KeyError(f"No entry for key {key!r} in spec.json")
    return struct.get("substructures", {})

def get_label(key: str) -> Dict[str, Any]:
    """
    Return the label for the given key.
    """
    struct = structure_specs.get(key)
    if struct is None:
        raise KeyError(f"No entry for key {key!r} in spec.json")
        return 'None'
        
    return struct.get("label", 'No Label')

def match_uri(tag: str,parent):
    uri = None
    if tag.startswith("_"):
        uri = structure_specs.get(tag)
    elif parent:
        valid_substrutures = get_substructures(parent.uri)
        uri = valid_substrutures.get(tag)  
    elif 'https://gedcom.io/terms/v7/record-' + tag in structure_specs.keys():
        uri = 'https://gedcom.io/terms/v7/record-' + tag
    elif 'https://gedcom.io/terms/v7/' + tag in structure_specs.keys():
        uri = 'https://gedcom.io/terms/v7/' + tag
    if uri == None:
        raise ValueError(f'Could not get uri for tag: {tag}, parent: {parent}')
    return uri

'''
MIT License

Copyright (c) 2022 David Straub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
# TODO: https://github.com/DavidMStraub

# GEDCOM 7 regex patterns thanks@DavidMStraub

# --- Common primitives ---
d = '\\ '                             # GEDCOM delimiter (escaped space)
integer = '[0-9]+'                    # One or more digits
nonzero = '[1-9]'                     # Digits 1–9

# --- Duration units ---
years  = f'{integer}y'
months = f'{integer}m'
weeks  = f'{integer}w'
days   = f'{integer}d'

# --- Age format ---
agebound = '[<>]'  # Optional boundary indicator (less than, greater than)
ageduration = (
    f'((?P<years>{years})({d}(?P<months1>{months}))?({d}(?P<weeks1>{weeks}))?'
    f'({d}(?P<days1>{days}))?|(?P<months2>{months})({d}(?P<weeks2>{weeks}))?'
    f'({d}(?P<days2>{days}))?|(?P<weeks3>{weeks})({d}(?P<days3>{days}))?|'
    f'(?P<days4>{days}))'
)
age = f'((?P<agebound>{agebound}){d})?{ageduration}'

# --- Tags and Enums ---
underscore = '_'
ucletter = '[A-Z]'
tagchar = f'({ucletter}|[0-9]|{underscore})'
exttag = f'{underscore}({tagchar})+'
stdtag = f'{ucletter}({tagchar})*'
tag = f'({stdtag}|{exttag})'
enum = tag

# --- Dates ---
daterestrict = 'FROM|TO|BET|AND|BEF|AFT|ABT|CAL|EST'
calendar = f'(?!{daterestrict})(GREGORIAN|JULIAN|FRENCH_R|HEBREW|{exttag})'
day = integer
month = f'(?!{daterestrict})({stdtag}|{exttag})'
year = integer
epoch = f'(?!{daterestrict})(BCE|{exttag})'

date = f'({calendar}{d})?(({day}{d})?{month}{d})?{year}({d}{epoch})?'

# --- Date variants with captures ---
date_capture = (
    f'((?P<calendar>{calendar}){d})?(((?P<day>{day}){d})?'
    f'(?P<month>{month}){d})?(?P<year>{year})({d}(?P<epoch>{epoch}))?'
)

dateapprox = f'(?P<qualifier>ABT|CAL|EST){d}(?P<dateapprox>{date})'
dateexact  = f'(?P<day>{day}){d}(?P<month>{month}){d}(?P<year>{year})'
dateperiod = f'((TO{d}(?P<todate1>{date}))?|FROM{d}(?P<fromdate>{date})({d}TO{d}(?P<todate2>{date}))?)'
daterange  = f'(BET{d}(?P<between>{date}){d}AND{d}(?P<and>{date})|AFT{d}(?P<after>{date})|BEF{d}(?P<before>{date}))'
datevalue  = f'({date}|{dateperiod}|{daterange}|{dateapprox})?'

# --- Media types ---
mt_char = "[ -!#-'*-+\\--.0-9A-Z^-~]"
mt_token = f'({mt_char})+'
mt_type = mt_token
mt_subtype = mt_token
mt_attribute = mt_token
mt_qtext = '[\t-\n -!#-\\[\\]-~]'
mt_qpair = '\\\\[\t-~]'
mt_qstring = f'"({mt_qtext}|{mt_qpair})*"'
mt_value = f'({mt_token}|{mt_qstring})'
mt_parameter = f'{mt_attribute}={mt_value}'
mediatype = f'{mt_type}/{mt_subtype}(;{mt_parameter})*'

# --- Line structure (GEDCOM record lines) ---
atsign = '@'
xref = f'{atsign}({tagchar})+{atsign}'
voidptr = '@VOID@'
pointer = f'(?P<pointer>{voidptr}|{xref})'
nonat = '[\t -?A-\\U0010ffff]'
noneol = '[\t -\\U0010ffff]'
linestr = f'(?P<linestr>({nonat}|{atsign}{atsign})({noneol})*)'
lineval = f'({pointer}|{linestr})'

level = f'(?P<level>0|{nonzero}[0-9]*)'
eol = '(\\\r(\\\n)?|\\\n)'
line = f'{level}{d}((?P<xref>{xref}){d})?(?P<tag>{tag})({d}{lineval})?{eol}'

# --- List formats ---
nocommasp = '[\t-\\x1d!-+\\--\\U0010ffff]'
nocomma = '[\t-+\\--\\U0010ffff]'
listitem = f'({nocommasp}|{nocommasp}({nocomma})*{nocommasp})?'
listdelim = f'({d})*,({d})*'
list = f'{listitem}({listdelim}{listitem})*'
list_enum = f'{enum}({listdelim}{enum})*'
list_text = list

# --- Names ---
namechar = '[ -.0-\\U0010ffff]'
namestr = f'({namechar})+'
personalname = f'({namestr}|({namestr})?/(?P<surname>{namestr})?/({namestr})?)'

# --- Time format ---
fraction = '[0-9]+'
second = '[012345][0-9]'
minute = '[012345][0-9]'
hour = '([0-9]|[01][0-9]|2[0123])'
time = f'(?P<hour>{hour}):(?P<minute>{minute})(:(?P<second>{second})(\\.(?P<fraction>{fraction}))?)?(?P<tz>Z)?'

# --- Text and special ---
anychar = '[\t-\\U0010ffff]'
text = f'({anychar})*'
special = text

# --- Boolean ---
boolean = 'Y'

# --- Banned Unicode Ranges ---
'''
banned = %x00-08 / %x0B-0C / %x0E-1F ; C0 other than LF CR and Tab
       / %x7F                        ; DEL
       / %x80-9F                     ; C1
       / %xD800-DFFF                 ; Surrogates
       / %xFFFE-FFFF                 ; invalid
; All other rules assume the absence of any banned characters
'''
banned = (
    '[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f\\x7f\\x80-\\x9f\\ud800-\\udfff'
    '\\ufffe-\\uffff]'
)




# TAGS
CONT = "CONT"
HEAD = "HEAD"
ABBR = "ABBR"
ADDR = "ADDR"
ADOP = "ADOP"
ADR1 = "ADR1"
ADR2 = "ADR2"
ADR3 = "ADR3"
AGE = "AGE"
AGNC = "AGNC"
ALIA = "ALIA"
ANCI = "ANCI"
ANUL = "ANUL"
ASSO = "ASSO"
AUTH = "AUTH"
BAPL = "BAPL"
BAPM = "BAPM"
BARM = "BARM"
BASM = "BASM"
BIRT = "BIRT"
BLES = "BLES"
BURI = "BURI"
CALN = "CALN"
CAST = "CAST"
CAUS = "CAUS"
CENS = "CENS"
CHAN = "CHAN"
CHIL = "CHIL"
CHR = "CHR"
CHRA = "CHRA"
CITY = "CITY"
CONF = "CONF"
CONL = "CONL"
COPR = "COPR"
CORP = "CORP"
CREA = "CREA"
CREM = "CREM"
CROP = "CROP"
CTRY = "CTRY"
DATA = "DATA"
DATE = "DATE"
DEAT = "DEAT"
DESI = "DESI"
DEST = "DEST"
DIV = "DIV"
DIVF = "DIVF"
DSCR = "DSCR"
EDUC = "EDUC"
EMAIL = "EMAIL"
EMIG = "EMIG"
ENDL = "ENDL"
ENGA = "ENGA"
EVEN = "EVEN"
EXID = "EXID"
FACT = "FACT"
FAM = "FAM"
FAMC = "FAMC"
FAMS = "FAMS"
FAX = "FAX"
FCOM = "FCOM"
FILE = "FILE"
FORM = "FORM"
GEDC = "GEDC"
GIVN = "GIVN"
GRAD = "GRAD"
HEIGHT = "HEIGHT"
HUSB = "HUSB"
IDNO = "IDNO"
IMMI = "IMMI"
INDI = "INDI"
INIL = "INIL"
LANG = "LANG"
LATI = "LATI"
LEFT = "LEFT"
LONG = "LONG"
MAP = "MAP"
MARB = "MARB"
MARC = "MARC"
MARL = "MARL"
MARR = "MARR"
MARS = "MARS"
MEDI = "MEDI"
MIME = "MIME"
NAME = "NAME"
NATI = "NATI"
NATU = "NATU"
NCHI = "NCHI"
NICK = "NICK"
NMR = "NMR"
NO = "NO"
NOTE = "NOTE"
NPFX = "NPFX"
NSFX = "NSFX"
OBJE = "OBJE"
OCCU = "OCCU"
ORDN = "ORDN"
PAGE = "PAGE"
PEDI = "PEDI"
PHON = "PHON"
PHRASE = "PHRASE"
PLAC = "PLAC"
POST = "POST"
PROB = "PROB"
PROP = "PROP"
PUBL = "PUBL"
QUAY = "QUAY"
REFN = "REFN"
RELI = "RELI"
REPO = "REPO"
RESI = "RESI"
RESN = "RESN"
RETI = "RETI"
ROLE = "ROLE"
SCHMA = "SCHMA"
SDATE = "SDATE"
SEX = "SEX"
SLGC = "SLGC"
SLGS = "SLGS"
SNOTE = "SNOTE"
SOUR = "SOUR"
SPFX = "SPFX"
SSN = "SSN"
STAE = "STAE"
STAT = "STAT"
SUBM = "SUBM"
SURN = "SURN"
TAG = "TAG"
TEMP = "TEMP"
TEXT = "TEXT"
TIME = "TIME"
TITL = "TITL"
TOP = "TOP"
TRAN = "TRAN"
TRLR = "TRLR"
TYPE = "TYPE"
UID = "UID"
VERS = "VERS"
WIDTH = "WIDTH"
WIFE = "WIFE"
WILL = "WILL"
WWW = "WWW"