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

    def get_lastest_articles(self):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute(" select * from article where "
                       "strftime('%Y-%m-%d','now') >= strftime"
                       "('%Y-%m-%d',date_publication) order by "
                       "date_publication DESC")
        article = cursor.fetchmany(5)
        return article


    def get_articles(self, titre):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        recherche = "%"+titre+"%"
        cursor.execute(("select * from article where titre like ? or "
                       "paragraphe like ? and strftime('%Y-%m-%d','now') >= strftime"
                       "('%Y-%m-%d',date_publication)"), (recherche,recherche,))
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
        cursor.execute("select * from article where id = ?",(idu,))
        return cursor.fetchone()


    def update_article(self, titre, paragraphe, idu):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        print titre, paragraphe ,idu
        cursor.execute("UPDATE article SET titre = ? , paragraphe = ? "
                    "WHERE id = ?",(titre, paragraphe, idu,))
        connexion.commit()
        return cursor.fetchone()


    def insert_article(self, titre, identifiant, auteur,
                       date_publication, paragraphe):
        connexion = self.get_connection()
        cursor = connexion.cursor()
        cursor.execute("insert into article(titre,identifiant,auteur,"
                       "date_publication,paragraphe) values(?, ?, ?, ?, ?)",
                       (titre, identifiant, auteur, date_publication, paragraphe))
        connexion.commit()

