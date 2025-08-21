# main_eurusd.py - Gráfico con formato de fecha mejorado

import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import webbrowser
import tempfile
import os
import pandas as pd

def create_eurusd_chart():
    """Crear gráfico de velas EUR/USD con formato de fecha limpio"""
    print("📂 Leyendo datos EUR/USD desde archivo local...")
    
    # Leer datos desde el archivo CSV local
    csv_path = "outputs/EURUSD.csv"
    
    try:
        if not os.path.exists(csv_path):
            print(f"❌ No se encontró el archivo {csv_path}")
            print("💡 Ejecuta primero 'python spy_data.py' para generar los datos")
            return
        
        # Leer CSV y configurar el índice de fecha
        hist = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        
        if hist.empty:
            print("❌ El archivo CSV está vacío")
            return
            
        print(f"✅ Datos cargados desde {csv_path}: {len(hist)} registros")
        
        # Filtrar solo días de semana (el forex no opera fines de semana)
        hist = hist[hist.index.weekday < 5]
        
        # Crear etiquetas de tiempo limpias para el eje X
        hist.index = hist.index.strftime('%d/%m %H:%M')
        
        print(f"✅ Datos procesados: {len(hist)} velas")
        
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV: {e}")
        print("💡 Ejecuta primero 'python spy_data.py' para generar los datos")
        return
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.75, 0.25],
        vertical_spacing=0,
        shared_xaxes=True,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # Add candlestick chart with better styling
    fig.add_trace(
        go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='EURUSD',
            increasing_line_color='#26a69a',  # Verde más profesional
            decreasing_line_color='#ef5350',  # Rojo más profesional
            increasing_fillcolor='rgba(38, 166, 154, 0.8)',
            decreasing_fillcolor='rgba(239, 83, 80, 0.8)',
            line=dict(width=1)
        ),
        row=1, col=1
    )
    
    # Add volume/range bars
    if 'Volume' in hist.columns and hist['Volume'].sum() > 0:
        fig.add_trace(
            go.Bar(
                x=hist.index,
                y=hist['Volume'],
                name='Volume',
                marker_color='royalblue',
                showlegend=False
            ),
            row=2, col=1
        )
        volume_title = "Volume"
    else:
        spread = hist['High'] - hist['Low']
        fig.add_trace(
            go.Bar(
                x=hist.index,
                y=spread,
                name='Daily Range',
                marker_color='royalblue',
                showlegend=False
            ),
            row=2, col=1
        )
        volume_title = "Daily Range"
    
    # Styling
    fig.update_layout(
        title=dict(
            text="EUR/USD - (15min)",
            x=0.5, xanchor="center",
            y=0.98, yanchor="top",
            font=dict(size=18, color="#2c3e50"),
            pad=dict(t=10, b=10)
        ),
        paper_bgcolor='#fafafa',
        plot_bgcolor='#fafafa',
        font=dict(color="#2c3e50", family="Arial"),
        height=800,
        margin=dict(t=60, r=40, b=40, l=80),
        legend=dict(
            orientation="h",
            x=0.5, xanchor="center",
            y=0.95, yanchor="top",
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1,
        ),
        xaxis_rangeslider_visible=False,
        dragmode='zoom'
    )
    
    # Configurar eje X con formato limpio
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        row=1, col=1, 
        showticklabels=False,
        type='category'  # Elimina fines de semana
    )
    
    # Eje X inferior con formato personalizado
    fig.update_xaxes(
        showgrid=False, 
        zeroline=False, 
        row=2, col=1,
        type='category',  # Elimina fines de semana
        tickangle=45,
        nticks=15,  # Número máximo de etiquetas
        title_text="Fecha y Hora",
        title_font=dict(size=12, color="#2c3e50")
    )
    
    # Configurar ejes Y
    fig.update_yaxes(
        title_text="Precio (EUR/USD)",
        title_font=dict(size=14, color="#2c3e50"),
        row=1, col=1,
        showgrid=False, 
        zeroline=False,
        tickformat='.5f'
    )
    
    fig.update_yaxes(
        title_text=volume_title,
        title_font=dict(size=14, color="#2c3e50"),
        row=2, col=1,
        showgrid=False, 
        zeroline=False
    )
    
    # Añadir líneas verticales para cada nuevo día
    daily_markers = []
    current_date = None
    
    for i, timestamp in enumerate(hist.index):
        date_part = timestamp.split(' ')[0]  # Obtener solo la parte de fecha 'dd/mm'
        if current_date is None or date_part != current_date:
            daily_markers.append(i)
            current_date = date_part
    
    # Añadir líneas verticales punteadas para nuevos días
    for marker in daily_markers[1:]:  # Omitir el primer día
        fig.add_vline(
            x=marker,
            line=dict(color="rgba(150,150,150,0.4)", width=1, dash="solid"),
            row="all"
        )
    
    # Precio actual para el print
    current_price = hist['Close'].iloc[-1]
    
    # Configuración del archivo HTML temporal (para abrir en navegador)
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    fig.write_html(
        temp_file.name, 
        auto_open=True,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'eurusd_clean_chart',
                'height': 800,
                'width': 1200,
                'scale': 2
            }
        }
    )
    temp_file.close()
    
    # Guardar copia permanente en la carpeta charts
    os.makedirs("charts", exist_ok=True)
    chart_filename = f"charts/eurusd_chart_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.html"
    fig.write_html(
        chart_filename,
        config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'eurusd_clean_chart',
                'height': 800,
                'width': 1200,
                'scale': 2
            }
        }
    )
    
    print(f"✅ Gráfico abierto en navegador: {temp_file.name}")
    print(f"💾 Gráfico guardado en: {chart_filename}")
    print(f"📊 Datos: {len(hist)} velas de 15 minutos")
    print(f"📈 Precio actual: {current_price:.5f}")
    print(f"📅 Período: {hist.index[0]} - {hist.index[-1]}")

if __name__ == "__main__":
    create_eurusd_chart()