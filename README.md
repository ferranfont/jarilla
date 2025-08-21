# Jarilla - Análisis de Divisas EUR/USD

Un proyecto de análisis financiero para el seguimiento y visualización del par de divisas EUR/USD con gráficos interactivos de velas.

## 🚀 Características

- **Descarga automática** de datos EUR/USD desde Yahoo Finance
- **Gráficos interactivos** de velas con intervalos de 15 minutos
- **Exportación de datos** a CSV para análisis adicional
- **Filtrado inteligente** que excluye fines de semana
- **Visualización profesional** con Plotly

## 📦 Instalación

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd jarilla
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno (opcional):
```bash
cp .env.example .env
# Edita .env con tus configuraciones
```

## 🎯 Uso

### Ejecución básica
```bash
python spy_data.py
```

### Solo gráficos
```bash
python chart_spy.py
```

### Usando el punto de entrada principal
```bash
python main.py
```

## 📊 Funcionalidades

### Datos descargados
- **Período**: Último mes por defecto
- **Intervalo**: Velas de 15 minutos
- **Par**: EUR/USD
- **Formato**: CSV guardado en `outputs/`

### Gráficos generados
- Gráfico de velas japonesas
- Indicador de volumen/rango diario
- Líneas de separación por días
- Exportación a PNG de alta calidad

## 📁 Estructura del proyecto

```
jarilla/
├── spy_data.py          # Descarga y procesa datos EUR/USD
├── chart_spy.py         # Genera gráficos interactivos
├── main.py              # Punto de entrada principal
├── requirements.txt     # Dependencias del proyecto
├── .env                 # Configuración (no versionado)
├── .gitignore          # Archivos ignorados por Git
└── outputs/            # Datos y gráficos generados
    └── EURUSD.csv      # Datos históricos
```

## ⚙️ Configuración

Las configuraciones se pueden ajustar en el archivo `.env`:

```bash
# Período de datos (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
DATA_PERIOD=1mo

# Intervalo de datos (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
DATA_INTERVAL=15m

# Par de divisas
CURRENCY_PAIR=EURUSD=X

# Dimensiones del gráfico
CHART_HEIGHT=800
CHART_WIDTH=1200
```

## 📈 Ejemplo de salida

```
📡 Descargando datos EUR/USD...
✅ Datos obtenidos: 1344 velas
✅ Gráfico guardado en: /tmp/tmpxxxx.html
📊 Datos: 1344 velas de 15 minutos
📈 Precio actual: 1.08934
📅 Período: 21/07 00:00 - 20/08 23:45
💾 CSV guardado en: outputs/EURUSD.csv
```

## 🛠️ Dependencias

- **yfinance**: Descarga de datos financieros
- **pandas**: Manipulación de datos
- **plotly**: Gráficos interactivos
- **python-dotenv**: Gestión de variables de entorno

## 📝 Licencia

Este proyecto está bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request