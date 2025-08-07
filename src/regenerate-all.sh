TERMID=204
TERMNAME=ss25
FIRSTTERMID=171 # no data before WS09/10


# Informatics
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-informatics
python fetch_curriculum_tree.py --parallel_drivers 5 --curriculum master-informatics
python print_html_table.py --termid $TERMID --curriculum master-informatics --output "../informatics-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-informatics --output ../informatics-all.html

# DEA
python update_course_database.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-dea
python fetch_curriculum_tree.py --parallel_drivers 5 --curriculum master-dea
python print_html_table.py --termid $TERMID --curriculum master-dea --output "../dea-$TERMNAME.html"
python print_html_table.py --termid $TERMID --oldtermsfrom $FIRSTTERMID --curriculum master-dea --output ../dea-all.html
