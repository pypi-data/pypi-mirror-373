# Scheduler and AllocationManager How-to
This document provides simple 'how-to' instructions.  It is assumed that the user is familiar with using a GUI application, such as opening and closing files, etc.  As such, those types of details will not be listed in this document.

## _Creating Schedules and Managing Workloads_

This package contains **two** individual programs that work in concert to allow the chairs of your department to create schedules and workloads from the same datasets.

### Scheduler
Creates schedules by dragging and dropping individual course class times around a grid, assigning teachers and labs and streams to said blocks.
Colour schemes indicate if there are any conflicts.

### AllocationManager

Assign teachers to courses and sections.  Manually enter student numbers.  CI calculations are done on the fly.

## _Launching Program_

### MAC

Use the search tool (Command-spacebar) open a terminal window

Navigate to the correct directory

```bash
cd Desktop
cd Scheduling_and_allocation
```

Run either the scheduler or allocation program

```bash
python3 SchedulerProgram.py
```

```bash
python3 AllocationManager.py
```

## _Data_
### Storage
The data for all of the schedule information is stored, per semester, in a CSV file.
The ```Scheduler``` requires only one ```CSV``` file, encapsulating all the information for a given semester.

* The ```AllocationManager``` requires two ```CSV``` files, one file for each semester, comprising a complete academic year.
>The ```CSV``` files in question are the same files for both application.  A file used for allocation can be used for scheduling, and vice-versa.

### Data definitions
* Course:
    * *needs_allocation*: Do we need to assign a teacher to this course
    * *Sections*: The sections that are being taught for this course
    * _hours per week_:  How many hours per week is required for this course
* Section:
    * *hours*: the number of hours per week that is assigned to the section.  If blocks are defined, then the number of hours is the sum total of all of the hours in the blocks for each section
    * *class time*: An individual time block where teachers are in the classroom.  Some courses do not have blocks (such as stage courses)
    * can assign: *teachers*, *labs*, *streams* to an individual section
* Class time:
    * *duration*: how long the block lasts
    * *start time*: when does the block start
    * *day of week*: what day is this block on
    * can assign: *teachers*, *labs*, *streams* to an individual section
* Teacher: Someone who teaches.
    * can be assigned to sections, and/or individual blocks
    * if assigned to sections, will automatically be assigned to all blocks within that section
* Lab: The classroom where the block will be taught
    * can be assigned to sections, and/or individual blocks
    * if assigned to sections, will automatically be assigned to all blocks within that section
* Stream: Defines a cohort of students.  Used to group together sections which will be taught to a cohort.


## _Creating required information_
If this is the first time that the user is using these tools, there will be no course information, or information about anything at all.  
It is recommended that the user creates the information in the order listed below.

### Create teachers, labs, streams
Both ```Scheduler``` and ```AlocationManager``` have tabs that allow the user to create new teachers, labs, and streams.
> In the teachers tab, there is a column RT, which is short for 'release time'.  It is important to enter release time for a teacher to avoid scheduling errors such as 'too few days'.

### Creating Courses, Sections, Class Times
Look for the ```Courses``` tab.  

On the left pane, there will be a tree like structure that displays all of the courses, the sections that belong to a course, blocks in sections.  In addition, any teacher or lab or stream that is assigned to a section or block will also be indicated.

Teachers, Labs and Streams that have already been defined are shown in the right three panes.

#### New Course
To create a new course, press the ```New Course``` button.
1. A new course will be created that has an empty course number
2. You must set a valid course number (a number that is not already been used).  
3. From this dialog box, the user can create sections, class times, etc, and assign teachers, labs and streams to all sections/class times for this course

.

## _Modifying Existing Information_
### Teachers, Labs, Streams
Go to the appropriate tabs, and edit the information directly

### Courses, Sections, Blocks
#### Drag 'n' Drop
Drag a teacher, or lab, or stream from any of the right panels onto the appropriate Course, Section or Class Time in the left panel, and it will be assigned acccordingly.

If you hover over a course or section for approximately 1/2 second, the tree will _open_ and expose its constituents (courses will show sections, sections will show class times)

#### Right-click
Right click any object on the tree, and a pop-up menu will appear, allowing the user to add, remove teachers, labs, streams, delete the object, edit the object, etc.

#### Double-click
Double click any Course, Section, Class Time object on the tree, and an appropriate dialog box will open, allowing the user to edit the object.

#### Keyboard
Navigate to any Course, Section, Block object on the tree, hit ```return```, and an appropriate dialog box will open, allowing the user to edit the object.

## _Creating Schedules_
Once all the lab information, streams, courses, teachers, etc have been created (and hopefully saved in a CSV file), the user can now create schedules for moving blocks around on the views.
* Go to the ```Schedules``` tab
    * There you will see a list of all possible 'Views', where each 'View' will be a schedule for that object.
    * Click on a button to see the 'View' associated with that object.
    * You can have as many 'Views' open as you would like.

### Modifying the Schedules

#### Moving Blocks
* Move the blocks around by selecting a block and then drag it with the mouse.  The block will be moved in all views in which it is assigned (teacher, lab, stream).
* If there is a conflict, the block will change colour to indicate what type of conflict is present.  The colour coding for the blocks is described at the top of the view.
* An _indirect_ conflict occurs when there is a time overlap for this block occurs in a different view.  For example, there may not be a conflict for the teacher in question, but there could be a conflict in the lab where the block has been assigned.
>NOTE: There is an unlimited number of undo and redo when moving blocks

#### Moving blocks between teachers and labs and streams
* Right click the block that you wish to modify.
* If the view is either ```teacher``` or ```stream```, then the user has the option to move all of the blocks within the course section to another teacher or stream.
* If the view is ```lab```, then the user has the option to move the single block to another lab.


### Conflict Resolution
* On the main application window (```Schedules``` tab), the buttons for each view will also be colour coded indicating which items have conflicts.  This will aid the user in knowing which views to open.
* If the user is on a teacher view, and a block has an _indirect_ conflict, double clicking the block will open the lab view that contains this block.
* If the user is on a lab view, and a block has an _indirect_ conflict, double clicking the block will open the teacher view that contains this block.

## _Allocating Teachers To Courses_
Once all the lab information, streams, courses, teachers, etc have been created (and hopefully saved in a CSV file, one per semester), the user can now assign to teachers to courses, and ensure that the workload distribution meets the college's requirements.

> NOTE: The CI calculation depends on the number of students in each course/section.  Update the student numbers to reflect the most accurate information you can obtain, to ensure that the CI calculations are reasonably accurate.
>
> NOTE: If your course has classes and labs, where the student numbers are not the same for all scheduled class times, the CI calculations will be WRONG!

There are two grids presented on the ```Allocation``` tab.  One for each semester.
Teachers are listed in the rows, and courses/sections define the columns.  Course names are displayed if the mouse hovers over the course number.
On the right, the CI calculation for the semester and year are indicated.

* The user can enter the number of hours that each teacher teaches for each course/section.  
* The bottom row of each grid indicates how many hours still needs to be allocated to a teacher.
* On the right, the ```RT``` column is the release time for that teacher and is used to calculate CI.  To modify the RT, go to the appropriate tab (Fall/Teacher for example) and modify the amount there.

> NOTE: As the data is modified on the allocation grid, it is also updating the schedule data as well.  For example, if a teacher's hours for a course/section is above zero, the teacher will be automatically assigned to that course/section.  Likewise, an empty or zero allocation of hours will remove that teacher from the course/section.

## _CI Rules_
* For each semester, a teacher may not have more than 55.
* A teacher must have between 80 and 85 CI for the whole year.

> NOTE: The college frowns upon teachers have a very low CI in the fall, although sometimes it is necessary.
