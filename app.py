
from flask import Flask, render_template, request, Response
from werkzeug.utils import secure_filename
from database.db import initialize_db
from database.models import Blog
import yake
import json
from mongoConnect2 import mongoConnect2

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost/blog-buddy'
}
db = initialize_db(app)

@app.route('/upload')
def index():
    return render_template('upload2.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files["file"]
        f.save(secure_filename(f.filename))
        with open(f.filename, 'r') as file:
            doc = file.read().replace('\n', '')
        # x ={"content":doc}
        # body = json.dumps(x)

    # mc = mongoConnect2()
    # mc.push_to_db(body)
        text=doc
        language = "en"
        max_ngram_size = 3
        deduplication_thresold = 0.9
        deduplication_algo = 'seqm'
        windowSize = 1
        numOfKeywords = 20

        custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_thresold,
                                                    dedupFunc=deduplication_algo, windowsSize=windowSize,
                                                    top=numOfKeywords, features=None)
        keywords = custom_kw_extractor.extract_keywords(text)

        # for kw in keywords:
        #     print(kw)

        # import time
        from highlight import TextHighlighter
        th = TextHighlighter(max_ngram_size=3, highlight_pre="<b >", highlight_post="</b>")
        # print(th.highlight(text, keywords))
        h_text= th.highlight(text, keywords)
        # print(type(html(h_text)))
        # Word cloud
        # %pip install wordcloud --user
        # from os import path
        # from PIL import Image
        from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
        from nltk.corpus import stopwords
        import matplotlib.pyplot as plt
        # %matplotlib inline
        # for index in range(len(dataset)):
        # temp += df['A'].iloc[index] + df['B'].iloc[index]
        stop_words = set(stopwords.words("english"))
        wordcloud = WordCloud(
            background_color='white',
            stopwords=stop_words,
            max_words=100,
            max_font_size=50,
            random_state=42
        ).generate(str(doc))
        # print(wordcloud)
        # fig = plt.figure(1)
        # plt.imshow(wordcloud)
        # plt.axis('off')
        # plt.show()
        # fig.savefig("static/components/word.png", dpi=900)
        wordcloud.to_file("static/components/word.png")
    # return th.highlight(text, keywords)
    #     time = time.time()
    return render_template("results.html", wordcloud=wordcloud, text=text, keywords=keywords, h_text=h_text)
    # return 'file '+f.filename+' uploaded successfully'+"\n\n"+str(x)#+ {'id': str(id)}, 200


@app.route('/blogs')
def get_blogs():
    blogs = Blog.objects().to_json()
    return Response(blogs, mimetype="application/json", status=200)

@app.route('/blogs', methods=['POST'])
def add_blog():
    body = request.get_json()
    blog = Blog(**body).save()
    id = blog.id
    return {'id': str(id)}, 200

@app.route('/blogs/<id>', methods=['PUT'])
def update_blog(id):
    body = request.get_json()
    Blog.objects.get(id=id).update(**body)
    return '', 200

@app.route('/blogs/<id>', methods=['DELETE'])
def delete_blog(id):
    Blog.objects.get(id=id).delete()
    return '', 200

@app.route('/blogs/<id>')
def get_blog(id):
    blogs = Blog.objects.get(id=id).to_json()
    return Response(blogs, mimetype="application/json", status=200)

if __name__ == '__main__':
    app.run(debug=True)