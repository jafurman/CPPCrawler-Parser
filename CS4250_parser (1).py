from urllib.error import HTTPError
from bs4 import BeautifulSoup as bs
import pymongo
import traceback


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

def get_target_page(db):
    try:
        # Collection
        col = db.pagesInCsDepartment
        # Find Page
        pipeline = [
            {'$match': {'title': 'Permanent Faculty'}}
        ]
        docs = col.aggregate(pipeline)
        for data in docs:
            html_source = data['html']
            print(html_source)
        return html_source
    except Exception as error:
        print("Mongo DB Error")
        return None


def cleansingList(input):
    # List of elements for remove...
    rm = ['Title:', 'Title', 'Office:', 'Office', 'Phone:', 'Phone', 'Email:', 'Email', 'Web:', 'Web', ':', ':']
    for x in range(0, len(rm)):
        try:
            input.remove(rm[x])
        except Exception as error:
            print('No need to remove')

    return input


def save_html_information(db, name, title, office, phone, email, web):
    try:
        # collection
        col = db.professors
        if name != '':
            doc = {
                "name": name,
                "title": title,
                "office": office,
                "phone": phone,
                "email": email,
                "web": web

            }
            result = col.insert_one(doc)
            print(result.inserted_id, ' has been successfully stored')
        else:
            print('No ned to store')
        return True
    except Exception as error:
        print("Mongo DB Error")
        return False


# Initial Info
partial_url_starter = 'https://www.cpp.edu'

# Get DB Connection
db = connectDataBase()

try:
    html_page = get_target_page(db)
except HTTPError as e:
    print(e)
else:
    # program continues.
    soupy = bs(html_page, "html.parser")
    # had to inspect the class name of 'clearfix' and grab the title for the class for professor name
    professors = soupy.find_all('div', {"class": "clearfix"})
    for prof in professors:
        pname = title = office = phone = email = web = ''
        prof_name = prof.find_all('h2')
        for name in prof_name:
            # print(name.get_text())
            pname = name.get_text().strip()
        ptag = prof.find_all('p')
        for p in ptag:
            info_list = p.get_text(strip=True, separator='\n').splitlines()
            clean_list = cleansingList(info_list)
            title = clean_list[0].replace(':', '').strip()
            office = clean_list[1].replace(':', '').strip()
            phone = clean_list[2].replace(':', '').strip()
            email = clean_list[3].replace(':', '').strip()
            web = partial_url_starter + clean_list[4].replace(':', '').strip()
        print(pname, title, office, phone, email, web)
        db_result = save_html_information(db, pname, title, office, phone, email, web)
        print(db_result)
