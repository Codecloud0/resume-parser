from flask import Flask, request, render_template_string
import pdfplumber
import re
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = '''
<!doctype html>
<title>Resume Parser</title>
<h2>Upload your resume (PDF)</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=file>
  <input type=submit value=Upload>
</form>
{% if result %}
<h3>Extracted Info:</h3>
<ul>
  <li><b>Email:</b> {{ result['email'] }}</li>
  <li><b>Phone:</b> {{ result['phone'] }}</li>
</ul>
{% endif %}
'''

def extract_info(text):
    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.findall(r"\+?\d[\d -]{8,}\d", text)
    return {
        "email": email[0] if email else "Not found",
        "phone": phone[0] if phone else "Not found"
    }

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    result = None
    if request.method == 'POST':
        f = request.files['file']
        filepath = os.path.join(UPLOAD_FOLDER, f.filename)
        f.save(filepath)

        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        result = extract_info(text)
    return render_template_string(HTML, result=result)

if __name__ == '__main__':
    app.run(debug=True)
