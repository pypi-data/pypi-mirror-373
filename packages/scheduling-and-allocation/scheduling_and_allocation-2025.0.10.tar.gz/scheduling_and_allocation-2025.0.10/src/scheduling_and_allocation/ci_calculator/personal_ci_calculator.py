PREP_FACTOR                = 0.9
PREP_BONUS_LIMIT           = 3.0
PREP_BONUS_FACTOR          = 0.2  # 1.1 - 0.9
PREP_CRAZY_BONUS_FACTOR    = 1.0

PES_FACTOR                 = 0.04
PES_BONUS_LIMIT            = 415
PES_BONUS_FACTOR           = 0.03

STUDENT_BONUS_LIMIT        = 75
STUDENT_BONUS_FACTOR       = 0.01
STUDENT_CRAZY_BONUS_LIMIT  = 160
STUDENT_CRAZY_BONUS_FACTOR = 0.1

HOURS_FACTOR               = 1.2

CI_FTE_PER_SEMESTER        = 40

prep_hours = 0
pes = 0
total_students = 0
num_preps = 0
hours = 0

while True:
    course_name = input("\nEnter Course name ").strip()
    if course_name == "":
        break
    new_prep_hours = int(input("How many hours? "))
    sections = int(input("Number of sections? "))
    students = int(input("Total number of students for all sections? "))

    prep_hours += new_prep_hours
    pes = pes + new_prep_hours * students
    hours += new_prep_hours * sections
    total_students += students
    num_preps += 1

# ------------------------------------------------------------------------
# hours in classroom * number of students
# ------------------------------------------------------------------------
CI_student = pes * PES_FACTOR

# bonus if pes is over 415
surplus = pes - PES_BONUS_LIMIT
bonus = surplus * PES_BONUS_FACTOR if surplus > 0 else 0
CI_student += bonus

# another bonus if total number of students is over student_bonus_limit
# (only for courses over 3 hours)
bonus = total_students * STUDENT_BONUS_FACTOR if total_students >= STUDENT_BONUS_LIMIT else 0
CI_student += bonus

# and yet another bonus if number of students is over Crazy student limit
if total_students >= STUDENT_CRAZY_BONUS_LIMIT:
    bonus = (total_students - STUDENT_CRAZY_BONUS_LIMIT) * STUDENT_CRAZY_BONUS_FACTOR
    CI_student += bonus

# ------------------------------------------------------------------------
# Preps (based on # of prep hours PER course)
# ------------------------------------------------------------------------
CI_preps = prep_hours * PREP_FACTOR

# bonus if number is the PREP_BONUS_LIMIT
if num_preps == PREP_BONUS_LIMIT:
    CI_preps += prep_hours * PREP_BONUS_FACTOR

# more bonus if over the limit
elif num_preps > PREP_BONUS_LIMIT:
    CI_preps += prep_hours * PREP_CRAZY_BONUS_FACTOR

# ------------------------------------------------------------------------
# Hours (based on contact hours per week)
# ------------------------------------------------------------------------
CI_hours = hours * HOURS_FACTOR

# ------------------------------------------------------------------------
# all done
# ------------------------------------------------------------------------
print( f"\nCI: \n"
       f"prep:               {CI_preps:5.2f}  \n"
       f"hours in classroom: {CI_hours:5.2f}  \n"
       f"student*hours:      {CI_student:5.2f}")
print( f"Total CI:           {CI_hours + CI_preps + CI_student:5.2f}")
