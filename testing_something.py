import pandas as pd
import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def load_links_from_file(filename="links.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return []


links = load_links_from_file()

print(links[0])
print(len(links))
