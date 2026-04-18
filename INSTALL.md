# Инструкция по установке VitalSign

## Содержание
- [Linux](#linux)
  - [Ubuntu/Debian](#ubuntudebian)
  - [Fedora/RHEL](#fedorarhel)
  - [Arch Linux](#arch-linux)
- [Windows](#windows)
- [Сборка EXE](#сборка-exe)
- [Создание пакетов](#создание-пакетов)

---

## Linux

### Ubuntu/Debian

#### Установка через PIP (рекомендуется)

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/VitalSign.git
cd VitalSign

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск
bash scripts/run_gui.sh
```

#### Установка системных зависимостей

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
sudo apt install libx11-dev libxtst-dev cmake build-essential
```

#### Создание .desktop файла для запуска из меню

```bash
cat > ~/.local/share/applications/vitalsign.desktop <<EOF
[Desktop Entry]
Name=VitalSign
Comment=Системный монитор
Exec=/path/to/VitalSign/scripts/run_gui.sh
Icon=/path/to/VitalSign/resources/icon.png
Terminal=false
Type=Application
Categories=System;Monitor;
EOF

chmod +x ~/.local/share/applications/vitalsign.desktop
```

---

### Fedora/RHEL

#### Установка через PIP

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/VitalSign.git
cd VitalSign

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск
bash scripts/run_gui.sh
```

#### Установка системных зависимостей

```bash
sudo dnf install python3 python3-pip python3-venv
sudo dnf install libX11-devel libXtst-devel cmake gcc-c++
```

---

### Arch Linux

#### Установка через PIP

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/VitalSign.git
cd VitalSign

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск
bash scripts/run_gui.sh
```

#### Установка системных зависимостей

```bash
sudo pacman -S python python-pip python-venv
sudo pacman -S libx11 libxtst cmake base-devel
```

#### Создание пакета AUR (опционально)

Создайте PKGBUILD:

```bash
# Maintainer: Your Name
pkgname=vitalsign
pkgver=1.0
pkgrel=1
pkgdesc="Продвинутый мониторинг системных ресурсов"
arch=('any')
url="https://github.com/yourusername/VitalSign"
license=('MIT')
depends=('python' 'python-pyqt6' 'python-psutil' 'python-matplotlib' 'python-numpy' 'python-gputil' 'python-pycpuinfo')
makedepends=('git' 'python-setuptools')
source=("git+$url.git")
sha256sums=('SKIP')

package() {
  cd "$srcdir/VitalSign"
  install -Dm755 scripts/run_gui.sh "$pkgdir/usr/bin/vitalsign"
  install -dm755 "$pkgdir/opt/vitalsign"
  cp -r * "$pkgdir/opt/vitalsign/"
}
```

Сборка:
```bash
makepkg -si
```

---

## Windows

### Установка через PIP

```powershell
# Клонирование репозитория
git clone https://github.com/yourusername/VitalSign.git
cd VitalSign

# Создание виртуального окружения
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск
scripts\run_gui.bat
```

### Создание ярлыка на рабочем столе

1. Нажмите правой кнопкой на рабочем столе
2. Создать → Ярлык
3. В поле "Укажите расположение объекта" введите:
   ```
   C:\path\to\VitalSign\scripts\run_gui.bat
   ```
4. Нажмите "Далее", дайте имя "VitalSign"
5. Нажмите "Готово"

---

## Сборка EXE

### PyInstaller

#### Простая сборка

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name VitalSign ui/python/gui_main.py
```

#### Полная сборка с ресурсами

```bash
pip install pyinstaller
pyinstaller --onefile \
  --windowed \
  --name VitalSign \
  --add-data "locales;locales" \
  --add-data "resources;resources" \
  --hidden-import PyQt6 \
  --hidden-import psutil \
  --hidden-import matplotlib \
  --hidden-import numpy \
  ui/python/gui_main.py
```

#### Использование spec-файла

```bash
pip install pyinstaller
pyinstaller VitalSign.spec
```

### Nuitka (более быстрые EXE)

```bash
pip install nuitka
python -m nuitka --standalone --onefile --windows-disable-console ui/python/gui_main.py
```

---

## Создание пакетов

### DEB пакет (Ubuntu/Debian)

#### Использование checkinstall

```bash
sudo apt install checkinstall
sudo checkinstall -D --pkgname=vitalsign --pkgversion=1.0 --pkgrelease=1 \
  --maintainer="your@email.com" \
  --requires="python3,python3-pyqt6,python3-psutil,python3-matplotlib" \
  --nodoc bash scripts/run_gui.sh
```

#### Установка созданного пакета

```bash
sudo dpkg -i vitalsign_1.0-1_amd64.deb
```

### RPM пакет (Fedora/RHEL)

#### Создание spec-файла

Создайте файл `vitalsign.spec`:

```spec
Name: vitalsign
Version: 1.0
Release: 1%{?dist}
Summary: Продвинутый мониторинг системных ресурсов
License: MIT
URL: https://github.com/yourusername/VitalSign
Source0: %{name}-%{version}.tar.gz

BuildRequires: python3-devel, python3-setuptools
Requires: python3, python3-pyqt6, python3-psutil, python3-matplotlib

%description
VitalSign - продвинутый мониторинг системных ресурсов с графическим интерфейсом.

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install --root=%{buildroot}

%files
%{python3_sitelib}/*
/usr/bin/vitalsign

%changelog
* $(date +%Y-%m-%d) Your Name <your@email.com> - 1.0-1
- Initial package
```

#### Сборка

```bash
rpmbuild -ba vitalsign.spec
```

### AppImage (универсальный формат для Linux)

```bash
# Установка tools
sudo apt install patchelf desktop-file-utils

# Скачивание appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Создание AppDir
mkdir -p VitalSign.AppDir/usr/bin
mkdir -p VitalSign.AppDir/usr/share/applications
mkdir -p VitalSign.AppDir/usr/share/icons

# Копирование файлов
cp scripts/run_gui.sh VitalSign.AppDir/usr/bin/vitalsign
cp resources/icon.png VitalSign.AppDir/usr/share/icons/vitalsign.png

# Создание .desktop файла
cat > VitalSign.AppDir/vitalsign.desktop <<EOF
[Desktop Entry]
Name=VitalSign
Exec=vitalsign
Icon=vitalsign
Type=Application
Categories=System;Monitor;
EOF

# Сборка
./appimagetool-x86_64.AppImage VitalSign.AppDir VitalSign-x86_64.AppImage
```

---

## Решение проблем

### Ошибка: ModuleNotFoundError: No module named 'PyQt6'

```bash
pip install PyQt6
```

### Ошибка: C++ system info library not available

Это предупреждение, программа продолжит работу с Python-версией. Для устранения:

```bash
sudo apt install libx11-dev libxtst-dev cmake build-essential
cd main/cpp
mkdir build && cd build
cmake ..
make
```

### Ошибка: Permission denied при запуске

```bash
chmod +x scripts/run_gui.sh
```

### Ошибка: Шрифты не отображаются

Убедитесь, что папка `resources/fonts/` существует и содержит шрифты.

---

## Автозапуск при старте системы

### Linux (Systemd)

```bash
# Создание service файла
cat > ~/.config/systemd/user/vitalsign.service <<EOF
[Unit]
Description=VitalSign System Monitor
After=graphical.target

[Service]
Type=simple
ExecStart=/path/to/VitalSign/scripts/run_gui.sh
Restart=on-failure

[Install]
WantedBy=default.target
EOF

# Активация
systemctl --user enable vitalsign.service
systemctl --user start vitalsign.service
```

### Windows

1. Откройте "Task Scheduler" (Планировщик заданий)
2. Создать задачу → "Create Basic Task"
3. Имя: "VitalSign"
4. Триггер: "When I log on"
5. Действие: "Start a program"
6. Программа: `C:\path\to\VitalSign\scripts\run_gui.bat`
7. Готово

---

## Обновление

### Обновление через git

```bash
cd VitalSign
git pull
source venv/bin/activate  # Linux
# или
venv\Scripts\activate  # Windows
pip install -r requirements.txt --upgrade
```

### Обновление через pip (если установлен как пакет)

```bash
pip install --upgrade vitalsign
```
