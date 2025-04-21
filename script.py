import time
import psutil
import pandas as pd
from collections import defaultdict

try:
    import pyadl
    amd_gpu_available = True
except ImportError:
    amd_gpu_available = False

def get_amd_gpu_stats():
    """Obtiene estadísticas de GPU AMD usando pyadl con manejo de errores mejorado"""
    if not amd_gpu_available:
        return None, None, None
    
    try:
        adl_manager = pyadl.ADLManager.getInstance()
        devices = adl_manager.getDevices()
        
        if not devices:
            return None, None, None
            
        gpu = devices[0]
        stats = {
            'utilization': None,
            'temperature': None,
            'power': None
        }
        
        # Obtener utilización (si está disponible)
        try:
            stats['utilization'] = gpu.getCurrentUsage()
        except AttributeError:
            pass
        
        # Obtener temperatura (si está disponible)
        try:
            stats['temperature'] = gpu.getCurrentTemperature()
        except AttributeError:
            pass
        
        # Obtener consumo de energía (solo para GPUs que lo soportan)
        try:
            stats['power'] = gpu.getCurrentPower()
        except AttributeError:
            # Método alternativo para RX 400 series
            try:
                stats['power'] = gpu.getCurrentPowerValue() / 1000  # Convertir mW a W
            except AttributeError:
                pass
        
        return stats['utilization'], stats['temperature'], stats['power']
        
    except Exception as e:
        print(f"\nError al leer GPU AMD: {str(e)}")
        return None, None, None

def monitor_system(duration=20, interval=1):
    """Monitorea el sistema durante el tiempo especificado"""
    data = []
    end_time = time.time() + duration
    
    print(f"\nIniciando monitoreo por {duration} segundos...")
    print(f"GPU AMD detectada: {'Sí' if amd_gpu_available else 'No'}")
    
    while time.time() < end_time:
        # Datos del CPU
        cpu_util = psutil.cpu_percent(interval=0.1)
        
        # Datos de GPU AMD
        gpu_util, gpu_temp, gpu_power = get_amd_gpu_stats()
        
        timestamp = time.strftime("%H:%M:%S")
        data.append({
            'timestamp': timestamp,
            'cpu_util': cpu_util,
            'gpu_util': gpu_util,
            'gpu_temp': gpu_temp,
            'gpu_power': gpu_power
        })
        
        # Mostrar datos en tiempo real
        power_display = f"{gpu_power:.1f}W" if gpu_power is not None else "N/A"
        print(f"\r[CPU: {cpu_util:.1f}% | GPU: {gpu_util or 'N/A'}% | Temp: {gpu_temp or 'N/A'}°C | Power: {power_display}]", end="")
        
        time.sleep(max(0, interval - 0.1))
    
    return pd.DataFrame(data)

def main():
    print("Sistema de Monitoreo para AMD RX 460 en Windows 10")
    print("Versión adaptada para RX 400 series\n")
    
    # Verificar dependencias
    print("Verificando dependencias...")
    try:
        import psutil
        import pandas as pd
    except ImportError:
        print("Error: Necesitas instalar psutil y pandas")
        print("Ejecuta: pip install psutil pandas")
        return
    
    if not amd_gpu_available:
        print("\nADL no disponible. Instala pyadl para monitorear la GPU AMD")
        print("Ejecuta: pip install pyadl")
        print("Asegúrate de tener los drivers AMD Adrenalin instalados")
        print("Reinicia después de instalar los drivers")
        return
    
    # Monitorear por 20 segundos
    df = monitor_system(duration=20, interval=1)
    
    # Calcular promedios
    print("\n\nResultados finales:")
    print(f"- CPU: Utilización promedio: {df['cpu_util'].mean():.2f}%")
    
    if amd_gpu_available:
        if not df['gpu_util'].isnull().all():
            print(f"- GPU: Utilización promedio: {df['gpu_util'].mean():.2f}%")
        else:
            print("- GPU: No se pudo obtener utilización")
        
        if not df['gpu_temp'].isnull().all():
            print(f"- GPU: Temperatura promedio: {df['gpu_temp'].mean():.2f}°C")
        else:
            print("- GPU: No se pudo obtener temperatura")
        
        if not df['gpu_power'].isnull().all():
            print(f"- GPU: Consumo de energía promedio: {df['gpu_power'].mean():.2f} W")
        else:
            print("- GPU: El consumo de energía no está disponible para este modelo")
    
    # Opción para guardar datos
    save = input("\n¿Guardar datos en CSV? (s/n): ").lower()
    if save == 's':
        filename = f"rx460_monitor_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Datos guardados en {filename}")

if __name__ == "__main__":
    main()