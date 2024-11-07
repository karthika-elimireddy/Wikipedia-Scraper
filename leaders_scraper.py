
import requests
import json
from bs4 import BeautifulSoup


def get_first_paragraph(wikipedia_url):
    
    response=requests.get(wikipedia_url)
    soup = BeautifulSoup(response.text,"html.parser")
    p_tags = soup.find_all('p')
    first_paragraph=''
    for p in p_tags:
        if len(p.get_text()) > 100 :
            first_paragraph = p.get_text()
            break
    return first_paragraph

def get_leaders(cookie_url,countries_url,leaders_url):

    cookies = requests.get(cookie_url).cookies
    countries = requests.get(countries_url,cookies=cookies).json()
    leaders_per_country={}
    for country in countries:
        try :
            response=requests.get(leaders_url, cookies = cookies, params={'country': country })
            if (response.status_code == 401 | response.status_code == 403):
                cookies = requests.get(cookie_url).cookies
                response = requests.get(leaders_url, cookies = cookies, params={'country': country })
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        
        leaders = response.json()
        for leader in leaders:
            for key in leader:
                if key == 'wikipedia_url':
                    leader['first_paragraph'] = get_first_paragraph(leader[key])
                    break
        leaders_per_country[country]=leaders

    return leaders_per_country

def save(leaders_per_country,file_name):
    
    with open(file_name, "w") as file:
        json.dump(leaders_per_country, file)

def read(file_name):
    with open(file_name, "r") as file:
        data = json.load(file)
    return data

def main():

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