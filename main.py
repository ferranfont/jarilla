#!/usr/bin/env python3
"""
Jarilla - Análisis de Divisas EUR/USD
Punto de entrada principal del proyecto
"""

import os
import sys
from dotenv import load_dotenv
from spy_data import get_spy_data

def main():
    """Función principal del proyecto Jarilla"""
    # Cargar variables de entorno
    load_dotenv()
    
    print("🔥 Iniciando Jarilla - Análisis EUR/USD")
    print("=" * 50)
    
    try:
        # Ejecutar análisis completo
        get_spy_data()
        print("\n✅ Análisis completado exitosamente")
        
    except KeyboardInterrupt:
        print("\n❌ Proceso interrumpido por el usuario")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        sys.exit(1)
        
    print("🎯 Jarilla finalizado")

if __name__ == "__main__":
    main()