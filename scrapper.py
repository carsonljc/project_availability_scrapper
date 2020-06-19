import pandas as pd
import json
import os

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
            print("No previous cache exists. Assuming no previous projects.")

    def get_name(self, item):
        name = str(item["ID"]) + str(item["Supervisor"]) + str(item["Project Title"])
        return name

    def __write_cache(self, filename):
        cache_list = []
        for index, row in self.projects.iterrows():
            name = self.get_name(row)
            cache_list.append(name)
        with open(filename, 'w') as outfile:
            json.dump(cache_list, outfile)

    def send_email(self, new_projects):
        print("Not implemented")

    def check_for_new(self):
        new_projects = []
        self.__read_cache(os.path.join(self.rootpath, "ece496fetcher.json"))
        for index, row in self.projects.iterrows():
            name = self.get_name(row)
            if name in self.old_projects:
                continue
            else:
                new_projects += [index]
        print(self.projects.loc[new_projects, :])
        self.send_email(new_projects)
        self.__write_cache(os.path.join(self.rootpath, "ece496fetcher.json"))


project_reader = ProjectReader(".")
project_reader.check_for_new()