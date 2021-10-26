import os
import threading
import requests as req
from bs4 import BeautifulSoup



class GetImages:

    def make_usable_links(self,url, links):
        # Filtering unuseful links and making links useful !
        for link in links:
            if 'http' not in link:
                try:
                    if '/' == link[0]:
                        links[links.index(link)] = url + link  # eg if /about -> https://example.com/about
                    else:
                        links[links.index(link)] = url + '/' + link  # eg if about -> https://example.com/about
                except:
                    pass

    def save_attribute_value_from_tags_to_attibute_value_list(self,all_tags, unique_attribute, final_list):
        for tag in all_tags:
            try:
                final_list.append(tag[unique_attribute])
            except Exception as e:
                pass

    def fetch_images_link(self,url):
        res = self.SecureConnection.get_request_session(self)

        if 'http' not in url:
            url = 'http://' + url

        html_data_res = res.get(url)

        if html_data_res.status_code == 200:

            soup = BeautifulSoup(html_data_res.content, 'lxml')
            img_tags = soup.find_all('img')
            all_images_links = []
            self.save_attribute_value_from_tags_to_attibute_value_list(img_tags, 'src', all_images_links)
            self.make_usable_links(url, all_images_links)
            print(f'[NOTE] Successfully Fetched {len(all_images_links)} links !')
            with open('img_links.txt', 'w') as f:
                for link in all_images_links:
                    f.write(link + '\n')


    def fetch_image_from_links_file(self,links_file_location='img_links.txt', saving_folder_name=os.getcwd()):
        img_folder_location = os.path.join(saving_folder_name, "images")

        if not os.path.exists(img_folder_location):
            os.makedirs(img_folder_location)

        with open(links_file_location, 'r') as f:
            links = f.readlines()

            self.TOTAL_IMAGES = len(links)

            for link in links:
                index = links.index(link)
                link = link.replace('\n', '')
                image_fetch_thread = threading.Thread(target=self.fetch_image, args=(link, img_folder_location, f'{index}',))
                image_fetch_thread.start()

    def fetch_image(self,url, folder_name, image_index):
        image_name = "image_" + image_index + ".jpg"

        try:
            image_extentation = str(url).split('/')[-1]

            if '.' in image_extentation:
                image_name = 'image_' + image_index + image_extentation[image_extentation.index('.'):]

                if "?" in image_name:
                    image_name = image_name[:image_name.index('?')]

                if '/' in image_name:
                    image_name = image_name[:image_name.index('/')]

                if '\n' in image_name:
                    image_name = image_name[:image_name.index('\n')]

                if '.' in image_name[image_name.index('.') + 1:]:
                    image_name = "image_" + image_index + ".jpg"

        except:
            image_name = "image_" + image_index + ".jpg"

        try:

            if 'http' not in url:
                url = 'http://' + url

            # res_raw_img = req.get(url,proxies=SecureConnection.torsocks_proxies)
            session = self.SecureConnection.get_request_session(self)
            res_raw_img = session.get(url, timeout=20)

            if res_raw_img.status_code == 200:
                with open(os.path.join(folder_name, image_name), 'wb') as f:
                    f.write(res_raw_img.content)
                print(f'[@] {image_name} Successfully Downloaded !\n')
            else:
                print(f'[{res_raw_img.status_code}]failed to fetch from {url}\n')

        except Exception as e:
            print(f'Failed to fetch images from {url} !\n [SCRIPT ERROR] {e}  !\n')
        finally:
            self.TOTAL_IMAGES = self.TOTAL_IMAGES - 1
            if self.TOTAL_IMAGES <= 0:
                self.ARE_ALL_IMAGES_DOWNLOADED = True
    class SecureConnection:

        def get_request_session(self):
            os.popen('tor')
            torsocks_proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
            req_session = req.session()
            req_session.proxies = torsocks_proxies
            return req_session

    def __init__(self, url):
        self.ARE_ALL_IMAGES_DOWNLOADED = False
        self.TOTAL_IMAGES = -1

        print('[NOTE] Fetching Images Link from website !')
        self.fetch_images_link(url)
        print('[NOTE] Downloading Images for fetched link (img_link.txt) from site !')
        self.fetch_image_from_links_file()
