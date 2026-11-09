# Fedora GNOME Setup

Colección de scripts para preparar y configurar **Fedora Workstation con GNOME**. Incluye configuración base del sistema, soporte NVIDIA, herramientas para equipos ASUS/ROG y un conjunto de herramientas gaming. También incorpora una interfaz gráfica GTK4/libadwaita para ejecutar los componentes desde una terminal integrada.

> **Importante:** revisa cada script y sus avisos antes de ejecutarlo. Los scripts realizan cambios en el sistema, habilitan repositorios e instalan paquetes mediante \`sudo\`.

## Contenido

| Componente | Archivo | Función |
|---|---|---|
| Sistema base | [\`gnome/setup-fedora-base.sh\`](gnome/setup-fedora-base.sh) | Configuración inicial de Fedora GNOME, RPM Fusion, multimedia, microcódigo, GPU, Flathub y herramientas GNOME. |
| NVIDIA | [\`nvidia/setup-nvidia.sh\`](nvidia/setup-nvidia.sh) | Instalación y verificación del controlador NVIDIA, akmods y PRIME Render Offload. |
| ASUS / ROG | [\`asus/setup-asusctl.sh\`](asus/setup-asusctl.sh) | Configuración de asusctl/asusd, ROG Control Center y Cardwire para hardware ASUS compatible. |
| Gaming | [\`gaming/setup-gaming-fedora.sh\`](gaming/setup-gaming-fedora.sh) | Steam, ProtonPlus, Heroic, GameMode, MangoHud, GOverlay y ajustes de compatibilidad. |
| Interfaz gráfica | [\`fedora_gnome_setup_gui.py\`](fedora_gnome_setup_gui.py) | Lanzador GTK4/libadwaita con terminal VTE integrada. |

## Requisitos generales

- Fedora Workstation (edición GNOME) en una instalación convencional.
- Cuenta de usuario con permisos de administrador mediante \`sudo\`.
- Conexión a Internet.
- Espacio suficiente para descargar e instalar paquetes.
- No ejecutar los scripts como usuario \`root\`: cada componente solicita elevación cuando la necesita.

Las variantes Atomic, como Silverblue, no están soportadas por todos los componentes. Consulta el manual de cada script antes de usarlo.

## Inicio rápido: scripts

Clona el repositorio:

\`\`\`bash
git clone https://github.com/csr79a/fedora-Gnome-setup.git
cd fedora-Gnome-setup
\`\`\`

Da permisos de ejecución y lanza el componente que necesites. Por ejemplo, configuración base:

\`\`\`bash
chmod +x gnome/setup-fedora-base.sh
./gnome/setup-fedora-base.sh
\`\`\`

Gaming:

\`\`\`bash
chmod +x gaming/setup-gaming-fedora.sh
./gaming/setup-gaming-fedora.sh
\`\`\`

NVIDIA:

\`\`\`bash
chmod +x nvidia/setup-nvidia.sh
./nvidia/setup-nvidia.sh
\`\`\`

Para comprobar el controlador NVIDIA después de reiniciar:

\`\`\`bash
./nvidia/setup-nvidia.sh --verify
\`\`\`

ASUS / ROG:

\`\`\`bash
chmod +x asus/setup-asusctl.sh
./asus/setup-asusctl.sh
\`\`\`

## Interfaz gráfica

Instala las dependencias de la GUI:

\`\`\`bash
sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4
\`\`\`

Desde la raíz del repositorio:

\`\`\`bash
python3 fedora_gnome_setup_gui.py
\`\`\`

La aplicación debe ejecutarse como usuario normal. Los scripts se ejecutan en una terminal VTE integrada, por lo que pueden mostrar progreso, solicitar respuestas y pedir la contraseña de sudo.

**Nota sobre la configuración actual:** el archivo GUI configura la acción base con la ruta \`base/setup-fedora-base.sh\`, pero el script del repositorio está en \`gnome/setup-fedora-base.sh\`. Hasta corregir esa ruta en \`fedora_gnome_setup_gui.py\`, la acción «Configurar Fedora» de la GUI no encontrará el script base. Los demás componentes locales usan las rutas que coinciden con el árbol actual.

## Orden de ejecución recomendado

1. **Sistema base**: prepara repositorios, multimedia, microcódigo, GPU y herramientas GNOME.
2. **NVIDIA**: solo si el equipo tiene GPU NVIDIA. Instala el controlador y puede requerir reinicio; después ejecuta \`--verify\`.
3. **ASUS / ROG**: solo en hardware ASUS compatible. El script es independiente.
4. **Gaming**: instala el ecosistema de juegos. Puede habilitar RPM Fusion si todavía no está instalado.

No es obligatorio ejecutar todos los componentes. Elige únicamente los que correspondan a tu equipo y necesidades.

## Documentación

- [Guía de instalación y primeros pasos](docs/INSTALACION.md)
- [Manual de componentes y scripts](docs/COMPONENTES.md)
- [Manual de la interfaz gráfica](docs/INTERFAZ-GRAFICA.md)

## Seguridad y alcance

- Lee el contenido de los scripts antes de ejecutarlos.
- Los scripts pueden añadir repositorios de terceros, instalar paquetes y modificar configuración del sistema.
- El script ASUS utiliza el repositorio Terra de Fyra Labs.
- El script ProtonPlus utiliza el COPR \`wehagy/protonplus\`.
- Heroic se descarga desde la publicación más reciente de su repositorio oficial de GitHub.
- El script NVIDIA está orientado a Fedora Workstation. Revisa los requisitos y avisos del propio script antes de ejecutarlo.
- La documentación describe el contenido actual del repositorio; no implica que cada script haya sido probado en todas las versiones de Fedora o configuraciones de hardware.

## Licencia

No se ha declarado todavía una licencia en este repositorio. Si quieres permitir reutilización y redistribución, añade un archivo \`LICENSE\` con la licencia que elijas.
