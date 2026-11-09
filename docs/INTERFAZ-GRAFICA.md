# Manual de la interfaz gráfica

## 1. Descripción

\`fedora_gnome_setup_gui.py\` es una aplicación de escritorio para Fedora GNOME construida con GTK4, libadwaita y VTE. Su propósito es reunir los scripts del proyecto en una ventana con navegación por secciones y una terminal integrada.

La GUI no reemplaza los scripts ni reescribe su lógica: los ejecuta tal como están. Los permisos administrativos los solicita cada script mediante \`sudo\`.

## 2. Dependencias

Instala los paquetes necesarios:

\`\`\`bash
sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4
\`\`\`

## 3. Arranque

Desde la carpeta raíz del repositorio:

\`\`\`bash
python3 fedora_gnome_setup_gui.py
\`\`\`

No la ejecutes con \`sudo\` ni como root. La aplicación comprueba que se inicia desde una cuenta normal.

## 4. Terminal integrada

La salida de cada script aparece en una terminal VTE real. Esto permite conservar:

- Colores y mensajes de estado.
- Barras de progreso.
- Preguntas interactivas mediante \`read\`.
- Solicitudes de contraseña de \`sudo\`.
- Interfaces de texto como \`whiptail\` o \`dialog\`, cuando el script las utilice.

No cierres la aplicación mientras un script siga trabajando, salvo que quieras interrumpir el proceso.

## 5. Modos de ejecución

La configuración de cada acción admite un campo \`modo\`:

| Modo | Comportamiento |
|---|---|
| \`auto\` | Valor predeterminado: ejecuta dentro de la terminal integrada. |
| \`integrado\` | Ejecuta dentro de la terminal integrada. |
| \`terminal\` | También utiliza la terminal integrada; no abre otra terminal externa. |
| \`gui\` | Para un componente que abre su propia aplicación gráfica; se lanza sin terminal integrada. |

## 6. Registros

La aplicación define su directorio de registros en:

\`\`\`text
~/.local/share/fedora-gnome-setup/logs
\`\`\`

Si necesitas soporte, conserva el registro y el mensaje completo del error.

## 7. Configuración de acciones

Las acciones se declaran en el diccionario \`CONFIG\` del archivo Python. Cada elemento incluye datos como:

- \`seccion\`: grupo que aparece en la navegación.
- \`titulo\`: nombre visible.
- \`descripcion\`: explicación breve.
- \`script\`: ruta del script.
- \`local\`: indica si el componente se resuelve como archivo local del proyecto.
- \`modo\`: modo de ejecución opcional.

La ruta del script se interpreta respecto al directorio raíz del archivo Python.

### Corrección necesaria en la configuración actual

La acción «Configurar Fedora» declara:

\`\`\`python
"script": "gnome/setup-fedora-base.sh"
\`\`\`

Pero el archivo del repositorio está ubicado en:

\`\`\`text
gnome/setup-fedora-base.sh
\`\`\`

La ruta correcta en `CONFIG` es:

\`\`\`python
"script": "gnome/setup-fedora-base.sh"
\`\`\`

Guarda el archivo y vuelve a iniciar la aplicación.

## 8. Solución de problemas

### La aplicación no arranca

Comprueba las dependencias:

\`\`\`bash
sudo dnf install python3-gobject gtk4 libadwaita vte291-gtk4
\`\`\`

Ejecuta desde una terminal para ver el error:

\`\`\`bash
python3 fedora_gnome_setup_gui.py
\`\`\`

### No encuentra un script

Comprueba que el archivo existe en la ruta configurada:

\`\`\`bash
ls -l gnome/setup-fedora-base.sh
ls -l nvidia/setup-nvidia.sh
ls -l asus/setup-asusctl.sh
ls -l gaming/setup-gaming-fedora.sh
\`\`\`

Revisa que el valor \`script\` de \`CONFIG\` coincida exactamente con la ruta relativa desde la raíz del repositorio.

### No aparece el diálogo de contraseña

La aplicación debe ejecutarse como usuario normal y el script debe solicitar sudo dentro de la terminal VTE. No inicies la GUI como root para evitar este problema.

### La terminal parece detenida

Algunos scripts esperan una respuesta o una contraseña. Revisa la terminal integrada antes de asumir que el proceso se ha bloqueado.

## 9. Alcance de las pruebas

Este manual describe el comportamiento declarado por el código actual. No implica que la aplicación haya sido probada en todas las versiones de Fedora, GTK4, libadwaita o VTE. La compatibilidad debe verificarse en el sistema de destino.
