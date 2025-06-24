# BookScape-Explorer_

![image](https://github.com/user-attachments/assets/c3b87e70-9486-4ed6-8bbe-2a463b9eb363)


# 📚 BookScape Explorer

BookScape Explorer is a powerful data analytics app built with **Streamlit**, integrated with the **Google Books API**, and connected to a **MySQL database**. It allows users to search for books by keyword, fetch up to **1000 book records**, insert them into a MySQL table, preview book posters, and download the dataset as a CSV.

---

## 🚀 Features

- 🔍 Search books from Google Books API by keyword.
- 📦 Fetch up to **1000 results** per query with pagination.
- 🧹 Clean and parse JSON responses into structured fields.
- 🗃️ Insert data into **MySQL** (`sql_query.api` table).
- 🖼️ Preview book posters and metadata.
- 📥 Download data as CSV directly from the app.
- 🎈 Celebratory animations after successful insertion.

---

## 🛠️ Tech Stack

| Tool         | Purpose                           |
|--------------|------------------------------------|
| Python       | Core scripting                    |
| Streamlit    | Web interface                     |
| Google Books API | Book data source              |
| MySQL        | Data storage (Relational DB)      |
| Pandas       | Data formatting and CSV export    |
| Requests     | API calls                         |

---

## 📂 Project Structure

📁 BookScapeExplorer/
│
├── bookscape_app.py # Main Streamlit app
├── README.md # Project readme
├── requirements.txt # Python dependencies
└── 📁 data/ # (Optional) for exports

1. Save this content as `README.md` in your project folder.
2. Add a `requirements.txt` with:
   ```txt
   streamlit
   requests
   mysql-connector-python
   pandas

🙋‍♀️ Author
Humaira Fathima N
📫 humaira2004super@gmail.com

git clone https://github.com/your-username/bookscape-explorer.git
cd bookscape-explorer

python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
