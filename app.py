
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
import yake
from highlight import TextHighlighter
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
import random
import os
import shutil

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('upload2.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        shutil.rmtree("Uploaded_docs")
        f = request.files["file"]
        os.mkdir("Uploaded_docs")
        f.save("Uploaded_docs/"+secure_filename(f.filename))
        with open("Uploaded_docs/"+f.filename, 'r') as file:
            doc = file.read().replace('\n', '')
        text = doc
        language = "en"
        max_ngram_size = 2
        deduplication_threshold = 0.9
        deduplication_algo = 'seqm'
        windowSize = 1
        numOfKeywords = 10

        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold,
                                                    dedupFunc=deduplication_algo, windowsSize=windowSize,
                                                    top=numOfKeywords, features=None)
        keywords = custom_kw_extractor.extract_keywords(text)

        th = TextHighlighter(max_ngram_size=3, highlight_pre="<b >", highlight_post="</b>")
        h_text= th.highlight(text, keywords)
        
        shutil.rmtree("static/components/Word_Cloud")

        stop_words = set(stopwords.words("english"))
        wordcloud = WordCloud(
            background_color='black',
            stopwords=stop_words,
            max_words=100,
            max_font_size=50,
            random_state=41
        ).generate(str(doc))
        x=str(random.random())
        # print(x)
        os.mkdir("static/components/Word_Cloud")
        path="static/components/Word_Cloud/word"+x+".png"
        wordcloud.to_file(path)
        
       
    
    return render_template("results.html", keywords=keywords, h_text=h_text, path = path)


if __name__ == '__main__':
    app.run(debug=True)