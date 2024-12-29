#!/usr/bin/env python3
import argparse
import requests 
from SmarTFUzz.url_fuzzer import (
    generate_url_permutations,
    send_http_request,
    send_selenium_requests,
    collect_keywords
)

def print_ascii_art():
    print(r""" 
   _____                   _______ ______ _    _         
  / ____|                 |__   __|  ____| |  | |        
 | (___  _ __ ___   __ _ _ __| |  | |__  | |  | |________
  \___ \| '_ ` _ \ / _` | '__| |  |  __| | |  | |_  /_  /
  ____) | | | | | | (_| | |  | |  | |    | |__| |/ / / / 
 |_____/|_| |_| |_|\__,_|_|  |_|  |_|     \____//___/___|""")


def main():
    testmessage = requests.get("https://wikipedia.de")
    print(f"{testmessage.content}")
    parser = argparse.ArgumentParser(description=" Fuzz URL smarter with smartfuzzer!")
    parser.add_argument("-u", "--url", required=True, help="Base URL as target (e.g., http(s)://example.com)")
    parser.add_argument("-w", "--words", nargs="+", required=True, help="Base words for permutations (e.g., admin, login, api, php...)")
    parser.add_argument("-m", "--max-length", type=int, default=3, help="Maximum permutation length, (default 3)")
    parser.add_argument("-s", "--separator", default="/", help="Seperator for URL paths (default: /)")
    parser.add_argument("-i", "--iterations", type=int, default = 3, help="Number of iterations(default 3 iterations)")
    args = parser.parse_args()

    print_ascii_art()

    base_url =args.url 
    base_words = args.words
    max_length = args.max_length
    separator = args.separator 
    iterations = args.iterations 

    try: 
        for iteration in range(iterations):
            print(f"\nIteration {iteration +1}:")
            url_paths = generate_url_permutations(base_words, max_length, separator)
            print(f"Generated {len(url_paths)} paths. \n")

            #send http reqeuest to get status code
            http_results = send_http_request(base_url, url_paths)
            for url, status in http_results: 
                if 200 <= status < 300:
                    print(f"[{status}]{url}")

            #send selenium requests 
            selenium_results = send_selenium_requests(base_url, url_paths)
            print("\nSelenium Completed Requests. Extracted Results:")
            for result in selenium_results:
                print(f"URL: {result['url']}")
                print(f"  Links: {len(result['links'])} - {result['links'][:3]}")
                print(f"  Headers: {result['headers']}")
                print(f"  Subheaders: {result['subheaders']}")
                print(f"  Errors: {result['errors']}")
                print()
            # Extract new keywords and update base_words
            new_keywords = collect_keywords(selenium_results)
            print(f"New Keywords Discovered: {new_keywords}")
            base_words = list(set(base_words) | new_keywords)
            print(f"Updated Base Words: {base_words}")
        
    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()