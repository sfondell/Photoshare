CREATE DATABASE photoshare;
USE photoshare;

CREATE TABLE Users (
    userid int4 AUTO_INCREMENT,
    gender varchar(10),
    bio varchar(255),
    fname varchar(20) NOT NULL,
    lname varchar(20) NOT NULL,
    email varchar(255) NOT NULL UNIQUE,
    dob DATE NOT NULL,
    password varchar(20) NOT NULL,
    profpic BLOB,
    hometown varchar(20),
  PRIMARY KEY (userid)
);

CREATE TABLE Albums (
    albumid int4 AUTO_INCREMENT,
    userid int4 NOT NULL,
    creation DATE NOT NULL,
    name varchar(20) NOT NULL,
  PRIMARY KEY (albumid),
  FOREIGN KEY (userid) REFERENCES Users(userid)
);

CREATE TABLE Photos (
    photoid int4 AUTO_INCREMENT,
    albumid int4 NOT NULL,
    userid int4 NOT NULL,
    data LONGBLOB NOT NULL,
    caption varchar(255),
  PRIMARY KEY (photoid),
  FOREIGN KEY (albumid) 
    REFERENCES Albums(albumid)
    ON DELETE CASCADE,
  FOREIGN KEY (userid) REFERENCES Users(userid)
);

CREATE TABLE Tags (
    tag varchar(20) NOT NULL,
    photoid int4 NOT NULL,
  PRIMARY KEY (tag),
  FOREIGN KEY (photoid) REFERENCES Photos(photoid)
);

CREATE TABLE Comments (
    commentid int4 AUTO_INCREMENT,
    photoid int4 NOT NULL,
    albumid int4 NOT NULL,
    userid int4 NOT NULL,
    commenttext varchar(255) NOT NULL,
    posttime TIMESTAMP NOT NULL,
  PRIMARY KEY (commentid),
  FOREIGN KEY (photoid)
    REFERENCES Photos(photoid)
    ON DELETE CASCADE,
  FOREIGN KEY (albumid)
    REFERENCES Albums(albumid)
    ON DELETE CASCADE,
  FOREIGN KEY (userid) REFERENCES Users(userid)
);

CREATE TABLE Friendships (
    userid int4 NOT NULL,
    friendid int4 NOT NULL,
    PRIMARY KEY (userid, friendid),
    FOREIGN KEY (userid) REFERENCES Users(userid),
    FOREIGN KEY (friendid) REFERENCES Users(userid)
);

CREATE TABLE Likes (
  userid int4 NOT NULL,
  photoid int4 NOT NULL,
  PRIMARY KEY (userid, photoid),
  FOREIGN KEY (userid) REFERENCES Users(userid),
  FOREIGN KEY (photoid)
    REFERENCES Photos(photoid)
    ON DELETE CASCADE
);