"""
    Scheduler and Allocation - create teacher/lab/course schedules
    Copyright (C) 2025  Sandy Bultena

    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and licensed under the GNU General Public License.
    (see <https://www.gnu.org/licenses/>)
"""
import os
import sys
import traceback

bin_dir: str = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(bin_dir, "../"))

def AllocationManager():
    try:
        from scheduling_and_allocation.presenter.allocation_manager import AllocationManager
        AllocationManager(bin_dir=bin_dir)
    except Exception as e:
        print()
        print("==================================================================")
        print("ERROR:")
        print("==================================================================")
        print(e)
        print()
        print("==================================================================")
        print("Trace")
        print("==================================================================")
        traceback.print_exc()
        print()
        print("==================================================================")
        print("System info")
        print("==================================================================")
        print(sys.version)
        print(sys.version_info)
        print()
        print()
        _=input("press enter to continue")


if __name__ == "__main__":
    AllocationManager()
