import os
import sys

from src.scheduling_and_allocation.gui_pages.allocation_manager_tk import AllocationManagerTk
from src.scheduling_and_allocation.model import SemesterType

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
print (os.path.join(bin_dir, "../../"))
logo_dir = os.path.join(bin_dir, "../../src/scheduling_and_allocation")
c = AllocationManagerTk("Hi",bin_dir = logo_dir)
c.create_welcome_page([SemesterType.winter, SemesterType.fall, SemesterType.summer])
c.start_event_loop()