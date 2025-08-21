from collections import deque
from typing import List, Tuple, Optional
from enum import Enum
import time

class ExtremoState(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    INVALIDATED = "invalidated"

class ExtremoType(Enum):
    MAXIMO = "maximo"
    MINIMO = "minimo"

class Extremo:
    def __init__(self, index: int, price: float, tipo: ExtremoType):
        self.index = index
        self.price = price
        self.tipo = tipo
        self.state = ExtremoState.PENDING
        self.timestamp = time.time()

class RealTimeExtremeDetector:
    def __init__(self, window_size: int = 10, confirmation_periods: int = 5, min_strength: float = 0.3):
        """
        Detector de máximos y mínimos en tiempo real
        
        Args:
            window_size: Tamaño de la ventana para detectar extremos (debe ser impar)
            confirmation_periods: Períodos necesarios para confirmar un extremo
            min_strength: Fuerza mínima del extremo (% de diferencia respecto al promedio de la ventana)
        """
        if window_size % 2 == 0:
            raise ValueError("window_size debe ser un número impar")
            
        self.window_size = window_size
        self.confirmation_periods = confirmation_periods
        self.half_window = window_size // 2
        self.min_strength = min_strength  # Filtro de fuerza mínima
        
        # Buffer para almacenar precios
        self.prices = deque(maxlen=window_size + confirmation_periods)
        self.price_index = 0
        
        # Lista de extremos detectados
        self.extremos_pending = []
        self.extremos_confirmed = []
        
    def add_price(self, price: float) -> List[Extremo]:
        """
        Añade un nuevo precio y retorna extremos confirmados en esta iteración
        
        Args:
            price: Nuevo precio
            
        Returns:
            Lista de extremos recién confirmados
        """
        self.prices.append(price)
        self.price_index += 1
        
        nuevos_confirmados = []
        
        # Solo empezamos a detectar cuando tenemos suficientes datos
        if len(self.prices) >= self.window_size:
            # Verificar si podemos detectar un extremo en el centro de la ventana actual
            extremo = self._detect_extremo()
            if extremo:
                self.extremos_pending.append(extremo)
        
        # Verificar confirmaciones de extremos pendientes
        if len(self.prices) >= self.window_size + self.confirmation_periods:
            confirmados = self._check_confirmations()
            nuevos_confirmados.extend(confirmados)
            
        return nuevos_confirmados
    
    def _detect_extremo(self) -> Optional[Extremo]:
        """
        Detecta si hay un extremo en el centro de la ventana actual
        """
        if len(self.prices) < self.window_size:
            return None
            
        # Obtener la ventana actual
        window = list(self.prices)[-self.window_size:]
        center_idx = self.half_window
        center_price = window[center_idx]
        
        # Verificar si es máximo local
        is_maximum = all(center_price >= price for i, price in enumerate(window) if i != center_idx)
        # Verificar si es mínimo local
        is_minimum = all(center_price <= price for i, price in enumerate(window) if i != center_idx)
        
        # Evitar extremos en precios iguales (planos)
        if self._is_flat_region(window, center_idx):
            return None
            
        # Calcular fuerza del extremo
        if is_maximum or is_minimum:
            if not self._is_strong_extremo(window, center_idx, is_maximum):
                return None
                
        if is_maximum:
            global_index = self.price_index - self.window_size + center_idx
            return Extremo(global_index, center_price, ExtremoType.MAXIMO)
            
        if is_minimum:
            global_index = self.price_index - self.window_size + center_idx
            return Extremo(global_index, center_price, ExtremoType.MINIMO)
            
        return None
    
    def _is_flat_region(self, window: List[float], center_idx: int, tolerance: float = 1e-6) -> bool:
        """
        Verifica si la región alrededor del centro es plana (precios muy similares)
        """
        center_price = window[center_idx]
        for i, price in enumerate(window):
            if abs(price - center_price) > tolerance:
                return False
        return True
    
    def _is_strong_extremo(self, window: List[float], center_idx: int, is_maximum: bool) -> bool:
        """
        Verifica si el extremo tiene suficiente fuerza para ser considerado significativo
        """
        center_price = window[center_idx]
        
        # Calcular promedio de la ventana excluyendo el centro
        other_prices = [price for i, price in enumerate(window) if i != center_idx]
        avg_price = sum(other_prices) / len(other_prices)
        
        # Calcular diferencia porcentual respecto al promedio
        if avg_price == 0:
            return False
            
        strength = abs(center_price - avg_price) / avg_price
        
        # Verificar si supera el umbral mínimo
        return strength >= self.min_strength
    
    def _check_confirmations(self) -> List[Extremo]:
        """
        Verifica qué extremos pendientes pueden ser confirmados
        """
        confirmados = []
        extremos_a_remover = []
        
        for extremo in self.extremos_pending:
            # Calcular cuántos períodos han pasado desde la detección
            periods_since_detection = self.price_index - extremo.index
            
            if periods_since_detection >= self.confirmation_periods:
                # Verificar si el extremo sigue siendo válido
                if self._is_extremo_still_valid(extremo):
                    extremo.state = ExtremoState.CONFIRMED
                    self.extremos_confirmed.append(extremo)
                    confirmados.append(extremo)
                else:
                    extremo.state = ExtremoState.INVALIDATED
                    
                extremos_a_remover.append(extremo)
        
        # Remover extremos procesados de la lista pending
        for extremo in extremos_a_remover:
            self.extremos_pending.remove(extremo)
            
        return confirmados
    
    def _is_extremo_still_valid(self, extremo: Extremo) -> bool:
        """
        Verifica si un extremo pendiente sigue siendo válido después del período de confirmación
        """
        # Obtener precios posteriores al extremo
        start_idx = max(0, len(self.prices) - (self.price_index - extremo.index))
        subsequent_prices = list(self.prices)[start_idx + 1:]
        
        if not subsequent_prices:
            return True
            
        if extremo.tipo == ExtremoType.MAXIMO:
            # Para máximos, verificar que no haya precios posteriores más altos
            return all(price <= extremo.price for price in subsequent_prices[-self.confirmation_periods:])
        else:
            # Para mínimos, verificar que no haya precios posteriores más bajos
            return all(price >= extremo.price for price in subsequent_prices[-self.confirmation_periods:])
    
    def get_confirmed_extremos(self) -> List[Extremo]:
        """Retorna todos los extremos confirmados"""
        return self.extremos_confirmed.copy()
    
    def get_pending_extremos(self) -> List[Extremo]:
        """Retorna extremos pendientes de confirmación"""
        return self.extremos_pending.copy()
    
    def get_latest_extremo(self, tipo: Optional[ExtremoType] = None) -> Optional[Extremo]:
        """
        Obtiene el último extremo confirmado, opcionalmente filtrado por tipo
        """
        filtered_extremos = self.extremos_confirmed
        if tipo:
            filtered_extremos = [e for e in self.extremos_confirmed if e.tipo == tipo]
            
        return filtered_extremos[-1] if filtered_extremos else None

def ejemplo_uso():
    """Ejemplo de uso del detector"""
    import random
    import matplotlib.pyplot as plt
    
    # Crear detector
    detector = RealTimeExtremeDetector(window_size=5, confirmation_periods=3)
    
    # Simular precios en tiempo real
    precios = []
    base_price = 100
    
    # Generar serie de precios con tendencia y ruido
    for i in range(100):
        # Añadir tendencia sinusoidal + ruido
        trend = 10 * (i / 20) * (1 + 0.5 * (i % 20 - 10) / 10)
        noise = random.uniform(-2, 2)
        price = base_price + trend + noise
        precios.append(price)
        
        # Procesar precio en tiempo real
        confirmados = detector.add_price(price)
        
        # Mostrar extremos recién confirmados
        for extremo in confirmados:
            print(f"Extremo confirmado: {extremo.tipo.value} en índice {extremo.index}, precio {extremo.price:.2f}")
    
    # Visualizar resultados
    plt.figure(figsize=(12, 6))
    plt.plot(precios, 'b-', label='Precios', alpha=0.7)
    
    # Marcar extremos confirmados
    for extremo in detector.get_confirmed_extremos():
        color = 'red' if extremo.tipo == ExtremoType.MAXIMO else 'green'
        marker = '^' if extremo.tipo == ExtremoType.MAXIMO else 'v'
        plt.scatter(extremo.index, extremo.price, color=color, marker=marker, s=100, 
                   label=extremo.tipo.value if extremo == detector.get_confirmed_extremos()[0] else "")
    
    plt.title('Detección de Extremos en Tiempo Real')
    plt.xlabel('Índice de Precio')
    plt.ylabel('Precio')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    print(f"\nTotal de extremos detectados: {len(detector.get_confirmed_extremos())}")
    print(f"Máximos: {len([e for e in detector.get_confirmed_extremos() if e.tipo == ExtremoType.MAXIMO])}")
    print(f"Mínimos: {len([e for e in detector.get_confirmed_extremos() if e.tipo == ExtremoType.MINIMO])}")

if __name__ == "__main__":
    ejemplo_uso()