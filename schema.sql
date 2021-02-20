create database sotd default character set 'utf8mb4';

use sotd;

-- MySQL
create table full_text (
    text_key int not null auto_increment
    , comment_id varchar(16) not null
    , full_text text
    , primary key (text_key)
)
;

create table submission (
    submission_id varchar(16) not null
    , title varchar(255) not null
    , permalink varchar(255) not null
    , created_time datetime -- local time
    , post_date date not null
    , primary key (submission_id)
)
;

-- Reddit IDs need 13 chars to store 64 bits...
-- 16 chars yields space for 82 bit unsigned integers (and then some).
create table comment (
    comment_id varchar(16) not null
    , created_time datetime not null -- local time
    , edited_time datetime -- local time
    , author_name varchar(255)
    , parent_id varchar(16)
    , score int
    , permalink varchar(1024) not null
    , submission_id varchar(16) not null
    , plaintext_key int
    , html_key int
    , primary key (comment_id)
    , foreign key (plaintext_key) references full_text(text_key)
    , foreign key (html_key) references full_text(text_key)
    , foreign key (submission_id) references submission(submission_id)
)
;

create table lather (
    lather_key int not null auto_increment
    , comment_id varchar(16) not null
    , maker varchar(255) not null
    , scent varchar(255)
    , confidence varchar(16) not null
    , manual_ind tinyint not null default 0
    , primary key (lather_key)
    , foreign key (comment_id) references comment(comment_id)
)
;
