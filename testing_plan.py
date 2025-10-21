from bs4 import BeautifulSoup

file_path = "dcs_minor_roster.html"

#student_names = []
student_majors = []

try:
    with open(file_path, "r", encoding="utf-8") as file:
        html_file = file.read()
    Soup = BeautifulSoup(html_file, "html.parser")

    table = Soup.find("table", {"id": "studentList"})
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) > 1:
            #name = cols[1].get_text(strip=True)
            major = cols[6].get_text(strip=True)
            #student_names.append(name)
            student_majors.append(major)

    for major in student_majors:
        print(major)

    #for name in student_names:
        #print(name)

except FileNotFoundError:
    print(f"Error: {html_file} not found.")