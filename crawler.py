"""
This script allows you to create tree maps of
websites easily by the click of a button.
The time the script will take to map a website
depends on how large the site is.
"""

__author__ = "BWBellairs"
__version__ = "0.1.6"

# Modules / Packages required are listed below
import threading
import urllib
import time
import bs4

ignoredTags = ["meta", "img", "video", "audio", "script", "style"]

class web_crawler(object):
    def __init__(self, home, blockExternal=True, crawlerAmount=1):
        """
        home is the origin point in
        a website where the crawler will
        start from
        """
        self.home = home
        self.domain = home.split(":")[1].strip("/")
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

            time.sleep(10)

            tasksNew = len(self.tasks)

            if tasksNew == tasksOld:
                self.threadsRun = False # Stop threads one tasks have stopped coming in. Site has finished being crawled.
                #raise SystemExit # Allow the program to exit

            tasksOld = len(self.tasks)

            # TODO: Check that all threads have stopped before exiting. thread.isAlive()
            # TODO: Fix relative threads. some hrefs="/blah" which needs to be appended onto self.home
    
    def crawler(self, name):
        """
        Individual crawlers can
        crawl a website more efficiently
        in a smaller amount of time
        """
        name = "[Crawler-{0}]".format(name) # This crawler's name

        index = 0 # I'm not using a for loop as they are limited to a range
        indexDone = -1 # This is used to keep track of which index this crawler has finished with
        while True:
            if not self.tasks[index]["assigned"]:
                self.tasks[index]["assigned"] = True # Assign the task to let the other threads know we're handling this one.

                currentTask = self.tasks[index] # Easier to reference this dictionary
                page = currentTask["page"] # Easier to use this shorter variable name. Trust me.

                print(page)

                if page in self.allLinks: # Don't want to search the same website
                    indexDone = index # Don't crawl a lage that's already been crawled

                elif not page.startswith(self.home) and self.blockExternalLinks: # Avoid External Links
                    indexDone = index # Continue with the next task as we don't want to crawl this link

                else:
                    pageSource = urllib.urlopen(page) # Get the page's content

                    soup = bs4.BeautifulSoup(pageSource, "html.parser") # Parse the page as html

                    tags = soup.find_all(href=True) # Finds all tags and put them into a list
                    tags = [tag for tag in tags if tag.name not in ignoredTags]

                    links = [tag["href"] for tag in tags]

                    # Adding links to self.tasks for crawling and to the current page for reference
                    self.tasks[index]["links"] = links

                    appendedLinks = [] # This list is used to avoid duplicate linkss found on a page

                    for link in links: # Iterating over the list of links found on the current page
                        if not link in self.allLinks and link != page and link not in appendedLinks: # Make sure no duplicate links are appended
                            self.tasks.append( # Appending the page to self.tasks so another thread can handle it
                                {
                                "page": link,
                                "assigned": False,
                                }
                            )

                            appendedLinks.append(link)

                    self.allLinks.append(page) # Keep track of all pages browsed

                    indexDone = index # We've done crawling this page
            
            if not self.threadsRun: # Stop this thread one this variable is True
                print("Ended")
                return

            elif len(self.tasks) > (index + 1) and index == indexDone:
                index += 1 # Look at the next task if it is available

                continue # Go to start of loop

# Example
main = web_crawler("https://google.co.uk", True, 2)
main.run()
