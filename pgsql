
---

## 🗄️ Database Schema

**Database**: `sql_query`  
**Table**: `api`

```sql
CREATE TABLE api (
  book_id VARCHAR(255) PRIMARY KEY,
  search_key VARCHAR(255),
  book_title VARCHAR(255),
  book_subtitle TEXT,
  book_authors TEXT,
  book_description TEXT,
  industryIdentifiers TEXT,
  text_readingModes BOOLEAN,
  image_readingModes BOOLEAN,
  pageCount INT,
  categories TEXT,
  language VARCHAR(50),
  imageLinks TEXT,
  ratingsCount INT,
  averageRating DECIMAL(3,2),
  country VARCHAR(10),
  saleability VARCHAR(50),
  isEbook BOOLEAN,
  amount_listPrice DECIMAL(10,2),
  currencyCode_listPrice VARCHAR(10),
  amount_retailPrice DECIMAL(10,2),
  currencyCode_retailPrice VARCHAR(10),
  buyLink TEXT,
  year TEXT
);
DESC api;

SELECT isEbook, COUNT(*) as count FROM api GROUP BY isEbook;

SELECT book_authors, COUNT(*) as count FROM api GROUP BY book_authors ORDER BY count DESC LIMIT 1;

SELECT book_authors, AVG(averageRating) as avg_rating FROM api GROUP BY book_authors ORDER BY avg_rating DESC LIMIT 1;

SELECT book_title, amount_retailPrice FROM api ORDER BY amount_retailPrice DESC LIMIT 5;

SELECT book_title, pageCount, year FROM api WHERE year > '2010' AND pageCount >= 500;

SELECT book_title, amount_listPrice, amount_retailPrice FROM api WHERE amount_listPrice IS NOT NULL AND amount_listPrice > 0 AND ((amount_listPrice - amount_retailPrice)/amount_listPrice) > 0.2;

SELECT isEbook, AVG(pageCount) FROM api GROUP BY isEbook;

SELECT book_authors, COUNT(*) as count FROM api GROUP BY book_authors ORDER BY count DESC LIMIT 3;

SELECT book_authors, COUNT(*) as count FROM api GROUP BY book_authors HAVING count > 10;

SELECT categories, AVG(pageCount) as avg_pages FROM api GROUP BY categories;

SELECT * FROM api WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3;

SELECT * FROM api WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM api);

SELECT book_authors, year, COUNT(*) FROM api GROUP BY book_authors, year HAVING COUNT(*) > 1;

SELECT * FROM api WHERE book_title LIKE '%magic%'; 

SELECT year, AVG(amount_retailPrice) as avg_price FROM api GROUP BY year ORDER BY avg_price DESC LIMIT 1;

WITH author_years AS (
    SELECT 
        TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(book_authors, ',', numbers.n), ',', -1)) AS author,
        CAST(year AS UNSIGNED) AS pub_year
    FROM api
    JOIN (
        SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
        UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8
        UNION ALL SELECT 9 UNION ALL SELECT 10
    ) numbers
    ON CHAR_LENGTH(book_authors) - CHAR_LENGTH(REPLACE(book_authors, ',', '')) + 1 >= numbers.n
    WHERE year REGEXP '^[0-9]{4}$'
),
author_years_distinct AS (
    SELECT DISTINCT author, pub_year FROM author_years
),
with_lag AS (
    SELECT *,
           LAG(pub_year, 1) OVER (PARTITION BY author ORDER BY pub_year) AS prev_year,
           LAG(pub_year, 2) OVER (PARTITION BY author ORDER BY pub_year) AS prev_prev_year
    FROM author_years_distinct
)
SELECT DISTINCT author
FROM with_lag
WHERE pub_year = prev_year + 1 AND prev_year = prev_prev_year + 1;

create table book_authors(author TEXT, year INT);

SELECT book_authors, year, COUNT(DISTINCT book_authors) as publisher_count FROM api GROUP BY book_authors, year HAVING publisher_count > 1;

SELECT 
    AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice END) as avg_ebook_price,
    AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice END) as avg_physical_price
FROM api;

SELECT book_title, averageRating, ratingsCount
FROM api
WHERE averageRating IS NOT NULL
AND averageRating > (SELECT AVG(averageRating) + 2 * STDDEV(averageRating) FROM api)
   OR averageRating < (SELECT AVG(averageRating) - 2 * STDDEV(averageRating) FROM api);
   
SELECT book_title, averageRating, ratingsCount
FROM api
WHERE averageRating IS NOT NULL
AND averageRating > (SELECT AVG(averageRating) + 2 * STDDEV(averageRating) FROM api)
   OR averageRating < (SELECT AVG(averageRating) - 2 * STDDEV(averageRating) FROM api);
   
SELECT book_authors, AVG(averageRating) as avg_rating, COUNT(*) as total_books
FROM api
GROUP BY book_authors
HAVING COUNT(*) > 10
ORDER BY avg_rating DESC
LIMIT 1;

