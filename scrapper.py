from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

import pandas as pd
import json
import os

RECIPIENTS = ["email@domain.com"]
ROOTPATH = "."
FROMEMAIL = "email@domain.com"
FROMPASS = "password"

class ProjectReader(object):
    def __init__(self, rootpath):
        target_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAuEACFOqoyAW6J3C1x0Mjq6XXf8vacVcy4BzHx4UgZQ_8ag2hzpCfEZCtT1YbBqx7tLrE1YY8rT7m/pubhtml"
        project_table = pd.read_html(target_url, header=1)[0]
        project_table["Open"] = project_table["Open"].str.strip().str.lower()
        still_open = project_table["Open"] == "open"
        self.projects = project_table[still_open]
        self.rootpath = rootpath

    def __read_cache(self, filename):
        try:
            with open(filename, "r") as json_file:
                self.old_projects = json.loads(json_file.read())
        except OSError:
            self.old_projects = []
            print("INFO: No previous cache exists. Assuming no previous projects.")

    def get_name(self, item):
        name = str(item["ID"]) + str(item["Supervisor"]) + str(item["Project Title"])
        return name

    def __write_cache(self, filename):
        cache_list = []
        for _, row in self.projects.iterrows():
            name = self.get_name(row)
            cache_list.append(name)
        with open(filename, 'w') as outfile:
            json.dump(cache_list, outfile)

    def send_email(self, new_projects):
        if new_projects.empty:
            print("INFO: No new projects, skipping sending email.")
            return

        print(new_projects)

        msg = MIMEMultipart()
        msg['Subject'] = "New ECE496 Projects Posted!"
        msg['From'] = FROMEMAIL


        html = """\
        <html>
        <head></head>
        <body>
            {0}
        </body>
        </html>
        """.format(new_projects.to_html())

        part1 = MIMEText(html, 'html')
        msg.attach(part1)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(FROMEMAIL, FROMPASS)
        server.sendmail(msg['From'], RECIPIENTS , msg.as_string())

    def check_for_new(self):
        new_projects = []
        self.__read_cache(os.path.join(self.rootpath, "ece496fetcher.json"))
        for index, row in self.projects.iterrows():
            name = self.get_name(row)
            if name in self.old_projects:
                continue
            else:
                new_projects += [index]
        self.send_email(self.projects.loc[new_projects, :])
        self.__write_cache(os.path.join(self.rootpath, "ece496fetcher.json"))

project_reader = ProjectReader(ROOTPATH)
project_reader.check_for_new()