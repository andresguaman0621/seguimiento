/* App Vue del funcionario: registra/gestiona su salida en curso. */
const { createApp } = Vue;

createApp({
  delimiters: ["[[", "]]"],
  data() {
    return {
      usuario: {},
      actividad: null,
      tipos: [],
      form: { tipo_actividad_id: null, comentario: "" },
      cargando: true,
      guardando: false,
      error: "",
      ahora: Date.now(),
      menuAbierto: false,
      _timer: null,
      _cerrarMenu: null,
    };
  },
  computed: {
    // Cronómetro de tiempo transcurrido en la actividad en curso.
    transcurrido() {
      if (!this.actividad) return "";
      // `ahora` se referencia para forzar recálculo cada segundo.
      void this.ahora;
      return Fmt.duracion(this.actividad.fecha_hora_inicio);
    },
  },
  methods: {
    fmtFechaHora: Fmt.fechaHora,
    iniciales(nombre) {
      if (!nombre) return "?";
      const partes = nombre.trim().split(/\s+/);
      const letras = partes.length > 1 ? partes[0][0] + partes[1][0] : partes[0].slice(0, 2);
      return letras.toUpperCase();
    },
    async cargar() {
      this.cargando = true;
      this.error = "";
      try {
        const [act, tipos] = await Promise.all([
          Api.get("/api/actividades/actual"),
          Api.get("/api/admin/tipos?solo_activos=1"),
        ]);
        this.actividad = act.actividad;
        this.tipos = tipos.tipos;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.cargando = false;
      }
    },
    async registrar() {
      if (!this.form.tipo_actividad_id || !this.form.comentario.trim()) return;
      this.guardando = true;
      this.error = "";
      try {
        const r = await Api.post("/api/actividades", {
          tipo_actividad_id: this.form.tipo_actividad_id,
          comentario: this.form.comentario.trim(),
        });
        this.actividad = r.actividad;
        this.form = { tipo_actividad_id: null, comentario: "" };
      } catch (e) {
        this.error = e.message;
      } finally {
        this.guardando = false;
      }
    },
    async finalizar() {
      await this._cerrar("finalizar");
    },
    async cancelar() {
      if (!confirm("¿Cancelar esta salida?")) return;
      await this._cerrar("cancelar");
    },
    async _cerrar(accion) {
      this.guardando = true;
      this.error = "";
      try {
        await Api.patch("/api/actividades/" + this.actividad.id + "/" + accion);
        this.actividad = null;
      } catch (e) {
        this.error = e.message;
      } finally {
        this.guardando = false;
      }
    },
    salir: () => Auth.salir(),
  },
  mounted() {
    const u = Auth.requerir("FUNCIONARIO");
    if (!u) return;
    this.usuario = u;
    this.cargar();
    this._timer = setInterval(() => {
      this.ahora = Date.now();
    }, 1000);
    // Cierra el menú de usuario al hacer clic fuera de él.
    this._cerrarMenu = () => {
      this.menuAbierto = false;
    };
    document.addEventListener("click", this._cerrarMenu);
  },
  unmounted() {
    if (this._timer) clearInterval(this._timer);
    if (this._cerrarMenu) document.removeEventListener("click", this._cerrarMenu);
  },
})
  .component("icon", Icon)
  .mount("#app");
