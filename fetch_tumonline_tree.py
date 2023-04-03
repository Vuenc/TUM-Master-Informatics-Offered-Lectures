from webdriver_manager.firefox import GeckoDriverManager
import webdriver_manager
import selenium
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
import pickle

def click_button(driver, button):
    onclick = button.get_attribute("onclick")
    script = f"arguments[0].f = () => {{{onclick.replace('this', 'arguments[0]')}}}; arguments[0].f();"
    print(script)
    result = driver.execute_script(script, button)
    # driver.execute_script("arguments[0].scrollIntoView();", button)
    # button.click()
    print("Opening", button.text)
    
def descendant_plus_buttons(element):
    # Plus buttons are distinguished by their background image, which has "tee_plus" in its filename
    return [a for a in element.find_elements(By.CSS_SELECTOR, "a") if "tee_plus" in a.value_of_css_property("background-image")]

def print_tree(tree, prefix="|--"):
    print(prefix[:-1], tree["name"])
    for child in tree["children"]:
        print_tree(child, prefix + "|--")


def main(url="https://campus.tum.de/tumonline/wbstpcs.showSpoTree?pStpStpNr=4731"):
    options = webdriver.FirefoxOptions()
    options.set_preference("intl.locale.requested", "en-US")
    options.add_argument("-headless")
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)


    driver.set_script_timeout(20)
    driver.get(url)
    plus_buttons = descendant_plus_buttons(driver)
    print([button.text for button in plus_buttons])
    (electives_button, ) = [button for button in plus_buttons if "Elective Modules" in button.text or ("Wahlmodulkatalog" in button.text and "Überfachliche" not in button.text)]
    
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
                    {"name": plus_button.text, "object": plus_button, "children": []}
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
        with open("tumonline_tree.obj", "wb") as f:
            pickle.dump(tree, f)
        driver.close()
        return tree

if __name__ == "__main__":
    main()