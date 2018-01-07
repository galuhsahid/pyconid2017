from app import app
import urllib2
from bs4 import BeautifulSoup
import string
import re
import csv
from HTMLParser import HTMLParser
import xml.etree.ElementTree
from flask.json import jsonify
import requests
import json
import pandas as pd
import pickle

# Title word count
def get_title_wc(soup):
    title = soup.findAll("h1", { "class" : "page-title project-title project-title--full" })
    title = title[0].contents[0].strip()
    title_wc = len(title.split())

    return title_wc

# Short story word count
def get_short_wc(soup):
    short_story = soup.findAll("div", { "class" : "project-short-story" })
    short_story = short_story[0].contents[0].strip()
    short_wc = len(short_story.split())

    return short_wc

# Story word count
def get_story_wc(soup):
    story = soup.findAll("article", { "class" : "project-detail__article" })

    # If no story update
    if len(story) < 2:
        story = story[0]
    else:
        story = story[1]

    story = story.get_text(separator=u' ')

    story_wc = len(story.split())-2 # Remove "DONASI SEKARANG"

    return story_wc

def get_collected_amt(soup):
    collected_amt = soup.find("h1", { "class" : "project-collected__amount" }).get_text()
    collected_amt = collected_amt.replace("Rp", "").replace(".", "").replace("\n", "").replace(" ", "")

    return collected_amt

def get_donation_target_amt(soup):
    amount = soup.find("h1", { "class" : "project-collected__amount" }).next_sibling
    donation_target_amt = amount[len("terkumpuldaritargetRp")+1:].replace(".", "").replace("\n", "").replace(" ", "").replace("Rp","")

    return donation_target_amt

def get_is_org(soup):
    org_image = soup.findAll("img", { "src" : "elements/images/verified-org.png" })

    if len(org_image) > 0:
        is_org = 1
    else:
        is_org = 0

    return is_org

def get_img_cnt(soup):
    images = []
    images = soup.findAll("img")
    images_filtered = []

    # Filter image links
    for image in images:
        try:
            img = str(image['src'].encode('utf-8').strip())
            if img is not None:
                if (not img.startswith('https://assets.kitabisa.com')) and (not img.startswith('/elements/images/')) and (not img.startswith('elements/images/')) and (not img.startswith('//googleads.g.doubleclick.net')) and (not img.startswith('https://static-00.kitabisa.com')) and (not img.startswith('https://www.facebook.com')):
                    images_filtered.append(img)
        except:
            pass

    img_cnt = len(images_filtered)
    
    return img_cnt

def get_vid_cnt(soup):
    videos = soup.findAll("iframe")
    vid_cnt = len(videos)-1 # Kurang 1 karena ada Google Tag Manager

    return vid_cnt

def get_donor_cnt(soup):
    donor_cnt = soup.find("span", { "class" : "fundraiser__count" }).get_text()

    return donor_cnt

def get_fundraiser_cnt(soup):
    fundraiser_cnt = soup.find("span", { "class" : "number" }).get_text()

    return fundraiser_cnt

def get_update_cnt(soup):
    update_titles = soup.findAll("h2", { "class" : "project-detail-article__title"})
    update_cnt = len(update_titles)

    return update_cnt

def get_reward_cnt(soup):
    rewards = soup.findAll("li", { "class" : "rewards-list__item cf" })
    reward_cnt = len(rewards)

    return reward_cnt

def get_min_max_reward(soup):
    rewards_amount_list = soup.findAll("span", { "class" : "reward-value"})

    if len(rewards_amount_list) > 0:
        min_reward = rewards_amount_list[0].get_text().replace("Donasi Rp ","").replace("atau lebih","").replace(".","").replace("Rp. ", "").replace("\n", "").replace(" ", "")
        max_reward = rewards_amount_list[len(rewards_amount_list)-1].get_text().replace("Donasi Rp ","").replace("atau lebih","").replace(".","").replace("Rp. ", "").replace("\n", "").replace(" ", "")

    else:
        min_reward = 0
        max_reward = 0

    return {"min_reward": min_reward, "max_reward": max_reward}

def get_facebook_data(soup, url):
    BASE_URL = "https://graph.facebook.com/v2.9/"
    ACCESS_TOKEN = "EAACEdEose0cBAJTUM0ZBlA6VPAFOZC0ijD7ErUcZAdlIqKI0E7LmwB6ZClInHyEZAJI39a6UHLxI7kWC8ZBGeurDdvL4mlJoUm9ZAtGCwyR9TKdTYAtAYpaCnzZCNFZBMfdnuRZABMTu196j6Nv7rULOkQLZB9XtoyGvxJEARxkRMSZAMU9bYzCZCIGRswcGmy9wUmRIZD"
    INFO_URL = BASE_URL + "?access_token=" + ACCESS_TOKEN + "&id={}&fields=engagement,og_object"

    url2 = INFO_URL.format(url)
    resp2 = requests.get(url2)
    code = resp2.status_code

    if(resp2.status_code == 200):
        info = json.loads(resp2.text)

        fb_reaction_count = str(info["engagement"]["reaction_count"])
        fb_comment_count = str(info["engagement"]["comment_count"])  
        fb_share_count = str(info["engagement"]["share_count"])

    else:
        fb_reaction_count = 0
        fb_comment_count = 0
        fb_share_count = 0

    return {"fb_reaction_count": fb_reaction_count, "fb_comment_count":fb_comment_count, "fb_share_count": fb_share_count}

# Specificity
def get_avg_weight(soup):
    story = soup.findAll("article", { "class" : "project-detail__article" })

    if len(story) < 2:
        story = story[0]
    else:
        story = story[1]

    story = story.get_text(separator=u' ')

    preprocessed_story = preprocess(story)
    avg_weight = calculate_avg_tfidf(preprocessed_story)

    return avg_weight

def calculate_sum_tfidf(string):
    weights_df_dict = pickle.load(open("./app/resources/weights_df_dict.p","rb"))
    
    count = sum(weights_df_dict.get(word, 0) for word in string.lower().split())
    return count

def calculate_avg_tfidf(string):
    string = str(string.encode('utf-8').strip())
    sum_of = calculate_sum_tfidf(string)
    length = len(string)
    if length == 0:
        return 0
    else:
        return sum_of/float(length)

def remove_stopwords(text):
    with open('./app/resources/stopwords.txt', 'r') as f:
        id_stopwords = f.read().splitlines()

    id_stopwords = set(id_stopwords)
    return ' '.join([word for word in text.split() if word not in id_stopwords])

def stem(text):
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

    # create stemmer
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()

    return stemmer.stem(str(text))

def preprocess(text):
    text = clearup(text)
    text = remove_stopwords(text)
    #text = stem(text)

    return text

# Clear digits, strange characters, etc.
def clearup(s):
  chars = string.punctuation+string.digits
  return re.sub('[%s]' % chars, '', s).lower()

def get_data(campaign):
    url = 'https://kitabisa.com/' + campaign
    if url != '':
        # Header to overcome robots.txt
        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Connection': 'keep-alive'}

        req = urllib2.Request(url, headers=hdr)
        conn = urllib2.urlopen(req)

        html = conn.read()

        soup = BeautifulSoup(html, "lxml")

        title_wc = get_title_wc(soup)
        short_wc = get_short_wc(soup)
        story_wc = get_story_wc(soup)
        collected_amt = get_collected_amt(soup)
        donation_target_amt = get_donation_target_amt(soup)
        update_cnt = get_update_cnt(soup)
        is_org = get_is_org(soup)
        img_cnt = get_img_cnt(soup)
        vid_cnt = get_vid_cnt(soup)
        donor_cnt = get_donor_cnt(soup)
        fundraiser_cnt = get_fundraiser_cnt(soup)
        reward_cnt = get_reward_cnt(soup)
        min_max_reward = get_min_max_reward(soup)
        min_reward = min_max_reward["min_reward"]
        max_reward = min_max_reward["max_reward"]
        avg_weight = get_avg_weight(soup)

        facebook_data = get_facebook_data(soup, url)
        fb_reaction_count = facebook_data["fb_reaction_count"]
        fb_share_count = facebook_data["fb_share_count"]
        fb_comment_count = facebook_data["fb_comment_count"]

        data = {
            "title_wc": title_wc,
            "short_wc": short_wc,
            "story_wc": story_wc,
            "donation_target_amt": donation_target_amt,
            "is_org": is_org,
            "img_cnt": img_cnt,
            "vid_cnt": vid_cnt,
            "donor_cnt": donor_cnt,
            "fundraiser_cnt": fundraiser_cnt,
            "update_cnt": update_cnt,
            "reward_cnt": reward_cnt,
            "max_reward": max_reward,
            "min_reward": min_reward,
            "avg_weight_new": avg_weight,
            "fb_reaction_count": fb_reaction_count,
            "fb_comment_count": fb_comment_count,
            "fb_share_count": fb_share_count,
            "collected_amt": collected_amt
        }

        return json.dumps(data)

