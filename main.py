from flask import Flask, request, render_template
import os
import PyPDF2
import docx2txt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_pdf(file_path):
    text = ""
    with open(file_path,'rb') as file:
        read_data = PyPDF2.PdfReader(file)
        for page in read_data.pages:
            text += page.extract_text()
    return text

def extract_text_docs(file_path):
    return docx2txt.process(file_path)

def extract_text_txt(file_path):
    with open(file_path,'r',encoding='utf-8') as file:
        return file.read()
    

def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_docs(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_txt(file_path)
    else:
        return ""
    
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/')
def matchresume():
    return render_template("app.html")  # Make sure app.html is inside the templates folder

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        jd = request.form.get('resumeText')
        resume_files = request.files.getlist('resumeFile')

        resumes = []
        for resume_file in resume_files:
            filenamee = os.path.join(app.config['UPLOAD_FOLDER'],resume_file.filename)
            resume_file.save(filenamee)
            resumes.append(extract_text(filenamee))

        if not resumes and not jd:
            return render_template('app.html',message="Please upload a resume or enter a job description")
    
        vec = TfidfVectorizer().fit_transform([jd] + resumes)
        vecs = vec.toarray()
        j_V = vecs[0]
        r_V = vecs[1:]

        sim = cosine_similarity([j_V],r_V)[0]
        top_in = sim.argsort()[-3:][::-1]
        top_r = [resume_files[i].filename for i in top_in]
        similarity_scores = [round(sim[i], 2) for i in top_in]
        print(top_r)
        print(similarity_scores)
        return render_template('app.html',message="Top matching resumes:",top_r=top_r,similarity_scores=similarity_scores)

    return render_template('app.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
