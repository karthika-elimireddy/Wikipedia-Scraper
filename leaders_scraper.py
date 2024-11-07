
import requests
import json
from bs4 import BeautifulSoup
import time
import re


def get_first_paragraph(wikipedia_url):

    """
    Fetches the first paragraph which has more than 100 characters from a given Wikipedia article URL.
    The extracted text is cleaned returned.

    Args:
        wikipedia_url (str): The URL of the Wikipedia article to fetch the first paragraph from.

    Returns:
        str: The first paragraph text from the Wikipedia article. 
    
    Raises:
        requests.exceptions.RequestException: If the HTTP request to the Wikipedia URL fails.
        
    """
    try:
        response=requests.get(wikipedia_url)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        

    soup = BeautifulSoup(response.text,"html.parser")
    p_tags = soup.find_all('p')
    first_paragraph=''
    for p in p_tags:
        if len(p.get_text()) > 100 :
            first_paragraph = clean_data(p.get_text())
            break
    return first_paragraph

def clean_data(text):
    """
    this fucntion cleans the data 'text'.replaces the html tags,
    unwanted text enclosed with [] and white spaces with an empty string

    Args:
        text (str): The first paragragh text of Wikipedia article.

    Returns:
        str: The cleaned first paragraph text from the Wikipedia article. 
    """
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    #text = re.sub(r'[^a-zA-Z0-9.,?!\'" ]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def get_leaders(cookie_url,countries_url,leaders_url):
    """
    Fetches the cookies of the URL, traverse through the endpoints countries and leaders of the URL and fetch 
    the list of countries and the corresponding leaders of the country and also 
    first paragraph of each leader from a given Wikipedia article URL and returns the results as a dictionary
    

    Args:
        cookie_url (str): The endpoint URL of the fetch the cookies to keep the session alive.
        countries_url: The endpoint URL to fetch the countries data.
        leaders_url: The endpoint URL to fetch the leaders data

    Returns:
        dict: countries with there corresponding leaders info. 
    
    Raises:
        requests.exceptions.RequestException: If the HTTP request to the Wikipedia URL fails.
        
    """

    start_time=time.time()
    with requests.Session() as session:
        cookies = session.get(cookie_url).cookies
        countries = session.get(countries_url,cookies=cookies).json()
        leaders_per_country={}
       
        for country in countries:
            try :
                response=session.get(leaders_url, cookies = cookies, params={'country': country })
                if (response.status_code == 401 | response.status_code == 403):
                    cookies = session.get(cookie_url).cookies
                    response = session.get(leaders_url, cookies = cookies, params={'country': country })
            except requests.exceptions.RequestException as e:
                print(f"An error occurred: {e}")
                continue

            leaders = response.json()
            for leader in leaders:
                for key in leader:
                    if key == 'wikipedia_url':
                        cleaned_paragraph = get_first_paragraph(leader[key])
                        leader['first_paragraph'] = cleaned_paragraph
                        break
            leaders_per_country[country]=leaders
    end_time = time.time()
    print(f"Execution time : {end_time - start_time} seconds")   
    return leaders_per_country

def save(leaders_per_country,file_name):
    """
    Saves the dictionary to a json file.

    Args:
        leaders_per_country (dict) : Contains all the retreived data.
        file_name (str) : Name of the JSON file.

    """
    with open(file_name, "w") as file:
        json.dump(leaders_per_country, file,indent = 4)

def read(file_name):
    """
    Reads the dictionary back from a stored json file.

    Args:
        file_name (str) : Name of the JSON file.
    
    Returns:
        Returns the data of JSON file
    """
    
    with open(file_name, "r") as file:
        data = json.load(file)
    return data

def main():

    """
    This function :
    1. Defining the base URL and constructing the specific endpoints for the cookies, 
       countries, and leaders data.
    2. Fetching the leaders data for each country using the 'get_leaders' function.
    3. Saving the fetched data to a JSON file ('leaders.json') using the 'save' function.
    4. Reading the saved JSON file using the 'read' function.
    5. Printing the results to the console.

    Args:
        None: This function doesn't take any parameters.

    Returns:
        None: The function performs actions but doesn't return a value. It prints the 
              result to the console.
    
    """

    root_url = "https://country-leaders.onrender.com"
    cookie_url = root_url + "/cookie"
    countries_url = root_url + "/countries"
    leaders_url = root_url + "/leaders"

    leaders_per_country = get_leaders(cookie_url,countries_url,leaders_url)
    save(leaders_per_country,"leaders.json")
    result=read("leaders.json")
    print(result)

if __name__ == "__main__":
    main()