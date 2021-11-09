import os
import glob
import pprint
from celery import shared_task
from .getImages import GetImages
from celery_progress.backend import ProgressRecorder

@shared_task(bind=True)
def process_images(self,link,csrfmiddlewaretoken):
    progress = ProgressRecorder(self)
    print("Processing Started!")
    object = GetImages()
    print('[NOTE] Fetching Images Link from website !')
    # fetching image links
    progress.set_progress(100,100,f'Fetching Links From The given Website')
    img_link_path,no_of_links,status_code = object.fetch_images_link(link,csrfmiddlewaretoken)

    if status_code == 200 and no_of_links == 0:
        return 'No Images Found!'
    elif status_code != 200:
        return 'Exited with status code: '+ str(status_code)

    if status_code == 200:

        print('[NOTE] Downloading Images for fetched links from site !')
        # fetching images from fetched links
        total_imgs = object.fetch_image_from_links_file(csrfmiddlewaretoken,img_link_path)
        print('[NOTE] Please wait until all the images are downloaded !')

        while not object.ARE_ALL_IMAGES_DOWNLOADED:
            progress.set_progress(total_imgs - object.TOTAL_IMAGES,total_imgs,f'Downloading Images... ')


        print("[NOTE]:Now We Begin Child Abuse Analysis")

        # getting path & all the images in the path
        folder_path = os.path.join(os.getcwd(),os.path.join('Data',os.path.join('images',os.path.join(csrfmiddlewaretoken))))
        img_paths = glob.glob(folder_path + r'/*.jpg')

        # if no JPG images are found error is showned
        if len(img_paths) == 0:
            return 'No Images Found'

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
        object.save_report(link,csrfmiddlewaretoken)
        progress.set_progress(100,100,f'Saving Report to database ...')
        '''
         Write delete code,
         which shall delete all the scraped images,
         from Data/csrfmiddlewaretoken/images/*
         [JEET]
        '''

        # if 0 is the length then Child Abusive Content is Not Found else it is found
        if len(object.results) == 0:
            return 'Child Abusive Content Not Found!'
        else:
            return 'Child Abusive Content Found!'
