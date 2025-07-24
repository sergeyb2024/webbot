import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)

# IMPORTANT: In a production environment on Heroku, you would configure CORS
# to only allow requests from your Vercel front-end domain.
# Example: CORS(app, resources={r"/api/*": {"origins": "https://your-vercel-app.vercel.app"}})
CORS(app)

DATABASE_NAME = 'f1_news.db'

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    return conn

@app.route('/api/search', methods=)
def search_articles():
    """
    API endpoint to search for articles in the database.
    It takes a 'keyword' query parameter.
    """
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"error": "Keyword parameter is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # The API performs a fast search on the pre-populated database.
    # This is much faster than scraping on-demand.
    query = "SELECT * FROM articles WHERE headline LIKE? OR summary LIKE? ORDER BY id DESC LIMIT 50"
    search_term = f'%{keyword}%'
    
    try:
        cursor.execute(query, (search_term, search_term))
        articles_raw = cursor.fetchall()
    except sqlite3.OperationalError as e:
        # This can happen if the scraper hasn't run yet and the table doesn't exist.
        print(f"Database error: {e}")
        return jsonify()

    conn.close()

    # Convert list of Row objects to list of dictionaries
    articles = [dict(row) for row in articles_raw]

    return jsonify(articles)

@app.route('/')
def index():
    return "F1 News Aggregator API is running. Use the /api/search endpoint."

if __name__ == '__main__':
    # Note: For production, this app is run by a Gunicorn server (see Procfile).
    app.run(debug=True)