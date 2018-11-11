#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
u/LEGO_IDEAS_BOT is a simple bot that serves various LEGO communities on Reddit with a useful comment every time
a LEGO Ideas link is posted. It has generally been given explicit permission to run.

This bot is self-contained and does not require any external files other than its credentials JSON file.
"""

import os
import re
import time
import traceback

import praw
import requests
import json
from lxml import html

'''USER CONFIGURATION'''

# Original bot requester: u/rock99rock
BOT_NAME = 'LEGO Ideas Bot'
VERSION_NUMBER = '1.0'  # Updated November 10, 2018
USER_AGENT = '{} v{}, a LEGO Ideas info provider for LEGO communities written by u/kungming2.'.format(BOT_NAME,
                                                                                                      VERSION_NUMBER)
SUBREDDIT = ('AFOL+bioniclelego+buildingblocks+customfigs+lego+Lego_Dimensions+legoadvice+LegoBDSM+legocanada+legodeal+'
             'legodeals+Legodimensions+legoideas+Legomarket+legomeme+legophotos+LEGOreviews+legos+legostarwars+'
             'legotechnic+legotrade+Minilego+mocs+MyOwnCreation+random_acts_of_lego+testingground4bots+legoleaks')
KEYWORDS = ['ideas.lego.com/projects/']

BOT_DISCLAIMER = ("\n\n---\n\n^LEGO ^Ideas ^Bot ^(v. {}) ^| [^Source](https://github.com/kungming2/LEGO_IDEAS_BOT) ^| "
                  "[^Bot ^Info/Support](https://www.reddit.com/message/compose/?to=kungming2&subject="
                  "About+LEGO+Ideas+Bot) ^| "
                  "^(If you like this project, **remember to vote for it!**)").format(VERSION_NUMBER)
# This is how many seconds the bot will wait between cycles.
WAIT = 60
SOURCE_FOLDER = os.path.dirname(os.path.realpath(__file__))  # Fetch the absolute directory the script is in.
FILE_ADDRESS_CREDENTIALS = SOURCE_FOLDER + "/_credentials.json"

# The main template for replies by the bot.
COMMENT_REPLY = '''
#### **[{project_title}]({project_link})** by {project_author} [[Photo]({project_image})]

##### {project_supporters} supporters | {project_days}

*{project_description}*
'''


def load_credentials():
    """
    Function that takes information about login and OAuth access from an external JSON file and loads it as a
    dictionary.

    :return: A dictionary with keys for important variables needed to log in and authenticate.
    """

    # Load the JSON file.
    f = open(FILE_ADDRESS_CREDENTIALS, 'r', encoding='utf-8')
    credentials_data = f.read()
    f.close()

    # Convert the JSON data into a Python dictionary.
    credentials_data = json.loads(credentials_data)

    return credentials_data


# Get the login info.
ideasbot_info = load_credentials()
USERNAME = ideasbot_info['username']
PASSWORD = ideasbot_info['password']
APP_ID = ideasbot_info['app_id']
APP_SECRET = ideasbot_info['app_secret']


def main_login():

    print("\nInitializing {} {}...\n".format(BOT_NAME, VERSION_NUMBER))
    global reddit
    global r

    print('Logging in...')
    reddit = praw.Reddit(client_id=APP_ID, client_secret=APP_SECRET, password=PASSWORD,
                         user_agent=USER_AGENT, username=USERNAME)
    r = reddit.subreddit(SUBREDDIT)

    return


def get_submission_from_comment(comment_id):  # Returns the parent submission as an object from a comment ID

    main_comment = reddit.comment(id=comment_id)  # Convert ID into comment object.
    main_submission = main_comment.link_id[3:]  # Strip the t3_ from front. 
    main_submission = reddit.submission(id=main_submission)  # Get actual submission object.

    return main_submission


def previous_comment_analyzer(reddit_submission):
    # A function that returns a dictionary that I can check against to make sure I don't post more than once per post.

    # Flatten the comments into a list.
    reddit_submission.comments.replace_more(limit=None)  # Replace all MoreComments with regular comments.
    comments = reddit_submission.comments.list()

    results = {}  # The main dictionary file we will return
    
    for comment in comments:
        try:  # Check if user is deleted
            cauthor = comment.author.name
        except AttributeError:
            # Comment author is deleted
            continue
            
        cbody = comment.body
        
        if cauthor == USERNAME:  # Comment is by the bot. 
            results['bot_results'] = []
            
            # Add the first line of the title.
            cline = cbody.split("[[Photo]", 1)[0]
            
            results['bot_results'].append(cline)  # Add the body of the comment to the dictionary's list.
    
    return results  # This will be a dictionary with values, or an empty one.


def lego_ideas_comment(url_number):
    project_link = 'https://ideas.lego.com/projects/' + url_number
    eth_page = requests.get(project_link)
    tree = html.fromstring(eth_page.content)  # now contains the whole HTML page
    project_title = tree.xpath('//h2[contains(@class,"h2")]/text()')
    project_title = project_title[0]
    project_author = tree.xpath('//div[contains(@class,"media-body media-middle media-full")]/h2/a/text()')
    project_author = project_author[0].strip()
    project_image = []

    # Main image that is used as thumbnail. All links will have one.
    project_image_links = tree.xpath('//div[contains(@class,"slide js-slide")]/img')

    # Process through the slides and get the JPEG links
    for element in project_image_links:
        if element.get('src') is not None:
            project_image.append(element.get('src'))
            print(element.get('src'))

    # Fetch the supporters. IDEAS hides it in JS now for some reason.
    try:
        project_supporters = tree.xpath('//script[contains(@type,"text/javascript")]/text()')
        project_supporters = project_supporters[-1]
        project_supporters = project_supporters.split('supportCount:', 1)[1]
        project_supporters = int(project_supporters.split(',', 1)[0].strip())
    except IndexError:
        project_supporters = "N/A"
        
    project_days = tree.xpath('//div[contains(@class,"phase_remaining_days")]/text()')
    
    if len(project_days) != 0:
        project_days = project_days[0] + " days left"
    else:  # This is no longer an active project.
        project_days = "Project expired"

    # Here are some of the common ones:
    # On Shelves, None (Expired)
    project_status = tree.xpath('//span[contains(@class,"project-phase-label")]/text()')
    # project_button = tree.xpath('//button[contains(@class,"btn btn-flat project-support-button")]/span/text()')

    if len(project_status) != 0:
        if "Approved" in str(project_status[0]) or "Sold" in str(project_status[0]) or "Shelves" in str(
                project_status[0]) or "Review" in str(project_status[0]) or "Achieved" in str(project_status[0]):
            project_supporters = "10,000"
        project_days = str(project_status[0])
    project_description = " ".join(tree.xpath('//div[contains(@class,"card-block cms")]/p/text()'))
    project_description = " ".join(project_description.split())  # Replace extra spaces and whitespace
    project_description = project_description.strip()

    try:
        # We get the first three sentences in the description.
        project_description = re.match(r'(?:[^.:;]+[.:;]){3}', project_description).group()
    except:
        project_description = project_description[0:400] + "."

    to_post = COMMENT_REPLY.format(project_title=project_title, project_link=project_link,
                                   project_image=project_image[0],
                                   project_author=project_author,
                                   project_supporters=project_supporters, project_days=project_days,
                                   project_description=project_description + "..")
    return to_post

    
def main_bot():
    print('Searching subreddits...')

    multireddit = reddit.multireddit(USERNAME, 'monitored')

    posts = []
    posts += list(r.new(limit=15))
    posts += list(multireddit.comments(limit=100))

    for post in posts:
        # Anything that needs to happen every loop goes here.
        pid = post.id
        purl = None
        check_lego = False

        if isinstance(post, praw.models.reddit.submission.Submission):
            purl = post.url
            if KEYWORDS[0] in purl:
                check_lego = True

        try:
            pauthor = post.author.name
        except AttributeError:
            # Author is deleted. We don't care about this post.
            continue

        if pauthor.lower() == USERNAME.lower():
            continue

        if post.saved:
            continue

        if isinstance(post, praw.models.reddit.comment.Comment):
            pbody = post.body
        else:
            pbody = '%s %s' % (post.title, post.selftext)
        pbody = pbody.lower()

        if not any(key.lower() in pbody for key in KEYWORDS) and not check_lego:  # Does it contain our keyword?
            continue
        else:
            check_lego = True

        if not check_lego:
            continue

        # Save the post so it won't be processed anymore.
        post.save()

        if purl is not None:
            if KEYWORDS[0] in purl:
                match = purl.split("ideas.lego.com/projects/")[1]  # Take the latter half of the URL
                match = match[0:36]

                ideas_comment = lego_ideas_comment(match)
                try:
                    post.reply(ideas_comment + BOT_DISCLAIMER)  # It's a post
                except:
                    continue
                print("Found a link to LEGO Ideas and replied with more information.")

        if KEYWORDS[0] in pbody:  # The comment contains a LEGO Ideas link
            match = pbody.split("ideas.lego.com/projects/")[1]  # Take the latter half of the URL
            match = match[0:36]

            # Format the thing nicely.
            ideas_comment = lego_ideas_comment(match)
            ideas_line = ideas_comment.split("[[Photo]", 1)[0]
            can_post = True
            
            try:
                if hasattr(post, "reply"):
                
                    # Code to check to see if it's been replied to before.
                    returned_data = previous_comment_analyzer(get_submission_from_comment(pid))
                    if len(returned_data) != 0:
                        if ideas_line in returned_data['bot_results']:
                            print("> I've commented in this thread before with the same Ideas link. Skipping...")
                            can_post = False
                        else:
                            can_post = True
                    
                    # We can post it.
                    if can_post:
                        post.reply(ideas_comment + BOT_DISCLAIMER)
                        print("Found a link to LEGO Ideas and replied with more information.")
                else:
                    post.reply(ideas_comment + BOT_DISCLAIMER)  # It's a post
                    print("Found a link to LEGO Ideas and replied with more information.")
            except:
                continue
              
                
# INFO FOR USER INPUT
main_login()  # Login.

while True:
    try:
        main_bot()
    except Exception as e:
        traceback.print_exc()

    print('LEGO Ideas Bot will run again in %d seconds. \n' % WAIT)
    time.sleep(WAIT)
