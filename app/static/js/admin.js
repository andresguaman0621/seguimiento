/* App Vue del panel de administración (jefatura). */
const { createApp } = Vue;

const TITULOS_TAB = {
  dashboard: "Dashboard",
  historial: "Historial de actividades",
  usuarios: "Usuarios",
  tipos: "Tipos de actividad",
};

createApp({
  delimiters: ["[[", "]]"],
  data() {
    return {
      usuario: {},
      tab: "dashboard",
      sidebarOpen: false,
      tabs: [
        { id: "dashboard", label: "Dashboard", icon: "dashboard" },
        { id: "historial", label: "Historial", icon: "history" },
        { id: "usuarios", label: "Usuarios", icon: "users" },
        { id: "tipos", label: "Tipos de actividad", icon: "tag" },
      ],
      cargando: false,
      error: "",

      dashboard: [],
      statsHoy: [],
      historial: [],
      filtros: { desde: "", hasta: "", usuario_id: "", estado: "" },

      usuarios: [],
      tipos: [],

      // Modales.
      modalUsuario: null,
      usuarioForm: { id: null, cedula: "", nombre: "", rol: "FUNCIONARIO" },
      modalTipo: null,
      tipoForm: { id: null, nombre: "" },
      modalError: "",
      modalGuardando: false,

      ahora: Date.now(),
      _timer: null,
    };
  },
  computed: {
    tituloTab() {
      return TITULOS_TAB[this.tab] || "Panel";
    },
    finalizadasHoy() {
      return this.statsHoy.filter((a) => a.estado === "FINALIZADA").length;
    },
  },
  methods: {
    fmtFechaHora: Fmt.fechaHora,
    fmtHora: Fmt.hora,
    desde(iso) {
      void this.ahora; // recalcula el tiempo fuera cada segundo
      return Fmt.duracion(iso);
    },
    iniciales(nombre) {
      if (!nombre) return "?";
      const partes = nombre.trim().split(/\s+/);
      const letras = partes.length > 1 ? partes[0][0] + partes[1][0] : partes[0].slice(0, 2);
      return letras.toUpperCase();
    },
    colorFor(id) {
      const paleta = ["avatar-c0", "avatar-c1", "avatar-c2", "avatar-c3", "avatar-c4", "avatar-c5", "avatar-c6"];
      return paleta[Number(id) % paleta.length];
    },

    async cambiarTab(id) {
      this.tab = id;
      this.error = "";
      this.sidebarOpen = false;
      if (id === "dashboard") await this.cargarDashboard();
      else if (id === "historial") await this.cargarHistorial();
      else if (id === "usuarios") await this.cargarUsuarios();
      else if (id === "tipos") await this.cargarTipos();
    },

    async _run(fn) {
      this.cargando = true;
      this.error = "";
      try {
        await fn();
      } catch (e) {
        this.error = e.message;
      } finally {
        this.cargando = false;
      }
    },

    // ---- Dashboard ----
    cargarDashboard() {
      return this._run(async () => {
        const hoyInicio = new Date();
        hoyInicio.setHours(0, 0, 0, 0);
        const hoyFin = new Date();
        hoyFin.setHours(23, 59, 59, 999);

        const [d, hoy] = await Promise.all([
          Api.get("/api/admin/dashboard"),
          Api.get(
            "/api/admin/actividades?desde=" +
              encodeURIComponent(hoyInicio.toISOString()) +
              "&hasta=" +
              encodeURIComponent(hoyFin.toISOString())
          ),
        ]);
        this.dashboard = d.actividades;
        this.statsHoy = hoy.actividades;
      });
    },

    // ---- Historial ----
    cargarHistorial() {
      return this._run(async () => {
        // Aseguramos tener la lista de usuarios para el filtro.
        if (!this.usuarios.length) {
          const u = await Api.get("/api/admin/usuarios");
          this.usuarios = u.usuarios;
        }
        const params = new URLSearchParams();
        if (this.filtros.desde) {
          params.set("desde", new Date(this.filtros.desde + "T00:00:00").toISOString());
        }
        if (this.filtros.hasta) {
          params.set("hasta", new Date(this.filtros.hasta + "T23:59:59").toISOString());
        }
        if (this.filtros.usuario_id) params.set("usuario_id", this.filtros.usuario_id);
        if (this.filtros.estado) params.set("estado", this.filtros.estado);
        const qs = params.toString();
        const r = await Api.get("/api/admin/actividades" + (qs ? "?" + qs : ""));
        this.historial = r.actividades;
      });
    },
    limpiarFiltros() {
      this.filtros = { desde: "", hasta: "", usuario_id: "", estado: "" };
      this.cargarHistorial();
    },

    // ---- Usuarios ----
    cargarUsuarios() {
      return this._run(async () => {
        const r = await Api.get("/api/admin/usuarios");
        this.usuarios = r.usuarios;
      });
    },
    abrirUsuario(u) {
      this.modalError = "";
      this.usuarioForm = u
        ? { id: u.id, cedula: u.cedula, nombre: u.nombre, rol: u.rol }
        : { id: null, cedula: "", nombre: "", rol: "FUNCIONARIO" };
      this.modalUsuario = true;
    },
    async guardarUsuario() {
      this.modalError = "";
      this.modalGuardando = true;
      try {
        const f = this.usuarioForm;
        if (f.id) {
          await Api.put("/api/admin/usuarios/" + f.id, { nombre: f.nombre, rol: f.rol });
        } else {
          await Api.post("/api/admin/usuarios", {
            cedula: f.cedula,
            nombre: f.nombre,
            rol: f.rol,
          });
        }
        this.modalUsuario = null;
        await this.cargarUsuarios();
      } catch (e) {
        this.modalError = e.message;
      } finally {
        this.modalGuardando = false;
      }
    },
    async toggleUsuario(u) {
      const accion = u.activo ? "desactivar" : "activar";
      if (!confirm("¿Seguro que deseas " + accion + " a " + u.nombre + "?")) return;
      await this._run(async () => {
        await Api.patch("/api/admin/usuarios/" + u.id + "/estado", { activo: !u.activo });
        await this.cargarUsuarios();
      });
    },

    // ---- Tipos ----
    cargarTipos() {
      return this._run(async () => {
        const r = await Api.get("/api/admin/tipos");
        this.tipos = r.tipos;
      });
    },
    abrirTipo(t) {
      this.modalError = "";
      this.tipoForm = t ? { id: t.id, nombre: t.nombre } : { id: null, nombre: "" };
      this.modalTipo = true;
    },
    async guardarTipo() {
      this.modalError = "";
      this.modalGuardando = true;
      try {
        const f = this.tipoForm;
        if (f.id) await Api.put("/api/admin/tipos/" + f.id, { nombre: f.nombre });
        else await Api.post("/api/admin/tipos", { nombre: f.nombre });
        this.modalTipo = null;
        await this.cargarTipos();
      } catch (e) {
        this.modalError = e.message;
      } finally {
        this.modalGuardando = false;
      }
    },
    async toggleTipo(t) {
      const accion = t.activo ? "desactivar" : "activar";
      if (!confirm("¿Seguro que deseas " + accion + ' "' + t.nombre + '"?')) return;
      await this._run(async () => {
        await Api.patch("/api/admin/tipos/" + t.id + "/estado", { activo: !t.activo });
        await this.cargarTipos();
      });
    },

    // ---- Helpers de presentación ----
    etiquetaEstado(e) {
      return { EN_CURSO: "En curso", FINALIZADA: "Finalizada", CANCELADA: "Cancelada" }[e] || e;
    },
    badgeEstado(e) {
      return {
        EN_CURSO: "badge-encurso",
        FINALIZADA: "badge-finalizada",
        CANCELADA: "badge-cancelada",
      }[e] || "";
    },
    salir: () => Auth.salir(),
  },
  mounted() {
    const u = Auth.requerir("ADMIN");
    if (!u) return;
    this.usuario = u;
    this.cargarDashboard();
    this._timer = setInterval(() => {
      this.ahora = Date.now();
    }, 1000);
  },
  unmounted() {
    if (this._timer) clearInterval(this._timer);
  },
})
  .component("icon", Icon)
  .mount("#app");
