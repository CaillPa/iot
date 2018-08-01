-- Script de creation de la base

-- Contient la trace de tous les badgages
CREATE TABLE IF NOT EXISTS log(
    id integer PRIMARY KEY,
    date TEXT NOT NULL,
    id_badge TEXT NOT NULL
);

-- Contient les ID des badges autorises
CREATE TABLE IF NOT EXISTS autorise(
    id integer PRIMARY KEY,
    id_badge TEXT NOT NULL
);

-- Contient la trace de tous les messages
CREATE TABLE IF NOT EXISTS messages(
    id integer PRIMARY KEY,
    date TEXT NOT NULL,
    message TEXT NOT NULL
);