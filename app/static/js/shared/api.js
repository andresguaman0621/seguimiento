/* Cliente HTTP compartido: envuelve fetch, adjunta el JWT y maneja sesiones.
   Expuesto como window.Api y window.Auth. */
(function () {
  const TOKEN_KEY = "seg_token";
  const USER_KEY = "seg_usuario";

  const Auth = {
    guardarSesion(token, usuario) {
      localStorage.setItem(TOKEN_KEY, token);
      localStorage.setItem(USER_KEY, JSON.stringify(usuario));
    },
    token() {
      return localStorage.getItem(TOKEN_KEY);
    },
    usuario() {
      try {
        return JSON.parse(localStorage.getItem(USER_KEY)) || null;
      } catch (e) {
        return null;
      }
    },
    limpiar() {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    },
    salir() {
      Auth.limpiar();
      window.location.href = "/login";
    },
    /* Guard de UX: exige sesión y (opcional) un rol. Redirige si no cumple. */
    requerir(rol) {
      const u = Auth.usuario();
      if (!Auth.token() || !u) {
        window.location.href = "/login";
        return null;
      }
      if (rol && u.rol !== rol) {
        window.location.href = u.rol === "ADMIN" ? "/admin" : "/funcionario";
        return null;
      }
      return u;
    },
  };

  /* Error con el mensaje del backend y el status HTTP. */
  class ApiError extends Error {
    constructor(mensaje, status) {
      super(mensaje);
      this.status = status;
    }
  }

  async function request(metodo, url, body) {
    const headers = { "Content-Type": "application/json" };
    const token = Auth.token();
    if (token) headers["Authorization"] = "Bearer " + token;

    const resp = await fetch(url, {
      method: metodo,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    // 401: sesión inválida/expirada -> volver al login.
    if (resp.status === 401 && !url.endsWith("/api/auth/login")) {
      Auth.salir();
      throw new ApiError("Sesión expirada", 401);
    }

    let datos = null;
    try {
      datos = await resp.json();
    } catch (e) {
      datos = null;
    }

    if (!resp.ok) {
      const msg = (datos && datos.error) || "Error inesperado";
      throw new ApiError(msg, resp.status);
    }
    return datos;
  }

  const Api = {
    get: (url) => request("GET", url),
    post: (url, body) => request("POST", url, body),
    put: (url, body) => request("PUT", url, body),
    patch: (url, body) => request("PATCH", url, body),
    ApiError,
  };

  /* Helpers de fecha/hora: el backend entrega ISO-8601 UTC; mostramos hora local. */
  const Fmt = {
    _pad(n) {
      return String(n).padStart(2, "0");
    },
    fechaHora(iso) {
      if (!iso) return "—";
      const d = new Date(iso);
      return (
        Fmt._pad(d.getDate()) +
        "/" +
        Fmt._pad(d.getMonth() + 1) +
        "/" +
        d.getFullYear() +
        " " +
        Fmt._pad(d.getHours()) +
        ":" +
        Fmt._pad(d.getMinutes())
      );
    },
    hora(iso) {
      if (!iso) return "—";
      const d = new Date(iso);
      return Fmt._pad(d.getHours()) + ":" + Fmt._pad(d.getMinutes());
    },
    /* Duración legible entre `iso` y ahora (o entre dos instantes). */
    duracion(desdeIso, hastaIso) {
      if (!desdeIso) return "";
      const ini = new Date(desdeIso).getTime();
      const fin = hastaIso ? new Date(hastaIso).getTime() : Date.now();
      let seg = Math.max(0, Math.floor((fin - ini) / 1000));
      const h = Math.floor(seg / 3600);
      seg -= h * 3600;
      const m = Math.floor(seg / 60);
      const s = seg - m * 60;
      if (h > 0) return h + "h " + Fmt._pad(m) + "m";
      if (m > 0) return m + "m " + Fmt._pad(s) + "s";
      return s + "s";
    },
  };

  window.Api = Api;
  window.Auth = Auth;
  window.Fmt = Fmt;
})();
