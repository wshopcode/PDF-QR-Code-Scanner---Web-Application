from flask import Flask, render_template, request, redirect
import fitz  # PyMuPDF
from pyzbar.pyzbar import decode
from PIL import Image
import io
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extract_qr_codes_from_pdf(pdf_path):
    qr_code_data = []
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Iterate through each page of the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)

        # Extract images from the current page
        images = page.get_images(full=True)

        # Iterate through each image on the page
        for img_index, img_info in enumerate(images):
            xref = img_info[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Decode QR code from the image
            qr_decoded = decode(Image.open(io.BytesIO(image_bytes)))

            # Append the decoded text to the list
            if qr_decoded:
                for qr_result in qr_decoded:
                    qr_code_data.append({
                        'page': page_num + 1,
                        'image': img_index + 1,
                        'data': qr_result.data.decode('utf-8')
                    })

    # Close the PDF document
    pdf_document.close()

    return qr_code_data


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Process the uploaded file
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            qr_code_data = extract_qr_codes_from_pdf(pdf_path)
            return render_template('result.html', qr_code_data=qr_code_data)
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
