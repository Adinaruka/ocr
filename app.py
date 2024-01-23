import re
from flask import Flask, render_template, request, jsonify
import os
from PIL import Image, ImageEnhance
import pytesseract as pt
import json
import string
from autocorrect import Speller
import requests
import cv2

app = Flask(__name__)

def show_image(img_path, size=(500, 500)):
                image = cv2.imread(img_path)
                image = cv2.resize(image, size)
                
                cv2.imshow("IMAGE", image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

test_img_path = r"C:\Users\Lenovo\Desktop\flask\test_images"

create_path = lambda f : os.path.join(test_img_path, f)


def download_image(url, save_path):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image from {url} downloaded successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from {url}: {e}")

def remove_punctuation(text):
    text = re.sub(' +', ' ', text)
    text = "".join([char for char in text if char not in string.punctuation])
    return text

def correct_text(text):
    spell = Speller(lang='en')
    new_text = spell(text)
    return new_text

def process_image(image_path):
    custom_oem_psm_config = r'--oem 3 --psm 12'

    image = Image.open(image_path)
    enhancer = ImageEnhance.Contrast(image)
    img = enhancer.enhance(2)
    
    text = pt.image_to_string(img, config=custom_oem_psm_config)
    text = text.replace("\n", " ")
    text = remove_punctuation(text)
    # text = correct_text(text)

    return text.strip()

@app.route('/')
def main():   
    return render_template('index.html')

@app.route('/success', methods=['POST'])   
def success():
    try:
        if request.method == 'POST':
            # import pdb; pdb.set_trace()
            # Read the contents of the file as JSON
            data = request.files['file']
            image_urls = json.loads(data.read())

            # Create a directory to store downloaded images (if not exists)
            download_dir = 'test_images'
            os.makedirs(download_dir, exist_ok=True)

            
            
            test_image_files = os.listdir(test_img_path)

            for f in test_image_files:
                print(f)

            

            #installing the tesseracrt
            pt.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # provide full path to tesseract.exe


            text_list = []

            for i, url in enumerate(image_urls["urls"]):
                image_filename = f"image_{i+1}.jpg"
                image_path = os.path.join(download_dir, image_filename)
                download_image(url, image_path)

                text = process_image(image_path)
                text_list.append(text)

            cleaned_list = [{"extracted_text": s.replace("\n", "")} for s in text_list]
            result = {"extracted_texts": cleaned_list}

            # Save result as a JSON file
            result_json_path = os.path.join(download_dir, 'result.json')
            with open(result_json_path, 'w') as json_file:
                json.dump(result, json_file, indent=4)

            return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
