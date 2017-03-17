create table article (
  id integer primary key,
  titre varchar(100),
  identifiant varchar(50),
  auteur varchar(100),
  date_publication text,
  paragraphe varchar(500)
);

insert into article values (1,'journal','ASSFDGFGGHMH','SADASFDGHM',"2009-10-17",'trop de cul');
insert into article values (2,'victoire','ligue des champions','KK_MM',"2017-03-11",'barca a gagne son match');
insert into article values (3,'gloire','web de 2','FF_MM',"2017-04-11",'bon');
insert into article values (4,'televise','journal','SADASFDGHM',"2004-10-17",'Jaime les codes');