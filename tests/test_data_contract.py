from backend.ui_contract import SCREENS
from backend.pipeline32 import PART_NAMES
def test_30_screens_exact(): assert len(SCREENS)==30 and SCREENS[0]["id"]==1 and SCREENS[-1]["id"]==30
def test_32_part_names_exact(): assert len(PART_NAMES)==32
