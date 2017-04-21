# coding: utf8

from flask import Flask
from flask import render_template
from flask import g
from flask import request
from flask import redirect
from flask import session
from flask import Response
from database import Database
from flask import jsonify
import hashlib
from functools import wraps
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import uuid
import sqlite3
from operator import concat

app = Flask(__name__)
app = Flask(__name__, static_url_path="", static_folder="static")
source_address = ""
password = ""
destination_address = ""


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
    data = get_db().get_lastest_articles(0)
    return render_template('index.html', articles=data)


@app.route('/recherche', methods=['POST'])
def get_article_find():
    recherche = request.form['recherche']
    articles = get_db().get_articles(recherche)
    if len(articles) == 0:
        return render_template('error.html', erreur='l\'article '
                                                    'inexistant'), 400
    else:
        return render_template('articles.html', articles=articles)


@app.route('/invitation/<jeton>')
def verifie_jeton(jeton):
    data = get_db().get_jeton(jeton)
    if (data is None):
        return render_template("error.html",
                               erreur="vous n\'etes pas autorise"
                                      " a creer un compte"), 400
    else:
        return render_template("creerCompte.html"), 200


@app.route('/creerCompte', methods=['POST'])
def creerCompte():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    if username == "" or password == "" or email == "":
        erreur = "nom ou le mot de passe ou l\'email est vide"
        return render_template("error.html", erreur=erreur), 400
    else:
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        get_db().create_user(username, email, salt, hashed_password)
        id_session = uuid.uuid4().hex
        get_db().save_session(id_session, username)
        session["id"] = id_session
        return render_template("ajoute.html")


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


@app.route('/article/<identifiant>', methods=["POST"])
@authentication_required
def get_article(identifiant):
    article = get_db().get_article(identifiant)
    if article is None:
        return render_template('error.html',
                               erreur='l\'article inexistant '), 400
    else:
        return render_template('article.html', article=article)


@app.route('/loginformulaire', methods=["GET"])
def loginformulaire():
    return render_template('connexion.html')


@app.route('/login', methods=["POST"])
def log_user():

    username = request.form["username"]
    password = request.form["password"]
    print username + " == " + password
    if username == "" or password == "":
        erreur = "username ou password  vide"
        return render_template("connexion.html", erreur=erreur), 400
    user = get_db().get_user_login_info(username)
    if user is None:
        erreur = "utilisateur inexistant"
        return render_template("connexion.html", erreur=erreur), 400
    salt = user[0]
    hashed_password = hashlib.sha512(password + salt).hexdigest()
    if hashed_password == user[1]:
        id_session = uuid.uuid4().hex
        get_db().save_session(id_session, username)
        session["id"] = id_session
        return redirect("/admin")
    else:
        erreur = "mot de passe incorrect"
        return render_template("connexion.html", erreur=erreur), 400


@app.route('/logout')
@authentication_required
def logout():
    if "id" in session:
        id_session = session["id"]
        session.pop('id', None)
        get_db().delete_session(id_session)
    return redirect("/")


def is_authenticated(session):
    return "id" in session


def send_unauthorized():
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


@app.route('/admin')
@authentication_required
def administrator():
    articles = get_db().get_all_articles()
    if articles is None:
        return render_template("error.html", erreur="base est vide")
    else:
        return render_template("articles.html", articles=articles), 200


@app.route('/modifier/<idu>')
@authentication_required
def get_articles_for_update(idu):
    if request.method == "GET":
        article = get_db().get_article_by_id(idu)
        return render_template('update.html', article=article)
    elif request.method == "POST":
        titre = request.form['titre']
        paragraphe = request.form['paragraphe']
        if 0 > len(titre.strip(' ')) or len(titre.strip(' ')) > 100:
            return render_template("error.html",
                                   erreur="le titre malformatée"), 400
        if 0 > len(paragraphe.strip(' ')) or len(paragraphe.strip(' ')) > 500:
            return render_template("erreur.html",
                                   erreur="le paragraphe malformatée"), 400
        get_db().update_article(titre, paragraphe, idu)
        return render_template("ajout.html"), 200


@app.route('/admin-nouveau')
@authentication_required
def add_new_article():
    return render_template('formulaire.html')


@app.route('/inserer', methods=['POST'])
@authentication_required
def inserer_nouveau_article():
    data = request.get_json()
    titre = data['titre']
    identifiant = data['identifiant']
    auteur = data['auteur']
    date_publication = data['date_publication']
    paragraphe = data['paragraphe']
    erreur = validation_parametres(titre, identifiant, auteur, paragraphe)
    if len(erreur) != 0:
        return jsonify({"erreur": erreur}), 400
    get_db().insert_article(titre, identifiant, auteur,
                            date_publication, paragraphe)
    return jsonify({"message": "l\'article bien ajoutee "}), 201


@app.route('/identifiant', methods=['POST'])
def identifiant_unique():
    data = request.get_json()
    title = data["title"]
    identifiant = former_identifiant(title)
    return identifiant, 200


@app.route('/identifiant/verification', methods=['POST'])
def verification_existence_identifiant():
    identifiant = request.get_json()["identifiant"]
    data = get_db().get_same_identifiant(identifiant)
    for row in data:
        if identifiant == row:
            return "OK", 200
    return "identifiant existe deja", 400


@app.route('/api/inserer', methods=['POST'])
def api_creer_nouveau_article():
    data = request.get_json()
    username = data['username']
    password = data['password']
    if username == "" or password == "":
        erreur = "username ou password  vide"
        return jsonify({"erreur": erreur}), 400
    user = get_db().get_user_login_info(username)
    if user is None:
        erreur = "utilisateur inexistant"
        return jsonify({"erreur": erreur}), 407
    salt = user[0]
    hashed_password = hashlib.sha512(password + salt).hexdigest()
    if hashed_password != user[1]:
        erreur = "mot de passe incorrect"
        return jsonify({"erreur": erreur}), 407
    titre = data['titre']
    identifiant = former_identifiant(titre)
    auteur = data['auteur']
    date_publication = data['date_publication']
    paragraphe = data['paragraphe']
    erreur = validation_parametres(titre, identifiant, auteur, paragraphe)
    if len(erreur) != 0:
        return jsonify({"erreur": erreur}), 400
    get_db().insert_article(titre, identifiant, auteur,
                            date_publication, paragraphe)
    return jsonify({"message": "l\'article bien ajoutee "}), 201


@app.route('/api/listeArticlePublie', methods=['GET'])
def api_lister_article_publie():
    articles = get_db().get_lastest_articles(1)
    if articles is None:
        return jsonify({"erreur": "Aucun article publie"}), 204
    return jsonify(articles), 200


@app.route('/api/article', methods=['POST'])
def information_article():
    data = request.get_json()
    nom = data["identifiant"]
    article = get_db().get_article(nom)
    if article is None:
        return jsonify({"erreur": "article inexistant"}), 404
    idu, titre, identifiant, auteur, date_publication, paragraphe = article
    return jsonify({"titre": titre,
                    "identifiant": identifiant,
                    "auteur": auteur,
                    "date_publication": date_publication,
                    "paragraphe": paragraphe}), 200


@app.route('/reinitialisation/motdepasse')
def reinitialisation():
    initialisation()
    envoi_mail()
    return redirect('/verifiermail')


@app.route('/verifiermail')
def verifier_mail():
    return render_template("verifiermail.html")


def validation_parametres(titre, identifiant, auteur, paragraphe):
    erreur = {}
    if 0 > len(titre.strip(' ')) or \
       len(titre.strip(' ')) > 100:
        erreur['titre'] = "le titre est malformatee"
    if 0 > len(identifiant.strip(' ')) or \
       len(identifiant.strip(' ')) > 50:
        erreur['identifiant'] = "l\' identifiant est malformatee"
    if 0 > len(auteur.strip(' ')) or \
       len(auteur.strip(' ')) > 100:
        erreur['auteur'] = "l\' auteur est malformatee"
    if 0 > len(paragraphe.strip(' ')) or \
            len(paragraphe.strip(' ')) > 500:
        erreur['paragraphe'] = "le paragraphe est malformatee"
    return erreur


def envoi_mail():
    global source_address
    global password
    global destination_address
    print "source =" + source_address + " mot " + password
    jeton = uuid.uuid4().hex
    body = "http://localhost:5000/invitation/"+jeton
    subject = "Invitation pour creer un compte administrateur"
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = source_address
    msg['To'] = destination_address
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(source_address, password)
    text = msg.as_string()
    server.sendmail(source_address, destination_address, text)
    server.quit()
    get_db().save_jeton(jeton, destination_address)
    connection = sqlite3.connect('db/db.db')
    connection.execute("insert into compte(mail,jeton,dateEnvoie)"
                       " values(?,?,strftime('%Y-%m-%d', 'now'))",
                       (destination_address, jeton,))
    connection.commit()


def initialisation():
    global source_address
    global password
    global destination_address
    config_file = open("conf.txt")
    line = config_file.readline()
    data = line.split(":")
    source_address = data[1]
    line = config_file.readline()
    data = line.split(":")
    password = data[1]
    line = config_file.readline()
    data = line.split(":")
    destination_address = data[1]
    config_file.close()


def former_identifiant(titre):
    identifiant = ""
    title = titre.strip()
    for i in range(0, len(title)):
        if title[i].isalpha() or title[i].isspace():
            if title[i].isspace():
                identifiant = identifiant + "_"
            else:
                identifiant = identifiant + title[i]
    identifiant = identifiant.lower()
    data = get_db().get_same_identifiant(identifiant)
    element = "0"
    if len(data) != 0:
        element = data[len(data)-1]
    if element.isdigit() and element is not "0":
        identifiant = identifiant + int(element) + 1
    return identifiant


app.secret_key = "(*&*&322387he738220)(*(*22347657"

if __name__ == '__main__':
    app.run()
