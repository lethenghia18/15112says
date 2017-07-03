from piazza_api import Piazza 
import time 
import string 

def cleanString(text):

    htmlElems = ['<div>', '</div>', '<p>', '</p>', '<br />', '</a>', '<strong>', 
                '</strong>', '\n', '-', '<em>', '</em>']
    # get rid of non-ascii, but still a few left 
    newText = "".join(i for i in text if ord(i)<128)
    # get rid of html Elements
    for elem in htmlElems: 
        newText = newText.replace(elem, " ")
    # gid rid of remaining non-asciis
    nonAscii = ['&#39;', '&#64;', '&#43;', '&amp;', '&#34;'] 
    for elem in nonAscii: 
        newText = newText.replace(elem, "")
    # get rid of <a href> link 
    while (newText.find("<a") != -1): 
        start = newText.find("<a")
        end = newText.find(">", start)
        newText = newText[:start] + newText[end+1:]
    # get rid of block code 
    while (newText.find("<pre>") != -1): 
        start = newText.find("<pre>")
        end = newText.find("</pre>", start)
        newText = newText[:start] + newText[end+6:]
    return newText

# write file from 112 websites 
def writeFile(filename, contents, mode="wt"):
    # wt = "write text"
    with open(filename, mode) as fout:
        fout.write(contents)

# return a dictionary, with (k, v) = (person, list of posts)
def parseContent(cs112, contents, instructorsID): 

    # loop through all posts and get content
    s = time.time()
    posts = cs112.iter_all_posts()
    for post in posts:
        # get text from note post (not QA post)
        history = post['history'][0] # get the 1st version, don't care about edited post 
        if history['uid'] in instructorsID: 
            # if it belongs to TA/prof, add content after cleaning string 
            contents[history['uid']].append(cleanString(history['content']))
        # get text from QA post, children can contain mutiply replies 
        if len(post['children']) > 0:
            for child in post['children']:
                if 'history' in child: 
                    reply = child['history'][0]
                    if reply['uid'] in instructorsID: 
                        contents[reply['uid']].append(cleanString(reply['content']))
                if len(child['children']) > 0: # for follow-up replies
                    for subChild in child['children']: 
                        if subChild['uid'] in instructorsID: 
                            contents[subChild['uid']].append(cleanString(subChild['subject']))
    e = time.time()
    print("Total webscraping time: ", (e-s), "s")

    return contents

# get posts from Piazza, parse the content, and output txt files for each person
def main():

    # make a Piazza object and log in 
    p = Piazza()
    p.user_login("nle@andrew.cmu.edu", "Thanhan1196")
    # and get the course network via ID, obtained via website: piazza.com/class/ID  
    cs112 = p.network("j2rysbgf7662ql")
    # get users id of all TAs + Professor, minus Paul
    users = cs112.get_all_users()
    contents, names = dict(), dict()
    instructorsID = []
    for user in users: 
        if (user['role'] == 'ta' or user['role'] == 'professor') and user['name'] != 'Paul': 
            instructorsID.append(user['id'])
            names[user['id']] = user['name']
            contents[user['id']] = []
    instructorsID = set(instructorsID)
    
    # parse content
    contents = parseContent(cs112, contents, instructorsID)

    for uid in contents: 
        posts = "".join(p for p in contents[uid])
        name = "%s.txt" % names[uid]
        writeFile(name, posts)

main()


