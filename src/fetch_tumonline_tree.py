from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import pickle
from dotenv import load_dotenv
import os
from curriculums import curriculums
import argparse
import tqdm

def click_button(driver, button):
    # The toggle buttons execute some script on `onclick` to expand the tree.
    # Therefore we extract this piece of code and execute it directly, to the same
    # effect as if the button had been clicked (but more reliable).
    onclick = button.get_attribute("onclick")
    script = (
        f"""arguments[0].f = () => {{{onclick.replace('this', 'arguments[0]')}}};
        arguments[0].f();"""
    )
    driver.execute_script(script, button)

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
    if parent_id is not None:
        return element.find_elements(By.XPATH,
                                     f"//tr[@id='{parent_id}']/following-sibling::*//a[contains(@id,'toggle')]")
    else:
        return element.find_elements(By.XPATH, "//a[contains(@id,'toggle')]")

def print_tree(tree, prefix="|--"):
    print(prefix[:-1], tree["name"])
    for child in tree["children"]:
        print_tree(child, prefix + "|--")

def get_number_of_credits(button):
    return button.find_element(By.XPATH, "../../../../td[4]//span").text


def main():
    parser = argparse.ArgumentParser(usage=
    """
    fetch_tumonline_tree.py [-h] --curriculum CURRICULUM
    Curriculum: valid options are `master-informatics', 'master-dea'
    """)
    parser.add_argument("--curriculum", required=True, default="master-informatics",
                        type=str, help="One of ['master-informatics', 'master-dea']")
    args = parser.parse_args()
    curriculum = curriculums[args.curriculum]

    # Start a headless Firefox instance
    options = webdriver.FirefoxOptions()
    options.set_preference("intl.locale.requested", "en-US") # doesn't help though
    options.add_argument("-headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),
                               options=options)
    driver.set_script_timeout(20)
    driver.implicitly_wait(5)

    # Load TUM online login credentials (the curriculum view is publicly available, but
    # only in German - when logged in, you get the English version)
    load_dotenv()
    login_tum_online(driver, os.getenv("TUMONLINE_USERNAME"),
                     os.getenv("TUMONLINE_PASSWORD"))

    # Navigate to curriculum tree site
    driver.get(curriculum.tree_url)
    
    # Find the "Elective Modules" subtree (ignore other top-level subtrees)
    plus_buttons = descendant_plus_buttons(driver)
    (electives_button, ) = [button for button in plus_buttons
                            if ("Elective Modules" in button.text
                                 or "Wahlmodulkatalog" in button.text
                                 or "Wahlmodule" in button.text)
                                 and "Überfachliche" not in button.text]
    
    # Since we don't have a lot of control or implicit information about the HTML
    # representation of the tree (it's flat in the HTML, not nested in tree form),
    # we need some tricks.
    # We perform a depth-first search as follows:
    # - pop current node from stack and click its "toggle" button. Then find all
    #   buttons and identify the newly added ones (for this purpose, keep track of all
    #   previously seen buttons).
    #   - this way, we build up a tree (parent/child relationships between buttons)
    #   - add children to search stack
    # - repeat until stack is exhausted
    seen_plus_buttons = set([button for button in plus_buttons])
    tree = {"name": electives_button.text,
            "object": electives_button,
            "children": [],
            "level": 0,
             # progress_ratio: by how much progress goes up once this node is completed
            "progress_ratio": 1.0
            }
    next_nodes = [tree]

    MAX_LEVELS = 4

    # We update the progress bar like this (given we don't know the total beforehand):
    # - every node has a "progress_ratio" in [0, 1]
    # - on completing this node, increase progress by a (1-SUBTREE_PROGRESS_RATIO) ratio
    #   of progress_ratio (or 1*progress_ratio if it is a leaf node)
    # - equally distribute the remainder of progress ratio to the children
    progress_bar = tqdm.tqdm(total=1,
                             bar_format="{desc}: {percentage:3.0f}%|{bar}|" +
                                        "[{elapsed}<{remaining}]")
    # estimate of how much of the work goes on in the subtree, vs. clicking the root
    SUBTREE_PROGRESS_RATIO = 0.98

    crawl_successful = False

    try:
        # Perform depth-first search
        while len(next_nodes) > 0:
            # Toggle the current nodes and collect its child nodes
            active_node = next_nodes.pop() # pop last node (-> DFS)
            if active_node["level"] < MAX_LEVELS:
                button = active_node["object"]
                click_button(driver, button)
                new_plus_buttons = [button for button 
                                    in descendant_plus_buttons(driver,
                                                               active_node.get("element_id"))
                                    if button not in seen_plus_buttons
                                    and "Master-Praktikum" not in button.text
                                    and "Practical Course" not in button.text]
                num_children = len(new_plus_buttons)
                active_node["children"] = [
                    {"name": plus_button.text,
                        "object": plus_button,
                        "credits": get_number_of_credits(plus_button),
                        "children": [],
                        "level": active_node["level"] + 1,
                        "progress_ratio": (
                            active_node["progress_ratio"]*SUBTREE_PROGRESS_RATIO/num_children),
                        "element_id": str(plus_button.get_attribute("id")
                                          ).removesuffix("-toggle")
                    }
                    for plus_button in new_plus_buttons
                ]
                next_nodes.extend(reversed(active_node["children"]))
                seen_plus_buttons = seen_plus_buttons.union(new_plus_buttons)
                progress_bar.update(active_node["progress_ratio"]*(1-SUBTREE_PROGRESS_RATIO)
                                    if num_children > 0
                                    else active_node["progress_ratio"])
            else:
                progress_bar.update(active_node["progress_ratio"])
        crawl_successful = True
    except Exception as e:
        print(e)
    finally:
        progress_bar.close()

        # Print text representation of tree
        print_tree(tree)

        # Save tree as pickle file after cleaning it (i.e. remove selenium objects)
        def clean_tree(tree):
            tree["object"] = None
            tree["name"] = str(tree["name"])
            for child in tree["children"]:
                clean_tree(child)
        clean_tree(tree)
        with open(curriculum.tree_file, "wb") as f:
            pickle.dump(tree, f)
        print(f"""Results written to pickle file '{curriculum.tree_file}'""")
        if not crawl_successful:
            print("Warning! There was an error, tree crawl incomplete (see above)")
        driver.close()
        return tree

if __name__ == "__main__":
    main()
