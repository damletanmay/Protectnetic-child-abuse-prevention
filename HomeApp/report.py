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

    return encrypted_zip_path

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
    pdf.ln()

    # [REMAINING] image code goes here along with displaying p & s content
    # img = Image.open(blur_img_1_path)
    # img = img.crop((10, 10, 490, 490)).resize((96, 96), resample=Image.NEAREST)
    # pdf.image(img, x = 80, y=100)

    pdf_folder_path = os.path.join(os.path.join(os.getcwd(),"media"),"pdf_reports")
    if not os.path.exists(pdf_folder_path):
        os.makedirs(pdf_folder_path)
    pdf_path = os.path.join(pdf_folder_path,csrfmiddlewaretoken+".pdf")
    pdf.output(pdf_path)
    return pdf_path
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

        if len(results) == 1 and len(images) == 1:
            report.img_1 = img_1
            report.img_2 = None
            report.zip = zip_images(csrfmiddlewaretoken,images[0],None)
            pdf_report = save_pdf(link,csrfmiddlewaretoken,img_1,None,results)
            report.pdf_report = pdf_report

        elif len(results) == 2 and len(images) == 2:
             # blurring second image only if found
             blur_image(images[1],img_2)
             report.img_1 = img_1
             report.img_2 = img_2
             report.zip = zip_images(csrfmiddlewaretoken,images[0],images[1])
             pdf_report = save_pdf(link,csrfmiddlewaretoken,img_1,img_2,results)
             report.pdf_report = pdf_report

        report.result = True

    report.save()
    print("Report Saved Successfully!")
    return pdf_report