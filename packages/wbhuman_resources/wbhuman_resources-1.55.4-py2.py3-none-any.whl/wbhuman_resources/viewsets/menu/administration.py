from wbcore.menus import Menu

from .absence import ABSENCEREQUESTTYPE_MENUITEM
from .calendars import DAYOFF_MENUITEM, DAYOFFCALENDAR_MENUITEM
from .employee import POSITION_MENUITEM

ADMINISTRATION_MENU = Menu(
    label="Administration",
    items=[
        DAYOFF_MENUITEM,
        ABSENCEREQUESTTYPE_MENUITEM,
        DAYOFFCALENDAR_MENUITEM,
        POSITION_MENUITEM,
    ],
)
