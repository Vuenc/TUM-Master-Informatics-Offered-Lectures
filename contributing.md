# Contributing
If you find a mistake, like a lecture missing, you can create an issue.

If you find the list is out of date because some information changed in TUM online, you can recreate the table by running the scripts:

1. Fetch data from the curriculum tree view by running `python fetch_curriculum_tree.py --curriculum master-informatics` (or `--master-dea`)
2. Regenerate HTML tables - e.g. for Informatics:
    - `python print_html_table.py --termid 198 --curriculum master-informatics --output ../build/informatics-ss23.html` for current semester table
    - `python print_html_table.py --termid 198 --curriculum master-informatics --oldtermsfrom 188 --output ../build/informatics-all.html` for last offered table
    - replace the term IDs: 198 is summer term 2023, 199 is winter term 2023/24, etc.
    
You can also regenerate all tables by running `sh src/regenerate-alls.sh`.

If you want a similar list for other study programs, I'm happy to collaborate! Just open an issue and we can have a look. The scripts should be easy to generalize to other programs.
