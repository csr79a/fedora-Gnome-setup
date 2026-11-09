# Manual de componentes y scripts

Este documento describe qué hace cada componente del repositorio, cuándo utilizarlo y qué consideraciones tener en cuenta.

## 1. Configuración base — GNOME

**Archivo:** \`gnome/setup-fedora-base.sh\`

**Objetivo:** preparar una instalación de Fedora Workstation con GNOME con los componentes generales del sistema.

### Funciones documentadas

- Configuración base del sistema.
- RPM Fusion y multimedia.
- Microcódigo de CPU con detección Intel/AMD.
- Detección de GPU y códecs por hardware para AMD, Intel y NVIDIA.
- Flatpak: retirar el remoto de Fedora y dejar Flathub.
- Herramientas GNOME: Retoques desde RPM de Fedora y Gestor de extensiones desde Flathub.

### Ejecución

\`\`\`bash
./gnome/setup-fedora-base.sh
\`\`\`

Opción especial documentada:

\`\`\`bash
MESA_FROM_TESTING=1 ./gnome/setup-fedora-base.sh
\`\`\`

### Resultado y códigos de salida

- \`0\`: terminó sin fallos críticos, aunque puede haber avisos.
- \`1\`: hubo al menos un fallo o el sistema no es Fedora con GNOME.

Los avisos y fallos se acumulan para mostrarse en el resumen final. Revisa ese resumen incluso si el código de salida es cero.

## 2. Controlador NVIDIA

**Archivo:** \`nvidia/setup-nvidia.sh\`

**Objetivo:** instalar y verificar el soporte NVIDIA.

### Funciones documentadas

- Detección de GPU NVIDIA.
- Comprobación de Secure Boot.
- RPM Fusion Free y Nonfree.
- Instalación de \`akmod-nvidia\`.
- \`xorg-x11-drv-nvidia-cuda\`, que aporta \`nvidia-smi\` y bibliotecas CUDA.
- \`libva-nvidia-driver\`.
- Herramientas \`glx-utils\` / \`glxinfo\`.
- Wrapper \`nvidia-run\` para PRIME Render Offload.
- Verificación del renderizado OpenGL.

### Modos de uso

Instalación/actualización:

\`\`\`bash
./nvidia/setup-nvidia.sh
\`\`\`

Solo verificación:

\`\`\`bash
./nvidia/setup-nvidia.sh --verify
\`\`\`

Ayuda:

\`\`\`bash
./nvidia/setup-nvidia.sh --help
\`\`\`

### Flujo recomendado

1. Ejecuta el modo normal.
2. Espera a que el proceso de compilación de módulos termine según indique el script.
3. Reinicia si se solicita.
4. Ejecuta \`--verify\`.

### Limitaciones

El encabezado del script indica que no soporta Silverblue/Kinoite y lo describe como Fedora Workstation/KDE. Aunque se mantiene como componente independiente de Plasma y Gaming, no se debe asumir compatibilidad completa con todas las sesiones GNOME sin probarlo en el equipo de destino.

Códigos de salida documentados:

- \`0\`: instalación/verificación correcta, instalación pendiente de reinicio indicada por el script o ausencia de GPU NVIDIA.
- \`1\`: error o cancelación del usuario.
- \`3\`: controlador no funcional sin que un reinicio pendiente lo explique, o verificación fallida.

## 3. ASUS / ROG

**Archivo:** \`asus/setup-asusctl.sh\`

**Objetivo:** configurar herramientas de control para hardware ASUS compatible.

### Funciones documentadas

- asusctl / asusd.
- ROG Control Center.
- Cardwire para gestión de GPU híbrida.
- Habilitación del repositorio Terra de Fyra Labs cuando sea necesario.
- GUI opcional \`cardwire-gui\`; el script indica que la CLI y el demonio pueden utilizarse sin esa GUI.

### Ejecución

\`\`\`bash
./asus/setup-asusctl.sh
\`\`\`

El script es interactivo: puede preguntar si deseas instalar o activar componentes. Responde según el hardware real de tu equipo.

### Consideraciones

- Es un componente independiente del script base.
- Está pensado para hardware ASUS compatible; no aporta utilidad a todos los equipos.
- Cardwire puede requerir que el LSM \`bpf\` esté activo para que su demonio arranque.
- Utiliza Terra, un repositorio de terceros. Valora esa dependencia antes de habilitarlo.

Códigos de salida documentados en el encabezado:

- \`0\`: correcto, hardware ASUS ausente o el usuario omitió las acciones.
- \`1\`: error al habilitar Terra o instalar/activar asusctl o Cardwire.

## 4. Gaming

**Archivo:** \`gaming/setup-gaming-fedora.sh\`

**Objetivo:** instalar herramientas y aplicar ajustes de compatibilidad para juegos en Fedora.

### Componentes

| Elemento | Función |
|---|---|
| RPM Fusion Free/Nonfree | Repositorios necesarios para obtener Steam en este flujo. |
| Steam | Plataforma de juegos. |
| ProtonPlus | Gestor de builds de compatibilidad, incluidas builds de Proton-GE. |
| Heroic Games Launcher | Lanzador para bibliotecas de juegos compatibles; descarga el último RPM publicado en GitHub. |
| GameMode | Solicita ajustes de rendimiento mientras se ejecuta un juego. |
| MangoHud | Overlay de métricas durante el juego. |
| GOverlay | Interfaz gráfica para configurar MangoHud. |
| \`game-performance\` | Wrapper que inhibe suspensión/inactividad y cambia temporalmente el perfil de energía cuando \`powerprofilesctl\` está disponible. |
| \`vm.max_map_count\` | Ajuste de compatibilidad utilizado por algunos juegos y herramientas. |
| ntsync | Comprueba e intenta cargar el módulo si el kernel lo proporciona. |

### Ejecución

\`\`\`bash
./gaming/setup-gaming-fedora.sh
\`\`\`

### Opciones de lanzamiento en Steam

Combinación sugerida:

\`\`\`text
gamemoderun mangohud %command%
\`\`\`

Para usar el wrapper:

\`\`\`text
game-performance gamemoderun mangohud %command%
\`\`\`

### Notas técnicas

- ProtonPlus se obtiene del COPR \`wehagy/protonplus\`.
- Heroic consulta la API de releases de su repositorio oficial de GitHub para localizar el RPM más reciente.
- GameMode crea \`/etc/gamemode.ini\` con \`renice=10\` solo si el archivo no existe; no sobrescribe una configuración existente.
- \`game-performance\` se instala en \`/usr/local/bin/game-performance\`. Si ya existe un archivo que no parece gestionado por este script, no lo sobrescribe.
- El ajuste de sysctl se guarda en \`/etc/sysctl.d/80-gamecompatibility.conf\`.
- ntsync solo se configura si el módulo y el dispositivo \`/dev/ntsync\` están disponibles. La disponibilidad depende del kernel.

## 5. Interfaz gráfica GTK4

**Archivo:** \`fedora_gnome_setup_gui.py\`

**Objetivo:** reunir acciones de configuración en una aplicación GNOME con terminal integrada.

### Dependencias

\`\`\`bash
sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4
\`\`\`

### Ejecución

Desde la raíz del repositorio:

\`\`\`bash
python3 fedora_gnome_setup_gui.py
\`\`\`

### Comportamiento documentado

- Utiliza GTK4, libadwaita y VTE.
- Hereda el tema de GNOME; no define una hoja de estilos propia.
- Ejecuta los scripts como usuario normal.
- Muestra la salida en una terminal real, con colores, progreso, preguntas y solicitudes de sudo.
- Contempla los modos \`auto\`, \`integrado\`, \`terminal\` y \`gui\` en la configuración de cada acción.
- Guarda registros bajo \`~/.local/share/fedora-gnome-setup/logs\`.

### Rutas de acciones

La configuración actual apunta a estas rutas:

- \`base/setup-fedora-base.sh\`
- \`nvidia/setup-nvidia.sh\`
- \`asus/setup-asusctl.sh\`
- \`gaming/setup-gaming-fedora.sh\`

En el repositorio, el script base está realmente en \`gnome/setup-fedora-base.sh\`. Es necesario cambiar la ruta de la acción base en \`CONFIG\` a \`gnome/setup-fedora-base.sh\` para que la GUI encuentre el archivo.

## 6. Qué componente debo ejecutar

| Situación | Componente |
|---|---|
| Instalación nueva de Fedora GNOME | Sistema base |
| Equipo con GPU NVIDIA | NVIDIA, además del sistema base |
| Portátil ASUS/ROG compatible | ASUS / ROG |
| Quiero Steam, Proton, MangoHud y GameMode | Gaming |
| Prefiero ejecutar las tareas desde una ventana | Interfaz gráfica, después de revisar sus rutas |

No es necesario ejecutar todos los componentes. Elige los que correspondan a tu hardware y objetivo.
