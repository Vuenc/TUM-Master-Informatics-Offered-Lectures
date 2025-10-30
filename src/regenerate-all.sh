TERMID=205
TERMNAME=ws25-26
FIRSTTERMID=171 # no data before WS09/10

# Bachelor Informatics
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum bachelor-informatics
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum bachelor-informatics
python print_html_table.py --termid $TERMID --curriculum bachelor-informatics --output "../build/bachelor-informatics-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum bachelor-informatics --output "../build/bachelor-informatics-all.html"

# Master Informatics
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-informatics
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum master-informatics
python print_html_table.py --termid $TERMID --curriculum master-informatics --output "../build/master-informatics-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-informatics --output "../build/master-informatics-all.html"

# DEA
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-dea
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum master-dea
python print_html_table.py --termid $TERMID --curriculum master-dea --output "../build/dea-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-dea --output "../build/dea-all.html"

# Master Information Systems
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-information-systems
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum master-information-systems
python print_html_table.py --termid $TERMID --curriculum master-information-systems --output "../build/master-information-systems-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-information-systems --output "../build/master-information-systems-all.html"
