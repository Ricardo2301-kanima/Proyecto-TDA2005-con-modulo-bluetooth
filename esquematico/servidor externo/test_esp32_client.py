#!/usr/bin/env python3
"""
ESP32 Audio Stream Client Simulator
───────────────────────────────────────────────────────────────
Simula un cliente ESP32 conectándose al servidor de streaming.
Útil para testing sin hardware real.

Uso:
    python3 test_esp32_client.py --server http://localhost:3000
    
    O en Windows:
    python test_esp32_client.py --server http://localhost:3000
"""

import requests
import time
import sys
import argparse
from datetime import datetime

class ESP32Simulator:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        self.stream_url = f"{self.server_url}/stream"
        self.status_url = f"{self.server_url}/status"
        self.connected = False
        self.bytes_received = 0
        self.chunks_received = 0

    def log(self, level, msg):
        """Imprimir log formateado."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        prefix = {
            'INFO': '💙',
            'WARN': '⚠️',
            'OK': '✓',
            'ERR': '❌'
        }.get(level, '•')
        print(f"[{timestamp}] {prefix} {msg}")

    def test_server_health(self):
        """Verificar que el servidor está corriendo."""
        self.log('INFO', f'Verificando servidor en {self.server_url}...')
        try:
            response = requests.get(self.status_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                self.log('OK', f'Servidor conectado - Estado: {data.get("statState", "unknown")}')
                return True
            else:
                self.log('ERR', f'Servidor respondió con código {response.status_code}')
                return False
        except requests.exceptions.ConnectionError:
            self.log('ERR', f'No se pudo conectar al servidor. ¿Está corriendo?')
            return False
        except Exception as e:
            self.log('ERR', f'Error al verificar servidor: {e}')
            return False

    def connect_and_stream(self, duration=30):
        """
        Simular conexión al stream HTTP.
        
        Args:
            duration: Segundos para mantener la conexión (0 = ilimitado)
        """
        self.log('INFO', f'Conectando al stream: {self.stream_url}')
        
        try:
            response = requests.get(self.stream_url, stream=True, timeout=10)
            
            if response.status_code != 200:
                self.log('ERR', f'Servidor respondió con código {response.status_code}')
                return False
            
            self.connected = True
            client_id = response.headers.get('X-Client-Id', 'unknown')
            self.log('OK', f'Conectado como cliente #{client_id}')
            
            start_time = time.time()
            chunk_count = 0
            
            try:
                for chunk in response.iter_content(chunk_size=4096):
                    if chunk:
                        self.bytes_received += len(chunk)
                        self.chunks_received += 1
                        chunk_count += 1
                        
                        # Mostrar progreso cada 50 chunks
                        if chunk_count % 50 == 0:
                            elapsed = time.time() - start_time
                            mb = self.bytes_received / (1024 * 1024)
                            speed = (self.bytes_received / 1024) / elapsed if elapsed > 0 else 0
                            self.log('INFO', 
                                f'Recibidos {mb:.2f} MB en {elapsed:.1f}s ({speed:.1f} KB/s) - {chunk_count} chunks')
                        
                        # Timeout automático si se especificó duration
                        if duration > 0 and (time.time() - start_time) > duration:
                            self.log('WARN', f'Timeout de {duration}s alcanzado')
                            break
                    
                    # Permitir Ctrl+C
                    time.sleep(0)  # Yield a otros threads
                    
            except KeyboardInterrupt:
                self.log('WARN', 'Desconexión manual (Ctrl+C)')
            except requests.exceptions.ChunkedEncodingError:
                self.log('WARN', 'El servidor cerró la conexión (probablemente skip/stop)')
            
            self.connected = False
            elapsed = time.time() - start_time
            mb = self.bytes_received / (1024 * 1024)
            
            self.log('OK', f'Desconectado después de {elapsed:.1f}s')
            self.log('INFO', f'Total: {self.bytes_received} bytes ({mb:.2f} MB) en {self.chunks_received} chunks')
            
            return True
            
        except requests.exceptions.Timeout:
            self.log('ERR', 'Timeout de conexión - servidor no responde')
            return False
        except requests.exceptions.ConnectionError as e:
            self.log('ERR', f'Error de conexión: {e}')
            return False
        except Exception as e:
            self.log('ERR', f'Error inesperado: {e}')
            return False

    def get_status(self):
        """Obtener y mostrar el estado actual del servidor."""
        try:
            response = requests.get(self.status_url, timeout=3)
            data = response.json()
            
            print("\n" + "="*60)
            print("ESTADO DEL SERVIDOR")
            print("="*60)
            print(f"¿Reproduciendo?:   {data.get('isPlaying', False)}")
            print(f"¿Pausado?:         {data.get('isPaused', False)}")
            print(f"Clientes conectados: {data.get('connectedClients', 0)}")
            print(f"Canción actual:    {data.get('currentItem', {}).get('title', 'Ninguna')}")
            print(f"Cola (tracks):     {len(data.get('queue', []))}")
            
            if data.get('queue'):
                print("\nProximas en cola:")
                for i, track in enumerate(data['queue'][:5], 1):
                    print(f"  {i}. {track.get('title', track.get('url', 'Sin título'))}")
            
            print("="*60 + "\n")
            return True
        except Exception as e:
            self.log('ERR', f'No se pudo obtener estado: {e}')
            return False

    def interactive_mode(self):
        """Modo interactivo para controlar el servidor."""
        print("\n" + "="*60)
        print("MODO INTERACTIVO - CONTROLES")
        print("="*60)
        print("c - Conectar al stream (30s)")
        print("s - Ver estado actual")
        print("q - Salir")
        print("="*60 + "\n")
        
        while True:
            try:
                cmd = input("Comando> ").strip().lower()
                
                if cmd == 'c':
                    self.bytes_received = 0
                    self.chunks_received = 0
                    self.connect_and_stream(duration=30)
                
                elif cmd == 's':
                    self.get_status()
                
                elif cmd == 'q':
                    self.log('INFO', 'Saliendo...')
                    break
                
                else:
                    print("Comando no reconocido")
            
            except KeyboardInterrupt:
                self.log('INFO', 'Saliendo...')
                break
            except Exception as e:
                self.log('ERR', str(e))

def main():
    parser = argparse.ArgumentParser(
        description='Simulador de cliente ESP32 para testing'
    )
    parser.add_argument('--server', default='http://localhost:3000',
                        help='URL del servidor (default: http://localhost:3000)')
    parser.add_argument('--duration', type=int, default=0,
                        help='Duración de la conexión en segundos (0 = ilimitado)')
    parser.add_argument('--interactive', action='store_true',
                        help='Modo interactivo')
    
    args = parser.parse_args()
    
    print("\n")
    print("╔════════════════════════════════════════════════════╗")
    print("║   ESP32 Audio Stream Client Simulator              ║")
    print("║   Testing sin hardware real                        ║")
    print("╚════════════════════════════════════════════════════╝")
    
    sim = ESP32Simulator(args.server)
    
    # Verificar servidor
    if not sim.test_server_health():
        print("\nNo se pudo conectar al servidor.")
        print(f"¿Está corriendo en {args.server}?")
        sys.exit(1)
    
    print()
    
    if args.interactive:
        sim.interactive_mode()
    else:
        # Modo automático
        sim.connect_and_stream(duration=args.duration if args.duration > 0 else None)

if __name__ == '__main__':
    main()