# 📊 Reportes de Análisis

Esta carpeta contiene la **documentación estática** de los análisis realizados en el proyecto.

## 🎯 Propósito

Los reportes aquí documentan las **conclusiones específicas** basadas en ejecuciones particulares del proyecto. A diferencia de los notebooks (que son código ejecutable), estos reportes capturan el estado del análisis en un momento específico.

## 📁 Estructura

```bash
reports/
├── 01_eda/
│   ├── report_latest.html    # Último reporte HTML generado
│   ├── ANALYSIS.md           # Documento de análisis con conclusiones (versionado)
│   └── README.md             # Metadatos y changelog de los reportes
├── 02_feature_engineering/
│   ├── report_latest.html    # Último reporte HTML generado
│   ├── ANALYSIS.md           # Documento de análisis con conclusiones (versionado)
│   └── README.md             # Metadatos y changelog de los reportes
├── 03_modeling/
│   ├── report_latest.html    # Último reporte HTML generado
│   ├── ANALYSIS.md           # Documento de análisis con conclusiones (versionado)
│   └── README.md             # Metadatos y changelog de los reportes
└── README.md                  # Este archivo
```

## 🔄 Cómo generar reportes

Después de ejecutar un notebook y obtener conclusiones:

1. **Generar reporte HTML:**

   ```bash
   # Para EDA
   python -m src.utils.generate_report notebooks/01_eda.ipynb

   # Para Feature Engineering
   python -m src.utils.generate_report notebooks/02_feature_engineering.ipynb

   # Para Modelado
   python -m src.utils.generate_report notebooks/03_modeling.ipynb
   ```

2. **Documentar conclusiones:**
   - Abrir `reports/[notebook_name]/ANALYSIS.md`
   - Copiar las conclusiones del notebook ejecutado
   - Completar con hallazgos y observaciones

3. **Versionar:**
   - Los reportes HTML se generan con timestamp (p. ej. `01_eda_report_20260130_120000.html`)
   - El script crea un enlace simbólico `report_latest.html` → último HTML generado (solo válido en tu máquina tras ejecutar `generate_report`)
   - **Estrategia:** Los archivos `.html` con timestamp no se versionan (están en `.gitignore`). Se versionan los `.md` (ANALYSIS.md, README.md). Si necesitás compartir un reporte HTML, generarlo y adjuntarlo por otro medio o publicarlo aparte; el symlink `report_latest.html` no se commitea para evitar enlaces rotos en otros clones.

## ⚠️ Importante

- **Los notebooks son código ejecutable** → deben funcionar con cualquier dataset
- **Los reportes son documentación estática** → capturan conclusiones de ejecuciones específicas
- **No hardcodear conclusiones en el código** → usar reportes para documentarlas
