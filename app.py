import streamlit as st
import requests
import mysql.connector
import pandas as pd
import time

# ------------------ CONFIG ------------------ #
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',         
    'database': 'sql_query'      
}

# ------------------ FETCH BOOKS ------------------ #
def fetch_books(search_term, max_results=1000):
    all_books = []
    start_index = 0
    max_per_request = 40

    while start_index < max_results:
        url = f"https://www.googleapis.com/books/v1/volumes?q={search_term}&startIndex={start_index}&maxResults={max_per_request}"
        response = requests.get(url)
        if response.status_code != 200:
            break
        data = response.json()
        items = data.get("items", [])
        all_books.extend(items)
        if len(items) < max_per_request:
            break
        start_index += max_per_request
        time.sleep(1)
    return all_books

# ------------------ PARSE BOOK ------------------ #
def parse_book(item, search_key):
    volume_info = item.get("volumeInfo", {})
    sale_info = item.get("saleInfo", {})

    return {
        'book_id': item.get("id"),
        'search_key': search_key,
        'book_title': volume_info.get("title"),
        'book_subtitle': volume_info.get("subtitle"),
        'book_authors': ", ".join(volume_info.get("authors", [])),
        'book_description': volume_info.get("description"),
        'industryIdentifiers': str(volume_info.get("industryIdentifiers")),
        'text_readingModes': volume_info.get("readingModes", {}).get("text"),
        'image_readingModes': volume_info.get("readingModes", {}).get("image"),
        'pageCount': volume_info.get("pageCount"),
        'categories': ", ".join(volume_info.get("categories", [])),
        'language': volume_info.get("language"),
        'imageLinks': volume_info.get("imageLinks", {}).get("thumbnail"),
        'ratingsCount': volume_info.get("ratingsCount"),
        'averageRating': volume_info.get("averageRating"),
        'country': sale_info.get("country"),
        'saleability': sale_info.get("saleability"),
        'isEbook': sale_info.get("isEbook"),
        'amount_listPrice': sale_info.get("listPrice", {}).get("amount"),
        'currencyCode_listPrice': sale_info.get("listPrice", {}).get("currencyCode"),
        'amount_retailPrice': sale_info.get("retailPrice", {}).get("amount"),
        'currencyCode_retailPrice': sale_info.get("retailPrice", {}).get("currencyCode"),
        'buyLink': sale_info.get("buyLink"),
        'year': volume_info.get("publishedDate", "")[:4]
    }

# ------------------ INSERT INTO MYSQL ------------------ #
def insert_into_mysql(data):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
    INSERT INTO api (
        book_id, search_key, book_title, book_subtitle, book_authors,
        book_description, industryIdentifiers, text_readingModes, image_readingModes,
        pageCount, categories, language, imageLinks, ratingsCount, averageRating,
        country, saleability, isEbook, amount_listPrice, currencyCode_listPrice,
        amount_retailPrice, currencyCode_retailPrice, buyLink, year
    ) VALUES (
        %(book_id)s, %(search_key)s, %(book_title)s, %(book_subtitle)s, %(book_authors)s,
        %(book_description)s, %(industryIdentifiers)s, %(text_readingModes)s, %(image_readingModes)s,
        %(pageCount)s, %(categories)s, %(language)s, %(imageLinks)s, %(ratingsCount)s, %(averageRating)s,
        %(country)s, %(saleability)s, %(isEbook)s, %(amount_listPrice)s, %(currencyCode_listPrice)s,
        %(amount_retailPrice)s, %(currencyCode_retailPrice)s, %(buyLink)s, %(year)s
    ) ON DUPLICATE KEY UPDATE book_title=VALUES(book_title);
    """

    inserted = 0
    for book in data:
        try:
            cursor.execute(query, book)
            inserted += 1
        except Exception as e:
            st.warning(f"⚠️ Book skipped: {book.get('book_title')} — {e}")

    conn.commit()
    cursor.close()
    conn.close()
    return inserted

# ------------------ STREAMLIT APP ------------------ #
st.set_page_config(page_title="BookScape Explorer", layout="centered", page_icon="📖")
st.title("📚 BookScape Explorer")
st.subheader("🔍 Fetch and Save Books from Google Books API to MySQL (Table: `api`)")

search_term = st.text_input("Enter a search term (e.g., 'data science', 'history', 'fantasy'):")

if st.button("🚀 Fetch and Insert 1000 Books", key="fetch_button"):
    if not search_term:
        st.error("Please enter a valid search term.")
    else:
        with st.spinner("Fetching books from Google Books API..."):
            raw_books = fetch_books(search_term)
            st.success(f"✅ {len(raw_books)} books fetched.")

        if len(raw_books) < 50:
            st.warning("⚠️ Only partial results received. Try a broader keyword.")

        with st.spinner("Processing and inserting into MySQL..."):
            parsed_books = [parse_book(book, search_term) for book in raw_books]
            count = insert_into_mysql(parsed_books)
            st.success(f"✅ {count} books inserted into MySQL table `api`.")

        # Convert to DataFrame
        df = pd.DataFrame(parsed_books)

        # Download as CSV
        st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="books.csv", mime='text/csv')

        # Show book posters
        st.subheader("📖 Book Preview")
        for book in parsed_books[:100]:  # Preview limit
            with st.container():
                cols = st.columns([1, 4])
                with cols[0]:
                    if book['imageLinks']:
                        st.image(book['imageLinks'], width=100)
                with cols[1]:
                    st.markdown(f"**Title:** {book['book_title']}")
                    st.markdown(f"**Author(s):** {book['book_authors']}")
                    st.markdown(f"**Year:** {book['year']}")
            st.balloons()

# ------------------ DATA ANALYSIS SECTION ------------------ #
# List of evaluation queries
query_options = {
    "1️⃣ Availability: eBooks vs Physical Books":
        "SELECT isEbook, COUNT(*) AS count FROM api GROUP BY isEbook",
        
    "2️⃣ Publisher with Most Books":
        "SELECT book_authors, COUNT(*) AS count FROM api GROUP BY book_authors ORDER BY count DESC LIMIT 1",
        
    "3️⃣ Publisher with Highest Average Rating":
        "SELECT book_authors, AVG(averageRating) AS avg_rating FROM api GROUP BY book_authors ORDER BY avg_rating DESC LIMIT 1",
        
    "4️⃣ Top 5 Most Expensive Books":
        "SELECT book_title, amount_retailPrice FROM api ORDER BY amount_retailPrice DESC LIMIT 5",
        
    "5️⃣ Books After 2010 with ≥500 Pages":
        "SELECT book_title, pageCount, year FROM api WHERE year > '2010' AND pageCount >= 500",
        
    "6️⃣ Books With Discounts > 20%":
        """
        SELECT book_title, amount_listPrice, amount_retailPrice 
        FROM api 
        WHERE amount_listPrice > 0 
          AND ((amount_listPrice - amount_retailPrice) / amount_listPrice) > 0.2
        """,
        
    "7️⃣ Avg Page Count: eBooks vs Physical":
        "SELECT isEbook, AVG(pageCount) AS avg_pages FROM api GROUP BY isEbook",
        
    "8️⃣ Top 3 Authors by Book Count":
        "SELECT book_authors, COUNT(*) AS count FROM api GROUP BY book_authors ORDER BY count DESC LIMIT 3",
        
    "9️⃣ Publishers with >10 Books":
        "SELECT book_authors, COUNT(*) AS count FROM api GROUP BY book_authors HAVING count > 10",
        
    "🔟 Avg Page Count per Category":
        "SELECT categories, AVG(pageCount) AS avg_pages FROM api GROUP BY categories",
        
    "1️⃣1️⃣ Books with >3 Authors":
        "SELECT * FROM api WHERE LENGTH(book_authors) - LENGTH(REPLACE(book_authors, ',', '')) + 1 > 3",
        
    "1️⃣2️⃣ Books with Ratings > Average":
        "SELECT * FROM api WHERE ratingsCount > (SELECT AVG(ratingsCount) FROM api)",
        
    "1️⃣3️⃣ Same Author & Year (Multiple Books)":
        "SELECT book_authors, year, COUNT(*) FROM api GROUP BY book_authors, year HAVING COUNT(*) > 1",
        
    "1️⃣4️⃣ Books with Keyword 'magic' in Title":
        "SELECT * FROM api WHERE book_title LIKE '%magic%'",
        
    "1️⃣5️⃣ Year with Highest Avg Book Price":
        "SELECT year, AVG(amount_retailPrice) AS avg_price FROM api GROUP BY year ORDER BY avg_price DESC LIMIT 1",
        
    "1️⃣6️⃣ Authors Published 3 Consecutive Years (Logic Needed)":  # placeholder
        "SELECT 'Needs window function or Python logic' AS note",
        
    "1️⃣7️⃣ Same Author, Same Year, Different Publisher (Approximate)":
        "SELECT book_authors, year, COUNT(*) FROM api GROUP BY book_authors, year HAVING COUNT(*) > 1",
        
    "1️⃣8️⃣ Avg Retail Price: eBooks vs Physical":
        """
        SELECT 
            AVG(CASE WHEN isEbook = 1 THEN amount_retailPrice END) AS avg_ebook_price,
            AVG(CASE WHEN isEbook = 0 THEN amount_retailPrice END) AS avg_physical_price
        FROM api
        """,
        
    "1️⃣9️⃣ Rating Outliers (2 SD Away)":
        """
        SELECT book_title, averageRating, ratingsCount
        FROM api
        WHERE averageRating > (SELECT AVG(averageRating) + 2 * STDDEV(averageRating) FROM api)
           OR averageRating < (SELECT AVG(averageRating) - 2 * STDDEV(averageRating) FROM api)
        """,
        
    "2️⃣0️⃣ Top Publisher by Avg Rating (Min 10 Books)":
        """
        SELECT book_authors, AVG(averageRating) AS avg_rating, COUNT(*) AS books
        FROM api
        GROUP BY book_authors
        HAVING COUNT(*) > 10
        ORDER BY avg_rating DESC
        LIMIT 1
        """
}
st.sidebar.markdown("### 🧠 Evaluation Metrics")
selected_query_label = st.sidebar.selectbox("Choose a SQL Query:", list(query_options.keys()))
run_query = st.sidebar.button("▶️ Run Query")


# ------------------ MAIN AREA RESULT ------------------ #
if run_query:  # ✅ only trigger if sidebar button is clicked
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(query_options[selected_query_label])
        result = cursor.fetchall()
        colnames = [i[0] for i in cursor.description]
        df_query = pd.DataFrame(result, columns=colnames)
        st.subheader("📊 Query Result")
        st.dataframe(df_query)
    except Exception as e:
        st.error(f"❌ Error running query: {e}")
    finally:
        cursor.close()
        conn.close()
