import pandas as pd
import pickle

hello = pd.read_excel("output.xlsx")
print(hello.shape[0])


def load_links_from_file(filename="links.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return []


helo = load_links_from_file()

print(len(helo))
