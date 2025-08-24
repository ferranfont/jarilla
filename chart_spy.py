# main_eurusd.py - Gráfico con formato de fecha mejorado

import yfinance as yf
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import webbrowser
import tempfile
import os
import pandas as pd
import sys
sys.path.append('quant_stats')
from extremos_realtime import RealTimeExtremeDetector, ExtremoType
from zigzag_detector import ZigzagDetector, ZigzagDirection

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
        
        # Detectar extremos en tiempo real
        print("🔍 Detectando máximos y mínimos...")
        
        # Detector original (ventana deslizante)
        detector_ventana = RealTimeExtremeDetector(window_size=7, confirmation_periods=3, min_strength=0.001)
        
        # Detector Zigzag (cambio porcentual)
        detector_zigzag = ZigzagDetector(min_change_pct=0.12, mode="percentage")
        
        # Procesar precios como si fuera en tiempo real
        extremos_detectados = []
        zigzag_points = []
        
        for i, (timestamp, row) in enumerate(hist.iterrows()):
            price = row['Close']  # Usar precio de cierre
            
            # Detector original
            confirmados = detector_ventana.add_price(price)
            extremos_detectados.extend(confirmados)
            
            # Detector Zigzag
            zigzag_point = detector_zigzag.add_price(price)
            if zigzag_point:
                zigzag_points.append(zigzag_point)
        
        print(f"✅ Extremos detectados (ventana): {len(extremos_detectados)}")
        maximos = [e for e in extremos_detectados if e.tipo == ExtremoType.MAXIMO]
        minimos = [e for e in extremos_detectados if e.tipo == ExtremoType.MINIMO]
        print(f"   📈 Máximos (resistencias): {len(maximos)}")
        print(f"   📉 Mínimos (soportes): {len(minimos)}")
        
        print(f"✅ Puntos Zigzag detectados: {len(zigzag_points)}")
        zigzag_peaks = [z for z in zigzag_points if z.direction == ZigzagDirection.UP]
        zigzag_valleys = [z for z in zigzag_points if z.direction == ZigzagDirection.DOWN]
        print(f"   🔺 Picos Zigzag: {len(zigzag_peaks)}")
        print(f"   🔻 Valles Zigzag: {len(zigzag_valleys)}")
        
        # Crear DataFrame con señales de extremos (ventana + zigzag)
        senales_data = []
        hist_reset = hist.reset_index()  # Reset index para acceso por índice numérico
        
        # Añadir extremos del detector de ventana
        for extremo in extremos_detectados:
            if extremo.index < len(hist_reset):
                row_data = hist_reset.iloc[extremo.index]
                senal = {
                    'timestamp': row_data.name if hasattr(row_data, 'name') else hist_reset.index[extremo.index],
                    'detector': 'ventana',
                    'tipo': 'resistencia' if extremo.tipo == ExtremoType.MAXIMO else 'soporte',
                    'close': row_data['Close'],
                    'open': row_data['Open'],
                    'high': row_data['High'],
                    'low': row_data['Low'],
                    'volume': row_data.get('Volume', 0),  # 0 si no hay volumen
                    'extremo_price': extremo.price,
                    'index_posicion': extremo.index
                }
                senales_data.append(senal)
        
        # Añadir puntos Zigzag
        for zigzag in zigzag_points:
            if zigzag.index < len(hist_reset):
                row_data = hist_reset.iloc[zigzag.index]
                senal = {
                    'timestamp': row_data.name if hasattr(row_data, 'name') else hist_reset.index[zigzag.index],
                    'detector': 'zigzag',
                    'tipo': 'pico' if zigzag.direction == ZigzagDirection.UP else 'valle',
                    'close': row_data['Close'],
                    'open': row_data['Open'],
                    'high': row_data['High'],
                    'low': row_data['Low'],
                    'volume': row_data.get('Volume', 0),
                    'extremo_price': zigzag.price,
                    'index_posicion': zigzag.index
                }
                senales_data.append(senal)
        
        # Crear DataFrame y guardar en CSV
        if senales_data:
            df_senales = pd.DataFrame(senales_data)
            # Guardar en outputs
            os.makedirs("outputs", exist_ok=True)
            csv_senales_path = f"outputs/senales_extremos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_senales.to_csv(csv_senales_path, index=False)
            print(f"💾 Señales guardadas en: {csv_senales_path}")
            print(f"📊 Total señales almacenadas: {len(df_senales)}")
        else:
            print("⚠️ No se detectaron señales para guardar")
        
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
    
    # Añadir señales de extremos detectados
    if extremos_detectados:
        # Preparar datos para los extremos
        indices_timestamp = list(hist.index)
        
        # Máximos (resistencias) - puntos verdes en el close
        max_x = []
        max_y = []
        for extremo in maximos:
            if extremo.index < len(indices_timestamp):
                timestamp = indices_timestamp[extremo.index]
                # Usar el precio close de la vela (que es el extremo.price)
                max_x.append(timestamp)
                max_y.append(extremo.price)  # extremo.price es el close
        
        if max_x:
            fig.add_trace(
                go.Scatter(
                    x=max_x,
                    y=max_y,
                    mode='markers',
                    name='Resistencias',
                    marker=dict(
                        symbol='circle',
                        size=6,
                        color='green',
                        line=dict(width=1, color='darkgreen')
                    ),
                    hovertemplate='<b>Resistencia</b><br>Precio: %{y}<br>Tiempo: %{x}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Mínimos (soportes) - puntos rojos en el close
        min_x = []
        min_y = []
        for extremo in minimos:
            if extremo.index < len(indices_timestamp):
                timestamp = indices_timestamp[extremo.index]
                # Usar el precio close de la vela (que es el extremo.price)
                min_x.append(timestamp)
                min_y.append(extremo.price)  # extremo.price es el close
        
        if min_x:
            fig.add_trace(
                go.Scatter(
                    x=min_x,
                    y=min_y,
                    mode='markers',
                    name='Soportes',
                    marker=dict(
                        symbol='circle',
                        size=6,
                        color='red',
                        line=dict(width=1, color='darkred')
                    ),
                    hovertemplate='<b>Soporte</b><br>Precio: %{y}<br>Tiempo: %{x}<extra></extra>'
                ),
                row=1, col=1
            )
        
        # Añadir puntos Zigzag al gráfico (diferentes colores/formas)
        if zigzag_points:
            indices_timestamp = list(hist.index)
            
            # Picos Zigzag - diamantes azules
            zigzag_peak_x = []
            zigzag_peak_y = []
            for zigzag in zigzag_peaks:
                if zigzag.index < len(indices_timestamp):
                    zigzag_peak_x.append(indices_timestamp[zigzag.index])
                    zigzag_peak_y.append(zigzag.price)
            
            if zigzag_peak_x:
                fig.add_trace(
                    go.Scatter(
                        x=zigzag_peak_x,
                        y=zigzag_peak_y,
                        mode='markers',
                        name='Zigzag Picos',
                        marker=dict(
                            symbol='diamond',
                            size=8,
                            color='blue',
                            line=dict(width=2, color='darkblue')
                        ),
                        hovertemplate='<b>Zigzag Pico</b><br>Precio: %{y}<br>Tiempo: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
            
            # Valles Zigzag - diamantes naranjas
            zigzag_valley_x = []
            zigzag_valley_y = []
            for zigzag in zigzag_valleys:
                if zigzag.index < len(indices_timestamp):
                    zigzag_valley_x.append(indices_timestamp[zigzag.index])
                    zigzag_valley_y.append(zigzag.price)
            
            if zigzag_valley_x:
                fig.add_trace(
                    go.Scatter(
                        x=zigzag_valley_x,
                        y=zigzag_valley_y,
                        mode='markers',
                        name='Zigzag Valles',
                        marker=dict(
                            symbol='diamond',
                            size=8,
                            color='orange',
                            line=dict(width=2, color='darkorange')
                        ),
                        hovertemplate='<b>Zigzag Valle</b><br>Precio: %{y}<br>Tiempo: %{x}<extra></extra>'
                    ),
                    row=1, col=1
                )
                
            # Conectar puntos Zigzag con línea
            if len(zigzag_points) > 1:
                all_zigzag_x = []
                all_zigzag_y = []
                for zigzag in sorted(zigzag_points, key=lambda z: z.index):
                    if zigzag.index < len(indices_timestamp):
                        all_zigzag_x.append(indices_timestamp[zigzag.index])
                        all_zigzag_y.append(zigzag.price)
                
                if len(all_zigzag_x) > 1:
                    fig.add_trace(
                        go.Scatter(
                            x=all_zigzag_x,
                            y=all_zigzag_y,
                            mode='lines',
                            name='Línea Zigzag',
                            line=dict(color='purple', width=1, dash='dot'),
                            hoverinfo='skip',
                            showlegend=False
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