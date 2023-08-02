# Informatics
TERMID=199
TERMNAME=ws23-24
FIRSTTERMID=171 # no data before WS09/10

python fetch_tumonline_tree.py --curriculum master-informatics
python print_html_table.py --termid $TERMID --curriculum master-informatics --output "../informatics-$TERMNAME.html"
python print_html_table.py --termid $TERMID --curriculum master-informatics --oldtermsfrom $FIRSTTERMID --output ../informatics-all.html
# DEA
python fetch_tumonline_tree.py --curriculum master-dea
python print_html_table.py --termid $TERMID --curriculum master-dea --output "../dea-$TERMNAME.html"
python print_html_table.py --termid $TERMID --curriculum master-dea --oldtermsfrom $FIRSTTERMID --output ../dea-all.html
