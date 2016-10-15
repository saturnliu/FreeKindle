#!/usr/bin/env python3

import json
import os.path

import sqlite3

from book import Book
from status import Status

data_dir = 'data'

books_cn = []
books_en = []
ids = set()

nodes = []

reviews = []


def load_book(file):
    if os.path.isfile(file):
        with open(file) as json_data:
            d = json.load(json_data)
            for b in d['books']:
                book = Book(b)
                if book.item_id in ids:
                    print('added: ' + book.item_id)
                    continue
                if book.languages and len(book.languages) > 0:
                    if book.languages[0] == 'chinese' or book.languages[0] == 'traditional_chinese':
                        books_cn.append(book.dict())
                    else:
                        books_en.append(book.dict())
                    ids.add(book.item_id)
                    reviews.append((book.item_id, book.editorial_review))
                else:
                    print('no language')
                    print(book.json())


if not os.path.exists(data_dir):
    os.mkdir(data_dir)


# read data to list

for i in range(1, 401):
    f_cn = 'page/kindle_free_books_cn_' + str(i) + '.json'
    f_en = 'page/kindle_free_books_en_' + str(i) + '.json'
    load_book(f_cn)
    load_book(f_en)

# save to database

status = Status()

status.new_count = len(books_cn) + len(books_en) - status.count

status.count = len(books_cn) + len(books_en)
status.bump()

conn = sqlite3.connect('data/books_' + str(status.version) + '.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS book_cn (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    score REAL,
    url TEXT,
    item_id TEXT,
    pages TEXT,
    publisher TEXT,
    brand TEXT,
    asin TEXT,
    edition TEXT,
    isbn TEXT,
    large_image_url TEXT,
    medium_image_url TEXT,
    small_image_url TEXT,
    region TEXT,
    release_date TEXT,
    publication_date TEXT,
    languages TEXT
    );''')

cur.executemany('''insert into book_cn (
    title,
    author,
    score,
    url,
    item_id,
    pages,
    publisher,
    brand,
    asin,
    edition,
    isbn,
    large_image_url,
    medium_image_url,
    small_image_url,
    region,
    release_date,
    publication_date,
    languages
    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', books_cn)

cur.execute('''CREATE TABLE IF NOT EXISTS book_en (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    score REAL,
    url TEXT,
    item_id TEXT,
    pages TEXT,
    publisher TEXT,
    brand TEXT,
    asin TEXT,
    edition TEXT,
    isbn TEXT,
    large_image_url TEXT,
    medium_image_url TEXT,
    small_image_url TEXT,
    region TEXT,
    release_date TEXT,
    publication_date TEXT,
    languages TEXT
    );''')

cur.executemany('''insert into book_en (
    title,
    author,
    score,
    url,
    item_id,
    pages,
    publisher,
    brand,
    asin,
    edition,
    isbn,
    large_image_url,
    medium_image_url,
    small_image_url,
    region,
    release_date,
    publication_date,
    languages
    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', books_en)

cur.execute('''CREATE TABLE IF NOT EXISTS status
    ( id INTEGER PRIMARY KEY AUTOINCREMENT, version INTEGER, count INTEGER, new_count INTEGER, time INTEGER );''')

cur.execute('insert into status (version, count, new_count, time) values (?, ?, ?, ?)', status.to_list())

conn.commit()
cur.close()
conn.close()

# save reviews to database

conn = sqlite3.connect('data/reviews_' + str(status.version) + '.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id TEXT,
    editorial_review TEXT
    );''')

cur.executemany('''insert into review (
    item_id,
    editorial_review
    ) values (?, ?)
    ''', reviews)

conn.commit()
cur.close()
conn.close()