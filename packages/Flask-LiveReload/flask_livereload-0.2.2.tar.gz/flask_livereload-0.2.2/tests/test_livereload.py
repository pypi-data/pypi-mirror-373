"""
Pruebas para Flask-LiveReload
"""

import os
import time
import pytest
from flask import Flask
from flask_livereload import LiveReload


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.debug = True
    LiveReload(app)
    return app


@pytest.fixture
def app_with_config():
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.debug = True
    
    # Configuración avanzada
    app.config["LIVERELOAD_WATCH_PATTERNS"] = [
        "statics/**/*.html",
        "statics/**/*.js",
        "templates/**/*.html",
    ]
    
    app.config["LIVERELOAD_IGNORE_PATTERNS"] = [
        "__pycache__",
        ".git",
        "*.pyc",
        "node_modules",
    ]
    
    LiveReload(app)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def client_with_config(app_with_config):
    return app_with_config.test_client()


def test_script_injection(client):
    """Test that the livereload script is injected into HTML responses."""
    @client.application.route('/')
    def index():
        return "<html><body>Hello</body></html>"

    response = client.get('/')
    assert response.status_code == 200
    # Verificar que el script se inyecta correctamente
    assert b'/_livereload' in response.data
    assert b'EventSource' in response.data


def test_script_not_injected_in_api_responses(client):
    """Test that the livereload script is not injected into non-HTML responses."""
    @client.application.route('/api/data')
    def api_data():
        return {"message": "Hello"}, 200, {'Content-Type': 'application/json'}

    response = client.get('/api/data')
    assert response.status_code == 200
    # Verificar que el script NO se inyecta en respuestas JSON
    assert b'/_livereload' not in response.data


def test_sse_mimetype(client):
    """Test that the SSE endpoint has the correct mimetype."""
    response = client.get('/_livereload')
    assert response.mimetype == 'text/event-stream'


def test_sse_initial_connection(client):
    """Test that SSE endpoint sends initial connection message."""
    with client.get('/_livereload') as response:
        # Leer la primera línea de la respuesta
        first_line = next(response.response)
        assert b'data: connected' in first_line or b': keepalive' in first_line


def test_script_injection_with_config(client_with_config):
    """Test script injection with custom configuration."""
    @client_with_config.application.route('/test')
    def test_route():
        return "<html><body><h1>Test</h1></body></html>"

    response = client_with_config.get('/test')
    assert response.status_code == 200
    assert b'/_livereload' in response.data


def test_sse_with_config(client_with_config):
    """Test SSE endpoint with custom configuration."""
    response = client_with_config.get('/_livereload')
    assert response.mimetype == 'text/event-stream'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])