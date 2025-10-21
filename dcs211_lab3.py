from Student import Student
from bs4 import BeautifulSoup as soup
import requests
import sys, os, csv
from prettytable import PrettyTable
from Student import Student
from bs4 import BeautifulSoup
from Student import Student

def command_line():
    if "--help" in sys.argv or len(sys.argv)==1:
        print("Usage: python dcs211_lab3.py <write CSV? False/True> <optional: HTML filename>")
        sys.exit(0)
    
    if len(sys.argv)==2:
        current_dir = os.getcwd()
        list_of_html=[]
        for filename in os.listdir(current_dir):
            if filename[-4:]=="html":
                list_of_html.append(filename)
        list_of_html=sorted(list_of_html)
        print(f"HTML files found:\n          {'\n          '.join(list_of_html)}")
        input(list_of_html[0])
        if bool(eval(sys.argv[1].title()))==True: 
            pass
        if bool(eval(sys.argv[1].title()))==False:
            pass




def parseMinors(soup: BeautifulSoup) -> tuple[dict[str, list[Student]], dict[str, list[Student]]]:
    '''Function to parse the DCS minors HTML and create dictionaries by year and by advisor.
    Parameters: 
        soup: BeautifulSoup object
    Returns: 
        tuple containing by_year, by_advisor dictionaries
    '''
    # Create empty dictionaries named by_year and by_adv
    by_year: dict[str, list[Student]] = {}
    by_adv: dict[str, list[Student]] = {}

    # Using BeautifulSoup .find() function, locate the table with id: "studentList" within the html roster
    table = soup.find("table", {"id": "studentList"})
    # If no such table is found, return empty dictionaries
    if not table:
        return by_year, by_adv 
    # Iterate through all the rows in the table except for the header which is row[0]
    for row in table.find_all("tr")[1:]: 
        # Iterate through all the columns
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        
        # Locate student information by using column indeces
        name = cols[1].get_text(strip=True)
        year = cols[3].get_text(strip=True)
        email = cols[5].get_text(strip=True)
        # Majors, minor, and GECs have an abbreviated title within abbr tags
        majors = [abbr.get_text() for abbr in cols[6].find_all("abbr")]
        minors = [abbr.get_text() for abbr in cols[7].find_all("abbr")]
        gecs   = [abbr.get_text() for abbr in cols[8].find_all("abbr")]
        # Locate advisor names wrapped inside span tag
        adv_td = cols[9]
        adv_span = adv_td.find("span")
        if adv_span and adv_span.get_text(strip=True):
            advisor = adv_span.get_text(strip=True)
        # Create Student object with all relevant information
        stu = Student(name, email, int(year), majors, minors, gecs, advisor)
        # Append the Student object values to by_year and by_adv tuples
        by_year.setdefault(year, []).append(stu)
        by_adv.setdefault(advisor, []).append(stu)

    return by_year, by_adv


def printOutput(by_year: dict[str, list[Student]], by_adv: dict[str, list[Student]]) -> None:
    '''
    Function to display the parsed DCS minors data in formatted tables.
    Parameters
        by_year : Dictionary of students grouped by class year.
        by_adv : Dictionary of students grouped by advisor.
    Returns:
        Three distinct tables
    '''
    # Grab student name in last, first format
    def name_key(stu: Student) -> tuple[str, str]:
        last, first = stu.getCSVList()[:2]
        return (last.lower(), first.lower())
    # Using PrettyTable and by_year dictionary, sort students by year and display all student information in class year ascending order
    roster_table = PrettyTable(["Student", "Email", "Year", "Major(s)", "Minor(s)", "Advisor"])
    for year in sorted(by_year.keys()):
        for stu in sorted(by_year[year], key=name_key):
            row = stu.getCSVList()
            roster_table.add_row([f"{row[0]}, {row[1]}", row[2], row[3], row[4], row[5], row[7]])
    print(roster_table)
    # From the by_year sorting, display the number of DCS minors for each class year in table form
    year_table = PrettyTable(["Year", "# DCS Minors"])
    for year in sorted(by_year.keys()):
        year_table.add_row([year, len(by_year[year])])
    print("\n" + str(year_table))
    # From the by_adv sorting, show the number of DCS minors assigned to each advisor in table form
    adv_table = PrettyTable(["Advisor", "# DCS Minors"])
    for adv in sorted(by_adv.keys()):
        adv_table.add_row([adv, len(by_adv[adv])])
    print("\n" + str(adv_table))


def writeCSVFiles(by_year: dict[str, list[Student]]) -> None:
    '''Write one CSV file per graduation year containing DCS minor information.
    Parameters: 
        by_year : Dictionary of students grouped by class year.
    '''
    # Using the by_year dictionary, sort students by year and create separate tables for each class year
    for year, students in by_year.items():
        fname = f"dcs_minors_{year}.csv"
        # Display message in terminal when processing the CSV files
        print(f"Writing {fname}...")
        # Build CSV file
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Last", "First", "Email", "Year", "Majors", "Minors", "GECs", "Advisor"])
            for stu in students:
                w.writerow(stu.getCSVList())


def main() -> None:
    # Command line argument for writing CSV file. Either True/False accepted
    writeCSV = False
    if len(sys.argv) > 1:
        try:
            writeCSV = bool(eval(sys.argv[1].title())) 
        except Exception:
            sys.exit("First argument must be True or False (case-insensitive).")

    # User can indicate specific html file name. If left blank, the html files will be listed alphabetically for the user to choose from and parse.
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
    # Read and parse the HTML file
    try:
        with open(html_file, "r", encoding="utf-8") as fh:
            html_text = fh.read()
    except Exception:
        sys.exit(f"Cannot open or read {html_file}")
    # soup object representing the parsed HTML
    soup = BeautifulSoup(html_text, "html.parser")
    by_year, by_adv = parseMinors(soup)
    # Execute writeCSVFiles and printOutput accordingly (depending on True/False input)
    if writeCSV:
        writeCSVFiles(by_year) 
    else:
        printOutput(by_year, by_adv)

if __name__ == "__main__":
    main()