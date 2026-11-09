# Guía de instalación y primeros pasos

Esta guía explica cómo descargar el proyecto, revisar los componentes y ejecutar los scripts en Fedora Workstation con GNOME.

## 1. Antes de empezar

1. Confirma que utilizas Fedora Workstation con GNOME.
2. Comprueba que tu usuario puede utilizar \`sudo\`.
3. Guarda tu trabajo y realiza una copia de seguridad de los datos importantes.
4. Lee el manual del componente que vayas a ejecutar.
5. Mantén una conexión estable a Internet.

No ejecutes estos scripts directamente como \`root\`. Están preparados para iniciarse desde una sesión de usuario normal y solicitar permisos administrativos mediante \`sudo\`.

## 2. Descargar el repositorio

\`\`\`bash
sudo dnf install git
git clone https://github.com/csr79a/fedora-Gnome-setup.git
cd fedora-Gnome-setup
\`\`\`

Para actualizar una copia ya descargada:

\`\`\`bash
cd fedora-Gnome-setup
git pull --ff-only
\`\`\`

## 3. Ejecutar la configuración base

\`\`\`bash
chmod +x gnome/setup-fedora-base.sh
./gnome/setup-fedora-base.sh
\`\`\`

El componente base contempla:

- Preparación de la configuración general del sistema.
- RPM Fusion y componentes multimedia.
- Microcódigo de CPU Intel/AMD.
- Detección de GPU y códecs por hardware.
- Configuración de Flatpak para utilizar Flathub.
- GNOME Tweaks (Retoques) y Gestor de extensiones.

El script acumula avisos y fallos y presenta un resumen al terminar. Consulta ese resumen antes de continuar.

### Opción MESA_FROM_TESTING

El script documenta una opción para los primeros días de una nueva versión de Fedora, cuando RPM Fusion puede ir por delante de los repositorios de Fedora:

\`\`\`bash
MESA_FROM_TESTING=1 ./gnome/setup-fedora-base.sh
\`\`\`

Utilízala únicamente si se da esa situación y has revisado el comportamiento del script.

## 4. Instalar el controlador NVIDIA

Solo si el equipo dispone de una GPU NVIDIA:

\`\`\`bash
chmod +x nvidia/setup-nvidia.sh
./nvidia/setup-nvidia.sh
\`\`\`

El flujo descrito por el propio script es:

1. Ejecutar la instalación.
2. Reiniciar cuando el script lo indique.
3. Volver a la carpeta del repositorio y verificar:

\`\`\`bash
./nvidia/setup-nvidia.sh --verify
\`\`\`

El script comprueba Secure Boot, instala los componentes del controlador y verifica el renderizado OpenGL y PRIME Render Offload. Si Secure Boot está activo, puede ser necesario resolver la firma del módulo antes de que el controlador cargue.

El encabezado del script indica que está destinado a Fedora Workstation y que no soporta variantes Atomic (Silverblue/Kinoite).

## 5. Configurar ASUS / ROG

Solo para equipos ASUS compatibles:

\`\`\`bash
chmod +x asus/setup-asusctl.sh
./asus/setup-asusctl.sh
\`\`\`

El script configura asusctl/asusd y componentes relacionados. Puede habilitar el repositorio Terra de Fyra Labs. Algunas funciones dependen del hardware y de los servicios disponibles. Lee las preguntas interactivas y no confirmes instalaciones que no necesites.

## 6. Instalar herramientas gaming

\`\`\`bash
chmod +x gaming/setup-gaming-fedora.sh
./gaming/setup-gaming-fedora.sh
\`\`\`

El script instala o configura Steam, ProtonPlus, Heroic Games Launcher, GameMode, MangoHud, GOverlay, el wrapper \`game-performance\`, \`vm.max_map_count\` y soporte ntsync cuando el kernel lo permite.

En Steam, la opción de lanzamiento sugerida por el script es:

\`\`\`text
gamemoderun mangohud %command%
\`\`\`

Para usar el wrapper adicional:

\`\`\`text
game-performance gamemoderun mangohud %command%
\`\`\`

## 7. Usar la interfaz gráfica

Instala las dependencias:

\`\`\`bash
sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4
\`\`\`

Ejecuta desde la raíz del repositorio:

\`\`\`bash
python3 fedora_gnome_setup_gui.py
\`\`\`

La aplicación ejecuta los scripts en una terminal VTE integrada. No la inicies como root: cada script administra sus propios permisos.

**Rutas de la GUI:** las acciones locales están configuradas para utilizar los scripts existentes en `gnome/`, `nvidia/`, `asus/` y `gaming/`.

## 8. Después de ejecutar

- Lee el resumen final de cada script.
- Atiende los avisos que indiquen que hace falta reiniciar.
- En NVIDIA, ejecuta \`--verify\` después del reinicio.
- Comprueba que las aplicaciones instaladas se abren correctamente.
- Si algo falla, conserva el mensaje de error completo y la salida de la terminal para diagnosticarlo.

## 9. Recuperación y precauciones

Estos scripts no sustituyen una copia de seguridad ni garantizan compatibilidad universal. Si un componente falla:

1. No repitas comandos de forma indiscriminada.
2. Copia el error y el resumen del script.
3. Comprueba qué repositorios y paquetes se modificaron.
4. Revisa el manual específico del componente.
5. Si el problema afecta al arranque o al controlador gráfico, utiliza un kernel anterior o un modo de recuperación de Fedora según corresponda.

No elimines repositorios, paquetes o archivos de configuración a ciegas: primero identifica qué componente los creó y qué otras aplicaciones dependen de ellos.
