from bs4 import BeautifulSoup as soup
import requests
import sys, os, csv
from prettytable import PrettyTable

from Student import Student


from bs4 import BeautifulSoup
from Student import Student

def parseMinors(soup):
    '''Function to parse the DCS minors HTML and create dictionaries by year and by advisor.
    Parameters: 
        soup: BeautifulSoup object
    Returns: 
        tuple containing dict_by_year, dict_by_advisor dictionaries
    '''
    by_year, by_adv = {}, {}

    # locate the main table of students
    table = soup.find("table", {"id": "studentList"})
    if not table:
        return by_year, by_adv

    # each student = one table row
    for row in table.find_all("tr")[1:]:     # skip header
        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        name = cols[1].get_text(strip=True)
        year = cols[3].get_text(strip=True)
        email = cols[5].get_text(strip=True)
        majors = [abbr.get_text() for abbr in cols[6].find_all("abbr")]
        minors = [abbr.get_text() for abbr in cols[7].find_all("abbr")]
        gecs   = [abbr.get_text() for abbr in cols[8].find_all("abbr")]
        advisor = cols[9].get_text(strip=True)

        stu = Student(name, email, int(year), majors, minors, gecs, advisor)

        by_year.setdefault(year, []).append(stu)
        by_adv.setdefault(advisor, []).append(stu)

    return by_year, by_adv


def printOutput(by_year, by_adv):
    '''
    Function to display the parsed DCS minors data in formatted tables.
    Parameters
        by_year : Dictionary of students grouped by class year.
        by_adv : Dictionary of students grouped by advisor.
    Returns:
        Three distinct tables
    '''
    roster_table = PrettyTable(["Student", "Email", "Year", "Major(s)", "Minor(s)", "Advisor"])
    for year in sorted(by_year.keys()):
        # sort by last, first name for readability
        for stu in sorted(by_year[year], key=lambda s: s.name):
            row = stu.getCSVList()
            roster_table.add_row([f"{row[0]}, {row[1]}", row[2], row[3], row[4], row[5], row[7]])
    print(roster_table)

    year_table = PrettyTable(["Year", "# DCS Minors"])
    for year in sorted(by_year.keys()):
        year_table.add_row([year, len(by_year[year])])
    print("\n" + str(year_table))

    adv_table = PrettyTable(["Advisor", "# DCS Minors"])
    for adv in sorted(by_adv.keys()):
        adv_table.add_row([adv, len(by_adv[adv])])
    print("\n" + str(adv_table))


def writeCSVFiles(by_year: dict) -> None:
    '''Write one CSV file per graduation year containing DCS minor information.
    Parameters: 
        by_year : Dictionary of students grouped by class year.
    '''
    for year, students in by_year.items():
        fname = f"dcs_minors_{year}.csv"
        print(f"Writing {fname}...")
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Last", "First", "Email", "Year", "Majors", "Minors", "GECs", "Advisor"])
            for stu in students:
                w.writerow(stu.getCSVList())


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--help":
        print("Usage: python dcs211_lab3.py <writeCSV True/False> <optional: HTML filename>")
        sys.exit(0)

    # first arg: writeCSV (accept True/False in any case form per spec)
    writeCSV = False
    if len(sys.argv) > 1:
        try:
            writeCSV = bool(eval(sys.argv[1].title()))  # e.g., 'false' -> False (per lab hint)
        except Exception:
            sys.exit("First argument must be True or False (case-insensitive).")

    # second arg: optional HTML filename; otherwise list .html files and prompt default
    if len(sys.argv) > 2:
        html_file = sys.argv[2]
    else:
        html_files = sorted(f for f in os.listdir(".") if f.lower().endswith(".html"))
        if not html_files:
            sys.exit("No .html files found in the current directory.")
        print("HTML files found:\n")
        for f in html_files:
            print(f)
        default = html_files[0]
        choice = input(f"\nEnter name of HTML source (return for default '{default}'): ").strip()
        html_file = choice if choice else default

    # read HTML
    try:
        with open(html_file, "r", encoding="utf-8") as fh:
            html_text = fh.read()
    except Exception:
        sys.exit(f"Cannot open or read {html_file}")

    # parse
    soup = BeautifulSoup(html_text, "html.parser")
    by_year, by_adv = parseMinors(soup)

    # output
    if writeCSV:
        writeCSVFiles(by_year)  # writes dcs_minors_<year>.csv files as in the example
    else:
        printOutput(by_year, by_adv)

if __name__ == "__main__":
    main()