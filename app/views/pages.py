"""Rutas que sirven las páginas HTML (cascarones que montan las apps Vue).

La seguridad real vive en la API (JWT). Estas páginas son públicas; cada app Vue
verifica el token en localStorage al montar y redirige a /login si hace falta.
"""
from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("pages", __name__)


@bp.get("/")
def index():
    return redirect(url_for("pages.login"))


@bp.get("/login")
def login():
    return render_template("login.html")


@bp.get("/funcionario")
def funcionario():
    return render_template("funcionario.html")


@bp.get("/admin")
def admin():
    return render_template("admin.html")
