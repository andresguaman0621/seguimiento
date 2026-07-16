/* App Vue de la pantalla de login. */
const { createApp } = Vue;

// Si ya hay sesión, ir directo al panel correspondiente.
(function () {
  const u = Auth.usuario();
  if (Auth.token() && u) {
    window.location.href = u.rol === "ADMIN" ? "/admin" : "/funcionario";
  }
})();

createApp({
  delimiters: ["[[", "]]"],
  data() {
    return { cedula: "", error: "", cargando: false };
  },
  methods: {
    async ingresar() {
      this.error = "";
      if (this.cedula.length !== 10) {
        this.error = "La cédula debe tener 10 dígitos.";
        return;
      }
      this.cargando = true;
      try {
        const r = await Api.post("/api/auth/login", { cedula: this.cedula });
        Auth.guardarSesion(r.token, r.usuario);
        window.location.href = r.usuario.rol === "ADMIN" ? "/admin" : "/funcionario";
      } catch (e) {
        this.error = e.message;
      } finally {
        this.cargando = false;
      }
    },
  },
})
  .component("icon", Icon)
  .mount("#app");
