import matplotlib.pyplot as pPlot
from wordcloud import WordCloud, STOPWORDS
import numpy as npy
from PIL import Image
import urllib2
from bs4 import BeautifulSoup

def create_wordcloud(path):
    return

def create_wordset():
    i = 0
    while(True):
        try:
            url = 'https://www.jotform.com/answers?from=' + str(i)
            response = urllib2.urlopen(url)
            html = response.read()

            soup = BeautifulSoup(html, 'html.parser')
            for classes in soup.find_all('div'):
                if classes.get('class') == 'dc-f-question-name':
                    print("Here, ", classes.a.string)
            i += 10
        except urllib2.URLError:
            # Means we have reached the end of our forum posts
            break

create_wordset()
