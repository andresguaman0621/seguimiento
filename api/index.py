"""Entrypoint WSGI para el runtime de Python de Vercel.

Vercel detecta este archivo (api/index.py) y expone la variable `app`
como funcion serverless. No se usa `run.py` aqui: no se llama a
`app.run()`, solo se construye y expone el objeto WSGI de Flask.
"""
import os
import sys

# Asegura que la raiz del proyecto (donde vive el paquete `app/`) este
# en el path de Python, sin importar el directorio de trabajo desde el
# que el runtime invoque este archivo.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

app = create_app()
