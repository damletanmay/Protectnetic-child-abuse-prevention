import os
import rsa
import zlib
from fpdf import FPDF
from .models import Report
from zipfile import ZipFile
from base64 import b64encode
from PIL import Image, ImageFilter
from Manthan_Hackathon import settings

def compress_data(data):
    print('Compressing data ...')
    return zlib.compress(data)

def data_to_base64(data):
    compressed_data = compress_data(data)
    print('Encoding raw data to base64 ...')
    b64_data = b64encode(compressed_data)
    return b64_data

def encrypt_by_rsa(public_key,datafile,encryptfileName):

    with open(datafile,'rb') as f_data:

        print('Reading data from file ...')

        data = f_data.read()

        data = data_to_base64(data)

        encrypted_data = b''
        total_data_length = len(data)
        length_of_chunk = 53
        data_left_for_encryption = total_data_length

        if int(total_data_length%length_of_chunk) != 0:
            extra_bytes_to_be_added = int(total_data_length%length_of_chunk)
            for _ in range(extra_bytes_to_be_added):
                data += b' '

        start = 0

        while data_left_for_encryption >=0:
            encrypted_data += rsa.encrypt(data[start:start+length_of_chunk],public_key)
            start += length_of_chunk
            data_left_for_encryption -= length_of_chunk

        with open(encryptfileName,'wb') as f:
            f.write(encrypted_data)

        print("Encrypted Zip File Saved")

def zip_images(csrfmiddlewaretoken,img_1_path,img_2_path):

    zip_folder_path = os.path.join(os.path.join(os.getcwd(),"media"),"encrypted_zip_files")
    zip_path = os.path.join(zip_folder_path,csrfmiddlewaretoken+".zip")
    encrypted_zip_path = os.path.join(zip_folder_path,csrfmiddlewaretoken+"_encrypted")
    save_path = os.path.join("encrypted_zip_files",csrfmiddlewaretoken+"_encrypted")
    public_key = settings.PUBLIC_KEY

    if not os.path.exists(zip_folder_path):
        os.makedirs(zip_folder_path)

    # save zip file of original images just so we can encrypt it.
    with ZipFile(zip_path, 'w') as zipObj2:
       zipObj2.write(img_1_path)
       if img_2_path:
           zipObj2.write(img_2_path)

    # encrypting zip file
    encrypt_by_rsa(public_key,zip_path,encrypted_zip_path)

    os.remove(zip_path) # delete the original zip without encryption

    return save_path

def blur_image(path,blur_img_path):
    img_src = path

    #Converting any image into usable format so that it can be saved int jpg or jpeg format for later use !
    original_img = Image.open(img_src).convert('RGB')

    #Increasing amount of blurriness in the image
    amount_of_blur = 20
    increasedBlurredImage = original_img.filter(ImageFilter.BoxBlur(amount_of_blur))

    increasedBlurredImage.save(blur_img_path, 'jpeg')

def save_pdf(link,csrfmiddlewaretoken,blur_img_1_path,blur_img_2_path,results):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",size=20)

    pdf.rect(7,7,195,282,"D") # For Border

    pdf.cell(195,20,'Analytics Report',align = 'C')

    pdf.ln()
    pdf.ln()

    if len(results) == 0:
        msg = "Child Abusive Content Not Found"
    else:
        msg = "Child Abusive Content Found"
    data = [
            ["Link",link],
            ["csrfmiddlewaretoken",csrfmiddlewaretoken],
            ["Result",msg]
    ]

    pdf.set_font("Times",size = 12)
    line_height = pdf.font_size * 3.5

    # for table
    for row in data:
        for idx,datum in enumerate(row):
            if idx == 0:
                col_width = pdf.epw / 4.5
                pdf.set_font("Times","B",size = 12)
            else:
                col_width = pdf.epw / 1.5
                pdf.set_font("Times",size = 12)
            pdf.multi_cell(col_width, line_height, datum, border=1, ln=3, max_line_height=pdf.font_size)

        pdf.ln(line_height)

    pdf.set_font("Times","B",size = 12)
    pdf.ln()
    # images

    pdf.line(x1=195, y1=100, x2=10, y2=100)

    if blur_img_1_path:
        images = []
        for key,value in results.items():
            images.append(key)

        sub_dict = results[images[0]]
        p_content_1 = sub_dict['porn']*100
        s_content_1 = sub_dict['sexy']*100

        if len(images) == 2:
            sub_dict = results[images[1]]
            p_content_2 = sub_dict['porn']*100
            s_content_2 = sub_dict['sexy']*100


        pdf.ln()
        pdf.cell(70,12,'Image - 1',align = 'R')
        pdf.ln()
        pdf.cell(70,12,f"P-content: {p_content_1}%",align="R")
        pdf.ln()
        pdf.cell(70,12,f"S-content: {s_content_1}%",align="R")
        pdf.ln()

        img1 = Image.open(blur_img_1_path)
        size=(200,200)
        img1 = img1.resize(size)
        pdf.image(img1, x = 90, y = 110)
        pdf.ln()

        pdf.line(x1=195, y1=190, x2=10, y2=190)
        pdf.ln()

    if blur_img_2_path:
        pdf.ln()
        pdf.ln()
        pdf.ln()
        pdf.cell(70,12,'Image - 2',align = 'R')
        pdf.ln()
        pdf.cell(70,12,f"P-content: {p_content_2}%",align="R")
        pdf.ln()
        pdf.cell(70,12,f"S-content: {s_content_2}%",align="R")
        pdf.ln()

        img2 = Image.open(blur_img_2_path)
        size=(200,200)
        img2 = img2.resize(size)
        pdf.image(img2, x = 90, y = 200)
        pdf.ln()

        pdf.line(x1=195, y1=280, x2=10, y2=280)


    pdf_folder_path = os.path.join(os.path.join(os.getcwd(),"media"),"pdf_reports")
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)

    file_name = csrfmiddlewaretoken+".pdf"
    save_path = os.path.join("pdf_reports",file_name)
    pdf_path = os.path.join(pdf_folder_path,file_name)
    pdf.output(pdf_path)
    return save_path


# Flow of below function
# 1 Zip original_img & save it
# 2 Encrypt the zip file & save it
# 3 Delete zip file generated in the first step
# 4 Save Blur Images
# 5 Save PDF
# 6 Save Report

def generate_report(link,csrfmiddlewaretoken,results):

    report = Report()
    report.link = link
    report.csrfmiddlewaretoken = csrfmiddlewaretoken

    if len(results) == 0:
         # No Child Abuse Detected
         # that means we save only result into pdf
         report.img_1 = None
         report.img_2 = None
         report.zip = None
         report.result = False
         pdf_report = save_pdf(link,csrfmiddlewaretoken,None,None,results)
         report.pdf_report = pdf_report

    else:

         # Child Abuse Detected

        '''
              Saving path of detected images into images array
              these images will be blured & saved to report
              while original images will be zipped & encrypted
              so that no one can have direct access to the images.
        '''

        images = []
        for key,val in results.items():
            images.append(key)
        print(images)

         # now these images will go into below path but blurred
        save_blur_images_path = os.path.join(os.path.join(os.getcwd(),"media"),'report_images')
        img_1 = os.path.join(save_blur_images_path,csrfmiddlewaretoken + '_1.jpg')
        img_2 = os.path.join(save_blur_images_path,csrfmiddlewaretoken + '_2.jpg')

        if not os.path.exists(save_blur_images_path):
         os.makedirs(save_blur_images_path)

         # blurring first image
        blur_image(images[0],img_1)
        save_img_1 = os.path.join('report_images',csrfmiddlewaretoken + '_1.jpg')
        save_img_2 = os.path.join('report_images',csrfmiddlewaretoken + '_2.jpg')
        if len(results) == 1 and len(images) == 1:
            report.img_1 = save_img_1
            report.img_2 = None
            report.zip = zip_images(csrfmiddlewaretoken,images[0],None)
            pdf_report = save_pdf(link,csrfmiddlewaretoken,img_1,None,results)
            report.pdf_report = pdf_report

        elif len(results) == 2 and len(images) == 2:
             # blurring second image only if found
             blur_image(images[1],img_2)
             report.img_1 = save_img_1
             report.img_2 = save_img_2
             report.zip = zip_images(csrfmiddlewaretoken,images[0],images[1])
             pdf_report = save_pdf(link,csrfmiddlewaretoken,img_1,img_2,results)
             report.pdf_report = pdf_report

        report.result = True

    report.save()
    print("Report Saved Successfully!")
    return pdf_report
