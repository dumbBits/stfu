# URL Fuzzer

## Overview

**URL Fuzzer** is a Python-based terminal application designed to discover hidden or restricted URL paths by generating permutations of user-specified keywords. The tool performs requests using both HTTP and Selenium, extracting and analyzing data dynamically to discover new keywords for deeper fuzzing.

---

## Features

- **Dynamic URL Permutations**:
  - Generates URL paths using user-provided base words.
- **HTTP and Selenium Requests**:
  - Tests paths using `requests` for static content and Selenium for JavaScript-rendered pages.
- **Keyword Extraction**:
  - Dynamically extracts keywords from links, headers, and other content to refine search.
- **CLI Support**:
  - Fully configurable from the terminal with arguments for base words, max length, iterations, and more.

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/url-fuzzer.git
cd url-fuzzer

pip install SmarTFUzz

pip install -r requirements.txt

chmod +x main.py