from github import Github
from github import Auth
from datetime import datetime
import re
import calendar
import locale
import json
from os import getenv

locale.setlocale(locale.LC_TIME, "sv_SE.UTF-8")
auth = Auth.Token(getenv("TOKEN"))

github_api = Github(auth=auth)

organization = "Folkuniversitetet-BFU-VT25";

def get_repos():
    org = github_api.get_organization(org=organization)

    repos = org.get_repos()

    lesson_repos = [repo for repo in repos if repo.name.startswith("lektion-")]

    return lesson_repos

def get_week_number(date):
    week_number = date.isocalendar().week
    
    return week_number

repos = get_repos()

github_api.close()

today = datetime.today()
current_week = get_week_number(today)

weeks = {}

for repo in repos:
    date_string = re.search("\d{4}-\d{2}-\d{2}", repo.name)
    lesson_date = date_string.group()

    date = datetime.strptime(lesson_date, "%Y-%m-%d")
    week = get_week_number(date)

    if not weeks.get(week): weeks[week] = []

    weeks[week].append({
        "date": lesson_date,
        "weekday": calendar.day_name[date.weekday()],
        "name": repo.name,
        "link": f"https://github.com/{organization}/{repo.name}",
        "description": repo.description or "–"
    })

markdown = f"# 📚 Programmering med Python - Lektionsöversikt HT25\n\n"
planning_file = open("course-planning/planning.json")
course_planning = json.load(planning_file)

for week_nr in range(17, 25):
    title = f"## ✅ Pågående: Vecka {week_nr}" if week_nr == current_week else f"## Vecka {week_nr}"
    week_content = course_planning[str(week_nr)].get('content')

    markdown += f"{title}\n\n"
    markdown += f"### Veckans innehåll: \n {week_content}\n\n"
    markdown += f"### Lektionsmaterial\n\n"

    if weeks.get(week_nr):
        lessons = weeks[week_nr]
        for lesson in lessons:
            markdown += f"- **{lesson.get("weekday")}** – [{lesson.get("name")}]({lesson.get("link")}) – {lesson.get("description")}\n"
    else:
        markdown += "_(Inget lektionsmaterial är publicerat denna vecka än)_\n"

    markdown += f"\n"

planning_file.close()

with open("docs/index.md", "w") as file:
    file.write(markdown)

