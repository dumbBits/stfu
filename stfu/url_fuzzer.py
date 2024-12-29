import itertools 
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import argparse
from webdriver_manager.chrome import ChromeDriverManager
import time 

def generate_url_permutations(base_words, max_length=3, separator="/"):
    #generate URL path permutations based on input base words.

    #Arguments: base_words (list): basic words  to permute
    #max_length: (int): maximum length of permutations. 
    #seperator (str): Seperator used to build URL paths.

    #Returns:
        #a List of generated URL Paths.

    if not base_words or max_length < 1:
        raise ValueError("Base words must be a non empty list and max_legth must be bigger 1")
    
    permutations = []
    for length in range(1, max_length +1):
        for perm in itertools.permutations(base_words, length):
            #join words with seperator 
            url_path = separator.join(perm)
            permutations.append(url_path)
    return permutations

#integration of selenium webcrawler 
def send_selenium_requests(base_url, paths):
    #use selenium to load URLS 
    results = []
    #set up selenium webdriver 
    options = Options()
    service = Service(ChromeDriverManager().install()) #Replace later
    options.headless = True
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")  # Recommended for headless mode
    options.add_argument("--no-sandbox")  # Needed for some environments like Docker
    options.add_argument("--disable-dev-shm-usage")  # Avoid resource issues in headless mode
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(service=service, options=options)

    for path in paths:
        full_url = urljoin(base_url, path)
        try:
            driver.get(full_url)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
            #ectract links 
            links = [link.get_attribute("href") for link in driver.find_elements(By.TAG_NAME, "a")]
            headers = [header.text for header in driver.find_elements(By.TAG_NAME, "h1")]
            subheaders = [subheader.text for subheader in driver.find_elements(By.TAG_NAME, "h2")]
            #extract errors 
            error_messages = [error.text for error in driver.find_elements(By.CLASS_NAME, "error")]

            #store extracted data 
            results.append({
                "url": full_url,
                "links": links,
                "headers": headers, 
                "subheaders": subheaders,
                "errors": error_messages
            })
            print(f"[SUCCESS]{full_url}-Extracted {len(links)}, links {len(headers), headers}")
        except Exception as e:
            (print(f"[Error] failed to load {full_url}: {e}"))

    driver.quit()
    return results 

def collect_keywords(results):
    #extract meaningful words to refeed them into the permutation class
    keywords = set()
    for result in results:
        links = result.get("links", [])
        for link in links:
            if link:
                segments = link.split("/") #line splitting into segments
                keywords.update(segments) #add unique segments as keywords 
        
        #extract words from headers & subheaders 
        headers = result.get("headers", [])
        subheaders = result.get("subheaders", [])
        keywords.update("headers")
        keywords.update("subheaders")
        errors = result.get("errors", [])
        #extract words from error messages 
        keywords.update("errors")
    #filter and clean up the words 
    filtered_keyword ={word.strip().lower() for word in keywords if word and len(word) > 2 }
    return filtered_keyword

def send_http_request(base_url, paths):
    #send http get requests to target URL 
    #Arguments: base_url: target  URL (http://example.com)
    #paths: list of URL paths to test
    #returns: list of successful paths and status code
    results = []
    for path in paths:
        full_url = urljoin(base_url, path) 
        try:
            response = requests.get(full_url, timeout=5)
            results.append((full_url, response.status_code))
            print(f"[{response.status_code}]{full_url}")
        except requests.RequestException as e:
            print(f"[Error] failed to connect to {full_url}: {e}")
    return results

def main():
    parser = argparse.ArgumentParser(description= "Fuzz URL smarter with SmartFuzz!")
    parser.add_argument()

    #example input
    base_words = ['admin', 'login', 'api']
    max_length = 3
    separator = "/"

    print_ascii_art()
    base_url = input("Enter the target URL (e.g: http://example.com)\n")

    #generate permutations 
    try: 
        for iteration in range(3):
            print(f"\nIteration {iteration + 1}:")
            url_paths = generate_url_permutations(base_words, max_length, separator,)
            print(f"Generated following Paths:{len(url_paths)}\n starting http requests...")
        
            http_results = send_http_request(base_url, url_paths)
            print("\ncompleted http requests. Succesful results:")
        
            selenium_results= send_selenium_requests(base_url, url_paths)
            print("\nSelenium Completed Requests. Extracted Results:")
            for result in selenium_results:
                print(f"URL: {result['url']}")
                print(f"  Links: {len(result['links'])} - {result['links'][:3]}")  # Show first 3 links
                print(f"  Headers: {result['headers']}")
                print(f"  Subheaders: {result['subheaders']}")
                print(f"  Errors: {result['errors']}")
                print()

            new_keywords = collect_keywords(selenium_results)
            print(f"new keywords discovered: {new_keywords}")
            #add new keywords 
            base_words = list(set(base_words) | new_keywords)
            print(f"updated Base Words: {base_words}")

        for url, status in http_results: 
            if 200 <= status <300: 
                print(f"[{status}]{url}")
        print("\nStarting Selenium requests...")
        selenium_results = send_selenium_requests(base_url, url_paths)
        print("\nSelenium completed. Successful results:")
        for url, content in selenium_results:
            print(f"{url} -Content Snippet: {content}")

    except ValueError as e:
        print(f"Error: {e}")