![CleanSweep](https://github.com/user-attachments/assets/b5586e9f-88c9-498f-ac9d-097925ec9a9a)

# CleanSweep 🧹

CleanSweep es una herramienta sencilla pero eficaz diseñada para limpiar archivos temporales y "basura" de sistemas Windows, liberando espacio en disco y mejorando el rendimiento. También permite seleccionar directorios personalizados para eliminar archivos no deseados.

## Características ✨

- Limpieza automática de directorios temporales comunes como `%TEMP%`, `C:\Windows\Temp`, y `C:\Windows\Prefetch`.
- Posibilidad de añadir directorios personalizados para su limpieza.
- Progreso en tiempo real con una interfaz atractiva usando la biblioteca [Rich](https://github.com/Textualize/rich).
- Visualización gráfica del espacio liberado.
- Opción para crear un acceso directo en el escritorio para un uso rápido.
- Interfaz de usuario en modo texto (TUI) moderna y fácil de usar.
  
## Instalación 🛠️

1. Clona este repositorio:

    ```bash
    git clone https://github.com/tuusuario/CleanSweep.git
    cd CleanSweep
    ```

2. Instala las dependencias requeridas:

    ```bash
    pip install -r requirements.txt
    ```

## Uso 🚀

Para ejecutar CleanSweep, simplemente ejecuta el siguiente comando en tu terminal:

```bash
python tempXterminator.py
