"""
Модуль для оценки производительности оборудования
"""

import re
from typing import Dict, Tuple


class HardwareRater:
    """Класс для оценки производительности CPU и GPU"""
    
    # База данных процессоров с оценками
    CPU_DATABASE = {
        # AMD Ryzen 9
        'ryzen 9 7950x': 100,
        'ryzen 9 7900x': 95,
        'ryzen 9 5950x': 98,
        'ryzen 9 5900x': 92,
        'ryzen 9 3950x': 85,
        'ryzen 9 3900x': 82,
        # AMD Ryzen 7
        'ryzen 7 7800x3d': 100,
        'ryzen 7 7700x': 90,
        'ryzen 7 5800x3d': 95,
        'ryzen 7 5800x': 88,
        'ryzen 7 5700x': 85,
        'ryzen 7 3700x': 78,
        'ryzen 7 3800x': 80,
        # AMD Ryzen 5
        'ryzen 5 7600x': 85,
        'ryzen 5 5600x': 82,
        'ryzen 5 5500': 70,
        'ryzen 5 3600': 75,
        'ryzen 5 2600': 60,
        # Intel Core i9
        'i9-14900k': 100,
        'i9-13900k': 98,
        'i9-12900k': 92,
        'i9-10900k': 80,
        'i9-9900k': 75,
        # Intel Core i7
        'i7-14700k': 95,
        'i7-13700k': 92,
        'i7-12700k': 88,
        'i7-12700': 85,
        'i7-11700k': 82,
        'i7-10700k': 78,
        'i7-9700k': 72,
        # Intel Core i5
        'i5-14600k': 88,
        'i5-13600k': 85,
        'i5-12600k': 82,
        'i5-12400': 78,
        'i5-11400': 72,
        'i5-10400': 68,
        'i5-9600k': 65,
        'i5-9400f': 60,
        # Intel Core i3
        'i3-13100': 60,
        'i3-12100': 58,
        'i3-10100': 50,
        # Intel старые
        'i7-8700k': 68,
        'i7-7700k': 62,
        'i5-8400': 55,
        'i5-7500': 50,
        # AMD старые
        'ryzen 1700': 55,
        'ryzen 1600': 52,
        # AMD FX
        'fx-9590': 35,
        'fx-8350': 32,
        # AMD APU
        'athlon': 20,
        'a10': 25,
        'a8': 22,
    }
    
    # База данных видеокарт с оценками
    GPU_DATABASE = {
        # NVIDIA RTX 40 series
        'rtx 4090': 100,
        'rtx 4080': 95,
        'rtx 4070 ti': 90,
        'rtx 4070': 85,
        'rtx 4060 ti': 78,
        'rtx 4060': 72,
        # NVIDIA RTX 30 series
        'rtx 3090 ti': 95,
        'rtx 3090': 92,
        'rtx 3080 ti': 90,
        'rtx 3080': 88,
        'rtx 3070 ti': 85,
        'rtx 3070': 82,
        'rtx 3060 ti': 78,
        'rtx 3060': 72,
        'rtx 3050': 60,
        # NVIDIA RTX 20 series
        'rtx 2080 ti': 75,
        'rtx 2080': 72,
        'rtx 2070': 68,
        'rtx 2060': 65,
        # NVIDIA GTX 16 series
        'gtx 1660 ti': 58,
        'gtx 1660': 55,
        'gtx 1650': 45,
        # NVIDIA GTX 10 series
        'gtx 1080 ti': 62,
        'gtx 1080': 58,
        'gtx 1070': 55,
        'gtx 1060': 48,
        'gtx 1050 ti': 40,
        'gtx 1050': 35,
        # AMD RX 7000 series
        'rx 7900 xtx': 98,
        'rx 7900 xt': 95,
        'rx 7800 xt': 88,
        'rx 7700 xt': 82,
        'rx 7600': 72,
        # AMD RX 6000 series
        'rx 6950 xt': 88,
        'rx 6900 xt': 85,
        'rx 6800 xt': 82,
        'rx 6800': 78,
        'rx 6750 xt': 72,
        'rx 6700 xt': 70,
        'rx 6600 xt': 65,
        'rx 6600': 60,
        'rx 6500 xt': 45,
        # AMD RX 5000 series
        'rx 5700 xt': 68,
        'rx 5700': 65,
        'rx 5600 xt': 58,
        'rx 5500 xt': 48,
        # AMD RX Vega
        'rx vega 64': 52,
        'rx vega 56': 50,
        # AMD RX 500 series
        'rx 580': 42,
        'rx 570': 38,
        'rx 560': 32,
        # AMD RX 400 series
        'rx 480': 40,
        'rx 470': 38,
        # NVIDIA старые
        'gtx 980 ti': 45,
        'gtx 980': 42,
        'gtx 970': 40,
        'gtx 960': 35,
        'gtx 780': 28,
        # Интегрированная графика
        'intel iris': 15,
        'intel uhd': 10,
        'intel hd': 8,
        'amd radeon vega': 12,
        'amd radeon graphics': 15,
    }
    
    @staticmethod
    def rate_cpu(cpu_name: str, cpu_cores: int = 0, cpu_freq: float = 0) -> Dict[str, any]:
        """Оценить процессор"""
        cpu_name_lower = cpu_name.lower()
        
        # Ищем в базе данных
        for db_name, score in HardwareRater.CPU_DATABASE.items():
            if db_name in cpu_name_lower:
                rating = HardwareRater._get_rating_description(score)
                return {
                    'name': cpu_name,
                    'score': score,
                    'rating': rating,
                    'category': HardwareRater._get_category(score)
                }
        
        # Если не найдено в базе, оцениваем по характеристикам
        if cpu_cores > 0 and cpu_freq > 0:
            estimated_score = HardwareRater._estimate_cpu_score(cpu_cores, cpu_freq)
            rating = HardwareRater._get_rating_description(estimated_score)
            return {
                'name': cpu_name,
                'score': estimated_score,
                'rating': rating,
                'category': HardwareRater._get_category(estimated_score),
                'estimated': True
            }
        
        # Если нет данных
        return {
            'name': cpu_name,
            'score': 0,
            'rating': 'Неизвестно',
            'category': 'unknown'
        }
    
    @staticmethod
    def rate_gpu(gpu_name: str, vram: int = 0, is_integrated: bool = False) -> Dict[str, any]:
        """Оценить видеокарту"""
        gpu_name_lower = gpu_name.lower()
        
        # Ищем в базе данных
        for db_name, score in HardwareRater.GPU_DATABASE.items():
            if db_name in gpu_name_lower:
                # Если это встроенная карта, снижаем оценку
                if is_integrated:
                    score = int(score * 0.6)  # Снижаем на 40%
                rating = HardwareRater._get_rating_description(score)
                return {
                    'name': gpu_name,
                    'score': score,
                    'rating': rating,
                    'category': HardwareRater._get_category(score),
                    'is_integrated': is_integrated
                }
        
        # Если не найдено в базе, оцениваем по VRAM
        if vram > 0:
            estimated_score = HardwareRater._estimate_gpu_score(vram)
            # Если это встроенная карта, снижаем оценку
            if is_integrated:
                estimated_score = int(estimated_score * 0.6)  # Снижаем на 40%
            rating = HardwareRater._get_rating_description(estimated_score)
            return {
                'name': gpu_name,
                'score': estimated_score,
                'rating': rating,
                'category': HardwareRater._get_category(estimated_score),
                'is_integrated': is_integrated,
                'estimated': True
            }
        
        # Если нет данных
        return {
            'name': gpu_name,
            'score': 0,
            'rating': 'Неизвестно',
            'category': 'unknown',
            'is_integrated': is_integrated
        }
    
    @staticmethod
    def _get_rating_description(score: int) -> str:
        """Получить описание оценки"""
        if score >= 90:
            return 'Отлично'
        elif score >= 75:
            return 'Очень хорошо'
        elif score >= 60:
            return 'Хорошо'
        elif score >= 45:
            return 'Средне'
        elif score >= 30:
            return 'Ниже среднего'
        elif score > 0:
            return 'Слабо'
        else:
            return 'Неизвестно'
    
    @staticmethod
    def _get_category(score: int) -> str:
        """Получить категорию"""
        if score >= 90:
            return 'flagship'
        elif score >= 75:
            return 'high_end'
        elif score >= 60:
            return 'mid_range'
        elif score >= 45:
            return 'entry_level'
        elif score > 0:
            return 'budget'
        else:
            return 'unknown'
    
    @staticmethod
    def _estimate_cpu_score(cores: int, freq: float) -> int:
        """Оценить CPU по количеству ядер и частоте"""
        # Базовая оценка
        base_score = cores * 5
        
        # Бонус за частоту
        freq_bonus = int(freq) * 2
        
        # Бонус за многоядерность
        if cores >= 16:
            multi_bonus = 20
        elif cores >= 12:
            multi_bonus = 15
        elif cores >= 8:
            multi_bonus = 10
        elif cores >= 6:
            multi_bonus = 5
        else:
            multi_bonus = 0
        
        total = base_score + freq_bonus + multi_bonus
        
        # Ограничиваем максимум
        return min(total, 85)
    
    @staticmethod
    def _estimate_gpu_score(vram: int) -> int:
        """Оценить GPU по объему VRAM"""
        if vram >= 24:
            return 90
        elif vram >= 16:
            return 80
        elif vram >= 12:
            return 70
        elif vram >= 8:
            return 60
        elif vram >= 6:
            return 50
        elif vram >= 4:
            return 40
        elif vram >= 2:
            return 25
        else:
            return 15
    
    @staticmethod
    def get_cpu_info() -> Dict[str, any]:
        """Получить информацию о CPU и его оценку"""
        try:
            import cpuinfo
            cpu_info = cpuinfo.get_cpu_info()
            
            cpu_name = cpu_info.get('brand_raw', 'Unknown CPU')
            cpu_cores = cpu_info.get('count', 0)
            
            # Попытка получить частоту
            try:
                import psutil
                freq = psutil.cpu_freq()
                cpu_freq = freq.max if freq else 0
            except:
                cpu_freq = 0
            
            rating = HardwareRater.rate_cpu(cpu_name, cpu_cores, cpu_freq)
            
            return {
                'name': cpu_name,
                'cores': cpu_cores,
                'frequency': cpu_freq,
                'architecture': cpu_info.get('arch', 'Unknown'),
                'rating': rating
            }
        except Exception as e:
            return {
                'name': 'Unknown CPU',
                'cores': 0,
                'frequency': 0,
                'architecture': 'Unknown',
                'rating': HardwareRater.rate_cpu('Unknown CPU')
            }
    
    @staticmethod
    def get_gpu_info() -> list:
        """Получить информацию о GPU и их оценки"""
        gpus = []
        
        try:
            import subprocess
            
            # Получаем информацию о GPU через lspci
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            gpu_lines = [line for line in result.stdout.split('\n') if 'vga' in line.lower() or '3d' in line.lower()]
            
            for line in gpu_lines:
                gpu_name = line.split(':')[2].strip() if ':' in line else 'Unknown GPU'
                
                # Определяем, встроенная ли видеокарта
                is_integrated = HardwareRater._is_integrated_gpu(gpu_name)
                
                # Пытаемся получить VRAM
                try:
                    result = subprocess.run(['lspci', '-v'], capture_output=True, text=True)
                    vram = 0
                    for v_line in result.stdout.split('\n'):
                        if gpu_name.split()[0] in v_line.lower() and 'prefetchable' in v_line:
                            match = re.search(r'(\d+)\s*[MG]B', v_line)
                            if match:
                                vram = int(match.group(1))
                                if 'GB' in v_line:
                                    vram *= 1024
                                break
                except:
                    vram = 0
                
                rating = HardwareRater.rate_gpu(gpu_name, vram, is_integrated)
                
                gpus.append({
                    'name': gpu_name,
                    'vram': vram,
                    'is_integrated': is_integrated,
                    'rating': rating
                })
            
        except Exception as e:
            pass
        
        # Если не нашли GPU, добавляем заглушку
        if not gpus:
            gpus.append({
                'name': 'Unknown GPU',
                'vram': 0,
                'is_integrated': False,
                'rating': HardwareRater.rate_gpu('Unknown GPU')
            })
        
        return gpus
    
    @staticmethod
    def _is_integrated_gpu(gpu_name: str) -> bool:
        """Определить, встроенная ли видеокарта"""
        gpu_name_lower = gpu_name.lower()
        
        # Intel встроенная графика
        if any(x in gpu_name_lower for x in ['intel iris', 'intel uhd', 'intel hd', 'intel graphics']):
            return True
        
        # AMD встроенная графика (APU)
        if any(x in gpu_name_lower for x in ['amd radeon vega', 'amd radeon graphics', 'radeon vega']):
            return True
        
        # Другие встроенные
        if any(x in gpu_name_lower for x in ['igpu', 'integrated', 'apu']):
            return True
        
        return False
