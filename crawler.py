"""
This script allows you to create tree maps of
websites easily by the click of a button.
The time the script will take to map a website
depends on how large the site is.
"""

__author__ = "BWBellairs"
__version__ = "0.1.0"

# Modules / Packages required are listed below
import validators
import threading
import requests
import time
import re

class web_crawler(object):
    def __init__(self, home, blockExternal=True, crawlerAmount=1):
        """
        home is the origin point in
        a website where the crawler will
        start from
        """
        self.home = home
        self.domain = ".".join(home.split("/")[2].split(".")[0:3]) if self.home.count("/") > 2 else home.split("/")[2]
        self.tld = self.domain.split(".")[1]
        
        # Task list allowing crawlers to communicate
        # We're adding self.home here as the point of origin
        self.tasks = [
            {
            "page": self.home,
            "assigned": False,
            }
        ]

        # Don't crawl outside of the site
        self.blockExternalLinks = blockExternal

        # Variable containing the maximum amount of crawlers
        self.maxCrawlers = crawlerAmount

        # A dictionary containing all the crawler threads
        self.crawlers = []

        # List to keep all links found and not cause any crawlers to go over the same link
        self.allLinks = []

    def run(self):
        self.threadsRun = True
        
        for index in range(self.maxCrawlers):
            strIndex = str(index) # For parsing into crawlers as name

            self.crawlers.append(
                threading.Thread(target=self.crawler, args=(strIndex,))
            )
            
            # We don't need daemon threads
            self.crawlers[index].setDaemon(False)

            # Starting the crawler thread
            self.crawlers[index].start()

        tasksOld = len(self.tasks)
        while True:

            time.sleep(5)

            tasksNew = len(self.tasks)

            if tasksNew == tasksOld:
                self.threadsRun = False

            tasksOld = len(self.tasks)

            raise SystemExit
                            

    def cprint(self, name, message):
        """
        This is needed as crazy formatting is produced when individual threads print to console
        on their own # Doesn't work
        """
        #print(name + " " + message)
        pass

    def isWebsite(self, website):
        if validators.url(website):
            return True
    
    def crawler(self, name):
        """
        Individual crawlers can
        crawl a website more efficiently
        in a smaller amount of time
        """
        name = "[Crawler-{0}]".format(name)

        self.cprint(name, "Started") # Showing this crawler has started

        index = 0 # I'm not using a for loop as they are limited to a range
        indexDone = -1 # This is used to keep track of which index this crawler has finished with
        while True:
            if not self.tasks[index]["assigned"]:
                self.tasks[index]["assigned"] = True

                currentTask = self.tasks[index]
                page = currentTask["page"]

                self.cprint(name, "Unassigned link found, assigning link ({0})".format(page))

                if not self.isWebsite(page):
                    if page.startswith("/"):
                        page = self.home + page[1:] if self.home.endswith("/") else self.home + page
                        
                    else:
                        page = self.home + "/" + page

                if page in self.allLinks:
                    self.cprint(name, "Link has already been searched ({0})".format(page))
                    indexDone = index

                elif not page.startswith(self.home) and self.blockExternalLinks:
                    self.cprint(name, "Link is external ({0})".format(page))
                    indexDone = index

                else:
                    self.cprint(name, "Searching page: {0}".format(page))

                    pageSource = requests.get(page).text

                    links = re.findall(r'href=[\'"]?([^\'" >]+)', pageSource)

                    # Adding links to self.tasks for crawling and to the current page for reference
                    self.tasks[index]["links"] = links

                    appendedLinks = []

                    for link in links:
                        if not link in self.allLinks and link != page and link not in appendedLinks:
                            self.tasks.append(
                                {
                                "page": link,
                                "assigned": False,
                                }
                            )

                            appendedLinks.append(link)

                    self.allLinks.append(currentTask["page"])

                    indexDone = index

                    print(page)

                    self.cprint(name, "Finished searching page: {0}".format(page))
            
            if not self.threadsRun:
                self.cprint(name, "Stopping - Finished Crawling")

                return

            elif len(self.tasks) > (index + 1) and index == indexDone:
                index += 1 # Look at the next task if it is available

                self.cprint(name, "Switching to [Task {0}]".format(index + 1)) # Real Index is used

                continue # Go to start of loop
                
            self.cprint(name, "Waiting for new task")

            #print(str(self.tasks))

# Example
main = web_crawler("https://google.com", True, 15)
main.run()
