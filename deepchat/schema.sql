DROP TABLE IF EXISTS chats;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS users;

CREATE TABLE "chats" (
	"id"	TEXT UNIQUE,
	"userId"	TEXT,
	PRIMARY KEY("id")
);

CREATE TABLE "messages" (
	"id"	INTEGER UNIQUE,
	"message"	TEXT,
	"chatId"	TEXT,
	"fromUser"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "users" (
	"id"	TEXT UNIQUE,
	"username"	TEXT UNIQUE,
	"password"	TEXT,
	PRIMARY KEY("id")
);