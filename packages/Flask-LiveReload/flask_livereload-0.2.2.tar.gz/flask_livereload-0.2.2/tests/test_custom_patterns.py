"""
Pruebas para patrones personalizados de Flask-LiveReload
"""

import os
import tempfile
import time
import pytest
from flask import Flask
from flask_livereload import LiveReload


@pytest.fixture
def app_with_custom_patterns():
    """Crear una aplicación Flask con patrones personalizados"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.debug = True
    
    # Configurar patrones personalizados
    app.config["LIVERELOAD_WATCH_PATTERNS"] = [
        "statics/**/*.html",
        "statics/**/*.js",
        "templates/**/*.html",
    ]
    
    app.config["LIVERELOAD_IGNORE_PATTERNS"] = [
        "__pycache__",
        ".git",
        "*.pyc",
    ]
    
    LiveReload(app)
    return app


@pytest.fixture
def client_with_custom_patterns(app_with_custom_patterns):
    return app_with_custom_patterns.test_client()


def test_script_injection_with_custom_patterns(client_with_custom_patterns):
    """Test que verifica la inyección del script con patrones personalizados"""
    @client_with_custom_patterns.application.route('/test')
    def test_route():
        return "<html><body><h1>Test</h1></body></html>"

    response = client_with_custom_patterns.get('/test')
    assert response.status_code == 200
    assert b'/_livereload' in response.data


def test_sse_endpoint_with_custom_patterns(client_with_custom_patterns):
    """Test que verifica el endpoint SSE con patrones personalizados"""
    response = client_with_custom_patterns.get('/_livereload')
    assert response.mimetype == 'text/event-stream'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])