import os
import glob
import pprint
import pandas as pd
from celery import shared_task
from .getImages import GetImages
from celery_progress.backend import ProgressRecorder
from .report import generate_report

'''
     This method is to process images,
      which will handle Downloading images,
      & send them into Analysis.

      [MASTER FUCNTION]
'''

# handle a single link
@shared_task(bind=True)
def process_link(self,link,csrfmiddlewaretoken):
    # this fucntion will return a list always
    # if report is being saved then the second parameter will be true
    # else it'll be zero
    # first parameter will be the data that will be needed to pass in frontend for results.

    progress = ProgressRecorder(self)
    print("Processing Started!")
    object = GetImages()

    print('[NOTE] Fetching Images Link from website !')
    # fetching image links
    progress.set_progress(100,100,f'Fetching Links From The given Website')
    try :
        img_link_path,no_of_links,status_code = object.fetch_images_link(link,csrfmiddlewaretoken)
    except Exception as e:
        print(e)
        return ['Enter a valid link.',0]

    if status_code == 200 and no_of_links == 0:
        return ['No images found on the given link.',0]
    elif status_code != 200:
        return ['Unable to scrape data from the given website.',0]

    if status_code == 200:

        print('[NOTE] Downloading Images for fetched links from site !')
        # fetching images from fetched links
        total_imgs = object.fetch_image_from_links_file(csrfmiddlewaretoken,img_link_path)
        print('[NOTE] Please wait until all the images are downloaded !')

        while not object.ARE_ALL_IMAGES_DOWNLOADED:
            progress.set_progress(total_imgs - object.TOTAL_IMAGES,total_imgs,f'Downloading Images... ')


        print("[NOTE]:Now We Begin Image Analysis for Detecting Child Abuse")

        # getting path & all the images in the path
        img_folder_path = os.path.join(os.getcwd(),os.path.join('Data',os.path.join('images',os.path.join(csrfmiddlewaretoken))))
        img_paths = glob.glob(img_folder_path + r'/*.jpg')

        # if no JPG images are found error is showned
        if len(img_paths) == 0:
            return ['No Images Found',0]

        # however if JPG images are found then
        object.TOTAL_JPG_IMAGES = len(img_paths)
        total_jpg = len(img_paths)
        print("Total JPG Images = " + str(object.TOTAL_JPG_IMAGES ))

        # iterative analysis 41 sec. for 31 images (Download & Analyze)

        for idx,path in enumerate(img_paths):
            if len(object.results) >= 2:
                object.IS_ANANLYSIS_DONE = True
                break
            if not object.IS_ANANLYSIS_DONE:
                index = idx+1
                progress.set_progress(index,total_jpg,f'Analyzing Images {index}/ {total_jpg}')
                object.age_P(path)

        # printing results & len of results which should be max. 2 as we stop ananlysis at 2
        pprint.pprint(object.results)
        print(len(object.results))


        # saving to report Database
        progress.set_progress(100,100,f'Generating Report ...')

        # generate report
        report_path = generate_report(link,csrfmiddlewaretoken,object.results)

        progress.set_progress(100,100,f'Saving Report to database ...')

        '''
         Write delete code,
         which shall delete all the scraped images & the links,
         from Data/images/csrfmiddlewaretoken/* &
         Data/links/csrfmiddlewaretoken/link/img_links.txt
         [JEET]
        '''

        # if 0 is the length then Child Abusive Content is Not Found else it is found
        if len(object.results) == 0:
            return [report_path,1]
        else:
            return [report_path,1]

# handle file
@shared_task(bind=True)
def process_file(self,file,path,csrfmiddlewaretoken_main):
    progress = ProgressRecorder(self)

    if file.endswith(".txt"):
        with open(path) as f:
            links = f.readlines()

    elif file.endswith(".csv"):
        links = pd.read_csv(path)['Links']

    print(links)
    print(len(links))
    links_improved = [link for link in links if link != ['\n']]
    total_links = len(links_improved)
    total_generated_reports = 0
    report_links = []
    report_links_path = []

    for idx,link in enumerate(links_improved):
        progress.set_progress(idx,total_links,f'Analyzing {idx}/{total_links} links ...')
        csrfmiddlewaretoken =  str(csrfmiddlewaretoken_main + "_" + str(idx))
        result = p_l(link,csrfmiddlewaretoken)
        if result[1] == 1:
            total_generated_reports+=1
            report_links.append(link)
            report_links_path.append(result[0])

    if total_generated_reports == 0:
        return ["No Child Abuse Found In Any of the links.",0]
    else:
        msg = str(f"<p>{total_generated_reports} out of {total_links} Reports Generated.</p>")
        msg2 = ""
        for idx,i in enumerate(report_links_path):
            msg2+="<p>Click <a href = " + 'media/' + report_links_path[idx] + " download >Here</a> to download report for " + report_links[idx] + "</p>"
        return [msg,1,msg2]


# writing process_link fucntion again without the progress bar & shared_task decorator so that it doesn't return
def p_l(link,csrfmiddlewaretoken):

        print("Processing Started!")
        object = GetImages()

        print('[NOTE] Fetching Images Link from website !')
        # fetching image links

        try :
            img_link_path,no_of_links,status_code = object.fetch_images_link(link,csrfmiddlewaretoken)
        except Exception as e:
            print(e)
            return ['Enter a valid link.',0]

        if status_code == 200 and no_of_links == 0:
            return ['No images found on the given link.',0]
        elif status_code != 200:
            return ['Unable to scrape data from the given website.',0]

        if status_code == 200:

            print('[NOTE] Downloading Images for fetched links from site !')
            # fetching images from fetched links
            total_imgs = object.fetch_image_from_links_file(csrfmiddlewaretoken,img_link_path)
            print('[NOTE] Please wait until all the images are downloaded !')

            while not object.ARE_ALL_IMAGES_DOWNLOADED:
                pass


            print("[NOTE]:Now We Begin Image Analysis for Detecting Child Abuse")

            # getting path & all the images in the path
            img_folder_path = os.path.join(os.getcwd(),os.path.join('Data',os.path.join('images',os.path.join(csrfmiddlewaretoken))))
            img_paths = glob.glob(img_folder_path + r'/*.jpg')

            # if no JPG images are found error is showned
            if len(img_paths) == 0:
                return ['No Images Found',0]

            # however if JPG images are found then
            object.TOTAL_JPG_IMAGES = len(img_paths)
            total_jpg = len(img_paths)
            print("Total JPG Images = " + str(object.TOTAL_JPG_IMAGES ))

            # iterative analysis 41 sec. for 31 images (Download & Analyze)

            for idx,path in enumerate(img_paths):
                if len(object.results) >= 2:
                    object.IS_ANANLYSIS_DONE = True
                    break
                if not object.IS_ANANLYSIS_DONE:
                    index = idx+1
                    object.age_P(path)

            # printing results & len of results which should be max. 2 as we stop ananlysis at 2
            pprint.pprint(object.results)
            print(len(object.results))

            # generate report
            report_path = generate_report(link,csrfmiddlewaretoken,object.results)

            '''
             Write delete code,
             which shall delete all the scraped images & the links,
             from Data/images/csrfmiddlewaretoken/* &
             Data/links/csrfmiddlewaretoken/link/img_links.txt
             [JEET]
            '''

            # if 0 is the length then Child Abusive Content is Not Found else it is found
            if len(object.results) == 0:
                return [report_path,1]
            else:
                return [report_path,1]
