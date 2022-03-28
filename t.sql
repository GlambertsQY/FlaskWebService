create database GraduationProject;
use GraduationProject;
create table Question
(
    id_q    int auto_increment primary key,
    text_q  text        not null,
    subject varchar(20) not null
)character set utf8 engine InnoDB;  -- 设置字符集，否则中文报错
create table StandardAnswer
(
    id_s   int auto_increment primary key,
    text_s text not null,
    id_q   int  not null,
    foreign key (id_q) references Question (id_q)
)character set utf8 engine InnoDB;
create table User
(
    username varchar(20) not null primary key,
    password varchar(20) not null,
    phone    varchar(20),
    mail     varchar(30)
)character set utf8 engine InnoDB;
drop table User;
drop table Question;
drop table StandardAnswer;
use graduationproject;
select *
from question;
select *
from StandardAnswer;
select *
from question,
     StandardAnswer
where question.id_q = StandardAnswer.id_q;
select *
from user;
delete
from question
where id_q >= 1;
delete
from StandardAnswer
where id_q >= 1;

update Question
set subject = '计算机综合'
where subject = '计算机';
update Question
set subject = '军事理论'
where id_q >= 82
  and id_q <= 169;
update Question
set subject = '地理'
where id_q >= 170;

create table Answer
(
    id_a   int  not null primary key,
    id_q   int  not null,
    text_a text not null,
    foreign key (id_q) references Question (id_q)
)character set utf8 engine InnoDB;

create table Score
(
    username varchar(20) not null,
    id_a     int         not null,
    time     varchar(20) not null,
    score    int         not null,
    primary key (username, id_a),
    foreign key (username) references User (username),
    foreign key (id_a) references Answer (id_a)
)character set utf8 engine InnoDB;
drop table Score;
drop table Answer;

select *
from Answer;
select *
from Score;
select *
from StandardAnswer;
