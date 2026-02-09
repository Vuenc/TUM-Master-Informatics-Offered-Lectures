import argparse
import atexit
import json
import time
from dataclasses import asdict, dataclass
from multiprocessing import Pool
from typing import Dict, List, Tuple

import selenium
import selenium.webdriver
import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager

from curriculums import Curriculum, curriculums

def click_button(driver, button):
    driver.execute_script("arguments[0].click()", button)

def login_tum_online(driver: webdriver.Firefox, username, password):
    # Login to TUM online with given credentials
    tumonline_url = "https://campus.tum.de"
    username_field_id = "id_brm-pm-dtop_login_uname_input"
    password_field_id = "id_brm-pm-dtop_login_pw_input"
    login_button_id = "id_brm-pm-dtop_login_submitbutton"
    driver.get(tumonline_url)
    driver.find_element(value=username_field_id).send_keys(username)
    driver.find_element(value=password_field_id).send_keys(password)
    driver.find_element(value=login_button_id).click

def get_offer_node_plus_buttons(driver, node_title: str):
    # Find table rows that contain an offer node, and select their descendant plus buttons
    offer_node_selector = f"span[contains(@title, '{node_title}')]"
    plus_button_selector = "a[contains(@class, 'KnotenLink')][not(contains(@style, 'tee_minus'))]"
    return driver.find_elements(By.XPATH, f"//tr[.//{offer_node_selector}]//{plus_button_selector}")

def get_previous_year_buttons_for_courses_without_entries(driver):
    # Find course tables with no entries, and locate their "previous year" buttons
    no_entries_table_selector = "td[contains(text(), 'No entries')]"
    previous_year_button_selector = "a[contains(@title, 'Show previous academic year with entries')]"
    return driver.find_elements(By.XPATH, f"//tr[.//{no_entries_table_selector}]//{previous_year_button_selector}")


def print_tree(tree, prefix="|--"):
    print(prefix[:-1], tree["name"])
    for child in tree["children"]:
        print_tree(child, prefix + "|--")

@dataclass
class CourseCurriculumInformation:
    urls: List[str]
    num_credits: int | None
    module_name: str | None
    rule_node_names_by_levels: Dict[int, str | None]

def extract_courses_with_credits(driver: webdriver.Firefox) -> Tuple[List[CourseCurriculumInformation], int | None, str | None, Dict[int, str | None]]:
    """
    Returns a list associating course links to their number of credits, as well as the Credits of the last
    entry on the page (since that might carry over to the next page), and the module name of the last entry (same here).
    """
    # Select (via the same XPath so they are ordered):
    # - the module names indicating the curriculum path (Rule nodes), and other nodes to deactivate previous Rule nods
    # - the rows belonging to credits (rows containing Module nodes)
    # - hrefs pointing to course links.
    node_span_selector = "//tr//td[1]//span//span[contains(@title, ' node')]"
    module_selector = "//tr[td[1]//span//span[contains(@title, 'Module node')]]"
    course_link_selector = "//a[contains(@href, 'pages/slc.tm.cp/course/')]"
    module_or_course_link_selector = f"{node_span_selector} | {module_selector} | {course_link_selector}"

    current_credits = None
    current_module_name = None
    current_course = None
    course_infos: List[CourseCurriculumInformation] = []
    # Rule nodes correspond to groups (electives group, subject areas, "Theory", and similar)
    current_rule_node_names_by_levels: Dict[int, str | None] = {}

    # By sequentially going through the results, we can associate course links to their amount of credits.
    for element in driver.find_elements(By.XPATH, module_or_course_link_selector):
        if element.tag_name == "span": # Rule node or other node
            node_title = element.get_attribute("title")
            assert node_title is not None
            if "Rule node" in node_title:
                # we identify the levels of rule nodes in the path based on their indent
                current_rule_node_names_by_levels[element.location["x"]] = element.text
            else:
                # reset rule node name at that level (so previous rule nodes don't stay active)
                current_rule_node_names_by_levels[element.location["x"]] = None
        elif element.tag_name == "tr": # Module node row
            current_module_name = element.find_element(By.XPATH, "td[1]//span//span").text
            credits_elements = element.find_elements(By.XPATH, "td[4]//span")
            current_credits = int(credits_elements[0].text) if len(credits_elements) > 0 and credits_elements[0].text.isdecimal() else None
            current_course = None
        else: # Link to course
            course_link = element.get_attribute("href")
            assert course_link is not None
            if current_course is None:
                current_course = CourseCurriculumInformation(
                    urls=[course_link], num_credits=current_credits, module_name=current_module_name,
                    rule_node_names_by_levels=current_rule_node_names_by_levels.copy()
                )
                course_infos.append(current_course)
            else:
                current_course.urls.append(course_link)
    
    return (course_infos, current_credits, current_module_name, current_rule_node_names_by_levels)

def wait_until_not_loading(driver):
    WebDriverWait(driver, 60).until(
        expected_conditions.invisibility_of_element_located((By.CLASS_NAME, "pageLoading"))
    )
    WebDriverWait(driver, 60).until(
        expected_conditions.invisibility_of_element_located((By.ID, "id-loader"))
    )

def prepare_driver(curriculum: Curriculum, gecko_driver_path: str):
    global driver
    # Start a headless Firefox instance
    options = webdriver.FirefoxOptions()
    options.set_preference("intl.locale.requested", "en-US") # doesn't help though
    options.add_argument("-headless")

    driver = webdriver.Firefox(service=Service(gecko_driver_path),
                               options=options)
    driver.set_script_timeout(20)
    driver.implicitly_wait(5)

    # Navigate to curriculum tree site
    tree_url = f"https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr={curriculum.curriculum_ids[0]}"
    driver.get(tree_url)
    wait_until_not_loading(driver)
    
    # Switch language to English
    driver.find_element(By.TAG_NAME, "coa-desktop-language-menu").click()
    time.sleep(5)
    driver.find_element(By.XPATH, f"//button[@title='Sprache Englisch'] | //button[@title='Language English']").click()

    atexit.register(lambda: driver.close() if driver is not None else ())

def get_page1_url_and_num_pages(curriculum):
    global driver
    assert isinstance(driver, selenium.webdriver.Firefox)

    # # Switch node filter to All (Expanded)
    driver.get(f"https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr={curriculum.curriculum_ids[0]}&pFilterType=20&pPageNr=&pStpKnotenNr=&pStartSemester=W")
    wait_until_not_loading(driver)

    page1_url = driver.current_url
    num_pages = int(driver.find_element(By.CLASS_NAME, "coTableNaviPageSelect").text.split("\n")[-1].removeprefix("of "))
    return page1_url, num_pages

driver = None

def main():
    parser = argparse.ArgumentParser(usage=
    """
    fetch_curriculum_tree.py [-h] --curriculum CURRICULUM
    Curriculum: valid options are `master-informatics', 'master-dea'
    """)
    parser.add_argument("--curriculum", required=True, default="master-informatics",
                        type=str, help="One of ['master-informatics', 'master-dea']")
    parser.add_argument("--parallel_drivers", default=1,
                        type=int, help="How many browser sessions to start in parallel to process different pages quicker")
    args = parser.parse_args()
    curriculum = curriculums[args.curriculum]

    gecko_driver_path = GeckoDriverManager().install()
    print("Installed Firefox Gecko driver to", gecko_driver_path)

    thread_pool = None
    try:
        thread_pool = Pool(args.parallel_drivers, initializer=prepare_driver, initargs=(curriculum, gecko_driver_path))
        time.sleep(4)
        [(page1_url, num_pages)] = thread_pool.map(get_page1_url_and_num_pages, [curriculum])
        results = tqdm.tqdm(thread_pool.imap(fetch_curriculum_course_infos,
                        list(zip(range(1, num_pages+1), [page1_url]*num_pages))), desc="Pages")
    finally:
        if thread_pool is not None:
            thread_pool.close()

    # The first course nodes on page n+1 can belong to the last module node on page n (or even n-1, etc. if the module node has enough entries).
    # Loop through all pages and set the module node of entries without module node that are at the page start to the previous page's last module node. 
    last_credits_on_previous_page = None
    last_module_name_on_previous_page = None
    last_rule_node_names_by_levels_on_previous_page: Dict[int, str | None] = {}
    all_curriculum_course_infos = []
    for (curriculum_course_infos, last_credits_on_page, 
         last_module_name_on_page, last_rule_node_names_by_levels) in results:
        for course_info in curriculum_course_infos:
            if course_info.num_credits is not None:
                break
            assert last_credits_on_previous_page is not None
            course_info.num_credits = last_credits_on_previous_page
            course_info.module_name = last_module_name_on_previous_page
        for course_info in curriculum_course_infos:
            course_info.rule_node_names_by_levels = {**last_rule_node_names_by_levels_on_previous_page, **course_info.rule_node_names_by_levels}
            course_info.rule_node_names_by_levels = {key: value for key, value in course_info.rule_node_names_by_levels.items() if value is not None}
        
        last_module_name_on_previous_page = last_module_name_on_page or last_module_name_on_previous_page
        last_credits_on_previous_page = last_credits_on_page or last_credits_on_previous_page
        last_rule_node_names_by_levels_on_previous_page = {**last_rule_node_names_by_levels_on_previous_page, **last_rule_node_names_by_levels}

        all_curriculum_course_infos.extend(curriculum_course_infos)

    with open(curriculum.tree_file_path, "w") as f:
        # save with indent=0 (will insert newlines, more diff-friendly)
        json.dump([asdict(course_info) for course_info in all_curriculum_course_infos], f, indent=0)
        print(f"""Results written to json file '{curriculum.tree_file_path}'""")

    return all_curriculum_course_infos

def fetch_curriculum_course_infos(page_and_page1_url: Tuple[int, str]) -> Tuple[List[CourseCurriculumInformation], int | None, str | None, Dict[int, str | None]]:
    """
    Algorithm:
    - go to curriculum page
    - click on "Node filter ( All (expanded) )" to get all module nodes in expanded form (individual course nodes still need to be expanded though).
    - for each page in the pagination (this function handles a single page):
        - click on all plus buttons to expand course details
        - extract all module rows (which contain the number of credits, and the module name (often, not always, incl. the course ID)) and
          all course links; associate course links to modules based on order of appearance
        - go to the next page
    """
    page, page1_url = page_and_page1_url
    global driver
    assert isinstance(driver, selenium.webdriver.Firefox)

    if page != 1 or driver.current_url != page1_url:
        driver.get(page1_url.replace("pPageNr=", f"pPageNr={page}"))
        wait_until_not_loading(driver)
        time.sleep(3)

    # Open remaining Rule Nodes and contained Module Nodes (most will be open already, but in edge cases they remain closed;
    # e.g. the Data Analytics Rule Node in Informatics curriculum, and its contained Module Nodes)
    plus_buttons = get_offer_node_plus_buttons(driver, "Rule node")
    for button in tqdm.tqdm(plus_buttons, leave=False, desc="Expanding rule nodes"):
        click_button(driver, button)
    plus_buttons = get_offer_node_plus_buttons(driver, "Module node")
    for button in tqdm.tqdm(plus_buttons, leave=False, desc="Expanding offer nodes"):
        click_button(driver, button)
    # Expand all offer nodes (click the plus buttons)
    plus_buttons = get_offer_node_plus_buttons(driver, "Offer node")
    for button in tqdm.tqdm(plus_buttons, leave=False, desc="Expanding course nodes"):
        click_button(driver, button)

    wait_until_not_loading(driver)

    # Go to previous years for course offer tables with no entries (max. 20 times)
    for year_ago in range(20):
        previous_year_buttons = get_previous_year_buttons_for_courses_without_entries(driver)
        if len(previous_year_buttons) == 0:
            break
        for button in tqdm.tqdm(previous_year_buttons, leave=False, desc=f"Still searching last time offered for {len(previous_year_buttons)} modules: {year_ago+1} years ago..."):
            click_button(driver, button)
        wait_until_not_loading(driver)

    return extract_courses_with_credits(driver)


if __name__ == "__main__":
    main()
