from dataclasses import dataclass, asdict
from typing import List, Tuple
from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
import json
from dotenv import load_dotenv
import os
from curriculums import curriculums, Curriculum
import argparse
import tqdm
import selenium
import time
from urllib.parse import urljoin


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

def descendant_plus_buttons(element, parent_id: str|None=None):
    # Plus buttons are distinguished by their element id containing "toggle"
    base_selector = "a[contains(@class,'KnotenLink')][not(contains(@style,'tee_minus'))]"
    if parent_id is not None:
        return element.find_elements(
            By.XPATH,
            f"//tr[@id='{parent_id}']/following-sibling::*//{base_selector}"
        )
    else:
        return element.find_elements(By.XPATH, f"//{base_selector}")

def print_tree(tree, prefix="|--"):
    print(prefix[:-1], tree["name"])
    for child in tree["children"]:
        print_tree(child, prefix + "|--")

@dataclass
class CourseCurriculumInformation:
    urls: List[str]
    num_credits: int | None
    module_name: str | None

def extract_courses_with_credits(driver: webdriver.Firefox) -> Tuple[List[CourseCurriculumInformation], int | None, str | None]:
    """
    Returns a list associating course links to their number of credits, as well as the Credits of the last
    entry on the page (since that might carry over to the next page), and the module name of the last entry (same here).
    """
    # Select both the rows belonging to credits (i.e. module nodes) as well as hrefs pointing to course links via the same XPath.
    # credits_selector = "//table[@id = 'tgt']/tbody/tr[contains(@class, 'coRow')]/td[4][normalize-space() != '']//span"
    module_selector = "//table[@id = 'tgt']/tbody/tr[contains(@class, 'coRow')][normalize-space(td[4]//span) != ''][td[1]//span//span]"
    course_link_selector = "//a[contains(@href, 'pages/slc.tm.cp/course/')"
    module_or_course_link_selector = f"{module_selector} | {course_link_selector}]"

    current_credits = None
    current_module_name = None
    current_course = None
    course_infos: List[CourseCurriculumInformation] = []

    # By sequentially going through the results, we can associate course links to their amount of credits.
    for element in driver.find_elements(By.XPATH, module_or_course_link_selector):
        if element.tag_name == "tr":
            current_module_name = element.find_element(By.XPATH, "td[1]//span//span").text
            current_credits = int(element.find_element(By.XPATH, "td[4]//span").text)
            current_course = None
        else:
            course_link = element.get_attribute("href")
            assert course_link is not None
            if current_course is None:
                current_course = CourseCurriculumInformation(urls=[course_link], num_credits=current_credits, module_name=current_module_name)
                course_infos.append(current_course)
            else:
                current_course.urls.append(course_link)
    
    return (course_infos, current_credits, current_module_name)

def wait_until_not_loading(driver):
    WebDriverWait(driver, 60).until(
        expected_conditions.invisibility_of_element_located((By.CLASS_NAME, "pageLoading"))
    )
    WebDriverWait(driver, 60).until(
        expected_conditions.invisibility_of_element_located((By.ID, "id-loader"))
    )

def main():
    parser = argparse.ArgumentParser(usage=
    """
    fetch_curriculum_tree.py [-h] --curriculum CURRICULUM
    Curriculum: valid options are `master-informatics', 'master-dea'
    """)
    parser.add_argument("--curriculum", required=True, default="master-informatics",
                        type=str, help="One of ['master-informatics', 'master-dea']")
    args = parser.parse_args()
    curriculum = curriculums[args.curriculum]

    # Start a headless Firefox instance
    options = webdriver.FirefoxOptions()
    options.set_preference("intl.locale.requested", "en-US") # doesn't help though
    # options.add_argument("-headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),
                               options=options)
    try:
        fetch_curriculum_course_infos(driver, curriculum)
    finally:
    #    driver.close()
        pass

def fetch_curriculum_course_infos(driver: webdriver.Firefox, curriculum: Curriculum):
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
    # TODO Identify course tables with no entries, and click "back" until you find an entry
    # TODO Parallelize: multiple drivers; e.g. share session by: for cookie in r1.get_cookies(): driver2.add_cookie(cookie)
    # TODO ignore exam nodes, only use course nodes (speedup!)
    # TODO also find module nodes with no credits section: otherwise, URLs might be wrongly associated with the module node before (e.g. Anerkennung Robotik -> Virtualization Techniques)
    # TODO more reliably find *module* names (which are more likely to contain course codes). Example: [EI71070] Advanced Cryptographic Implementations (module node); Advanced Cryptographic Implementations (exam node, but also has credits and hence used).

    driver.set_script_timeout(20)
    driver.implicitly_wait(5)

    # Navigate to curriculum tree site
    driver.get(curriculum.tree_url)
    
    # Switch language to English
    driver.find_element(By.TAG_NAME, "coa-desktop-language-menu").click()
    driver.find_element(By.XPATH, f"//button[@title='Sprache Englisch']").click()
    time.sleep(2)

    # Switch node filter to All (Expanded)
    driver.find_element(By.XPATH, f"//button[@id='ca-id-stpvw-elementart-knoten']").click()
    driver.find_element(By.XPATH, f"//a[@id='ca-id-cs-nav-alle-expanded']").click()

    wait_until_not_loading(driver)
    time.sleep(3)

    num_pages = int(driver.find_element(By.CLASS_NAME, "coTableNaviPageSelect").text.split("\n")[-1].removeprefix("of "))
    last_credits_on_previous_page = None
    last_module_name_on_previous_page = None
    all_curriculum_course_infos = []

    for page in tqdm.tqdm(range(num_pages)):
        plus_buttons = descendant_plus_buttons(driver)
        for button in tqdm.tqdm(plus_buttons, leave=False):
            click_button(driver, button)

        wait_until_not_loading(driver)

        curriculum_course_infos, last_credits_on_page, last_module_name_on_page = extract_courses_with_credits(driver)
        # print(curriculum_course_infos)
        for course_info in curriculum_course_infos:
            if course_info.num_credits is not None:
                break
            assert last_credits_on_previous_page is not None
            course_info.num_credits = last_credits_on_previous_page
            course_info.module_name = last_module_name_on_previous_page
        
        last_module_name_on_previous_page = last_module_name_on_page or last_module_name_on_previous_page
        last_credits_on_previous_page = last_credits_on_page or last_credits_on_previous_page

        all_curriculum_course_infos.extend(curriculum_course_infos)

        # Go to next page
        next_page_button = next(iter(driver.find_elements(By.XPATH, f"//a[@class='coTableNaviNextPage']")), None)
        if next_page_button is None:
            break

        next_page_url = next_page_button.get_attribute("href")
        assert next_page_url is not None
        driver.get(next_page_url)
        wait_until_not_loading(driver)
        time.sleep(5)

    with open(curriculum.tree_file_path, "w") as f:
        # save with indent=0 (will insert newlines, more diff-friendly)
        json.dump([asdict(course_info) for course_info in all_curriculum_course_infos], f, indent=0)
        print(f"""Results written to json file '{curriculum.tree_file_path}'""")
    
    driver.close()
    return all_curriculum_course_infos

    # # Find the "Elective Modules" subtree (ignore other top-level subtrees)
    # plus_buttons = descendant_plus_buttons(driver)
    # (electives_button, ) = [button for button in plus_buttons
    #                         if ("Elective Modules" in button.text
    #                              or "Wahlmodulkatalog" in button.text
    #                              or "Wahlmodule" in button.text)
    #                              and "Überfachliche" not in button.text]
    
    # # Since we don't have a lot of control or implicit information about the HTML
    # # representation of the tree (it's flat in the HTML, not nested in tree form),
    # # we need some tricks.
    # # We perform a depth-first search as follows:
    # # - pop current node from stack and click its "toggle" button. Then find all
    # #   buttons and identify the newly added ones (for this purpose, keep track of all
    # #   previously seen buttons).
    # #   - this way, we build up a tree (parent/child relationships between buttons)
    # #   - add children to search stack
    # # - repeat until stack is exhausted
    # seen_plus_buttons = set([button for button in plus_buttons])
    # tree = {"name": electives_button.text,
    #         "object": electives_button,
    #         "children": [],
    #         "level": 0,
    #          # progress_ratio: by how much progress goes up once this node is completed
    #         "progress_ratio": 1.0
    #         }
    # next_nodes = [tree]

    # MAX_LEVELS = 4

    # # We update the progress bar like this (given we don't know the total beforehand):
    # # - every node has a "progress_ratio" in [0, 1]
    # # - on completing this node, increase progress by a (1-SUBTREE_PROGRESS_RATIO) ratio
    # #   of progress_ratio (or 1*progress_ratio if it is a leaf node)
    # # - equally distribute the remainder of progress ratio to the children
    # progress_bar = tqdm.tqdm(total=1,
    #                          bar_format="{desc}: {percentage:3.0f}%|{bar}|" +
    #                                     "[{elapsed}<{remaining}]")
    # # estimate of how much of the work goes on in the subtree, vs. clicking the root
    # SUBTREE_PROGRESS_RATIO = 0.98

    # crawl_successful = False

    # try:
    #     # Perform depth-first search
    #     while len(next_nodes) > 0:
    #         # Toggle the current nodes and collect its child nodes
    #         active_node = next_nodes.pop() # pop last node (-> DFS)
    #         if active_node["level"] < MAX_LEVELS:
    #             button = active_node["object"]
    #             click_button(driver, button)
    #             new_plus_buttons = [button for button 
    #                                 in descendant_plus_buttons(driver,
    #                                                            active_node.get("element_id"))
    #                                 if button not in seen_plus_buttons
    #                                 and "Master-Praktikum" not in button.text
    #                                 and "Practical Course" not in button.text]
    #             num_children = len(new_plus_buttons)
    #             active_node["children"] = [
    #                 {"name": plus_button.text,
    #                     "object": plus_button,
    #                     "credits": get_number_of_credits(plus_button),
    #                     "children": [],
    #                     "level": active_node["level"] + 1,
    #                     "progress_ratio": (
    #                         active_node["progress_ratio"]*SUBTREE_PROGRESS_RATIO/num_children),
    #                     "element_id": str(plus_button.get_attribute("id")
    #                                       ).removesuffix("-toggle")
    #                 }
    #                 for plus_button in new_plus_buttons
    #             ]
    #             next_nodes.extend(reversed(active_node["children"]))
    #             seen_plus_buttons = seen_plus_buttons.union(new_plus_buttons)
    #             progress_bar.update(active_node["progress_ratio"]*(1-SUBTREE_PROGRESS_RATIO)
    #                                 if num_children > 0
    #                                 else active_node["progress_ratio"])
    #         else:
    #             progress_bar.update(active_node["progress_ratio"])
    #     crawl_successful = True
    # except Exception as e:
    #     print(e)
    # finally:
    #     progress_bar.close()

    #     # Print text representation of tree
    #     print_tree(tree)

    #     # Save tree as pickle file after cleaning it (i.e. remove selenium objects)
    #     def clean_tree(tree):
    #         del tree["object"]
    #         del tree["progress_ratio"]
    #         tree["name"] = str(tree["name"])
    #         for child in tree["children"]:
    #             clean_tree(child)
    #     clean_tree(tree)
    #     with open(curriculum.tree_file_path, "w") as f:
    #         # save with indent=0 (will insert newlines, more diff-friendly)
    #         json.dump(tree, f, indent=0)
    #     print(f"""Results written to json file '{curriculum.tree_file_path}'""")
    #     if not crawl_successful:
    #         print("Warning! There was an error, tree crawl incomplete (see above)")
    #     driver.close()
    #     return tree

if __name__ == "__main__":
    main()
