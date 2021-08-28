import urllib.request
import re
from string import ascii_uppercase
import sqlite3

if __name__ == '__main__':
    hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
    url = 'https://www.advfn.com/nyse/newyorkstockexchange.asp?companies='

    conn = sqlite3.connect("companies.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE stocks
                      (id              INTEGER PRIMARY KEY,
                       ticker_name     text NOT NULL UNIQUE,
                       unit_price      INTEGER,
                       purchased_date  text,
                       sold_date       text,
                       quantity_bought INTEGER,
                       quantity_sold   INTEGER
                       );''')

    cursor.execute('''CREATE TABLE companies
                      (id             INTEGER PRIMARY KEY,
                       company_name   text NOT NULL,
                       ticker_name    text NOT NULL UNIQUE
                       );''')

    cursor.execute('''CREATE TABLE companies_stocks (
                         company_id INTEGER,
                         stock_id   INTEGER,
                         FOREIGN KEY(company_id) REFERENCES companies(id),
                         FOREIGN KEY(stock_id)   REFERENCES stocks(id)
                    );''')

    companies = {}
    for letter in ascii_uppercase:
        new_url  = url + letter
        req      = urllib.request.Request(new_url, headers=hdr)
        response = urllib.request.urlopen(req)
        html     = ''.join(response.read().decode('utf-8'))
        pattern  = r'<tr class="ts[0-1]">\s*<td align="left">\s*<a href="[^\"]+">([^<]+)</a>\s*</td>\s*<td>\s*<a href="[^\"]+">([^\<]+)'
        matches  = re.findall(pattern, html)
        for name, ticker in matches:
            print('%s: %s'%(ticker.ljust(10, ' '), name))
            cursor.execute('''INSERT INTO companies (ticker_name, company_name)
                              VALUES( "%s", "%s" );''' % (ticker, name))

    conn.commit()

    conn.close()
