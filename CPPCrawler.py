# CPPCrawler.py

from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import traceback
import datetime


def connectDataBase():
    # Create a database connection object using pymongo
    # --> add your Python code here
    try:
        client = pymongo.MongoClient(host="localhost", port=27017)
        print("---Client---")
        print(client)
        db = client.CPPpages
        print("---DB---")
        print(db)
        return db
    except Exception as error:
        traceback.print_exc()
        print("Database not connected successfully")


def find_target_page_title(partial_url_starter, url_string):
    if url_string.startswith("/sci/computer-science/"):
        url_string = partial_url_starter + url_string

    html_page = urlopen(url_string)
    soup_obj = bs(html_page.read(), "html.parser")
    tag_h1 = soup_obj.find('h1', {"class": "cpp-h1"})

    if tag_h1:
        targetPageTitle = tag_h1.get_text()
    else:
        targetPageTitle = ''

    return targetPageTitle


# adding the documents to the database connection object
def save_html_content_db(partial_url_starter, url_string, page_title):
    print(url_string)
    db = connectDataBase()
    col = db.pagesInCsDepartment
    create_date = datetime.datetime.now()

    if url_string.startswith("/sci/computer-science/"):
        url_string = partial_url_starter + url_string

    html_obj = urlopen(url_string)
    soup = bs(html_obj.read(), "html.parser")
    html_text = soup.find_all('html')

    doc = {
        "url": url_string,
        "title": page_title,
        "html": str(html_text),
        "created_at": create_date
    }

    result = col.insert_one(doc)
    print(result.inserted_id)


# appending seeds to the frontier to add to DB
def append_seeds(partial_url_starter, frontier_list, url_string):
    if url_string in frontier_list:
        print('Already Visited')
    else:
        if url_string.startswith("/sci/computer-science/"):
            url_string = partial_url_starter + url_string
        frontier_list.append(url_string)
    return frontier_list


# Initial Frontier

initialFrontier = ['https://www.cpp.edu/sci/computer-science/']
partial_url_starter = 'https://www.cpp.edu'

# Add links to Frontier

try:
    html_page = urlopen(initialFrontier[0])
except HTTPError as e:
    print(e)
else:
    my_soup = bs(html_page.read(), "html.parser")
    all_links = my_soup.find_all('a', {})
    link_cnt = 0
    for link in all_links:
        hrefLink = link.get("href")
        if str(hrefLink).startswith("/sci/computer-science/") or str(hrefLink).startswith("http"):
            print(hrefLink)
            initialFrontier = append_seeds(partial_url_starter, initialFrontier, hrefLink)
            print(initialFrontier)
            title = find_target_page_title(partial_url_starter, hrefLink)
            save_html_content_db(partial_url_starter, hrefLink, title)
            # if the target page <h1> tag is the desired tag, stop the crawler
            if str(title).strip() == 'Permanent Faculty':
                print(f"STOP Here because target page was found at page titled: {title}")
                # remove all elements from frontier
                initialFrontier.clear()
                break
            link_cnt += 1
            print(f"Link count is {link_cnt}")
