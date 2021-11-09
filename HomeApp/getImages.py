import os
import glob
import pprint
import threading
from PIL import Image
import requests as req
from .models import Report
from bs4 import BeautifulSoup
from .AgeDetection import detect_age_and_p
from django.shortcuts import render, redirect

# This class gets Images from link if possible & Analyzes Them
class GetImages:

    # below function outputs useful links from which images can be fetched
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

    # below function saves a txt file with all the links in it
    def fetch_images_link(self,url,csrfmiddlewaretoken):

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
            # saving links to Data/link/csrfmiddlewaretoken/img_link.txt for making it unique
            img_links_folder = os.path.join(os.getcwd(),os.path.join('Data',os.path.join('links',os.path.join(csrfmiddlewaretoken))))
            img_link_path = os.path.join(img_links_folder,'img_links.txt')

            if not os.path.exists(img_links_folder):
                os.makedirs(img_links_folder)

            with open(img_link_path, 'w') as f:
                for link in all_images_links:
                    f.write(link + '\n')

            print(img_link_path)
            # sending Successfull results to process_images()
            return img_link_path,len(all_images_links),html_data_res.status_code

        # sending errors so it can detect errors in process_images()
        return None,-1,html_data_res.status_code

    # below function fetches images from link file & saves them
    # all is done using MultiThreading
    def fetch_image_from_links_file(self,csrfmiddlewaretoken,img_link_path):
        # unique folder location to request
        img_folder_location = os.path.join(os.getcwd(),os.path.join('Data',os.path.join('images',os.path.join(csrfmiddlewaretoken))))
        print(img_folder_location)
        if not os.path.exists(img_folder_location):
            os.makedirs(img_folder_location)

        with open(img_link_path, 'r') as f:
            links = f.readlines()

            self.TOTAL_IMAGES = len(links)
            total_imgs = len(links)
            for link in links:
                index = links.index(link)
                link = link.replace('\n', '')
                image_fetch_thread = threading.Thread(target=self.fetch_image, args=(link, img_folder_location, f'{index}',))
                # starting thread
                image_fetch_thread.start()

        return total_imgs

    # below function is used in fetch_image_from_links_file() to download images
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
                    path = os.path.join(folder_name, image_name)
                print(f'[@] {image_name} Successfully Downloaded !\n')
            else:
                print(f'[{res_raw_img.status_code}]failed to fetch from {url}\n')

        except Exception as e:
            print(f'Failed to fetch images from {url} !\n [SCRIPT ERROR] {e}  !\n')
        finally:
            self.TOTAL_IMAGES = self.TOTAL_IMAGES - 1
            if self.TOTAL_IMAGES <= 0:
                self.ARE_ALL_IMAGES_DOWNLOADED = True

    # SecureConnection class is used to remain anonymous while fetching images data
    class SecureConnection:

        def get_request_session(self):
            os.popen('tor')
            torsocks_proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
            req_session = req.session()
            req_session.proxies = torsocks_proxies
            return req_session

    # to intialize certain variables used in certian functions
    def __init__(self):
        self.ARE_ALL_IMAGES_DOWNLOADED = False
        self.TOTAL_IMAGES = -1
        self.IS_ANANLYSIS_DONE = False
        self.TOTAL_JPG_IMAGES = -1
        self.results = {}

    # for analysis purposes
    def age_P(self,path):
        try:
            if not self.IS_ANANLYSIS_DONE:
                res = detect_age_and_p(path)
                if type(res) == dict:
                    sub_dict = res[path]
                    p_content = sub_dict['porn']*100
                    s_content = sub_dict['sexy']*100
                    h_content = sub_dict['hentai']*100

                    if p_content > 50 or s_content > 50 or h_content > 50:
                        self.results.update(res)
                        print("Result Stored")
        except Exception as ex:
            print("Exception in Age_P:")
            print(ex)

        finally:
            self.TOTAL_JPG_IMAGES = self.TOTAL_JPG_IMAGES - 1
            if self.TOTAL_JPG_IMAGES <= 0:
                self.IS_ANANLYSIS_DONE = True


    def save_report(self,url,csrfmiddlewaretoken):
        report = Report()
        report.link = url
        report.csrfmiddlewaretoken = csrfmiddlewaretoken

        if len(self.results) == 0:
            # No C Abuse Detected
            report.img_1 = None
            report.img_2 = None
            report.result = False
        else:
            # C Abuse Detected
            # saving path of detected images into images array
            images = []
            for key,val in self.results.items():
                images.append(key)
            print(images)

            # now these images will go into below path
            save_report_images_path = os.path.join(os.path.join(os.getcwd(),"media"),'report_images')

            if not os.path.exists(save_report_images_path):
                os.makedirs(save_report_images_path)

            img_1 = os.path.join(os.path.join(os.path.join(os.getcwd(),"media"),'report_images'),str(csrfmiddlewaretoken) + '_' + str('1.jpg'))
            img_2 = os.path.join(os.path.join(os.path.join(os.getcwd(),"media"),'report_images'),str(csrfmiddlewaretoken) + '_' + str('2.jpg'))


            # saving first image
            file = images[0]
            img = Image.open(file)
            img.save(img_1)


            if len(self.results) == 1 and len(images) == 1:
                report.img_1 = img_1
                report.img_2 = None
            elif len(self.results) == 2 and len(images) == 2:
                # saving second image0 only if found
                file = images[1]
                img = Image.open(file)
                img.save(img_2)

                report.img_1 = img_1
                report.img_2 = img_2

            report.result = True

        report.save()
        print("Report Saved Successfully!")


    '''
     This method is to process_images,
      which will handle Downloading images,
      & send them into Analysis.

      [MASTER FUCNTION]
    '''
    # def process_images(self,url,csrfmiddlewaretoken):
    #
    #     print('[NOTE] Fetching Images Link from website !')
    #     # fetching image links
    #     img_link_path,no_of_links,status_code = self.fetch_images_link(url,csrfmiddlewaretoken)
    #
    #     # print(status_code)
    #     # print(no_of_links)
    #
    #     # if no images are found then this will return error
    #     # if status_code == 200 and no_of_links == 0:
    #     #     self.ARE_ALL_IMAGES_DOWNLOADED = True
    #     #     return render(request, 'search.html', {'error': 'No images Found On given link'})
    #     # # if not able to scrap any image then this will return error
    #     # elif status_code != 200:
    #     #     self.ARE_ALL_IMAGES_DOWNLOADED = True
    #     #     return render(request, 'search.html', {'error': 'Exited with status code: '+ str(status_code)})
    #
    #     # if everything is fine it'll move forward
    #
    #     if status_code == 200:
    #
    #         print('[NOTE] Downloading Images for fetched links from site !')
    #         # fetching images from fetched links
    #         self.fetch_image_from_links_file(csrfmiddlewaretoken,img_link_path)
    #
    #         print('[NOTE] Please wait until all the images are downloaded !')
    #
    #         while not self.ARE_ALL_IMAGES_DOWNLOADED:
    #             # Waiting till all images are downloaded in all threads
    #             pass
    #
    #         print("[NOTE]:Now We Begin Child Abuse Analysis")
    #
    #         # getting path & all the images in the path
    #         folder_path = os.path.join(os.getcwd(),os.path.join('Data',os.path.join('images',os.path.join(csrfmiddlewaretoken))))
    #         img_paths = glob.glob(folder_path + r'/*.jpg')
    #
    #         # if no JPG images are found error is showned
    #         # if len(img_paths) == 0:
    #         #     return render(request,'search.html',{'error':'No Images Found'})
    #
    #         # however if JPG images are found then
    #         self.TOTAL_JPG_IMAGES = len(img_paths)
    #         print("Total JPG Images = "+str(self.TOTAL_JPG_IMAGES ))
    #
    #         # # MultiThreading 6 Min 2 sec. for 31 images (Download & Analyze)
    #         #
    #         # for path in img_paths:
    #         #     t= threading.Thread(target=self.age_P,args=(path,))
    #         #     t.start()
    #         # # wait till all threads' analysis is done
    #         # while not self.IS_ANANLYSIS_DONE:
    #         #     print("Doing Analysis")
    #         #     if len(self.results) >= 2:
    #         #         self.IS_ANANLYSIS_DONE = True
    #         #     else:
    #         #         pass
    #
    #         # iterative analysis 41 sec. for 31 images (Download & Analyze)
    #
    #         for path in img_paths:
    #             if len(self.results) >= 2:
    #                 self.IS_ANANLYSIS_DONE = True
    #                 break
    #             if not self.IS_ANANLYSIS_DONE:
    #                 self.age_P(path)
    #
    #         # printing results & len of results which should be max. 2 as we stop ananlysis at 2
    #         pprint.pprint(self.results)
    #         print(len(self.results))
    #
    #
    #         # saving to report Database
    #         self.save_report(url,csrfmiddlewaretoken)
    #
    #         '''
    #          Write delete code,
    #          which shall delete all the scraped images,
    #          from Data/csrfmiddlewaretoken/images/*
    #          [JEET]
    #         '''
    #         # if 0 is the length then Child Abusive Content is Not Found else it is found
    #         # if len(self.results) == 0:
    #         #     return render(request, 'search.html',{'msg':'Child Abusive Content Not Found!'})
    #         # else:
    #         #     return render(request, 'search.html',{'msg':'Child Abusive Content Found!'})
