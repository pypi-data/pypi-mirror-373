# =================================================================================================================
# to create an executable folder that needs no python installer
# =================================================================================================================
# NOTE: this is OS dependent, so must be done for each OS that you wish to have an installer for
#
# run these commands from the 'src' directory, the result will be in the 'dist' directory
# copy one of the executables into the other's directory, zip and give to user
python -m pip install pyinstaller  # or python3 if on mac

python -m PyInstaller SchedulerProgram.py   --icon scheduler_icon.ico   --add-binary scheduling_and_allocation/schedule_logo.png:scheduling_and_allocation --add-binary scheduling_and_allocation/schedule_ico.png:scheduling_and_allocation --add-binary scheduling_and_allocation/modified_tk/Images/:scheduling_and_allocation/modified_tk/Images/ --add-data scheduling_and_allocation/export/view_template.tex:scheduling_and_allocation/export/ --add-binary scheduling_and_allocation/allocation_ico.png:scheduling_and_allocation/ --add-binary scheduling_and_allocation/allocation_logo.png:scheduling_and_allocation/

python3 -m PyInstaller AllocationManager.py --icon allocation_icon.ico  --add-binary scheduling_and_allocation/schedule_logo.png:scheduling_and_allocation --add-binary scheduling_and_allocation/schedule_ico.png:scheduling_and_allocation --add-binary scheduling_and_allocation/modified_tk/Images/:scheduling_and_allocation/modified_tk/Images/ --add-data scheduling_and_allocation/export/view_template.tex:scheduling_and_allocation/export/ --add-binary scheduling_and_allocation/allocation_ico.png:scheduling_and_allocation/ --add-binary scheduling_and_allocation/allocation_logo.png:scheduling_and_allocation/
