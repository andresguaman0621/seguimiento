"""Utilidades compartidas: validación de cédula y manejo de fechas UTC."""
from datetime import datetime, timezone


def now_utc_iso():
    """Devuelve el instante actual en UTC, formato ISO-8601 (ej: 2026-07-15T14:30:00Z)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cedula_formato_valido(cedula):
    """Valida que la cédula sean exactamente 10 dígitos numéricos."""
    return isinstance(cedula, str) and len(cedula) == 10 and cedula.isdigit()


def cedula_ecuatoriana_valida(cedula):
    """Valida una cédula ecuatoriana: 10 dígitos + dígito verificador (módulo 10).

    Refuerzo opcional al formato: comprueba el código de provincia (01-24)
    y el algoritmo de verificación del último dígito.
    """
    if not cedula_formato_valido(cedula):
        return False

    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        return False

    tercer_digito = int(cedula[2])
    if tercer_digito >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for coef, digito in zip(coeficientes, [int(c) for c in cedula[:9]]):
        producto = coef * digito
        if producto >= 10:
            producto -= 9
        total += producto

    verificador = (10 - (total % 10)) % 10
    return verificador == int(cedula[9])
