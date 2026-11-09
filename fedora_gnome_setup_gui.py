#!/usr/bin/env python3
"""Fedora GNOME Setup: ventana GTK4 + libadwaita que reúne los scripts de
configuración del sistema.

Usa solo widgets de libadwaita y ninguna hoja de estilos propia, así que hereda
sin más el tema de GNOME (modo claro/oscuro, color de acento, tipografía).

La GUI ejecuta los scripts del proyecto tal cual, sin modificarlos. Corre como
usuario normal; los scripts piden sudo por sí mismos, dentro de la propia ventana.

La salida de los scripts se muestra en una terminal real (VTE): colores, barras
de progreso, preguntas (read), contraseña de sudo y cuadros whiptail/dialog
funcionan como en cualquier terminal, sin traducciones intermedias.

Modos de ejecución (campo opcional "modo" de cada acción en CONFIG):

  auto        (por defecto) El script se ejecuta DENTRO de esta ventana, en la
              terminal integrada.
  integrado   Igual que auto.
  terminal    Igual que auto (la terminal ya es real; no hace falta abrir otra).
  gui         Para scripts que abren su propia aplicación gráfica: el proyecto se
              actualiza (si es remoto) y el script se lanza sin terminal.

Dependencias (Fedora):
  sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4
"""
import os
import signal
import subprocess
import sys
from pathlib import Path

try:
    import gi

    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    gi.require_version("Vte", "3.91")
    from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk, Pango, Vte
except (ImportError, ValueError) as err:
    sys.stderr.write(
        f"Faltan dependencias de la interfaz ({err}).\n"
        "Instálalas con:\n"
        "  sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4\n")
    sys.exit(1)

APP_ID = "local.fedoragnomesetup.App"
TITULO = "Fedora GNOME Setup"
ROOT = Path(__file__).resolve().parent
LOG_DIR = Path.home() / ".local/share/fedora-gnome-setup/logs"
MODOS = ("auto", "integrado", "gui", "terminal")

# Icono simbólico del tema por sección. Si una sección no aparece aquí se usa
# el icono genérico.
SECCIONES = {
    "Sistema":     "preferences-system-symbolic",
    "Gaming":      "applications-games-symbolic",
    "NVIDIA":      "video-display-symbolic",
    "ASUS / ROG":  "computer-symbolic",
    "Rendimiento": "utilities-system-monitor-symbolic",
    "Terminal":    "utilities-terminal-symbolic",
}
ICONO_DEFECTO = "application-x-executable-symbolic"

CONFIG = {
    "carpeta_proyectos": "~/.local/share/fedora-gnome-setup/components",
    "acciones": [
        {"seccion": "Sistema", "titulo": "Configurar Fedora", "descripcion": "Configuración base: RPM Fusion, multimedia, códecs, microcódigo y Flathub.", "script": "gnome/setup-fedora-base.sh", "local": True},
        {"seccion": "NVIDIA", "titulo": "Instalar NVIDIA", "descripcion": "Instala y configura el driver NVIDIA mediante el script del proyecto.", "script": "nvidia/setup-nvidia.sh", "local": True},
        {"seccion": "ASUS / ROG", "titulo": "Instalar ASUS / ROG", "descripcion": "Instala y configura asusctl / ROG Control mediante el script del proyecto.", "script": "asus/setup-asusctl.sh", "local": True},
        {"seccion": "Gaming", "titulo": "Instalar gaming", "descripcion": "Instala la configuración y herramientas gaming de Fedora.", "script": "gaming/setup-gaming-fedora.sh", "local": True},
    ],
}

# Script de bash fijo: recibe DIR, URL y SCRIPT como $1, $2 y $3 (sin
# interpolar nada en el texto, para evitar problemas de quoting).
PREPARAR = r'''
d=$1; url=$2; s=$3
if [ -d "$d/.git" ]; then
    git -C "$d" pull --ff-only || echo "AVISO: no se pudo actualizar; se usa la copia local."
else
    mkdir -p "$(dirname "$d")" && git clone "$url" "$d" || { echo "ERROR: no se pudo clonar $url"; exit 1; }
fi
[ -f "$d/$s" ] || { echo "ERROR: no existe $s en $d"; exit 1; }
'''

# Clases de estilo estándar de libadwaita para cada estado de una acción.
CLASES_ESTADO = {"ok": "success", "error": "error", "run": "accent", "off": "dim-label"}


def repo_name(url):
    return url.rstrip("/").removesuffix(".git").split("/")[-1]


def icono_seccion(nombre):
    return SECCIONES.get(nombre, ICONO_DEFECTO)


def entorno():
    """Entorno para los scripts, como lista 'CLAVE=valor' para VTE. Se evitan
    los paginadores, que dejarían el script esperando una tecla."""
    env = os.environ.copy()
    env.update({"TERM": "xterm-256color", "COLORTERM": "truecolor",
                "PAGER": "cat", "GIT_PAGER": "cat", "SYSTEMD_PAGER": "",
                "LANZADOR_INTEGRADO": "1"})
    return [f"{k}={v}" for k, v in env.items()]


def esc(texto):
    """Escapa texto para widgets de libadwaita que interpretan marcado Pango."""
    return GLib.markup_escape_text(texto)


class FilaAccion(Adw.ActionRow):
    """Una acción: título, descripción, estado y botón de ejecución."""

    def __init__(self, item, on_run):
        super().__init__()
        self.item = item
        self.set_title(esc(item["titulo"]))
        self.set_subtitle(esc(item.get("descripcion", "")))

        icono = Gtk.Image.new_from_icon_name(icono_seccion(item["seccion"]))
        self.add_prefix(icono)

        self.lbl_estado = Gtk.Label(valign=Gtk.Align.CENTER)
        self.lbl_estado.add_css_class("caption")
        self.set_estado("off", "Sin ejecutar")

        peligroso = bool(item.get("peligroso"))
        self.boton = Gtk.Button(label="Quitar" if peligroso else "Ejecutar",
                                valign=Gtk.Align.CENTER)
        self.boton.add_css_class("destructive-action" if peligroso else "suggested-action")
        self.boton.connect("clicked", lambda _b: on_run(item))

        self.add_suffix(self.lbl_estado)
        self.add_suffix(self.boton)

    def set_estado(self, tipo, texto):
        for clase in CLASES_ESTADO.values():
            self.lbl_estado.remove_css_class(clase)
        self.lbl_estado.add_css_class(CLASES_ESTADO.get(tipo, "dim-label"))
        self.lbl_estado.set_label(texto)

    def set_ocupado(self, ocupado):
        self.boton.set_sensitive(not ocupado)


class Ventana(Adw.ApplicationWindow):
    def __init__(self, app, config):
        super().__init__(application=app, title=TITULO)
        self.set_default_size(1000, 700)
        self.set_size_request(360, 400)

        self.base = Path(os.path.expanduser(config["carpeta_proyectos"]))
        self.acciones = config["acciones"]
        self.ctx = None
        self.child_pid = None
        self.cerrar_forzado = False
        self.filtro_seccion = None
        self.filas = []
        self._timers = {}

        self.toasts = Adw.ToastOverlay()
        self.nav = Adw.NavigationView()
        self.toasts.set_child(self.nav)
        self.set_content(self.toasts)

        self.pagina_inicio = self._build_home()
        self.pagina_run = self._build_run()
        # La primera página añadida es la raíz; la de ejecución se apila a demanda.
        self.nav.add(self.pagina_inicio)
        self.nav.add(self.pagina_run)

        self.connect("close-request", self._on_close)
        self._refrescar()

    # ---------------------------------------------------------------- inicio

    def _orden_secciones(self):
        orden = []
        for item in self.acciones:
            if item["seccion"] not in orden:
                orden.append(item["seccion"])
        return orden

    def _build_home(self):
        # --- barra lateral: secciones
        self.lista = Gtk.ListBox()
        self.lista.add_css_class("navigation-sidebar")
        self.secciones = []  # secciones[i] = nombre de sección, None = todas
        self._fila_seccion(None, "Todas las acciones", "view-list-symbolic")
        for sec in self._orden_secciones():
            self._fila_seccion(sec, sec, icono_seccion(sec))
        self.lista.connect("row-selected", self._seccion_elegida)
        self.lista.connect("row-activated", lambda *_: self.split.set_show_content(True))

        vista_lateral = Adw.ToolbarView()
        vista_lateral.add_top_bar(Adw.HeaderBar())
        vista_lateral.set_content(Gtk.ScrolledWindow(child=self.lista))
        pagina_lateral = Adw.NavigationPage.new(vista_lateral, TITULO)

        # --- contenido: acciones de la sección elegida
        # El buscador se crea antes que la lista: el filtro lo consulta al añadir filas.
        self.entrada_busqueda = Gtk.SearchEntry(hexpand=True,
                                                placeholder_text="Buscar acciones")
        self.entrada_busqueda.connect("search-changed", lambda _e: self._refrescar())
        self.barra_busqueda = Gtk.SearchBar(child=self.entrada_busqueda)
        self.barra_busqueda.connect_entry(self.entrada_busqueda)

        self.listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE,
                                     valign=Gtk.Align.START)
        self.listbox.add_css_class("boxed-list")
        self.listbox.set_filter_func(self._filtro)
        for item in self.acciones:
            fila = FilaAccion(item, self.run)
            self.filas.append(fila)
            self.listbox.append(fila)

        clamp = Adw.Clamp(maximum_size=760, margin_top=18, margin_bottom=18,
                          margin_start=12, margin_end=12, child=self.listbox)
        lista_scroll = Gtk.ScrolledWindow(child=clamp, vexpand=True)
        vacio = Adw.StatusPage(icon_name="edit-find-symbolic",
                               title="Sin resultados",
                               description="Prueba con otra búsqueda.")
        self.pila = Gtk.Stack()
        self.pila.add_named(lista_scroll, "lista")
        self.pila.add_named(vacio, "vacio")

        self.btn_buscar = Gtk.ToggleButton(icon_name="system-search-symbolic",
                                           tooltip_text="Buscar")
        self.btn_buscar.bind_property(
            "active", self.barra_busqueda, "search-mode-enabled",
            GObject.BindingFlags.BIDIRECTIONAL | GObject.BindingFlags.SYNC_CREATE)

        self.titulo_w = Adw.WindowTitle.new("Todas las acciones", "")
        cabecera = Adw.HeaderBar()
        cabecera.set_title_widget(self.titulo_w)
        cabecera.pack_end(self.btn_buscar)

        vista_contenido = Adw.ToolbarView()
        vista_contenido.add_top_bar(cabecera)
        vista_contenido.add_top_bar(self.barra_busqueda)
        vista_contenido.set_content(self.pila)
        self.pagina_contenido = Adw.NavigationPage.new(vista_contenido, "Acciones")

        # --- división barra lateral / contenido, con colapso en ventanas estrechas
        self.split = Adw.NavigationSplitView()
        self.split.set_min_sidebar_width(200)
        self.split.set_max_sidebar_width(280)
        self.split.set_sidebar(pagina_lateral)
        self.split.set_content(self.pagina_contenido)

        bp = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 640sp"))
        bp.add_setter(self.split, "collapsed", True)
        self.add_breakpoint(bp)

        pagina = Adw.NavigationPage.new(self.split, TITULO)
        pagina.set_tag("inicio")
        self.lista.select_row(self.lista.get_row_at_index(0))
        return pagina

    def _fila_seccion(self, nombre, etiqueta, icono):
        caja = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12,
                       margin_top=8, margin_bottom=8, margin_start=6, margin_end=6)
        caja.append(Gtk.Image.new_from_icon_name(icono))
        caja.append(Gtk.Label(label=etiqueta, xalign=0, hexpand=True,
                              ellipsize=Pango.EllipsizeMode.END))
        self.lista.append(Gtk.ListBoxRow(child=caja))
        self.secciones.append(nombre)

    def _seccion_elegida(self, _lista, fila):
        if fila is None:
            return
        self.filtro_seccion = self.secciones[fila.get_index()]
        self._refrescar()

    def _visible(self, item):
        texto = self.entrada_busqueda.get_text().strip().lower()
        ok_sec = self.filtro_seccion is None or item["seccion"] == self.filtro_seccion
        objetivo = (item["titulo"] + " " + item.get("descripcion", "")).lower()
        return ok_sec and (not texto or texto in objetivo)

    def _filtro(self, fila):
        return self._visible(fila.item)

    def _refrescar(self):
        self.listbox.invalidate_filter()
        n = sum(1 for fila in self.filas if self._visible(fila.item))
        nombre = self.filtro_seccion or "Todas las acciones"
        plural = "acción" if n == 1 else "acciones"
        self.titulo_w.set_title(nombre)
        self.titulo_w.set_subtitle(f"{n} {plural} disponibles")
        self.pagina_contenido.set_title(nombre)
        self.pila.set_visible_child_name("lista" if n else "vacio")

    def _fila_de(self, item):
        for fila in self.filas:
            if fila.item is item:
                return fila
        return None

    # -------------------------------------------------------------- ejecución

    def _build_run(self):
        self.term = Vte.Terminal()
        self.term.set_scrollback_lines(10000)
        self.term.set_font(Pango.FontDescription.from_string("Monospace 11"))
        self.term.set_hexpand(True)
        self.term.set_vexpand(True)
        self.term.set_margin_start(6)
        self.term.set_margin_end(6)
        self.term.set_margin_top(6)
        self.term.connect("child-exited", self._terminado)
        self._colores_terminal()
        Adw.StyleManager.get_default().connect(
            "notify::dark", lambda *_: self._colores_terminal())

        self.btn_cancelar = Gtk.Button(label="Cancelar")
        self.btn_cancelar.add_css_class("destructive-action")
        self.btn_cancelar.connect("clicked", lambda _b: self.cancelar())
        cabecera = Adw.HeaderBar()
        cabecera.pack_end(self.btn_cancelar)

        self.lbl_estado = Gtk.Label(xalign=0, hexpand=True,
                                    ellipsize=Pango.EllipsizeMode.END)
        self.btn_volver = Gtk.Button(label="Volver")
        self.btn_volver.connect("clicked", lambda _b: self.volver())
        barra = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12,
                        margin_top=8, margin_bottom=8, margin_start=12, margin_end=12)
        barra.append(self.lbl_estado)
        barra.append(self.btn_volver)

        vista = Adw.ToolbarView()
        vista.add_top_bar(cabecera)
        vista.set_content(Gtk.ScrolledWindow(child=self.term))
        vista.add_bottom_bar(barra)
        pagina = Adw.NavigationPage.new(vista, "Ejecución")
        pagina.set_tag("ejecucion")
        return pagina

    def _colores_terminal(self):
        """Fondo y texto de la terminal según el modo claro/oscuro del sistema."""
        oscuro = Adw.StyleManager.get_default().get_dark()
        fondo, texto = Gdk.RGBA(), Gdk.RGBA()
        fondo.parse("#1e1e1e" if oscuro else "#ffffff")
        texto.parse("#dcdcdc" if oscuro else "#241f31")
        self.term.set_colors(texto, fondo, None)

    def _sistema(self, mensaje, color="36"):
        """Escribe un mensaje propio de la GUI en la terminal (no del script)."""
        self.term.feed(f"\r\n\x1b[1;{color}m{mensaje}\x1b[0m\r\n".encode())

    def _estado(self, tipo, texto):
        self.lbl_estado.set_label(texto)
        for clase in CLASES_ESTADO.values():
            self.lbl_estado.remove_css_class(clase)
        self.lbl_estado.add_css_class(CLASES_ESTADO.get(tipo, "dim-label"))

    def _controles(self, ejecutando):
        self.pagina_run.set_can_pop(not ejecutando)
        self.btn_cancelar.set_visible(ejecutando)
        self.btn_volver.set_sensitive(not ejecutando)
        for fila in self.filas:
            fila.set_ocupado(ejecutando)
        if ejecutando:
            GLib.idle_add(self._enfocar_terminal)

    def _enfocar_terminal(self):
        self.term.grab_focus()
        return False

    def _ejecutando(self):
        return self.ctx is not None and self.ctx.get("fase") in ("preparar", "ejecutar")

    def run(self, item):
        if self._ejecutando():
            return
        if item.get("peligroso"):
            dlg = Adw.AlertDialog.new(
                "Confirmar",
                f"«{item['titulo']}» puede eliminar paquetes y archivos.\n\n¿Ejecutarlo?")
            dlg.add_response("no", "Cancelar")
            dlg.add_response("si", "Ejecutar")
            dlg.set_response_appearance("si", Adw.ResponseAppearance.DESTRUCTIVE)
            dlg.set_default_response("no")
            dlg.set_close_response("no")
            dlg.connect("response", lambda _d, r: r == "si" and self.iniciar(item))
            dlg.present(self)
            return
        self.iniciar(item)

    def iniciar(self, item):
        modo = item.get("modo", "auto")
        if modo not in MODOS:
            modo = "auto"
        local = bool(item.get("local"))
        dest = ROOT if local else self.base / repo_name(item["repo"])
        script = dest / item["script"]
        gui = modo == "gui"
        self.ctx = {"item": item, "modo": modo, "dest": dest, "script": script,
                    "fase": "preparar" if (gui and not local) else "ejecutar",
                    "cancelado": False}

        self.term.reset(True, True)
        self.pagina_run.set_title(item["titulo"])
        self._estado("run", "En ejecución…")
        self._marcar(item, "run", "En ejecución…")
        self._controles(True)
        self.nav.push_by_tag("ejecucion")

        if local and not script.is_file():
            self._fin(f"No existe el script: {script}", "Falló")
            return
        if local and gui:
            self._lanzar_gui(script)
            return
        if local:
            self._sistema("▶ Ejecutando el script local…")
            self._spawn(["bash", str(script)])
        elif gui:
            self._sistema("▶ Preparando el proyecto (git)…")
            self._spawn(["bash", "-c", PREPARAR, "_", str(dest), item["repo"], item["script"]])
        else:
            self._sistema("▶ Preparando y ejecutando el proyecto…")
            self._spawn(["bash", "-c", PREPARAR + 'exec bash "$d/$s"', "_",
                         str(dest), item["repo"], item["script"]])

    def _spawn(self, argv):
        self.child_pid = None
        self.term.spawn_async(
            Vte.PtyFlags.DEFAULT, str(Path.home()), argv, entorno(),
            GLib.SpawnFlags.DEFAULT, None, None, -1, None, self._spawn_listo)

    def _spawn_listo(self, _term, pid, error):
        if error is not None:
            self._fin(f"No se pudo iniciar: {error.message}", "Falló")
            return
        self.child_pid = pid

    def _terminado(self, _term, status):
        ctx = self.ctx
        if ctx is None:
            return
        rc = os.waitstatus_to_exitcode(status)
        self._quitar_timers()
        self.child_pid = None
        if ctx["cancelado"]:
            self._fin("Cancelado por el usuario.", "Cancelado", off=True)
        elif ctx["fase"] == "preparar":
            if rc != 0:
                self._fin("No se pudo preparar el proyecto.", f"Falló (código {rc})")
            else:
                self._lanzar_gui(ctx["script"])
        elif rc == 0:
            self._fin("El script terminó correctamente.", "Completado", ok=True)
        else:
            self._fin(f"El script terminó con código {rc}.", f"Falló (código {rc})")

    # --- cancelar / matar

    def cancelar(self):
        if not self._ejecutando() or self.ctx["cancelado"]:
            return
        self.ctx["cancelado"] = True
        self._sistema("Cancelando…", "33")
        # Ctrl+C por la propia terminal: llega al grupo en primer plano aunque
        # el script esté corriendo comandos como root (sudo/dnf).
        self.term.feed_child(b"\x03")
        self._timers["term"] = GLib.timeout_add_seconds(4, self._escalar, "term", signal.SIGTERM)
        self._timers["kill"] = GLib.timeout_add_seconds(8, self._escalar, "kill", signal.SIGKILL)

    def _escalar(self, nombre, sig):
        self._timers.pop(nombre, None)
        self._senal(sig)
        return False

    def _senal(self, sig):
        if self.child_pid is None:
            return
        try:
            os.killpg(os.getpgid(self.child_pid), sig)
        except (ProcessLookupError, PermissionError, OSError):
            pass

    def _quitar_timers(self):
        for nombre in list(self._timers):
            GLib.source_remove(self._timers.pop(nombre))

    # --- scripts con interfaz gráfica propia (modo "gui")

    def _lanzar_gui(self, script):
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ruta = LOG_DIR / f"{script.stem}.log"
        try:
            with open(ruta, "wb") as salida:
                proc = subprocess.Popen(
                    ["bash", str(script)], stdin=subprocess.DEVNULL,
                    stdout=salida, stderr=subprocess.STDOUT,
                    start_new_session=True, cwd=str(Path.home()))
        except OSError as err:
            self._fin(f"No se pudo iniciar: {err}", "Falló")
            return
        self.ctx.update(fase="gui", proc_gui=proc, log_gui=ruta)
        self._sistema("▶ Abriendo la aplicación (sin terminal)…")
        GLib.timeout_add_seconds(3, self._comprobar_gui)

    def _comprobar_gui(self):
        ctx = self.ctx
        if ctx is None or ctx.get("fase") != "gui":
            return False
        rc = ctx["proc_gui"].poll()
        if rc in (None, 0):
            self._fin("Aplicación iniciada. Puedes cerrar esta vista.",
                      "Iniciada", ok=True)
            return False
        try:
            cola = ctx["log_gui"].read_text(encoding="utf-8", errors="replace")[-3000:]
        except OSError:
            cola = ""
        if cola:
            self._sistema("Salida del script:", "33")
            self.term.feed(cola.replace("\n", "\r\n").encode())
        self._fin(f"La aplicación terminó con código {rc}.", f"Falló (código {rc})")
        return False

    # --- fin de una ejecución

    def _marcar(self, item, tipo, texto):
        fila = self._fila_de(item)
        if fila is not None:
            fila.set_estado(tipo, texto)

    def _fin(self, mensaje, estado, ok=False, off=False):
        item = self.ctx.get("item") if self.ctx else None
        self._sistema(mensaje, "32" if ok else ("33" if off else "31"))
        tipo = "ok" if ok else ("off" if off else "error")
        self._estado(tipo, estado)
        if item is not None:
            self._marcar(item, tipo, estado)
            if ok:
                self.toasts.add_toast(Adw.Toast.new(f"{item['titulo']}: {estado.lower()}"))
        self._quitar_timers()
        self.ctx = None
        self._controles(False)

    def volver(self):
        if not self._ejecutando():
            self.nav.pop()

    # ----------------------------------------------------------------- cierre

    def _on_close(self, _ventana):
        if self.cerrar_forzado or not self._ejecutando():
            return False
        dlg = Adw.AlertDialog.new("Salir", "Hay un script en ejecución. ¿Cancelarlo y salir?")
        dlg.add_response("no", "Seguir")
        dlg.add_response("si", "Cancelar y salir")
        dlg.set_response_appearance("si", Adw.ResponseAppearance.DESTRUCTIVE)
        dlg.set_default_response("no")
        dlg.set_close_response("no")
        dlg.connect("response", self._salir_respuesta)
        dlg.present(self)
        return True

    def _salir_respuesta(self, _dlg, respuesta):
        if respuesta == "si":
            self.cerrar_forzado = True
            self._senal(signal.SIGTERM)
            self.close()


def aviso_fatal(app, titulo, texto):
    """Ventana mínima con un mensaje de error; se cierra con el botón de la barra."""
    ventana = Adw.ApplicationWindow(application=app, title=TITULO)
    ventana.set_default_size(520, 460)
    vista = Adw.ToolbarView()
    vista.add_top_bar(Adw.HeaderBar())
    vista.set_content(Adw.StatusPage(icon_name="dialog-error-symbolic",
                                     title=titulo, description=esc(texto)))
    ventana.set_content(vista)
    ventana.present()


class Aplicacion(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.connect("activate", self._activar)

    def _activar(self, app):
        ventana = app.get_active_window()
        if ventana is not None:
            ventana.present()
            return
        if os.geteuid() == 0:
            aviso_fatal(app, "No como root",
                        "Ejecuta el lanzador como usuario normal; "
                        "los scripts piden sudo por sí mismos.")
            return
        try:
            ventana = Ventana(app, CONFIG)
        except OSError as err:
            aviso_fatal(app, "Error de configuración",
                        f"No se pudo iniciar la configuración:\n{err}")
            return
        ventana.present()


def main():
    return Aplicacion().run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
