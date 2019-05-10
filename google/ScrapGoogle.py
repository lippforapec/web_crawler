import requests
from bs4 import BeautifulSoup
import time
import psycopg2
import os
import categories 
import itertools
import json
from datetime import datetime

USER_AGENT = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

class GoogleScraper:
    def __init__(self):
        self.dbname = "lipp"
        self.tablename = "app_search"
        self.results = []
        self.categories = categories.CATEGORIES
        self.topics = categories.TOPICS
        self.queries = []
        self.news_topic = categories.NEWS_TOPICS

    def fetch_results(self,search_term, number_results, language_code):
        assert isinstance(search_term, str), 'Search term must be a string'
        assert isinstance(number_results, int), 'Number of results must be an integer'
        escaped_search_term = search_term.replace(' ', '+')

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results, language_code)
        response = requests.get(google_url, headers = USER_AGENT)
        response.raise_for_status()
        return search_term, response.text


    def fetch_news_results(self,search_term, number_results, language_code):
        assert isinstance(search_term, str), 'Search term must be a string'
        assert isinstance(number_results, int), 'Number of results must be an integer'
        escaped_search_term = search_term.replace(' ', '+')

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}&tbm=nws'.format(escaped_search_term, number_results, language_code)
        response = requests.get(google_url, headers = USER_AGENT)
        response.raise_for_status()
        return search_term, response.text

    # PARSING  다르게 해야함
    def parse_results(self,html, query):
        soup = BeautifulSoup(html, 'html.parser')
        rank = 1
        found_results =[]
        result_block = soup.find_all('div', attrs={'class': 'g'})
        #print(result_block)
        for result in result_block:
            try: 
                link = result.find('a', href=True)
                #print(link)
                title = result.find('h3')
                description = result.find('div', attrs={'class': 'st'})
                #print(link,title,description)
                if link and title:
                    link = link['href']
                    title = title.get_text()
                    if description:
                        description = description.get_text()
                    if link != '#':
                        found_results.append({'rank': rank, 'title': title, 'summary': description, 'link': link})
                        rank += 1
            except Exception as e:
                print(e)
        if len(found_results) >0:
            print(len(found_results))
            return json.dumps(found_results)
        else:
            return


    def scrape_google(self,search_term, number_results, language_code,news):
        try:
            print(search_term)
            query = ""
            html = ""
            if news:
                query, html = self.fetch_news_results(search_term, number_results, language_code)
                results = self.parse_results(html, query)
                return results
            else: 
                query, html = self.fetch_results(search_term, number_results, language_code)
                results = self.parse_results(html, query)
                return results
        except AssertionError:
            raise Exception("Incorrect arguments parsed to function")
        except requests.HTTPError:
            raise Exception("You appear to have been blocked by Google")
        except requests.RequestException:
            raise Exception("Appears to be an issue with your connection")



    def get_results(self):
        self.results = [(self.scrape_google(category[1]+" "+topic[1],10,"en",0)
                        , category[1]+" "+topic[1], category[0], topic[0],datetime.now()) 
                        for category, topic 
                        in list(itertools.product(self.categories,self.topics))]
        
        print(self.results)
        print(tuple(self.results))
        return 

    def get_news_result(self):
        #print(list(itertools.product(self.categories,self.news_topic)))
        self.results = [(self.scrape_google(category[1]+" "+topic[1],10,"en",1)
                        , category[1]+" "+topic[1], category[0], topic[0],datetime.now()) 
                        for category, topic 
                        in list(itertools.product(self.categories,self.news_topic))]
        
        print(self.results[:10])
        print(tuple(self.results))
        return 

    def db_connect_test(self):
        try:
            connection = psycopg2.connect(user = "",
                                        password = "",
                                        host = "",
                                        port = "5432",
                                        database = "")

            cursor = connection.cursor()
            # Print PostgreSQL Connection properties
            sql = """
                    INSERT INTO app_search(results,query, category,topic,created_at)
                    VALUES (%s,%s,%s,%s,%s)
                """#.format(self.tablename)
            cursor.executemany(sql, tuple(self.results))
            #print ( connection.get_dsn_parameters(),"\n")
            # Print PostgreSQL version
            cursor.execute("SELECT * from public.app_search")
            record = cursor.fetchone()
            print("You are connected to - ", record,"\n")
        except (Exception, psycopg2.Error) as error :
            print ("Error while connecting to PostgreSQL", error)

    #def result_to_table(self):


if __name__ == '__main__':
    test=GoogleScraper()
    test.get_news_result()
    test.db_connect_test()

    

    


