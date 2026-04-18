"""
Web Helper - Помощник для поиска информации о дистрибутивах
"""

import webbrowser
from typing import Dict, List


class WebHelper:
    """Помощник для веб-ресурсов о дистрибутивах"""
    
    DISTRO_RESOURCES = {
        'Ubuntu': {
            'official': 'https://ubuntu.com',
            'documentation': 'https://ubuntu.com/server/docs',
            'community': 'https://ubuntu.com/community',
            'download': 'https://ubuntu.com/download',
            'forums': 'https://ubuntuforums.org'
        },
        'Fedora': {
            'official': 'https://fedoraproject.org',
            'documentation': 'https://docs.fedoraproject.org',
            'community': 'https://discussion.fedoraproject.org',
            'download': 'https://fedoraproject.org/download',
            'wiki': 'https://fedoraproject.org/wiki'
        },
        'Arch Linux': {
            'official': 'https://archlinux.org',
            'wiki': 'https://wiki.archlinux.org',
            'documentation': 'https://wiki.archlinux.org',
            'community': 'https://bbs.archlinux.org',
            'download': 'https://archlinux.org/download'
        },
        'Debian': {
            'official': 'https://www.debian.org',
            'documentation': 'https://www.debian.org/doc',
            'community': 'https://www.debian.org/support',
            'download': 'https://www.debian.org/distrib',
            'wiki': 'https://wiki.debian.org'
        },
        'Linux Mint': {
            'official': 'https://linuxmint.com',
            'documentation': 'https://linuxmint.com/documentation.php',
            'community': 'https://forums.linuxmint.com',
            'download': 'https://linuxmint.com/download.php'
        },
        'Pop!_OS': {
            'official': 'https://pop.system76.com',
            'documentation': 'https://support.system76.com',
            'community': 'https://forums.system76.com',
            'download': 'https://pop.system76.com'
        },
        'Manjaro': {
            'official': 'https://manjaro.org',
            'wiki': 'https://wiki.manjaro.org',
            'community': 'https://forum.manjaro.org',
            'download': 'https://manjaro.org/download'
        },
        'openSUSE': {
            'official': 'https://www.opensuse.org',
            'documentation': 'https://doc.opensuse.org',
            'community': 'https://forums.opensuse.org',
            'download': 'https://software.opensuse.org/distributions'
        },
        'CentOS': {
            'official': 'https://www.centos.org',
            'documentation': 'https://docs.centos.org',
            'community': 'https://forums.centos.org',
            'download': 'https://www.centos.org/download'
        },
        'Kubuntu': {
            'official': 'https://kubuntu.org',
            'documentation': 'https://kubuntu.org/documentation',
            'community': 'https://forum.kubuntu.org',
            'download': 'https://kubuntu.org/download'
        },
        'Lubuntu': {
            'official': 'https://lubuntu.me',
            'documentation': 'https://lubuntu.me/documentation',
            'community': 'https://lubuntu.me/community',
            'download': 'https://lubuntu.me/downloads'
        },
        'Xubuntu': {
            'official': 'https://xubuntu.org',
            'documentation': 'https://xubuntu.org/documentation',
            'community': 'https://xubuntu.org/community',
            'download': 'https://xubuntu.org/download'
        }
    }
    
    GENERAL_RESOURCES = {
        'DistroWatch': 'https://distrowatch.com',
        'Linux.org': 'https://linux.org',
        'Linux.com': 'https://linux.com',
        'Arch Linux Wiki': 'https://wiki.archlinux.org',
        'Ubuntu Wiki': 'https://help.ubuntu.com',
        'Fedora Wiki': 'https://fedoraproject.org/wiki'
    }
    
    @staticmethod
    def get_distro_resources(distro_name: str) -> Dict[str, str]:
        """Получить ресурсы для конкретного дистрибутива"""
        # Нормализуем имя дистрибутива
        for key, resources in WebHelper.DISTRO_RESOURCES.items():
            if distro_name.lower() in key.lower():
                return resources
        return {}
    
    @staticmethod
    def open_url(url: str):
        """Открыть URL в браузере"""
        webbrowser.open(url)
    
    @staticmethod
    def search_distro_info(distro_name: str):
        """Поиск информации о дистрибутиве"""
        query = f"{distro_name} Linux distro review"
        webbrowser.open(f"https://www.google.com/search?q={query}")
    
    @staticmethod
    def get_all_distros() -> List[str]:
        """Получить список всех дистрибутивов"""
        return list(WebHelper.DISTRO_RESOURCES.keys())
    
    @staticmethod
    def get_hardware_resources() -> Dict[str, str]:
        """Получить ресурсы по железу"""
        return {
            'Arch Wiki - Hardware': 'https://wiki.archlinux.org/index.php/Hardware',
            'Ubuntu Hardware': 'https://help.ubuntu.com/community/HardwareSupport',
            'Linux Hardware': 'https://linux-hardware.org',
            'PCI IDs': 'https://pci-ids.ucw.cz'
        }
    
    @staticmethod
    def get_driver_resources() -> Dict[str, str]:
        """Получить ресурсы по драйверам"""
        return {
            'NVIDIA Drivers': 'https://www.nvidia.com/Download/index.aspx',
            'AMD Drivers': 'https://www.amd.com/support',
            'Intel Drivers': 'https://www.intel.com/content/www/us/en/download-center/home.html',
            'Ubuntu Drivers': 'https://help.ubuntu.com/community/BinaryDriverHowto'
        }
