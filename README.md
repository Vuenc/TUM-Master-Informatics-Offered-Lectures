# TUM Master Informatics: Offered Lectures
This document aims to provide a list of lectures that are being offered this semester for the Informatics master at TUM, grouped by area of specialization:

- TUM provides a list of modules in the Informatics master **by area of specialization** [here](https://www.in.tum.de/en/current-students/masters-programs/informatics/elective-modules/fpso-2018/) - *but without (reliable) information which modules are actually being offered*.
- The TUMonline course search lists the courses that are **actually being offered in the current semester** - *but without information about the area the course is in*.

This repo merges the two sources of information, to provide the list of lectures that are being offered, grouped by area of specialization.

*This list is not official, might be incomplete or have errors. Use with care!*

I created this list by matching modules from TUMonline that will actually be offered with the
list of elective modules. I only included lectures (VO) and lectures with integrated exercises (VI).
There may be errors: For example, new courses might be missing if they are not yet associated
with the correct curriculum on TUMonline.


# Contributing
You can send a pull request if you find a lecture is missing, or a lecture is wrongly included.

- lecture wrongly included: Strike it through (like e.g. *~~Patterns in Software Engineering~~*)
- lecture missing:  Add a line on the second sheet with the INxxxx code and the lecture name. Then re-apply the the filter on the first sheet, cell J3. The lecture should appear either under an area of specialization, or at the bottom if it's not in the official elective modules table.

Please re-generate the pdf afterwards by exporting columns A-H as pdf.


### How to update the table
I use the following steps to update the table of offered lectures every semester. I usually update the table one or two weeks before the lecture period starts to make sure that all courses are already visible in TUM online.

1. Update the list of courses in the curriculum
    - go to [https://www.in.tum.de/in/fuer-studierende/master-studiengaenge/informatik/wahlmodule/fpso-2018/](https://www.in.tum.de/in/fuer-studierende/master-studiengaenge/informatik/wahlmodule/fpso-2018/) (or whatever the current FPSO is) and copy the table, starting at the first heading Elective Modules of the Area ..." until the end of the section "Elective Modules not Assigned to any Area:"
    - paste this table into the *Modules by Master Areas* sheet
2. Fetch the list of currently offered courses
    - run `python fetch_courses.py --termid <TERM_ID>`. For `<TERM_ID>`, substitute the number of the current semester: For winter 2022/23, this is 197, for summer 2023 this is 198, and so on.
    - the script first fetches all courses associated with the Master Informatics curriculum, then all courses not associated with the curriculum but which have a `INxxxx` module number. For each of the two, it first outputs a list of `INxxxx` numbers followed by a list of course names
3. Update the offered courses
    - in the "Offered modules from TUM online (Master)" and "Offered modules from TUM online (Other IN)" sheets, clear the data in the "Module No." and the "Title" columns
    - copy-paste the first block of `INxxxx` numbers from the script output into the "Module No." column of the first sheet, and the second block of `INxxxx` numbers from the script output into the "Module No." column of the second sheet
    - copy-paste the first block of course names from the script output into the "Title" column of the first sheet, and the second block of course names from the script output into the "Title" column of the second sheet
    - in the "Modules by Master Areas" sheet, re-apply the filter in the "Offered in the current semester?" column
4. Export the pdf
    - in the "Modules by Master Areas" sheet, select the columns until "THEO" and export the selection as pdf.