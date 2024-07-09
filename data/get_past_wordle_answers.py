import requests
from bs4 import BeautifulSoup

# URL of the website
url = "https://www.rockpapershotgun.com/wordle-past-answers"

# Make a request to fetch the web page content
response = requests.get(url)
response.raise_for_status()  # Raise an error if the request was unsuccessful

# Parse the web page content
soup = BeautifulSoup(response.content, 'html.parser')

# Find the div with the specified class
div = soup.find('div', class_='article_body_content article-styling')

# Find all the list items within the div
list_items = div.find_all('li')

# Extract the text from each list item and store them in a list
words = [item.get_text() for item in list_items]

# Write the words to a file
with open('past_wordle_answers.txt', 'w') as file:
    for word in words:
        if len(word) == 5:
            file.write(word.lower() + '\n')

print("Past Wordle answers have been saved to past_wordle_answers.txt")
