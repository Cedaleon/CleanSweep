import os
import shutil
import time
import psutil
import win32com.client
import tkinter as tk
from tkinter import filedialog
from rich import print
from rich.console import Console, Group
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich.style import Style
from rich.prompt import Prompt

# Inicialización de la consola de Rich
console = Console()

def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def eliminar_archivos(directorio):
    eliminados = 0
    espacio_liberado = 0
    for root, dirs, files in os.walk(directorio):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                size = os.path.getsize(file_path)
                os.remove(file_path)
                eliminados += 1
                espacio_liberado += size
            except PermissionError:
                pass
        for name in dirs:
            dir_path = os.path.join(root, name)
            try:
                size = get_size(dir_path)
                shutil.rmtree(dir_path)
                eliminados += 1
                espacio_liberado += size
            except PermissionError:
                pass
    return eliminados, espacio_liberado

def crear_layout():
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    return layout

def actualizar_layout(layout, header, main, footer):
    layout["header"].update(Panel(header, border_style="bold cyan"))
    layout["main"].update(Align.center(main, vertical="middle"))
    layout["footer"].update(Panel(footer, border_style="bold cyan"))

def crear_acceso_directo():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path = os.path.join(desktop, "Limpiador de Temporales.lnk")
    target = os.path.abspath(__file__)
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = os.path.dirname(target)
    shortcut.save()

def seleccionar_directorio():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter
    directorio = filedialog.askdirectory()
    return directorio

def limpiar_temporales():
    layout = crear_layout()

    # Título de inicio
    header = Text("🧹 Limpieza de Archivos Temporales", style="bold cyan", justify="center")
    
    progress = Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(complete_style="green", finished_style="green"),
        "[green][progress.percentage]{task.percentage:>3.0f}%",
    )

    directorios_default = [("%Temp%", os.getenv("TEMP")),
                           ("Temp", r"C:\Windows\Temp"),
                           ("Prefetch", r"C:\Windows\Prefetch")]

    # Opción para agregar directorios personalizados
    agregar_custom = Prompt.ask("¿Desea agregar directorios personalizados? (s/n)")
    if agregar_custom.lower() == 's':
        while True:
            print("Seleccione un directorio o presione Cancelar para terminar.")
            custom_dir = seleccionar_directorio()
            if not custom_dir:  # Si el usuario cancela la selección
                break
            if os.path.isdir(custom_dir):
                directorios_default.append((os.path.basename(custom_dir), custom_dir))
                print(f"[bold green]Directorio agregado: {custom_dir}[/bold green]")
            else:
                print(f"[bold red]El directorio {custom_dir} no existe.[/bold red]")

    table = Table(show_header=True, header_style="bold magenta", expand=True, width=80)
    table.add_column("Directorio", style="cyan", justify="center")
    table.add_column("Archivos/Carpetas Eliminados", justify="center")
    table.add_column("Espacio Liberado", justify="center")

    total_eliminados = 0
    total_espacio_liberado = 0

    # Preparar el contenido inicial
    contenido_inicial = Panel("Iniciando limpieza...", border_style="green", style="bold")

    with Live(layout, refresh_per_second=4, screen=True, auto_refresh=False) as live:
        # Configurar el diseño inicial
        actualizar_layout(layout, header, contenido_inicial, "Preparando...")
        live.refresh()

        for nombre, directorio in directorios_default:
            task = progress.add_task(f"[cyan]Limpiando {nombre}...", total=100)
            
            eliminados, espacio_liberado = eliminar_archivos(directorio)
            total_eliminados += eliminados
            total_espacio_liberado += espacio_liberado

            progress.update(task, advance=100)
            table.add_row(
                nombre, 
                f"[bold green]{eliminados}[/bold green]",
                f"[bold green]{espacio_liberado / (1024*1024):.2f} MB[/bold green]"
            )

            actualizar_layout(layout, header, progress, f"Limpiando {nombre}...")
            live.refresh()
            time.sleep(0.5)  # Pausa reducida para una experiencia más fluida

        # Resultados finales
        table.add_row("", "", "")
        table.add_row(
            "[bold green]Total", 
            f"[bold green]{total_eliminados}[/bold green]",
            f"[bold green]{total_espacio_liberado / (1024*1024):.2f} MB[/bold green]"
        )

        resultado = Panel(
            table,
            title="📊 Resultados de la Limpieza",
            border_style="green",
            expand=False,
            width=82
        )

        # Visualización gráfica del espacio liberado
        total_disk_space = psutil.disk_usage('/').total
        percent_freed = (total_espacio_liberado / total_disk_space) * 100
        space_graph = Progress(
            TextColumn("[bold]Espacio liberado:"),
            BarColumn(complete_style="green"),
            TextColumn("[green]{task.percentage:.2f}%")
        )
        space_task = space_graph.add_task("", total=100)
        space_graph.update(space_task, completed=percent_freed)

        # Crear un nuevo Panel para el mensaje final
        mensaje_final = Panel(
            Group(
                Align.center(Text("✨ Limpieza completada ✨", style="bold green")),
                Text(),  # Línea en blanco
                space_graph,
                Text(),  # Línea en blanco
                Align.center(Text("Presione Enter para salir", style="italic cyan"))
            ),
            border_style="green",
            width=60,
            expand=False
        )

        # Combinar el resultado y el mensaje final en un grupo
        contenido_final = Group(
            resultado,
            Text("\n"),  # Agregar un espacio entre los paneles
            Align.center(mensaje_final)  # Centrar el panel del mensaje final
        )

        actualizar_layout(layout, header, contenido_final, "")
        live.refresh()
        
        # Esperar a que el usuario presione Enter
        input()

    # Preguntar si desea crear un acceso directo
    crear_acceso = Prompt.ask("¿Desea crear un acceso directo en el escritorio? (s/n)")
    if crear_acceso.lower() == 's':
        crear_acceso_directo()
        print("[bold green]Acceso directo creado en el escritorio.[/bold green]")

if __name__ == "__main__":
    # Configuramos la codificación sin mostrar ningún mensaje
    os.system('chcp 65001 >nul 2>&1')
    limpiar_temporales()
