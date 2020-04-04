create database pythonstudy;
use pythonstudy;
create table user(
    id int auto_increment primary key ,
    user_name varchar(80) not null unique ,
    email varchar(120) not null unique
    );
drop table user;

create database GraduationProject;
use graduationproject;
create table question(
    id_q int auto_increment primary key ,
    text_q text not null ,
    subject varchar(20) not null
);
create table StandardAnswer(
    id_s int auto_increment primary key ,
    text_s text not null ,
    id_q int not null ,
    foreign key (id_q) references question(id_q)
);
create table User(
    username varchar(20) not null primary key ,
    password varchar(20) not null ,
    phone varchar(20),
    mail varchar(30)
);
drop table user;
drop table question;
drop table StandardAnswer;
use graduationproject;
select * from question;
select * from StandardAnswer;
select * from question,StandardAnswer where question.id_q= StandardAnswer.id_q;
select * from user;
delete  from question where id_q>=1;
delete from StandardAnswer where id_q>=1;

update question set subject = '计算机综合' where subject = '计算机';
update question set subject = '军事理论' where id_q>=30 and id_q<=92;
update question set subject = '地理' where id_q>=93;

