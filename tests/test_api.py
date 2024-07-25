import pytest
from app.main import app
from unittest.mock import patch
import psycopg2


# Fixture for creating a test client for the Flask app
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Test case for missing all required parameters
def test_missing_parameters(client):
    response = client.get('/rates')
    assert response.status_code == 400
    assert response.json == {"error": "Missing required parameters"}

# Test case for missing individual required parameters
def test_missing_individual_parameters(client):
    response = client.get('/rates?date_to=2024-01-10&origin=PORT1&destination=PORT2')
    assert response.status_code == 400
    assert response.json == {"error": "Missing required parameters"}

    response = client.get('/rates?date_from=2024-01-01&origin=PORT1&destination=PORT2')
    assert response.status_code == 400
    assert response.json == {"error": "Missing required parameters"}

    response = client.get('/rates?date_from=2024-01-01&date_to=2024-01-10&destination=PORT2')
    assert response.status_code == 400
    assert response.json == {"error": "Missing required parameters"}

# Test case for invalid date format
def test_invalid_date_format(client):
    response = client.get('/rates?date_from=invalid-date&date_to=2024-01-10&origin=PORT1&destination=PORT2')
    assert response.status_code == 400
    assert response.json == {"error": "Invalid date format. Use YYYY-MM-DD."}

# Test case for no data available for the given parameters
def test_no_data(client):
    response = client.get('/rates?date_from=2024-01-01&date_to=2024-01-10&origin=PORT1&destination=PORT2')
    assert response.status_code == 200
    assert response.json == []

# Test case for valid data using mock to simulate database connection and query results
@patch('app.main.get_db_connection')
def test_valid_data_with_mock(mock_get_db_connection, client):
    mock_conn = mock_get_db_connection.return_value
    mock_cursor = mock_conn.cursor.return_value

    # Mocking the fetchall method to return predefined data
    mock_cursor.fetchall.return_value = [
        ('2023-01-01', 1000),
        ('2023-01-02', 1100)
    ]

    response = client.get('/rates?date_from=2023-01-01&date_to=2023-01-10&origin=PORT1&destination=PORT2')
    assert response.status_code == 200
    assert response.json == [
        {"day": "2023-01-01", "average_price": 1000},
        {"day": "2023-01-02", "average_price": 1100}
    ]

# Test case for handling database connection error
@patch('app.main.get_db_connection')
def test_database_error(mock_get_db_connection, client):
    # Simulating a database connection error
    mock_get_db_connection.side_effect = psycopg2.DatabaseError("Database connection failed")

    response = client.get('/rates?date_from=2023-01-01&date_to=2023-01-10&origin=PORT1&destination=PORT2')
    assert response.status_code == 500
    assert "error" in response.json
