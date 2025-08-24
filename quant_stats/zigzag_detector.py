from typing import List, Optional, Tuple
from enum import Enum
import time

class ZigzagDirection(Enum):
    UP = "up"
    DOWN = "down"

class ZigzagMode(Enum):
    PERCENTAGE = "percentage"
    PIPS = "pips"
    ABSOLUTE = "absolute"

class ZigzagPoint:
    def __init__(self, index: int, price: float, direction: ZigzagDirection, timestamp: Optional[float] = None):
        self.index = index
        self.price = price
        self.direction = direction
        self.timestamp = timestamp or time.time()
        self.confirmed = False

class ZigzagDetector:
    def __init__(self, min_change_pct: float = 0.15, min_change_pips: float = 15.0, 
                 mode: str = "percentage", pip_value: float = 0.0001):
        """
        Detector Zigzag para identificar puntos de giro significativos
        
        Args:
            min_change_pct: Cambio mínimo en porcentaje (ej: 0.15 = 0.15%)
            min_change_pips: Cambio mínimo en pips (para forex)
            mode: "percentage", "pips", o "absolute"
            pip_value: Valor de un pip (0.0001 para EUR/USD)
        """
        self.min_change_pct = min_change_pct / 100.0  # Convertir a decimal
        self.min_change_pips = min_change_pips
        self.mode = ZigzagMode(mode)
        self.pip_value = pip_value
        
        # Estado del detector
        self.prices = []
        self.price_index = 0
        self.current_trend = None  # None, UP, DOWN
        self.last_pivot = None  # Último punto de giro confirmado
        self.potential_pivot = None  # Punto de giro potencial
        
        # Puntos de giro detectados
        self.zigzag_points = []
        
    def add_price(self, price: float) -> Optional[ZigzagPoint]:
        """
        Añade un nuevo precio y retorna un punto zigzag si se detecta
        
        Args:
            price: Nuevo precio
            
        Returns:
            ZigzagPoint si se confirma un punto de giro, None en caso contrario
        """
        self.prices.append(price)
        self.price_index += 1
        
        # Primer precio
        if len(self.prices) == 1:
            self.last_pivot = ZigzagPoint(0, price, ZigzagDirection.UP)  # Dirección inicial arbitraria
            return None
            
        # Segundo precio - establecer tendencia inicial
        if len(self.prices) == 2:
            if price > self.prices[0]:
                self.current_trend = ZigzagDirection.UP
                self.last_pivot.direction = ZigzagDirection.DOWN  # El anterior era un mínimo
            else:
                self.current_trend = ZigzagDirection.DOWN
                self.last_pivot.direction = ZigzagDirection.UP    # El anterior era un máximo
            return None
            
        return self._check_for_pivot(price)
    
    def _check_for_pivot(self, current_price: float) -> Optional[ZigzagPoint]:
        """
        Verifica si el precio actual constituye un punto de giro
        """
        if not self.last_pivot:
            return None
            
        change = self._calculate_change(self.last_pivot.price, current_price)
        significant_change = self._is_significant_change(change)
        
        # Si estamos en tendencia alcista
        if self.current_trend == ZigzagDirection.UP:
            # Buscar un techo (punto donde empezar a bajar)
            if self._is_potential_peak():
                # Verificar si la caída desde el pico potencial es significativa
                peak_price = self._get_recent_high()
                peak_index = self._get_recent_high_index()
                
                if peak_price and peak_index is not None:
                    change_from_peak = self._calculate_change(peak_price, current_price)
                    if self._is_significant_change(change_from_peak) and change_from_peak < 0:
                        # Confirmar el pico como punto de giro
                        pivot = ZigzagPoint(peak_index, peak_price, ZigzagDirection.UP)
                        pivot.confirmed = True
                        self.zigzag_points.append(pivot)
                        self.last_pivot = pivot
                        self.current_trend = ZigzagDirection.DOWN
                        return pivot
                        
        # Si estamos en tendencia bajista        
        elif self.current_trend == ZigzagDirection.DOWN:
            # Buscar un valle (punto donde empezar a subir)
            if self._is_potential_valley():
                # Verificar si la subida desde el valle potencial es significativa
                valley_price = self._get_recent_low()
                valley_index = self._get_recent_low_index()
                
                if valley_price and valley_index is not None:
                    change_from_valley = self._calculate_change(valley_price, current_price)
                    if self._is_significant_change(change_from_valley) and change_from_valley > 0:
                        # Confirmar el valle como punto de giro
                        pivot = ZigzagPoint(valley_index, valley_price, ZigzagDirection.DOWN)
                        pivot.confirmed = True
                        self.zigzag_points.append(pivot)
                        self.last_pivot = pivot
                        self.current_trend = ZigzagDirection.UP
                        return pivot
        
        return None
    
    def _calculate_change(self, from_price: float, to_price: float) -> float:
        """
        Calcula el cambio según el modo configurado
        """
        if self.mode == ZigzagMode.PERCENTAGE:
            return ((to_price - from_price) / from_price) * 100.0
        elif self.mode == ZigzagMode.PIPS:
            return (to_price - from_price) / self.pip_value
        else:  # ABSOLUTE
            return to_price - from_price
    
    def _is_significant_change(self, change: float) -> bool:
        """
        Verifica si un cambio es lo suficientemente significativo
        """
        abs_change = abs(change)
        
        if self.mode == ZigzagMode.PERCENTAGE:
            return abs_change >= (self.min_change_pct * 100.0)
        elif self.mode == ZigzagMode.PIPS:
            return abs_change >= self.min_change_pips
        else:  # ABSOLUTE
            return abs_change >= self.min_change_pct  # Reutilizar como valor absoluto
    
    def _is_potential_peak(self, lookback: int = 3) -> bool:
        """
        Verifica si hay un pico potencial en los últimos precios
        """
        if len(self.prices) < lookback + 1:
            return False
            
        recent_prices = self.prices[-lookback-1:]
        max_price = max(recent_prices)
        max_index = recent_prices.index(max_price)
        
        # El máximo debe estar en el medio, no al final
        return max_index < len(recent_prices) - 1
    
    def _is_potential_valley(self, lookback: int = 3) -> bool:
        """
        Verifica si hay un valle potencial en los últimos precios
        """
        if len(self.prices) < lookback + 1:
            return False
            
        recent_prices = self.prices[-lookback-1:]
        min_price = min(recent_prices)
        min_index = recent_prices.index(min_price)
        
        # El mínimo debe estar en el medio, no al final
        return min_index < len(recent_prices) - 1
    
    def _get_recent_high(self, lookback: int = 5) -> Optional[float]:
        """
        Obtiene el precio más alto reciente
        """
        if len(self.prices) < lookback:
            return max(self.prices) if self.prices else None
        return max(self.prices[-lookback:])
    
    def _get_recent_high_index(self, lookback: int = 5) -> Optional[int]:
        """
        Obtiene el índice del precio más alto reciente
        """
        if len(self.prices) < lookback:
            recent_prices = self.prices
            offset = 0
        else:
            recent_prices = self.prices[-lookback:]
            offset = len(self.prices) - lookback
            
        if not recent_prices:
            return None
            
        max_price = max(recent_prices)
        local_index = recent_prices.index(max_price)
        return offset + local_index
    
    def _get_recent_low(self, lookback: int = 5) -> Optional[float]:
        """
        Obtiene el precio más bajo reciente
        """
        if len(self.prices) < lookback:
            return min(self.prices) if self.prices else None
        return min(self.prices[-lookback:])
    
    def _get_recent_low_index(self, lookback: int = 5) -> Optional[int]:
        """
        Obtiene el índice del precio más bajo reciente
        """
        if len(self.prices) < lookback:
            recent_prices = self.prices
            offset = 0
        else:
            recent_prices = self.prices[-lookback:]
            offset = len(self.prices) - lookback
            
        if not recent_prices:
            return None
            
        min_price = min(recent_prices)
        local_index = recent_prices.index(min_price)
        return offset + local_index
    
    def get_zigzag_points(self) -> List[ZigzagPoint]:
        """
        Retorna todos los puntos zigzag detectados
        """
        return self.zigzag_points.copy()
    
    def get_last_pivot(self) -> Optional[ZigzagPoint]:
        """
        Retorna el último punto de giro confirmado
        """
        return self.last_pivot
    
    def reset(self):
        """
        Reinicia el detector
        """
        self.prices.clear()
        self.price_index = 0
        self.current_trend = None
        self.last_pivot = None
        self.potential_pivot = None
        self.zigzag_points.clear()

def ejemplo_uso():
    """
    Ejemplo de uso del detector Zigzag
    """
    import random
    import matplotlib.pyplot as plt
    
    # Crear detector Zigzag
    detector = ZigzagDetector(min_change_pct=0.2, mode="percentage")
    
    # Generar precios sintéticos
    precios = []
    base_price = 1.1000
    
    for i in range(100):
        # Tendencia con ruido
        trend = 0.0001 * (i % 40 - 20)  # Oscilación
        noise = random.uniform(-0.0005, 0.0005)
        price = base_price + trend + noise
        precios.append(price)
        
        # Detectar puntos zigzag
        pivot = detector.add_price(price)
        if pivot:
            print(f"Pivot detectado: {pivot.direction.value} en índice {pivot.index}, precio {pivot.price:.5f}")
    
    # Visualizar resultados
    plt.figure(figsize=(12, 6))
    plt.plot(precios, 'b-', label='Precios', alpha=0.7)
    
    # Marcar puntos zigzag
    pivots = detector.get_zigzag_points()
    for pivot in pivots:
        color = 'green' if pivot.direction == ZigzagDirection.UP else 'red'
        marker = '^' if pivot.direction == ZigzagDirection.UP else 'v'
        plt.scatter(pivot.index, pivot.price, color=color, marker=marker, s=100, 
                   label=f'{pivot.direction.value}' if pivot == pivots[0] else "")
    
    # Conectar puntos zigzag con líneas
    if len(pivots) > 1:
        pivot_x = [p.index for p in pivots]
        pivot_y = [p.price for p in pivots]
        plt.plot(pivot_x, pivot_y, 'k--', alpha=0.6, linewidth=1)
    
    plt.title('Detector Zigzag - Puntos de Giro')
    plt.xlabel('Índice')
    plt.ylabel('Precio')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
    
    print(f"\nTotal puntos zigzag: {len(pivots)}")

if __name__ == "__main__":
    ejemplo_uso()