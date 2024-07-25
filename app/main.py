from datetime import datetime

from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

# Establish a database connection using credentials from the environment variable
def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except psycopg2.DatabaseError as e:
        app.logger.error(f"Database connection failed: {e}")
        raise

# Validate date strings are in the format YYYY-MM-DD
def validate_date(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        return False

@app.route('/rates', methods=['GET'])
def get_rates():
    # Extract parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    origin = request.args.get('origin')
    destination = request.args.get('destination')

    # Ensure all required parameters are present
    if not all([date_from, date_to, origin, destination]):
        return jsonify({"error": "Missing required parameters"}), 400
    
    # Validate date format
    if not validate_date(date_from) or not validate_date(date_to):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # SQL query to compute average prices per day between origin and destination
        query = """
            WITH RECURSIVE region_tree AS (
                SELECT slug FROM regions WHERE slug = %(destination)s
                UNION
                SELECT r.slug
                FROM regions r
                INNER JOIN region_tree rt ON r.parent_slug = rt.slug
            ),
            port_list AS (
                SELECT p.code
                FROM ports p
                WHERE p.parent_slug IN (SELECT slug FROM region_tree)
                UNION
                SELECT %(destination)s
            )
            SELECT day, AVG(price) as average_price
            FROM prices
            WHERE day >= %(date_from)s AND day <= %(date_to)s
            AND orig_code = %(origin)s
            AND dest_code IN (SELECT code FROM port_list)
            GROUP BY day
            HAVING COUNT(price) >= 3
            UNION
            SELECT day, AVG(price) as average_price
            FROM prices
            WHERE day >= %(date_from)s AND day <= %(date_to)s
            AND orig_code IN (SELECT code FROM port_list)
            AND dest_code = %(destination)s
            GROUP BY day
            HAVING COUNT(price) >= 3
            ORDER BY day;
        """

        parameters = {
            'date_from': date_from,
            'date_to': date_to,
            'origin': origin,
            'destination': destination
        }

        cur.execute(query, parameters)
        rows = cur.fetchall()

        # Convert query results into JSON-serializable format
        result = [{"day": row[0], "average_price": row[1]} for row in rows]

        cur.close()
        conn.close()

        return jsonify(result)
    except psycopg2.Error as e:
        app.logger.error(f"Query failed: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
