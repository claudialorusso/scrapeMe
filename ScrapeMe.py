# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 11:10:49 2021

@author: ClaudiaLorusso
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import os.path
from datetime import datetime
from time import sleep
import numpy as np
import winsound
import random
from urllib import request

class ScrapeMe:
    """
    Simple script in python that allows you to scrape some public information
    (laws and regulaments) from "Consiglio Regionale della Puglia"s web page,
    using BeautifulSoup.
    If the software suddenly crushes, you can simply restart it:
    it wont reload pages that had been already visited.
    
    DISCLAIMER: This is for didactit purpose only!
    """
    def __load_page__(self, soup, page_num):
        """
        Loads the page with the specified number.

        Parameters
        ----------
        soup : BeautifulSoup object
            Data structure representing the parsed HTML page.
        page_num : int
            Number of the page you want to load.

        Returns
        -------
        soup : BeautifulSoup object
            Data structure representing the page_num parsed HTML page.

        """

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
        }
        
        payload = {
            "__EVENTTARGET": "gwLeggi",
            "__EVENTARGUMENT": "Page${}".format(page_num),
            "__LASTFOCUS": "",
            "__ASYNCPOST": "true",
        }
    
        for inp in soup.select("input"):
            payload[inp["name"]] = inp.get("value")
            
        api_url = "http://portale2015.consiglio.puglia.it/documentazione/leges/risultati.aspx"
        soup = BeautifulSoup(
            requests.post(api_url, data=payload, headers=headers).content,
            "html.parser",
        )
        return soup
    
    def __get_links__(self):
        """
        Scrapes the list of the links pointing to the every law and regulament
        contained into the "Consiglio della Regione Puglia"s database.
        Every link will be saved into a .txt file named laws_link.txt.
        You can find the file into the Utils folder.
        
        Returns
        -------
        link_list : list
            contains evrey link that points to the DB documents
        """
        if os.path.isfile("Utils\laws_link.txt")==False or os.stat("Utils\laws_link.txt").st_size == 0:
        
            url = "http://portale2015.consiglio.puglia.it/documentazione/leges/risultati.aspx"
            soup = BeautifulSoup(requests.get(url).content, "html.parser")
            page=1
            
            link_list = list()
            
            while(page<251):
                
                soup_page = self.__load_page__(soup, page)
                table = soup_page.find_all("a")
                
                pattern_url = "http://portale2015.consiglio.puglia.it/documentazione/leges/"
                
                for row in table:
                    pattern = r"modulo.aspx.id=\d+"
                    match = re.findall(pattern, str(row.get("href")))
                    for i in match:
                        url = pattern_url + i
                        link_list.append(url) 
                page+=1
            
            #stampo su file i link delle leggi
            with open('Utils\laws_link.txt', 'w+') as f:
            #with open('Utils\laws_dif.txt', 'w+') as f:
                for item in link_list:
                    f.write("%s\n" % item)
        else:
            #link_file = open('Utils\laws_link.txt', 'r')
            link_file = open('Utils\laws_dif.txt', 'r')
            link_list = link_file.read().splitlines()
            link_file.close()
        return link_list    
    
    def __get_content__(self, url):
        """
        Scrapes the desired content from the specified url.
        Every info is then saved into a .json file thanks to the __save_info__
        method.
        
        Parameters
        ----------
        url : string
            the url page from which scrape the desired info.

        Returns
        -------
        string
            .json file path (testing pourpose)

        """
        with open('Utils\laws_processed.txt', "a+") as link_file:
            link_list = link_file.read().splitlines()
            link_file.close()
        if (url in set(link_list)) == False:
            with open('Utils\laws_processed.txt', "a") as myfile:
                myfile.write(url+'\n')
                myfile.close()
                
            user_agent = self.get_random_ua()
            
            referer = 'https://google.it'
            headers = {
                'user-agent': user_agent,
                'referer': referer,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Pragma': 'no-cache'
                }
  
            req = requests.get(url, headers)

            soup = BeautifulSoup(req.content, 'html.parser')
            
            
            #get year
            pattern = r'(?:(?:18|19|20|21)[0-9]{2})'
            reg = re.findall(pattern, str(soup.find(id = "lblAnno")))
            
            year = reg[0]
            
            
            #get number

            # initializing tag
            tag1 = "span id=\"lblNumero\""
            tag2 = "span"
      
            # regex to extract required strings
            pattern = "<" + tag1 + ">(.*?)</" + tag2 + ">"
    
            reg = re.findall(pattern, str(soup.find(id = "lblNumero")))
            
            try:
                number = reg[0]
            except IndexError:
                number = str()
                print(url)
            
            #get date
            
            pattern = r'(((0[1-9]|[12][0-9]|3[01])([-./])(0[13578]|10|12)([-./])(\d{4}))|(([0][1-9]|[12][0-9]|30)([-./])(0[469]|11)([-./])(\d{4}))|((0[1-9]|1[0-9]|2[0-8])([-./])(02)([-./])(\d{4}))|((29)(\.|-|\/)(02)([-./])([02468][048]00))|((29)([-./])(02)([-./])([13579][26]00))|((29)([-./])(02)([-./])([0-9][0-9][0][48]))|((29)([-./])(02)([-./])([0-9][0-9][2468][048]))|((29)([-./])(02)([-./])([0-9][0-9][13579][26])))'
            reg = re.findall(pattern, str(soup.find(id = "lblData")))
            
            date_r = reg[0]
            date = date_r[0]
            
            
            #get title
            
            # initializing tag
            tag1 = "span id=\"lblTitolo\""
            tag2 = "span"
      
            # regex to extract required strings
            pattern = "<" + tag1 + ">(.*?)</" + tag2 + ">"
    
            reg = re.findall(pattern, str(soup.find(id = "lblTitolo")), re.DOTALL)
            
            try:
                title = reg[0]
            except IndexError:
                title = ""
                print("Error in getting title:\t",url)
            
            #get avviso
            
            # initializing tag
            tag1 = "span id=\"lblStorVig\""
            tag2 = "span"
      
            # regex to extract required strings
            pattern = "<" + tag1 + ">(.*?)</" + tag2 + ">"
    
            reg = re.findall(pattern, str(soup.find(id = "lblStorVig")), re.DOTALL)
            
            try:
                avviso = reg[0]
                if (avviso == "Regolamento Storico"):
                    avviso = "REG"
                elif (avviso == "Regolamento Vigente"):
                    avviso = "REG"
                else:
                    avviso = "LR"
            except IndexError:
                avviso = "LR"
                print("LR vs REG:\t", url)
            
            
            
            #get body

            # Initializing variable
    
            gfg = BeautifulSoup(request.urlopen(url).read().decode('utf-8', 'ignore'), features='lxml')
     
            # Extracting data for article section
            bodyHtml = gfg.find('body')
     
            # Calculating result
            body = bodyHtml.get_text()#unicodedata.normalize("NFKD",bodyHtml.get_text())
            body = re.sub("’", "'", body)
            body = re.sub("“", '"', body) 
            body = re.sub("”", '"', body)
            body = re.sub(r"(?<!\\)\\n|\n", " ", body)
            body = " ".join(body.split())
            
            #saving everything into a json file
            return self.__save_info__(year, number, date, title, body, avviso)
        

    def get_random_ua(self):
        """
        Gives you the chance to get a random User-agent from a .txt named
        ua_file.txt. You can find the specified file into the Utils folder.

        Returns
        -------
        random_ua : string
            random User-Agent

        """
        random_ua = ''
        ua_file = 'Utils/ua_file.txt'
        try:
            with open(ua_file) as f:
                lines = f.readlines()
            if len(lines) > 0:
                prng = np.random.RandomState()
                index = prng.permutation(len(lines) - 1)
                idx = np.asarray(index, dtype=np.int64)[0]
                random_ua = unicodedata.normalize("NFKD",lines[int(idx)]).replace("\n", "")
        except Exception as ex:
            print('Exception in random_ua:')
            print(str(ex))
        finally:
            return random_ua
        
    def __save_info__(self, year, number, date, title, body, avviso):
        """
        Saves every law (or regulament) info into a .json file
        Parameters
        ----------
        year : string
            law's emanation year
        number : int
            law's number
        date : string
            law's emanation date
        title : string
            law's description
        body : string
            law's content
        avviso : string
            = LR, if it is a law
            = REG, if it is a regulament

        Returns
        -------
        path_file : string
            .json path file (test pourposes)

        """
        try:
            d = datetime.strptime(date, "%d/%m/%Y").strftime('%Y_%m_%d')
            
            file_name = avviso+"-"+ d + "-" +number+".json"
            
            path_file = "DB/"+file_name
            
            file_details = {
                'adv': avviso,
                'year': year,
                'date': date,
                'number': number,
                'title': title,
                'body': body
             }
            
            with open(path_file, 'x+', encoding='utf-8-sig') as json_file:
                json.dump(file_details, json_file, ensure_ascii=False)
                json_file.close()
        except FileExistsError:
            pass
        return path_file       
            
            
    def create_DB(self):
        """
        Creates the desired DB with every law and regulament.
        NO duplicates will be added in the folder.

        Returns
        -------
        None.

        """
        
        try:
            link_list = self.__get_links__()
            
            link_list.reverse()
            random.shuffle(link_list)
            
            for link in link_list:
                self.__get_content__(link)
                sleep(.5)
                
        except ConnectionError as ce:
            print(ce.message)
            print("\nSlowdown kid! You overwhelmed the server!!")
        
    def load_content(self, path):
        """
        You can use this method to correcly print a law's body from
        the json file in which it stands.

        Parameters
        ----------
        path : string
            path of the law

        Returns
        -------
        None.

        """
        #f = open(path)
        
        
        with open(path, encoding="utf-8-sig", errors="ignore") as f:
            data = json.load(f)
            f.close()
        print(data)
        print(data.get('body'))

"""
sc = ScrapeMe()
sc.create_DB()

#sc.load_content("Leggi_prova_DB\LR-1972_01_13-1.json")
winsound.Beep(440, 1000)
"""

if os.path.isfile("Utils\laws_link.txt") and os.stat("Utils\laws_link.txt").st_size != 0:
    link_file = open('Utils\laws_link.txt', 'r')
    link_list = link_file.read().splitlines()
    link_file.close()
    link_file = open('Utils\laws_processed.txt', 'r')
    link_processed = link_file.read().splitlines()
    link_file.close()
    diff = list(set(link_list)-set(link_processed))
    
    with open('Utils\laws_dif.txt', 'w+') as f:
        for item in diff:
            f.write("%s\n" % item)
        f.close()
    
    print(diff)
    if(set(link_list)==set(link_processed)):
        print("DONE :)")
    else:
        sc = ScrapeMe()
        sc.create_DB()
        winsound.Beep(440, 1000)
else:
    sc = ScrapeMe()
    sc.create_DB()
    winsound.Beep(440, 1000)
