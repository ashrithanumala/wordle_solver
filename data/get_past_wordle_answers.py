import requests
from bs4 import BeautifulSoup

url = "https://www.rockpapershotgun.com/wordle-past-answers"
response = requests.get(url)
response.raise_for_status() 

soup = BeautifulSoup(response.content, 'html.parser')
div = soup.find('div', class_='article_body_content article-styling')
list_items = div.find_all('li')
words = [item.get_text() for item in list_items]

with open('past_wordle_answers.txt', 'w') as file:
    for word in words:
        if len(word) > 5:
            file.write(word.split(" ")[-1].lower() + '\n')
        else:
            file.write(word.lower() + '\n')

print("Past Wordle answers have been saved to past_wordle_answers.txt")
