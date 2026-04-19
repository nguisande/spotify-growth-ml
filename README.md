# Spotify Growth ML — Predicción de Popularidad y Señales de Engagement

## 📌 Descripción del proyecto

Este proyecto desarrolla un **pipeline profesional de Data Science orientado a Growth Marketing**, cuyo objetivo es **predecir el nivel de popularidad de canciones en Spotify** utilizando metadatos de la plataforma y señales de contexto asociadas a playlists y artistas.

El foco no está únicamente en el modelo final, sino en **todo el proceso end‑to‑end**: desde la ingesta de datos vía API con autenticación OAuth, pasando por la construcción de datasets versionados, el análisis exploratorio (EDA), el feature engineering y la preparación para modelos de Machine Learning.

El proyecto simula un caso real de negocio donde se busca anticipar el **potencial de engagement de un contenido** (en este caso, una canción), de forma análoga a cómo en Growth Marketing se predice el desempeño de campañas, productos o contenidos digitales.

---

## 🎯 Objetivos específicos

* Diseñar un **pipeline de ingesta robusto** utilizando la Spotify Web API con autenticación OAuth de usuario.
* Construir un **dataset estructurado y reproducible** a partir de playlists reales del usuario, playlist publicas y un search de canciones a partir de patrones. 
* Realizar un **análisis exploratorio profundo (EDA)** para entender la distribución de popularidad, sesgos de origen y calidad de datos.
* Definir un **target de Machine Learning** claro y justificado (clasificación de popularidad alta vs baja).
* Realizar un **feature engineering** basico para cerrar un dataset model-ready.
* Aplicar un **modelado supervisado** y comparacion de baselines.
* Preparar la base para futuras etapas de:
  * Feature engineering avanzado.
  * Integración de señales externas (ej. Google Trends).
  * Entrenamiento y evaluación de otros modelos de ML.

---

## 🚀 Motivación

La motivación principal del proyecto es **aprender a trabajar como un Científico de Datos profesional**, replicando prácticas reales de la industria:

* Manejo de APIs con autenticación OAuth.
* Diseño modular del código (clientes, scripts, notebooks).
* Versionado y persistencia de datos en formatos eficientes (Parquet).
* Separación clara entre datos crudos, intermedios y procesados.
* Documentación clara y reproducible del proyecto.

Además, el dominio de Spotify permite trabajar con un problema **realista, escalable y cercano al mundo de Growth Marketing**, donde el concepto de *popularidad* funciona como proxy de engagement, awareness e intención del usuario.

---

## 👥 Audiencia

Este proyecto está pensado para:

* **Recruiters y líderes técnicos** que quieran evaluar capacidades reales en Data Science.
* **Equipos de Growth / Marketing Analytics** interesados en modelos de predicción de performance.
* **Estudiantes de Data Science** que busquen un ejemplo completo y profesional de proyecto end‑to‑end.
* **Desarrolladores y analistas** que quieran aprender buenas prácticas de trabajo con APIs y pipelines de datos.

---

## 🗂️ Estructura del proyecto

```bash
spotify-growth-ml/
├── README.md
├── CHANGELOG.md
├── LICENCE
├── requirements.txt
├── .env.example
├── data/
│   ├── raw/              # Datos crudos obtenidos desde Spotify API
│   ├── interim/          # Datos intermedios (con target definido)
│   └── processed/        # Datos listos para modelado (futuro)
├── notebooks/
│   ├── 01_eda.ipynb      # Análisis exploratorio y definición del target
│   ├── 02_feature_engineering.ipynb   # Seleccion de features para modelado
│   └── 03_modeling.ipynb               # Modelado
│   └── 04_hypothesis.ipynb             # Validacion de hipotesis
├── src/
│   ├── config.py         # Configuración general y paths
│   ├── auth/
│   │   └── spotify_oauth.py   # Flujo OAuth con usuario
│   ├── data_ingestion/
│   │   ├── spotify_client.py
│   │   ├── build_spotify_raw_dataset.py              # Playlists del usuario
│   │   ├── build_spotify_raw_dataset_public_playlists.py       # Playlists publicas
│   │   ├── build_spotify_raw_dataset_search_tracks.py    # Tracks
│   │   └── merge_raw_datasets.py                     # Concatena y deduplica los tres
│   └── utils/
│       └── generate_report.py  # Script para generar reportes HTML
├── reports/              # Documentación estática de análisis
│   ├── 01_eda/
│   │   ├── report_latest.html  # Último reporte HTML generado
│   │   ├── ANALYSIS_YYYYMMDD.md         # Documento con conclusiones (versionado)
│   │   └── README.md           # Metadatos y changelog de los reportes
│   ├── 02_feature_engineering/
│   │   ├── report_latest.html  # Último reporte HTML generado
│   │   ├── ANALYSIS_YYYYMMDD.md         # Documento con conclusiones (versionado)
│   │   └── README.md           # Metadatos y changelog de los reportes
│   ├── 03_modeling/
│   │   ├── report_latest.html  # Último reporte HTML generado
│   │   ├── ANALYSIS_YYYYMMDD.md        # Documento con conclusiones (versionado)
│   │   └── README.md           # Metadatos y changelog de los reportes
│   └── README.md
├── tokens/
│   └── spotify_tokens.json   # Tokens OAuth (no versionado)
└── .gitignore
```

## 🔎 Data Sources & Limitations

Este proyecto utiliza la Spotify Web API como principal fuente de datos.

Durante la etapa de ingesta se consideran las siguientes limitaciones técnicas:

- El endpoint `/search` de Spotify limita la paginación a los primeros **1000 resultados por query** (`offset + limit <= 1000`).
- Para escalar el volumen de datos, se implementa una estrategia basada en:
  - múltiples queries genéricas,
  - deduplicación por `track_id`,
  - combinación de fuentes (playlists de usuario, playlists públicas y search).

Estas decisiones permiten construir datasets grandes y reproducibles respetando las políticas de la API.

---
## 📁 Estructura del dataset RAW

El dataset RAW ("merged_raw") contiene 14 columnas:
- **track_id**: The Spotify ID for the track. 
- **track_name**: The name of the track.
- **track_popularity**: The popularity of the track. The value will be between 0 and 100, with 100 being the most popular.
- **duration_ms**: The track length in milliseconds.
- **explicit**: Whether or not the track has explicit lyrics ( true = yes it does; false = no it does not OR unknown). 
- **album_id**: The Spotify ID of the album.
- **album_name**: The name of the album. In case of an album takedown, the value may be an empty string. 
- **album_release_date**: The date the album was first released.
- **artist_id**: The Spotify ID of the artist.
- **artist_name**: The name of the artist. 
- **playlist_id**: The Spotify ID of the playlist.
- **playlist_name**: The name of the playlist.
- **added_at**: The date and time the track or episode was added. Note: some very old playlists may return null in this field.
- **source**: The source of the track (user_playlists, public_playlists, search_tracks)
- **search_query**: Query used to catch de track. 
- **search_market**: Market of the searched track.

La informacion provista anteriormente fue extraida directamente desde la la pagina oficial de la API. Los campos **source**, **search_query** y **search_market** son introducidos en los scripts de ingesta para identificar las fuentes, la query utilizada y el mercado al cual pertenecen las canciones. En el caso de las canciones obtenidas de las playlist del usuario (user_playlists) o las playlist publicas (public_playlists), los campos **search_query** y **search_market** contienen registros nulos. 

---

## Documentacion oficial de la API

**Link**: https://developer.spotify.com/ 

---

## 🔁 Cómo replicar el proyecto

### 1️⃣ Clonar el repositorio

```bash
git clone <repo_url>
cd spotify-growth-ml
```

### 2️⃣ Crear entorno virtual e instalar dependencias

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Configurar credenciales de Spotify

1. Crear una app en [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Configurar Redirect URI:

```text
http://127.0.0.1:8888/callback
```

3. Crear archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Completar:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### 4️⃣ Ejecutar OAuth de usuario

```bash
python -m src.auth.spotify_oauth
```

Luego abrir en el navegador:

```text
http://127.0.0.1:8888/login
```

Aceptar permisos. Esto generará `tokens/spotify_tokens.json`.

---

### 5️⃣ Construccion de los datasets crudos

```bash
# Si no activaste el venv, ejecuta
source .venv/bin/activate

# Dataset con playlist privadas
python -m src.data_ingestion.build_spotify_raw_dataset
# Dataset con playlist publicas
python -m src.data_ingestion.build_spotify_raw_dataset_public_playlists
# Dataset con tracks search
python -m src.data_ingestion.build_spotify_raw_dataset_search_tracks
# Merge de datasets
python -m src.data_ingestion.merge_raw_datasets

```

Salidas esperadas:

* Archivos en `data/raw/`: cada script de playlists/tracks guarda un `.parquet` (y el de playlists de usuario además un `.csv`). El merge genera un único `.parquet` con sufijo `spotify_tracks_merged_raw_*.parquet`.
* Log con shape del dataset (ej. 1289 filas x 13 columnas)
* Log con shape antes y después de la dedupe (merge). 

---

### 6️⃣ Ejecutar el EDA

Abrir Jupyter:

```bash
jupyter notebook
```

Correr:

```text
notebooks/01_eda.ipynb
```

Este notebook:

* Analiza la calidad de los datos.
* Explora la distribución de popularidad.
* Define el target `popular_high`.
* Guarda el dataset intermedio en `data/interim/`.

---

## 📊 Documentación y Reportes

Este proyecto separa el **código ejecutable** (notebooks) de la **documentación estática** (reportes):

- **Notebooks** (`notebooks/`): Código que puede ejecutarse con cualquier dataset
- **Reportes** (`reports/`): Documentación que captura conclusiones de ejecuciones específicas

### Generar reportes

Después de ejecutar un notebook y obtener conclusiones:

1. **Generar reporte HTML:**
   ```bash
   python -m src.utils.generate_report notebooks/01_eda.ipynb
   ```
   Esto generará un reporte HTML en `reports/01_eda/` con todos los outputs del notebook.

2. **Documentar conclusiones:**
   - Abrir `reports/01_eda/ANALYSIS.md`
   - Copiar las conclusiones del notebook ejecutado
   - Completar con hallazgos y observaciones específicas

3. **Versionar:**
   - Los reportes HTML se generan con timestamp
   - El archivo `report_latest.html` siempre apunta al más reciente
   - Los archivos `.md` deben commitearse junto con el código

### ¿Por qué separar código de documentación?

- **Código ejecutable:** Los notebooks deben funcionar con cualquier dataset y generar conclusiones dinámicamente
- **Documentación estática:** Los reportes capturan el estado del análisis en un momento específico, útil para:
  - Compartir resultados con stakeholders
  - Documentar decisiones tomadas en base a datos específicos
  - Mantener un historial de análisis realizados

Ver más detalles en `reports/README.md`.

---

### Politica de versionado de artefactos (GitHub)

Para evitar crecimiento innecesario del repositorio:
- Se conserva solo la **ultima version con timestamp por familia** para `.csv` y `.parquet`.
- Se eliminan versiones historicas anteriores.
- Se eliminan archivos canonicos sin timestamp cuando duplican la misma familia (por ejemplo en `model_performance`).

---

## 🧠 Estado actual del proyecto

* ✅ Ingesta desde Spotify API con OAuth
* ✅ Dataset crudo versionado
* ✅ EDA completo
* ✅ Target de ML definido
* ✅ Feature engineering básico
* ✅ Clasificación supervisada con validación cruzada, ensambles y optimización de hiperparámetros
* ✅ Regresión supervisada con validación cruzada y optimización de hiperparámetros
* ✅ Aprendizaje no supervisado con clustering, ensamble (Consensus Clustering) y análisis de enriquecimiento

**Modelo en producción recomendado:** `GradientBoosting_Tuned` (clasificación) — ROC-AUC `0.9518`, F1 clase 1 `0.8083`

---

## 📈 Próximos pasos

1. **Feature engineering avanzado** — Incorporar audio features de la Spotify API (`danceability`, `energy`, `valence`, `tempo`) para mejorar el R² de regresión (actualmente `0.66`) y potencialmente también la clasificación. Estas features están disponibles vía el endpoint `/audio-features` y representan la brecha de señal más relevante identificada por los resultados actuales.

2. **Pipeline de scoring reproducible** — Serializar `GradientBoosting_Tuned` con `joblib` y construir un script `src/scoring/score_tracks.py` que reciba un parquet de tracks nuevos y devuelva predicción binaria + probabilidad de `popular_high`. Documentar contrato de entrada (las 10 features requeridas) y contrato de salida.

3. **Validación temporal** — Reemplazar el holdout estratificado por un split temporal usando `album_release_year` como eje (por ejemplo: train en tracks anteriores a 2024, test en 2024+) para medir degradación real por data drift y evaluar si el modelo generaliza a lanzamientos futuros.

4. **Optimización del umbral de decisión** — Definir el umbral operativo de `GradientBoosting_Tuned` según el objetivo de negocio: umbral bajo (maximizar recall) para no perder tracks de alto potencial; umbral alto (maximizar precisión) para campañas de inversión selectiva. Construir curva Precision-Recall con análisis de costo.

5. **Integración de señales externas** — Conectar `pytrends` (ya en `requirements.txt`) para enriquecer el dataset con volumen de búsqueda en Google Trends por artista en la semana de lanzamiento, como proxy de awareness externo a la plataforma.

---

**Autor:** Nicolás Guisande
**Rol:** Growth / Data Science
**Objetivo:** Construir proyectos de Data Science aplicados a negocio, con estándares profesionales.

---
## Licencia

El **código fuente** de este repositorio está licenciado bajo la **MIT License**.

📄 Ver el archivo [`LICENSE`](LICENSE) para el texto completo.

> Nota: La licencia MIT aplica al **código** y documentación propia. No otorga derechos sobre **contenido/datos de terceros** (por ejemplo, datos provenientes de Spotify).