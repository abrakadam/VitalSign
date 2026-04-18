"""
GPU Monitor - Мониторинг видеокарт
"""

import psutil
import subprocess

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class GPUMonitor:
    """Мониторинг GPU"""
    
    def __init__(self):
        self.gpus = []
    
    def is_available(self) -> bool:
        """Проверить доступность GPU мониторинга"""
        return GPU_AVAILABLE
    
    def get_all_gpus(self) -> list:
        """Получить информацию о всех GPU"""
        gpu_list = []
        
        # Пробуем GPUtil
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                for gpu in gpus:
                    gpu_info = {
                        'id': gpu.id,
                        'name': gpu.name,
                        'load': gpu.load * 100,
                        'memory_used': gpu.memoryUsed,
                        'memory_total': gpu.memoryTotal,
                        'temperature': gpu.temperature,
                        'uuid': gpu.uuid,
                        'driver': 'NVIDIA'
                    }
                    gpu_list.append(gpu_info)
            except Exception as e:
                print(f"Ошибка при получении информации о GPU через GPUtil: {e}")
        
        # Пробуем через lspci если GPUtil не сработал
        if not gpu_list:
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'VGA' in line or '3D' in line or 'Display' in line:
                        gpu_info = {
                            'id': 0,
                            'name': line,
                            'load': 0,
                            'memory_used': 0,
                            'memory_total': 0,
                            'temperature': 0,
                            'uuid': 'N/A',
                            'driver': 'Unknown'
                        }
                        gpu_list.append(gpu_info)
            except Exception as e:
                print(f"Ошибка при получении информации о GPU через lspci: {e}")
        
        return gpu_list
    
    def get_gpu_details(self, gpu_id: int = 0) -> dict:
        """Получить детальную информацию о конкретном GPU"""
        gpus = self.get_all_gpus()
        if gpu_id < len(gpus):
            gpu = gpus[gpu_id]
            details = {
                'name': gpu['name'],
                'load': gpu['load'],
                'memory_used': gpu['memory_used'],
                'memory_total': gpu['memory_total'],
                'temperature': gpu['temperature'],
                'driver': gpu.get('driver', 'N/A')
            }
            
            # Дополнительная информация через nvidia-smi
            if gpu.get('driver') == 'NVIDIA':
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=driver_version,cuda_version,serial,uuid', '--format=csv,noheader'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        parts = result.stdout.strip().split(',')
                        if len(parts) >= 4:
                            details['driver_version'] = parts[0]
                            details['cuda_version'] = parts[1]
                            details['serial'] = parts[2]
                            details['uuid'] = parts[3]
                except Exception:
                    pass
            
            return details
        
        return {}
    
    def get_total_memory(self) -> float:
        """Получить общую память всех GPU в GB"""
        gpus = self.get_all_gpus()
        total = sum(gpu['memory_total'] for gpu in gpus)
        return total / 1024.0  # MB to GB
