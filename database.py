# coding: utf8

# Copyright 2017 Jacques Berger
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sqlite3
from operator import concat


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/db.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    def get_lastest_articles(self, choix):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute(" select * from article where "
                       "strftime('%Y-%m-%d','now') >= strftime"
                       "('%Y-%m-%d',date_publication) order by "
                       "date_publication DESC")
        if choix == 1:
            return self.fomater_donne(cursor.fetchall())
        else:
            return cursor.fetchmany(5)

    def get_articles(self, titre):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        recherche = "%"+titre+"%"
        cursor.execute(("select * from article where titre like ? or "
                        "paragraphe like ? and "
                        "strftime('%Y-%m-%d','now') >= strftime"
                        "('%Y-%m-%d', date_publication)"), (recherche,
                                                            recherche,))
        return cursor.fetchall()

    def get_all_articles(self):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute('select * from article')
        return cursor.fetchall()

    def get_article(self, identifiant):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("select * from article where identifiant = ?",
                       (identifiant,))
        return cursor.fetchone()

    def get_article_by_id(self, idu):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("select * from article where id = ?", (idu,))
        return cursor.fetchone()

    def update_article(self, titre, paragraphe, idu):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("UPDATE article SET titre = ? , paragraphe = ? "
                       "WHERE id = ?", (titre, paragraphe, idu,))
        connexion.commit()
        return cursor.fetchone()

    def insert_article(self, titre, identifiant, auteur,
                       date_publication, paragraphe):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("insert into article(titre,identifiant,auteur,"
                       "date_publication,paragraphe) values(?, ?, ?, ?, ?)",
                       (titre, identifiant, auteur, date_publication,
                        paragraphe))
        connexion.commit()

    def create_user(self, username, email, salt, hashed_password):
        connection = self.get_connection()
        connection.execute(("insert into users(utilisateur, email, salt, hash)"
                            " values(?, ?, ?, ?)"), (username, email, salt,
                                                     hashed_password))
        connection.commit()

    def get_user_login_info(self, username):
        cursor = self.get_connection().cursor()
        cursor.execute(("select salt, hash from users where utilisateur=?"),
                       (username,))
        user = cursor.fetchone()
        if user is None:
            return None
        else:
            return user[0], user[1]

    def save_session(self, id_session, username):
        connection = self.get_connection()
        connection.execute(("insert into sessions(id_session, utilisateur) "
                            "values(?, ?)"), (id_session, username))
        connection.commit()

    def delete_session(self, id_session):
        connection = self.get_connection()
        connection.execute(("delete from sessions where id_session=?"),
                           (id_session,))
        connection.commit()

    def get_session(self, id_session):
        cursor = self.get_connection().cursor()
        cursor.execute(("select utilisateur from sessions where id_session=?"),
                       (id_session,))
        data = cursor.fetchone()
        if data is None:
            return None
        else:
            return data[0]

    def save_jeton(self, jeton, mail):
        connection = self.get_connection()
        connection.execute(("insert into compte(mail, jeton)"
                            "values(?,?)"), (mail, jeton))
        connection.commit()

    def get_jeton(self, jeton):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(("select mail from compte where jeton=?"),
                       (jeton,))
        data = cursor.fetchone()
        print data
        if data is None:
            return None
        else:
            print "ok"
            cursor.execute(("delete from compte where jeton=?"), (jeton,))
            connection.commit()
            return data[0]

    def get_same_identifiant(self, identifiant):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        recherche = "%" + identifiant + "%"
        cursor.execute(("select * from article where identifiant like ?"),
                       (recherche,))
        return cursor.fetchall()

    def fomater_donne(self, article):
        listeArticle = []
        for row in article:
            listeArticle.append(self.construire(row))
        return listeArticle

    def save_jeton(self, destination_address, jeton):
        connection = self.get_connection()
        connection.execute("insert into compte(mail,jeton,dateEnvoie) "
                           "values(?, ?, strftime('%Y-%m-%d','now'))",
                           (destination_address, jeton,))
        connection.commit()

    def content_user(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute('select * from users')
        return cursor.fetchall()

    def construire(self, row):
        return {"id": row[0], "titre": row[1], "identifiant": row[2],
                "auteur": row[3], "date_publication": row[4],
                "paragraphe": row[5]}


