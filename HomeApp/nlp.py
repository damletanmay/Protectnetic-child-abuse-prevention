import os
import joblib
import requests as req
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

def predict_link(URL):
    try:
        URL = URL.strip().replace('\n','')
        if 'http' not in URL:
            URL = 'http://'+URL
        path = os.path.join(os.path.join(os.path.join(os.getcwd(),"HomeApp"),"models"),'child_abusive_detection_model.pkl')
        model = joblib.load(path)
        proxies = {'http':'socks5h://localhost:9050','https':'socks5h://localhost:9050'}
        res = req.get(URL,proxies=proxies,headers = {'User-Agent':UserAgent().random})
        if res.status_code ==200:
            html_text = res.content
            soup = BeautifulSoup(html_text,'lxml')
            results = model.predict([soup.get_text()])
            if results[0] == 1:
                print(f'URL : {URL} -> child absuive')
                return 1
            else:
                print(f'URL : {URL} -> not child absuive')
                return 0
        else:
            print('Something went wrong !')
            return -1
    except Exception as e:
        print(e)
        print(f'[-] {URL} not working !')
        return -1
