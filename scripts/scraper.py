# Write web scraper to get data from the url mentioned in a file named config.yml
# The scraper should be able to scrape the data from the url and store it in a JSON file.
# suggest libraries to be used for the same.
from json import dump as write_json, load as read_json
from yaml import load as read_yaml, Loader
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait as wait
from selenium.webdriver.chrome.options import Options
from time import sleep

def main():
    # setup the browser
    options = Options()
    options.add_argument('headless')
    browser = Chrome(options=options)
    # Read the config file
    with open("./scripts/config.yml", 'r') as config_file:
        print("📖 Reading config file...")
        config = read_yaml(config_file, Loader=Loader)
        config_file.close()
    # read the config file
    url = config['URL']
    base_url = url['base']
    selectors = config['selectors']
    path = config['PATH']
    # open the base url in browser
    browser.get(base_url)
    # Parse the source using BeautifulSoup
    content = BeautifulSoup(browser.page_source, 'html.parser')
    # Get the sidebar content within the element with class 'site-sidebar'
    sidebar = content.select(selectors['sidebar'])
    # Get the list item elements within the sidebar > nav element
    nav_menu_items = sidebar[0].select(selectors['navigation_menu_item'])
    # Create a dictionary to store the blueprint name and url
    blueprint_dict: dict[str, str] = {}
    # find the list item with the .slds-media__body content as 'Component Blueprints'
    for item in nav_menu_items:
        if item.select(selectors['navigation_menu_item_title'])[0].text == config['blueprints_menu_item_title']:
            # Get the list of blueprints
            blueprints = item.select('ul > li > a')
            # Iterate through the list of blueprints
            for blueprint in blueprints:
                # Get the blueprint name
                blueprint_name: str = blueprint.text
                # Get the blueprint url
                blueprint_url: str = blueprint['href']
                # Add the blueprint name and url to the dictionary
                blueprint_dict[blueprint_name] = blueprint_url
                print(f"✔️ found Blueprint: {blueprint_name} - {blueprint_url}")
    print(f"✏️ Writing blueprints to {path['blueprints_output']}")
    # Write the dictionary to a json file
    with open(path['blueprints_output'], 'w') as json_file:
        write_json(blueprint_dict, json_file, indent=2)
        json_file.close()
    # sleep for 5 seconds before making the next request
    print("⏳ Sleeping for 5 seconds...")
    sleep(5)

    # create a dictionary to store the styling hooks
    styling_hooks_dict: dict[str, str] = {}
    # open the json file
    with open(path['blueprints_output'], 'r') as blueprints_file:
        # load the json file
        blueprints_dict = read_json(blueprints_file)
        blueprints_file.close()
    # iterate through the blueprints, exclude the blueprint with name in the exclude list in config file
    for blueprint_name, blueprint_url in blueprints_dict.items():
        if blueprint_name not in config['excluded_blueprint_titles']:
            print(f"🔍 Searching for Styling Hooks in {blueprint_name}")
            # get the blueprint response from base url + blueprint url
            browser.get(base_url + blueprint_url)
            wait(driver=browser, timeout=10).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'site-sticky-navbar')))
            # parse the blueprint response
            blueprint_content = BeautifulSoup(browser.page_source, 'html.parser')
            # check if the blueprint has an element with id 'Styling-Hooks-Overview'
            if blueprint_content.select(selectors['styling_hooks_menu']):
                print(f"✔️ Found Styling Hooks in {blueprint_name}")
                # get the styling hooks table
                styling_hooks_table = blueprint_content.select(selectors['styling_hooks_table'])
                # if the styling hooks table is not found, print a warning and continue
                if len(styling_hooks_table) == 0:
                    print(f"⚠️ Styling Hooks table not found in {blueprint_name}")
                    continue
                # get the table rows
                styling_hooks_table_rows = styling_hooks_table[0].select(selectors['styling_hooks_table_row'])
                # iterate through the table rows
                for row in styling_hooks_table_rows:
                    # get the styling hook name
                    styling_hook_name = row.select(selectors['styling_hook_name'])[0].text
                    # get the styling hook fallback value
                    styling_hook_fallback_value = row.select(selectors['styling_hook_fallback_value'])[0].text
                    # add the styling hook name and fallback to the dictionary
                    styling_hooks_dict[styling_hook_name] = styling_hook_fallback_value
            else:
                print(f"⚠️ No Styling Hooks found in {blueprint_name}")
        else:
            print(f"⚠️ Excluded Blueprint: {blueprint_name}")
    if len(styling_hooks_dict) == 0:
        print("⚠️ No Styling Hooks found in any of the blueprints")
    else:
        print(f"✏️ Writing styling hooks to {path['styling_hooks_output']}")
        # write the styling hooks dictionary to a json file
        with open(path['styling_hooks_output'], 'w') as json_file:
            write_json(styling_hooks_dict, json_file, indent=2)
            json_file.close()
    browser.quit()


if __name__ == '__main__':
    main()

