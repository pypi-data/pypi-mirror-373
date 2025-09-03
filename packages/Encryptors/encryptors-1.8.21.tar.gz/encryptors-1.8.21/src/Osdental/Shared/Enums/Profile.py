from enum import StrEnum
class Profile(StrEnum):
    SUPER_ADMIN = 'SPAU'
    ADMIN_OSD = 'OSDA'
    MARKETING = 'OSDMK'
    EXT_ADMIN = 'ADEX'
    EXT_USER = 'EXTU'
    BOOKKEEPER = 'BKEU'
    PRODENT = 'OSDBI'
    LIMITED = 'LTD'