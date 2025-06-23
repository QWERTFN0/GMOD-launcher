import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import subprocess
import os
import winreg
import json
import webbrowser
from PIL import Image, ImageTk
from typing import Optional, List, Dict

class GModLauncher:
    def __init__(self, root):
        self.root = root
        self.dark_mode = False
        self.language = "ru"
        self.favorite_servers = []
        self.custom_servers = []
        self.server_history = []
        
        # Инициализация путей
        self.steam_path: Optional[str] = None
        self.gmod_path: Optional[str] = None
        self.update_paths()
        
        # Загрузка сохраненных данных
        self.load_data()
        
        # Локализация
        self.setup_localization()
        
        # Загрузка изображений
        self.load_images()
        
        # Настройка интерфейса
        self.setup_ui()
        self.load_servers()
        self.load_mods()
        
        # Применяем тему
        self.apply_theme()
        self.update_language()
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.gmod_process = None
    
    def setup_localization(self):
        """Настройка локализации"""
        self.localization = {
            "ru": {
                "title": "Garry's Mod Launcher",
                "subtitle": "Custom Launcher",
                "tabs": ["Серверы", "Моды", "Настройки"],
                "server_columns": ["Название", "Игроки", "Карта", "Пинг", "Адрес"],
                "buttons": {
                    "launch": "Запустить GMod",
                    "refresh": "Обновить всё",
                    "exit": "Выход",
                    "connect": "Подключиться",
                    "mods_folder": "Открыть папку модов",
                    "update_paths": "Обновить пути",
                    "manual_select": "Ручной выбор GMod",
                    "theme_light": "☀️",
                    "theme_dark": "🌙",
                    "add_server": "Добавить сервер",
                    "add_favorite": "В избранное",
                    "remove_favorite": "Удалить из избранного",
                    "install_mod": "Установить мод",
                    "workshop": "Мастерская Steam"
                },
                "settings": {
                    "paths": "Пути",
                    "launch_options": "Параметры запуска",
                    "console": "Запустить с консолью (-console)",
                    "not_found": "Не найден",
                    "select_gmod": "Выберите gmod.exe",
                    "success": "Успех",
                    "path_set": "Путь к GMod успешно установлен",
                    "error": "Ошибка",
                    "not_gmod": "Выбранный файл не является gmod.exe",
                    "updated": "Обновлено",
                    "all_updated": "Все данные успешно обновлены",
                    "enter_ip": "Введите IP сервера:",
                    "enter_port": "Введите порт сервера (по умолчанию 27015):",
                    "server_added": "Сервер добавлен!",
                    "mod_install": "Введите ID мода из мастерской Steam:",
                    "mod_installed": "Мод установлен!",
                    "no_steam": "Steam не найден, установка невозможна"
                }
            },
            "en": {
                "title": "Garry's Mod Launcher",
                "subtitle": "Custom Launcher",
                "tabs": ["Servers", "Mods", "Settings"],
                "server_columns": ["Name", "Players", "Map", "Ping", "Address"],
                "buttons": {
                    "launch": "Launch GMod",
                    "refresh": "Refresh All",
                    "exit": "Exit",
                    "connect": "Connect",
                    "mods_folder": "Open Mods Folder",
                    "update_paths": "Update Paths",
                    "manual_select": "Manual GMod Select",
                    "theme_light": "☀️",
                    "theme_dark": "🌙",
                    "add_server": "Add Server",
                    "add_favorite": "Add to Favorites",
                    "remove_favorite": "Remove from Favorites",
                    "install_mod": "Install Mod",
                    "workshop": "Steam Workshop"
                },
                "settings": {
                    "paths": "Paths",
                    "launch_options": "Launch Options",
                    "console": "Launch with console (-console)",
                    "not_found": "Not found",
                    "select_gmod": "Select gmod.exe",
                    "success": "Success",
                    "path_set": "GMod path set successfully",
                    "error": "Error",
                    "not_gmod": "Selected file is not gmod.exe",
                    "updated": "Updated",
                    "all_updated": "All data updated successfully",
                    "enter_ip": "Enter server IP:",
                    "enter_port": "Enter server port (default 27015):",
                    "server_added": "Server added!",
                    "mod_install": "Enter Steam Workshop mod ID:",
                    "mod_installed": "Mod installed!",
                    "no_steam": "Steam not found, installation impossible"
                }
            }
        }
    
    def load_data(self):
        """Загрузка сохраненных данных"""
        try:
            if os.path.exists("launcher_data.json"):
                with open("launcher_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorite_servers = data.get("favorites", [])
                    self.custom_servers = data.get("custom_servers", [])
                    self.server_history = data.get("history", [])
        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
    
    def save_data(self):
        """Сохранение данных"""
        try:
            data = {
                "favorites": self.favorite_servers,
                "custom_servers": self.custom_servers,
                "history": self.server_history
            }
            with open("launcher_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")
    
    def load_images(self):
        """Загрузка локальных изображений"""
        try:
            # Основной логотип (150x150)
            self.icon_image = ImageTk.PhotoImage(Image.open("gmo.png").resize((150, 150), Image.LANCZOS))
            
            # Маленький логотип для заголовка (50x50)
            self.small_icon = ImageTk.PhotoImage(Image.open("gmo.png").resize((50, 50), Image.LANCZOS))
            
            # Фоновое изображение
            bg_img = Image.open("gar3main.png")
            self.bg_image = ImageTk.PhotoImage(bg_img.resize((1000, 700), Image.LANCZOS))
            self.bg_image_dark = ImageTk.PhotoImage(bg_img.resize((1000, 700), Image.LANCZOS).point(lambda p: p * 0.4))
        except Exception as e:
            print(f"Ошибка загрузки изображений: {e}")
            self.icon_image = None
            self.small_icon = None
            self.bg_image = None
            self.bg_image_dark = None
    
    def setup_ui(self):
        """Настройка основного интерфейса"""
        self.root.title(self._("title"))
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Устанавливаем иконку окна
        if self.small_icon:
            self.root.iconphoto(False, self.small_icon)
        
        # Главный контейнер
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Установка фона
        self.bg_label = ttk.Label(self.main_frame)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Контент поверх фона
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок с логотипом
        self.header_frame = ttk.Frame(self.content_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        if self.icon_image:
            ttk.Label(self.header_frame, image=self.icon_image).pack(side=tk.LEFT, padx=10)
        
        title_frame = ttk.Frame(self.header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.title_label = ttk.Label(title_frame, font=('Helvetica', 18, 'bold'))
        self.title_label.pack(anchor=tk.W)
        self.subtitle_label = ttk.Label(title_frame, font=('Helvetica', 10))
        self.subtitle_label.pack(anchor=tk.W)
        
        # Кнопки управления
        control_frame = ttk.Frame(self.header_frame)
        control_frame.pack(side=tk.RIGHT)
        
        self.theme_btn = ttk.Button(control_frame, width=3, 
                                   command=self.toggle_theme)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        self.lang_btn = ttk.Button(control_frame, text="RU/EN", 
                                  command=self.toggle_language)
        self.lang_btn.pack(side=tk.LEFT)
        
        # Основное содержимое
        self.body_frame = ttk.Frame(self.content_frame)
        self.body_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(self.body_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        self.setup_servers_tab()
        self.setup_mods_tab()
        self.setup_settings_tab()
        
        # Панель кнопок внизу
        self.bottom_frame = ttk.Frame(self.content_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Зеленая кнопка запуска (полностью зеленая)
        self.launch_btn = tk.Button(self.bottom_frame, 
                                  bg="#4CAF50", fg="black",
                                  relief=tk.RAISED, bd=2,
                                  command=self.launch_gmod)
        self.launch_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        self.refresh_btn = ttk.Button(self.bottom_frame,
                                    command=self.refresh_all)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.exit_btn = ttk.Button(self.bottom_frame,
                                 command=self.on_close)
        self.exit_btn.pack(side=tk.RIGHT, padx=5)

    def _(self, key):
        """Получение локализованного текста"""
        return self.localization[self.language].get(key, key)

    def update_language(self):
        """Обновление всех текстов при смене языка"""
        self.root.title(self._("title"))
        self.title_label.config(text=self._("title"))
        self.subtitle_label.config(text=self._("subtitle"))
        
        # Обновление вкладок
        for i, tab_name in enumerate(self._("tabs")):
            self.notebook.tab(i, text=tab_name)
        
        # Обновление кнопок
        self.launch_btn.config(text=self._("buttons")["launch"])
        self.refresh_btn.config(text=self._("buttons")["refresh"])
        self.exit_btn.config(text=self._("buttons")["exit"])
        self.lang_btn.config(text="RU/EN" if self.language == "ru" else "EN/RU")
        
        # Обновление серверов
        if hasattr(self, 'servers_tree'):
            for i, col in enumerate(self._("server_columns")):
                self.servers_tree.heading(f"#{i+1}", text=col)
        
        # Обновление других элементов
        if hasattr(self, 'connect_btn'):
            self.connect_btn.config(text=self._("buttons")["connect"])
        if hasattr(self, 'mods_folder_btn'):
            self.mods_folder_btn.config(text=self._("buttons")["mods_folder"])
        if hasattr(self, 'add_server_btn'):
            self.add_server_btn.config(text=self._("buttons")["add_server"])
        if hasattr(self, 'favorite_btn'):
            self.favorite_btn.config(text=self._("buttons")["add_favorite"])
        if hasattr(self, 'install_mod_btn'):
            self.install_mod_btn.config(text=self._("buttons")["install_mod"])
        if hasattr(self, 'workshop_btn'):
            self.workshop_btn.config(text=self._("buttons")["workshop"])

    def toggle_language(self):
        """Переключение языка"""
        self.language = "en" if self.language == "ru" else "ru"
        self.update_language()

    def apply_theme(self):
        """Применение текущей темы"""
        if self.dark_mode:
            # Темная тема
            bg_color = '#2d2d2d'
            fg_color = '#ffffff'
            btn_color = '#3d3d3d'
            self.bg_label.config(image=self.bg_image_dark if self.bg_image_dark else self.bg_image)
            self.theme_btn.config(text=self._("buttons")["theme_dark"])
            
            # Стили для темной темы
            self.style = ttk.Style()
            self.style.configure('.', background=bg_color, foreground='black')
            self.style.configure('TFrame', background=bg_color)
            self.style.configure('TLabel', background=bg_color, foreground=fg_color)
            self.style.configure('TButton', background=btn_color, foreground='black')
            self.style.configure('Treeview', background=bg_color, fieldbackground=bg_color, 
                               foreground=fg_color, selectbackground='#0078d7')
            self.style.map('Treeview', background=[('selected', '#0078d7')], 
                          foreground=[('selected', 'white')])
            
            # Зеленая кнопка (остается зеленой в темной теме)
            self.launch_btn.config(bg="#4CAF50", fg="black")
        else:
            # Светлая тема
            bg_color = '#f0f0f0'
            fg_color = '#000000'
            btn_color = '#e1e1e1'
            self.bg_label.config(image=self.bg_image)
            self.theme_btn.config(text=self._("buttons")["theme_light"])
            
            # Стили для светлой темы
            self.style = ttk.Style()
            self.style.configure('.', background=bg_color, foreground='black')
            self.style.configure('TFrame', background=bg_color)
            self.style.configure('TLabel', background=bg_color, foreground=fg_color)
            self.style.configure('TButton', background=btn_color, foreground='black')
            self.style.configure('Treeview', background=bg_color, fieldbackground=bg_color, 
                               foreground=fg_color, selectbackground='#0078d7')
            self.style.map('Treeview', background=[('selected', '#0078d7')], 
                          foreground=[('selected', 'white')])
            
            # Зеленая кнопка
            self.launch_btn.config(bg="#4CAF50", fg="black")

    def toggle_theme(self):
        """Переключение темы"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def refresh_all(self):
        """Обновление всех данных"""
        self.update_paths()
        self.load_servers()
        self.load_mods()
        messagebox.showinfo(self._("settings")["updated"], 
                          self._("settings")["all_updated"])

    def update_paths(self):
        """Обновление путей к Steam и GMod"""
        self.steam_path = self.find_steam_path()
        self.gmod_path = self.find_gmod_path()
    
    def find_steam_path(self) -> Optional[str]:
        """Поиск пути к Steam через реестр Windows"""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                path = winreg.QueryValueEx(key, "InstallPath")[0]
                if os.path.exists(path):
                    return path
        except Exception as e:
            print(f"Не удалось найти Steam в реестре: {e}")
        
        # Альтернативные пути поиска
        alternate_paths = [
            os.path.join(os.getenv("ProgramFiles(x86)", ""), "Steam"),
            os.path.expanduser("~") + "\\Steam",
            "C:\\Steam",
            "D:\\Steam"
        ]
        
        for path in alternate_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def find_gmod_path(self) -> Optional[str]:
        """Поиск пути к Garry's Mod"""
        if not self.steam_path:
            return None
            
        # Стандартный путь
        standard_path = os.path.join(self.steam_path, "steamapps", "common", "GarrysMod", "gmod.exe")
        if os.path.exists(standard_path):
            return standard_path
            
        # Поиск через библиотеки Steam
        library_folders_path = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
        if os.path.exists(library_folders_path):
            try:
                with open(library_folders_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if '"path"' in line:
                            path = line.split('"')[-2].replace('\\\\', '\\')
                            test_path = os.path.join(path, "steamapps", "common", "GarrysMod", "gmod.exe")
                            if os.path.exists(test_path):
                                return test_path
            except Exception as e:
                print(f"Ошибка чтения libraryfolders.vdf: {e}")
        
        return None

    def setup_servers_tab(self):
        """Настройка вкладки с серверами"""
        self.servers_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.servers_tab, text=self._("tabs")[0])
        
        # Таблица серверов
        self.servers_tree = ttk.Treeview(self.servers_tab, columns=("name", "players", "map", "ping", "address"), show="headings")
        for i, col in enumerate(self._("server_columns")):
            self.servers_tree.heading(f"#{i+1}", text=col)
        
        # Настройка столбцов
        self.servers_tree.column("name", width=250, anchor=tk.W)
        self.servers_tree.column("players", width=70, anchor=tk.CENTER)
        self.servers_tree.column("map", width=120, anchor=tk.W)
        self.servers_tree.column("ping", width=50, anchor=tk.CENTER)
        self.servers_tree.column("address", width=120, anchor=tk.W)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.servers_tab, orient="vertical", command=self.servers_tree.yview)
        self.servers_tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.servers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления серверами
        btn_frame = ttk.Frame(self.servers_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.connect_btn = ttk.Button(btn_frame, command=self.connect_to_server)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.add_server_btn = ttk.Button(btn_frame, command=self.add_custom_server)
        self.add_server_btn.pack(side=tk.LEFT, padx=5)
        
        self.favorite_btn = ttk.Button(btn_frame, command=self.toggle_favorite)
        self.favorite_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_mods_tab(self):
        """Настройка вкладки с модами"""
        self.mods_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mods_tab, text=self._("tabs")[1])
        
        # Список модов
        self.mods_list = tk.Listbox(self.mods_tab, selectmode=tk.MULTIPLE)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self.mods_tab, orient="vertical", command=self.mods_list.yview)
        self.mods_list.configure(yscrollcommand=scrollbar.set)
        
        # Размещение
        self.mods_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления модами
        btn_frame = ttk.Frame(self.mods_tab)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.mods_folder_btn = ttk.Button(btn_frame, command=self.open_mods_folder)
        self.mods_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.install_mod_btn = ttk.Button(btn_frame, command=self.install_workshop_mod)
        self.install_mod_btn.pack(side=tk.LEFT, padx=5)
        
        self.workshop_btn = ttk.Button(btn_frame, command=self.open_workshop)
        self.workshop_btn.pack(side=tk.LEFT, padx=5)
    
    def setup_settings_tab(self):
        """Настройка вкладки с настройками"""
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text=self._("tabs")[2])
        
        # Настройки путей
        path_frame = ttk.LabelFrame(self.settings_tab, text=self._("settings")["paths"], padding=10)
        path_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(path_frame, text=f"Путь к Steam: {self.steam_path or self._('settings')['not_found']}").pack(anchor=tk.W)
        ttk.Label(path_frame, text=f"Путь к GMod: {self.gmod_path or self._('settings')['not_found']}").pack(anchor=tk.W)
        
        btn_frame = ttk.Frame(path_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text=self._("buttons")["update_paths"], 
                  command=self.update_paths).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=self._("buttons")["manual_select"], 
                  command=self.manual_path_select).pack(side=tk.LEFT, padx=5)
        
        # Параметры запуска
        launch_frame = ttk.LabelFrame(self.settings_tab, text=self._("settings")["launch_options"], padding=10)
        launch_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(launch_frame, text="Дополнительные параметры:").pack(anchor=tk.W)
        self.launch_options = ttk.Entry(launch_frame)
        self.launch_options.pack(fill=tk.X, pady=5)
        self.launch_options.insert(0, "-windowed -w 1920 -h 1080")
        
        self.console_var = tk.IntVar()
        ttk.Checkbutton(launch_frame, text=self._("settings")["console"], 
                       variable=self.console_var).pack(anchor=tk.W)

    def add_custom_server(self):
        """Добавление пользовательского сервера"""
        ip = simpledialog.askstring(self._("settings")["enter_ip"], 
                                   self._("settings")["enter_ip"])
        if not ip:
            return
            
        port = simpledialog.askstring(self._("settings")["enter_port"], 
                                     self._("settings")["enter_port"],
                                     initialvalue="27015")
        if not port:
            port = "27015"
            
        address = f"{ip}:{port}"
        server_info = (f"Пользовательский сервер {len(self.custom_servers)+1}", 
                      "0/0", "?", "?", address)
        
        self.custom_servers.append(server_info)
        self.save_data()
        self.load_servers()
        messagebox.showinfo(self._("settings")["success"], 
                          self._("settings")["server_added"])

    def toggle_favorite(self):
        """Добавление/удаление сервера из избранного"""
        selected = self.servers_tree.focus()
        if not selected:
            messagebox.showwarning(self._("settings")["error"], 
                                 "Выберите сервер!")
            return
            
        server = self.servers_tree.item(selected)['values']
        address = server[4]  # Адрес сервера
        
        # Проверяем, есть ли сервер в избранном
        if any(s[4] == address for s in self.favorite_servers):
            # Удаляем из избранного
            self.favorite_servers = [s for s in self.favorite_servers if s[4] != address]
            self.favorite_btn.config(text=self._("buttons")["add_favorite"])
        else:
            # Добавляем в избранное
            self.favorite_servers.append(server)
            self.favorite_btn.config(text=self._("buttons")["remove_favorite"])
        
        self.save_data()

    def install_workshop_mod(self):
        """Установка мода из мастерской Steam"""
        if not self.steam_path:
            messagebox.showerror(self._("settings")["error"], 
                               self._("settings")["no_steam"])
            return
            
        mod_id = simpledialog.askstring(self._("settings")["mod_install"], 
                                       self._("settings")["mod_install"])
        if not mod_id:
            return
            
        try:
            # Формируем команду для установки мода
            steamcmd = os.path.join(self.steam_path, "steamcmd.exe")
            command = f'"{steamcmd}" +login anonymous +workshop_download_item 4000 {mod_id} +quit'
            
            # Запускаем установку
            subprocess.Popen(command, shell=True)
            messagebox.showinfo(self._("settings")["success"], 
                              self._("settings")["mod_installed"])
        except Exception as e:
            messagebox.showerror(self._("settings")["error"], 
                               f"Ошибка установки мода: {e}")

    def open_workshop(self):
        """Открытие мастерской Steam"""
        webbrowser.open("https://steamcommunity.com/workshop/browse/?appid=4000")

    def manual_path_select(self):
        """Ручной выбор пути к GMod"""
        path = filedialog.askopenfilename(
            title=self._("settings")["select_gmod"],
            filetypes=[("Garry's Mod", "gmod.exe"), ("Executable files", "*.exe")]
        )
        
        if path and os.path.basename(path).lower() == "gmod.exe":
            self.gmod_path = path
            messagebox.showinfo(self._("settings")["success"], 
                              self._("settings")["path_set"])
            self.update_paths()
        elif path:
            messagebox.showerror(self._("settings")["error"], 
                               self._("settings")["not_gmod"])
    
    def open_mods_folder(self):
        """Открытие папки с модами"""
        if not self.steam_path:
            messagebox.showerror(self._("settings")["error"], 
                               "Не найден путь к Steam!")
            return
            
        mods_path = os.path.join(self.steam_path, "steamapps", "common", "GarrysMod", "garrysmod", "addons")
        if os.path.exists(mods_path):
            os.startfile(mods_path)
        else:
            messagebox.showerror(self._("settings")["error"], 
                               "Папка с модами не найдена!")

    def load_servers(self):
        """Загрузка списка серверов"""
        # Очищаем список
        for i in self.servers_tree.get_children():
            self.servers_tree.delete(i)
        
        # Тестовые данные
        servers = [
            ("DarkRP #1 | Начальный уровень", "24/32", "rp_downtown_v4c_v2", "45", "gmod.example.com:27015"),
            ("TTT Pro | Профессиональный режим", "12/16", "ttt_minecraft", "62", "ttt.example.com:27015"),
            ("Murder Mystery | Загадочные убийства", "8/10", "mu_mansion", "38", "murder.example.com:27015"),
            ("Sandbox | Свободное творчество", "15/20", "gm_flatgrass", "55", "sandbox.example.com:27015"),
            ("Zombie Survival | Выживание", "18/24", "zs_lighthouse", "42", "zombie.example.com:27015")
        ]
        
        # Добавляем избранные серверы
        for server in self.favorite_servers:
            self.servers_tree.insert("", tk.END, values=server, tags=('favorite',))
        
        # Добавляем обычные серверы
        for server in servers:
            self.servers_tree.insert("", tk.END, values=server)
        
        # Добавляем пользовательские серверы
        for server in self.custom_servers:
            self.servers_tree.insert("", tk.END, values=server, tags=('custom',))
        
        # Настраиваем теги для цветового выделения
        self.servers_tree.tag_configure('favorite', background='#fffacd')  # Светло-желтый для избранных
        self.servers_tree.tag_configure('custom', background='#e6f7ff')    # Светло-голубой для пользовательских

    def load_mods(self):
        """Загрузка списка модов"""
        self.mods_list.delete(0, tk.END)
        
        if not self.steam_path:
            self.mods_list.insert(tk.END, "Не найден путь к Steam!")
            return
            
        mods_path = os.path.join(self.steam_path, "steamapps", "common", "GarrysMod", "garrysmod", "addons")
        
        if os.path.exists(mods_path):
            try:
                mods = [d for d in os.listdir(mods_path) 
                       if os.path.isdir(os.path.join(mods_path, d)) and not d.startswith(".")]
                
                if not mods:
                    self.mods_list.insert(tk.END, "Моды не найдены!")
                    return
                
                for mod in sorted(mods):
                    self.mods_list.insert(tk.END, mod)
            except Exception as e:
                self.mods_list.insert(tk.END, f"Ошибка загрузки модов: {e}")
        else:
            self.mods_list.insert(tk.END, "Папка с модами не найдена!")

    def launch_gmod(self):
        """Запуск Garry's Mod"""
        if not self.gmod_path:
            messagebox.showerror(self._("settings")["error"], 
                               "Garry's Mod не найден!")
            return
            
        try:
            # Базовые параметры запуска
            args = [self.gmod_path]
            
            # Добавляем дополнительные параметры
            options = self.launch_options.get().strip()
            if options:
                args.extend(options.split())
            
            # Добавляем консоль, если нужно
            if self.console_var.get():
                args.append("-console")
            
            # Скрываем окно лаунчера
            self.root.withdraw()
            
            # Запускаем игру
            self.gmod_process = subprocess.Popen(args)
            
            # Проверяем завершение процесса
            self.root.after(1000, self.check_gmod_process)
                
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror(self._("settings")["error"], 
                               f"Не удалось запустить игру:\n{e}")

    def check_gmod_process(self):
        """Проверка состояния процесса GMod"""
        if self.gmod_process.poll() is None:
            # Процесс еще работает, проверяем снова через секунду
            self.root.after(1000, self.check_gmod_process)
        else:
            # Процесс завершен, показываем лаунчер снова
            self.root.deiconify()
            self.gmod_process = None

    def connect_to_server(self):
        """Подключение к выбранному серверу"""
        selected = self.servers_tree.focus()
        if not selected:
            messagebox.showwarning(self._("settings")["error"], 
                                 "Выберите сервер из списка!")
            return
        
        server_info = self.servers_tree.item(selected)['values']
        address = server_info[4]  # Адрес сервера
        
        # Добавляем сервер в историю
        if server_info not in self.server_history:
            self.server_history.append(server_info)
            self.save_data()
        
        if not self.gmod_path:
            messagebox.showerror(self._("settings")["error"], 
                               "Garry's Mod не найден!")
            return
            
        try:
            # Формируем команду для подключения
            args = [self.gmod_path, "-connect", address]
            
            # Добавляем дополнительные параметры
            options = self.launch_options.get().strip()
            if options:
                args.extend(options.split())
            
            # Скрываем окно лаунчера
            self.root.withdraw()
            
            # Запускаем игру с подключением к серверу
            self.gmod_process = subprocess.Popen(args)
            
            # Проверяем завершение процесса
            self.root.after(1000, self.check_gmod_process)
                
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror(self._("settings")["error"], 
                               f"Не удалось подключиться к серверу:\n{e}")

    def on_close(self):
        """Обработчик закрытия окна"""
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GModLauncher(root)
    root.mainloop()