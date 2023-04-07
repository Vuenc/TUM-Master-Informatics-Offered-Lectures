from webdriver_manager.firefox import GeckoDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import pickle
from dotenv import load_dotenv
import os
from curriculums import curriculums
import argparse
from curriculums import curriculums

def click_button(driver, button):
    onclick = button.get_attribute("onclick")
    script = f"arguments[0].f = () => {{{onclick.replace('this', 'arguments[0]')}}}; arguments[0].f();"
    print(script)
    result = driver.execute_script(script, button)
    # driver.execute_script("arguments[0].scrollIntoView();", button)
    # button.click()
    print("Opening", button.text)



# def click_many_buttons(driver, button):
#     onclick = button.get_attribute("onclick")
#     script = f"arguments[0].f = () => {{{onclick.replace('this', 'arguments[0]')}}}; arguments[0].f();"
#     print(script)
#     result = driver.execute_script(script, button)
#     # driver.execute_script("arguments[0].scrollIntoView();", button)
#     # button.click()
#     print("Opening", button.text)

def login_tum_online(driver: webdriver.Firefox, username, password):
    tumonline_url = "https://campus.tum.de"
    username_field_id = "id_brm-pm-dtop_login_uname_input"
    password_field_id = "id_brm-pm-dtop_login_pw_input"
    login_button_id = "id_brm-pm-dtop_login_submitbutton"
    driver.get(tumonline_url)
    driver.find_element(value=username_field_id).send_keys(username)
    driver.find_element(value=password_field_id).send_keys(password)
    driver.find_element(value=login_button_id).click

def descendant_plus_buttons(element):
    # Plus buttons are distinguished by their background image, which has "tee_plus" in its filename
    # return [a for a in element.find_elements(By.CSS_SELECTOR, "a") if "tee_plus" in a.value_of_css_property("background-image")]
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
    parser.add_argument("--curriculum", required=True, default="master-informatics", type=str, help="One of ['master-informatics', 'master-dea']")
    args = parser.parse_args()
    curriculum = curriculums[args.curriculum]

    options = webdriver.FirefoxOptions()
    options.set_preference("intl.locale.requested", "en-US") # doesn't help though
    options.add_argument("-headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)


    driver.set_script_timeout(20)
    driver.implicitly_wait(5)

    load_dotenv()

    login_tum_online(driver, os.getenv("TUMONLINE_USERNAME"), os.getenv("TUMONLINE_PASSWORD"))

    driver.get(curriculum.tree_url)
    
    plus_buttons = descendant_plus_buttons(driver)
    print([button.text for button in plus_buttons])
    (electives_button, ) = [button for button in plus_buttons if ("Elective Modules" in button.text or "Wahlmodulkatalog" in button.text or "Wahlmodule" in button.text) and "Überfachliche" not in button.text]
    
    seen_plus_buttons = set([button for button in plus_buttons])
    
    tree = {"name": electives_button.text, "object": electives_button, "children": []}
    active_levels = [tree]

    MAX_LEVELS = 4
    num_levels = 0

    try:
        while len(active_levels) > 0 and num_levels < MAX_LEVELS:
            new_active_levels = []
            for active_level in active_levels:
                button = active_level["object"]
                click_button(driver, button)
                new_plus_buttons = [button for button in descendant_plus_buttons(driver) if button not in seen_plus_buttons and "Master-Praktikum" not in button.text]
                active_level["children"] = [
                    {"name": plus_button.text, "object": plus_button, "credits": get_number_of_credits(plus_button), "children": []}
                    for plus_button in new_plus_buttons
                ]
                new_active_levels.extend(active_level["children"])
                seen_plus_buttons = seen_plus_buttons.union(new_plus_buttons)
            active_levels = new_active_levels
            num_levels += 1
    except Exception as e:
        print(e)
    finally:
        print_tree(tree)
        def clean_tree(tree):
            tree["object"] = None
            tree["name"] = str(tree["name"])
            for child in tree["children"]: clean_tree(child)
        clean_tree(tree)
        with open(curriculum.tree_file, "wb") as f:
            pickle.dump(tree, f)
        driver.close()
        return tree

if __name__ == "__main__":
    main()