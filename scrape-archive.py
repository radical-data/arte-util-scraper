import bs4
import lxml
import requests
import os
import pandas as pd
import re

os.makedirs('images', exist_ok=True)

projects = []


def select_variable(selector, variable_name='something'):
    try:
        return soupProject.select(selector)[0].get_text().strip()
    except:
        print('%s missing' % variable_name)
        return ''


link = 'https://www.arte-util.org/projects/'
res = requests.get(link)
res.raise_for_status()
soup = bs4.BeautifulSoup(res.text, 'lxml')
projectElems = soup.select('li.archive-item > header > a')
for project in projectElems:
    # scrape page
    projectLink = project.get('href')
    print('scraping ' + projectLink)
    resProject = requests.get(projectLink)
    resProject.raise_for_status()
    soupProject = bs4.BeautifulSoup(resProject.text, 'lxml')

    # get information tangled in title
    extra_info = select_variable('header.single-intro > div:nth-child(1)')
    extra_info = re.findall('[^/]*/[^/]', extra_info)
    arte_util_archive_number = re.findall('\w+', extra_info[0])[1]
    dates = re.findall('\w+', extra_info[1])
    started = dates[0]
    try:
        ended = dates[1]
    except:
        ended = ''

    # get the easier information
    title = select_variable('header.single-intro h2:nth-child(3)')
    short_description = select_variable(
        'header.single-intro > div:nth-child(1) > div:nth-child(5)', 'short description')
    initiators = select_variable('.single-content > p:nth-child(2)')
    description = select_variable('.single-content > p:nth-child(4)')
    location = select_variable('.single-content > p:nth-child(6)')
    goals = select_variable('.single-content > p:nth-child(8)')
    beneficial_outcomes = select_variable('.single-content > p:nth-child(10)')
    maintained_by = select_variable('.single-content > p:nth-child(12)')
    users = select_variable('.single-content > p:nth-child(14)', 'users')

    # get links
    links = soupProject.select('.break-word')
    links_cleaned = []
    for link in links:
        l = link.get('href')
        links_cleaned.append(l)

    # get images
    imageLinks = soupProject.select('img.no-top-margin')
    imageLinksBottom = soupProject.select(
        '.single-project-image > a:nth-child(1) > img:nth-child(1)')
    for link in imageLinksBottom:
        imageLinks.append(link)
    imageLinks_cleaned = []
    for iteration, imageLink in enumerate(imageLinks):
        imageLink_cleaned = imageLink.get('src')
        print('downloading ' + imageLink_cleaned)
        try:
            res = requests.get(imageLink_cleaned)
            res.raise_for_status()
            filename = re.sub('[^0-9A-zÀ-ÿ]+', '-', title)
            filename = filename + "-" + str(iteration) + \
                os.path.splitext(imageLink_cleaned)[1]
            filename = filename.lower()
            imageFile = open("images/" + filename, "wb")
            for chunk in res.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
            imageLinks_cleaned.append(filename)
        except:
            print('image is empty')

    new_project = {
        'arte_util_archive_number': arte_util_archive_number, 'title': title, 'started': started, 'ended': ended, 'location': location, 'initiators': initiators, 'short_description': short_description, 'description': description, 'goals': goals, 'beneficial_outcomes': beneficial_outcomes, 'maintained_by': maintained_by, 'users': users, 'images': imageLinks_cleaned, 'links': links_cleaned}
    print(new_project)
    projects.append(new_project)

print(projects)
df = pd.DataFrame(projects)

df.to_csv('arte-util-database.csv')
