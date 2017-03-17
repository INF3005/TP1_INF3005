# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from database import Database

app = Flask(__name__)
app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.route('/')
def start():
    data = get_db().get_lastest_articles()
    return render_template('index.html', articles=data)


@app.route('/recherche', methods=['POST'])
def get_article_find():
    recherche = request.form['recherche']
    articles = get_db().get_articles(recherche)
    print articles
    if len(articles) == 0 :
        return render_template('error.html', erreur='l\'article inexistant'),400
    else:
        return render_template('articles.html', articles=articles)


@app.route('/article/<identifiant>')
def get_article(identifiant):
    article = get_db().get_article(identifiant)
    print article
    if article is None:
        return render_template('error.html', erreur='l\'article inexistant ')\
            ,400
    else:
        return render_template('article.html', article=article)


@app.route('/admin')
def administrator():
    articles = get_db().get_all_articles()
    if articles is None:
        return render_template('adminError.html', erreur='la base est vide')
    else:
        return render_template('admin.html', articles=articles)


@app.route('/modifier/<idu>', methods=['GET'])
def get_articles_for_update(idu):
    article = get_db().get_article_by_id(idu)
    return render_template('update.html',article=article)


@app.route('/modifier/<idu>', methods=['POST'])
def update_article(idu):
    titre = request.form['titre']
    paragraphe = request.form['paragraphe']

    if 0 > len(titre.strip(' ')) or len(titre.strip(' ')) > 100:
        return render_template('error.html',erreur='le titre malformatée'),400
    if 0 > len(paragraphe.strip(' ')) or len(paragraphe.strip(' ')) > 500:
        return render_template('error.html',erreur='le paragraphe malformatée'),400
    get_db().update_article(titre, paragraphe, idu)
    return redirect('ajoute')



@app.route('/admin-nouveau')
def add_new_article():
    return render_template('formulaire.html')


@app.route('/inserer', methods=['POST'])
def inserer_nouveau_article():
    titre = request.form['titre']
    identifiant = request.form['identifiant']
    auteur = request.form['auteur']
    date_publication = request.form['date_publication']
    paragraphe = request.form['paragraphe']
    erreur = validation_parametres(request)
    if len(erreur) != 0:
        return render_template('formulaire.html', erreur=erreur)
    get_db().insert_article(titre, identifiant, auteur,
                                     date_publication, paragraphe)
    return redirect('ajoute')


def validation_parametres(request):
    erreur = {}
    if 0 > len(request.form['titre'].strip(' ')) or \
       len(request.form['titre'].strip(' ')) > 100:
        erreur['titre'] = "le titre est malformatee"
    if 0 > len(request.form['identifiant'].strip(' ')) or \
       len(request.form['identifiant'].strip(' ')) > 50:
        erreur['identifiant'] = "l\' identifiant est malformatee"
    if 0 > len(request.form['auteur'].strip(' ')) or \
       len(request.form['auteur'].strip(' ')) > 100:
        erreur['auteur'] = "l\' auteur est malformatee"
    if 0 > len(request.form['paragraphe'].strip(' ')) or \
       len(request.form['paragraphe'].strip(' ')) > 500:
        erreur['paragraphe'] = "le paragraphe est malformatee"
    return erreur


if __name__ == '__main__':
    app.run(debug=True)
