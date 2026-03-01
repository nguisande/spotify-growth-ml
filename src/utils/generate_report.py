"""
Script para generar reportes HTML desde notebooks ejecutados.

Uso:
    python -m src.utils.generate_report notebooks/01_eda.ipynb
    python -m src.utils.generate_report notebooks/02_feature_engineering.ipynb
    python -m src.utils.generate_report notebooks/03_modeling.ipynb
"""
import sys
from pathlib import Path
from datetime import datetime
import subprocess


def generate_html_report(notebook_path: Path, output_dir: Path = None):
    """
    Genera un reporte HTML desde un notebook ejecutado.
    
    Args:
        notebook_path: Ruta al notebook (.ipynb)
        output_dir: Directorio de salida (default: reports/{notebook_name}/)
    """
    notebook_path = Path(notebook_path)
    
    if not notebook_path.exists():
        raise FileNotFoundError(f"No se encontró el notebook: {notebook_path}")
    
    # Determinar directorio de salida
    if output_dir is None:
        notebook_name = notebook_path.stem
        base_dir = notebook_path.resolve().parent.parent
        output_dir = base_dir / "reports" / notebook_name
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{notebook_path.stem}_report_{timestamp}.html"
    
    # Ejecutar nbconvert
    cmd = [
        "jupyter", "nbconvert",
        "--to", "html",
        "--output", str(output_file),
        "--execute",  # Ejecutar el notebook antes de convertir
        str(notebook_path)
    ]
    
    print(f"Generando reporte HTML desde {notebook_path.name}...")
    print(f"Salida: {output_file}")
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Reporte generado exitosamente: {output_file}")
        
        # Crear symlink al último reporte
        latest_link = output_dir / "report_latest.html"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(output_file.name)
        print(f"✅ Enlace creado: {latest_link}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al generar reporte: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: jupyter-nbconvert no encontrado. Instalá con: pip install nbconvert")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m src.utils.generate_report <notebook_path> [output_dir]")
        sys.exit(1)
    
    notebook_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    generate_html_report(notebook_path, output_dir)
