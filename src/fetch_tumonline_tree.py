from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import pickle
from dotenv import load_dotenv
import os
from curriculums import curriculums
import argparse
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

def descendant_plus_buttons(element):
    # Plus buttons are distinguished by their element id containing "toggle"
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
    print([button.text for button in plus_buttons])
    (electives_button, ) = [button for button in plus_buttons
                            if ("Elective Modules" in button.text
                                 or "Wahlmodulkatalog" in button.text
                                 or "Wahlmodule" in button.text)
                                 and "Überfachliche" not in button.text]
    
    # Since we don't have a lot of control or implicit information about the HTML
    # representation of the tree (it's flat in the HTML, not nested in tree form),
    # we need some tricks.
    # We perform a breadth-first search as follows:
    # - click all "toggle" buttons on the current level
    #   - after each click, search for all buttons and identify the newly added ones
    #     (for this purpose, keep track of all previously seen buttons)
    #   - this way, we build up tree information (parent/child relationships between
    #     buttons) and identify buttons that lie on the next level
    # - when a level is exhausted, repeat the procedure for all identified buttons on
    #   the next level, until the max. number of levels is reached
    seen_plus_buttons = set([button for button in plus_buttons])
    tree = {"name": electives_button.text, "object": electives_button, "children": []}
    active_nodes = [tree]

    MAX_LEVELS = 4
    num_levels = 0

    try:
        # Perform breadth-first search
        while len(active_nodes) > 0 and num_levels < MAX_LEVELS:
            new_active_nodes = []
            # For nodes on current level, toggle them and collect child nodes
            for active_node in active_nodes:
                button = active_node["object"]
                click_button(driver, button)
                new_plus_buttons = [button for button in descendant_plus_buttons(driver)
                                    if button not in seen_plus_buttons
                                    and "Master-Praktikum" not in button.text]
                active_node["children"] = [
                    {"name": plus_button.text,
                     "object": plus_button,
                     "credits": get_number_of_credits(plus_button),
                     "children": []}
                    for plus_button in new_plus_buttons
                ]
                new_active_nodes.extend(active_node["children"])
                seen_plus_buttons = seen_plus_buttons.union(new_plus_buttons)

            # Replace current level with next level
            active_nodes = new_active_nodes
            num_levels += 1
    except Exception as e:
        print(e)
    finally:
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
        driver.close()
        return tree

if __name__ == "__main__":
    main()