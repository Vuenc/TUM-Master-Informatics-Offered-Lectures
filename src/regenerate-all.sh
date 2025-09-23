TERMID=205
TERMNAME=ws25-26
FIRSTTERMID=171 # no data before WS09/10

# Bachelor Informatics
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum bachelor-informatics
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum bachelor-informatics
python print_html_table.py --termid $TERMID --curriculum bachelor-informatics --output "../bachelor-informatics-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum bachelor-informatics --output ../bachelor-informatics-all.html

# Master Informatics
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-informatics
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum master-informatics
python print_html_table.py --termid $TERMID --curriculum master-informatics --output "../master-informatics-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-informatics --output ../master-informatics-all.html

# DEA
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-dea
python fetch_curriculum_tree.py --parallel_drivers 15 --curriculum master-dea
python print_html_table.py --termid $TERMID --curriculum master-dea --output "../dea-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-dea --output ../dea-all.html
