"""
Tkinter GUI Client for PC Assembly System v3.
Fixed: clients tab, active sessions, category dropdown, filters, layout.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import json

STATUS_MAP = {
    'accepted': 'Принят',
    'assembling': 'В сборке',
    'ready': 'Готов',
    'issued': 'Выдан',
    'cancelled': 'Отменён'
}
RU_TO_EN = {v: k for k, v in STATUS_MAP.items()}

CATEGORIES = {
    'CPU': 1, 'GPU': 2, 'RAM': 3, 'Motherboard': 4,
    'Storage': 5, 'PSU': 6, 'Case': 7
}
PC_CATEGORIES = {'Игровой': 1, 'Офисный': 2, 'Рабочая станция': 3}

class PCAssemblyClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Система сборки компьютеров на заказ")
        self.root.geometry("1200x800")
        self.root.configure(bg="#2c3e50")
        
        self.server_host = 'localhost'
        self.server_port = 5000
        self.socket = None
        self.current_user = None
        self.use_orm = True
        
        self.setup_ui()
        self.connect_to_server()
    
    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_host, self.server_port))
            self.status_var.set("Подключено к серверу")
        except Exception:
            self.socket = None
            self.status_var.set("Нет подключения")
    
    def send_request(self, request):
        try:
            if not self.socket:
                return {'success': False, 'error': 'Нет подключения к серверу'}
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self.socket.recv(16384)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def setup_ui(self):
        header = tk.Frame(self.root, bg='#2c3e50', height=50)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="Система сборки компьютеров на заказ", 
                 bg='#2c3e50', fg='white', font=('Arial', 16, 'bold')).pack(side=tk.LEFT, padx=15, pady=10)
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Подключиться", command=self.connect_to_server)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        mode_menu = tk.Menu(menubar, tearoff=0)
        self.orm_var = tk.BooleanVar(value=True)
        mode_menu.add_checkbutton(label="ORM режим", variable=self.orm_var, 
                                   command=lambda: self.set_mode(self.orm_var.get()))
        menubar.add_cascade(label="Режим", menu=mode_menu)
        
        self.status_var = tk.StringVar(value="Не подключено")
        tk.Label(self.root, textvariable=self.status_var, bg='#2c3e50', fg='white', 
                 relief=tk.FLAT, font=('Arial', 10)).pack(side=tk.BOTTOM, fill=tk.X)
        
        content = tk.Frame(self.root, bg='#ecf0f1')
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
        
        self.notebook = ttk.Notebook(content)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.tabs = {}
        tab_configs = [
            ("Авторизация", self.setup_login_tab),
            ("Комплектующие", self.setup_components_tab),
            ("Клиенты", self.setup_clients_tab),
            ("Каталог сборок", self.setup_catalog_tab),
            ("Конфигуратор", self.setup_configurator_tab),
            ("Заказы", self.setup_orders_tab),
            ("Финансы", self.setup_finance_tab),
            ("Администрирование", self.setup_admin_tab)
        ]
        
        for name, setup_func in tab_configs:
            frame = tk.Frame(self.notebook, bg='#ecf0f1')
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame
            setup_func(frame)
        
        for i in range(1, len(tab_configs)):
            self.notebook.tab(i, state='disabled')
    
    def set_mode(self, use_orm):
        self.use_orm = use_orm
        self.status_var.set(f"Режим: {'ORM' if use_orm else 'SQL'}")
    
    def enable_tabs(self):
        for i in range(1, 7):
            self.notebook.tab(i, state='normal')
        if self.current_user and self.current_user.get('role') == 'admin':
            self.notebook.tab(7, state='normal')
    
    def setup_login_tab(self, frame):
        inner = tk.Frame(frame, bg='#ecf0f1')
        inner.pack(expand=True)
        
        tk.Label(inner, text="Авторизация", bg='#ecf0f1', font=('Arial', 18, 'bold')).pack(pady=20)
        
        form = tk.Frame(inner, bg='#ecf0f1')
        form.pack(pady=10)
        
        tk.Label(form, text="Имя пользователя:", bg='#ecf0f1', font=('Arial', 12)).grid(row=0, column=0, padx=5, pady=8, sticky='e')
        self.username_entry = tk.Entry(form, width=30, font=('Arial', 12))
        self.username_entry.grid(row=0, column=1, padx=5, pady=8)
        self.username_entry.insert(0, "admin")
        
        tk.Label(form, text="Пароль:", bg='#ecf0f1', font=('Arial', 12)).grid(row=1, column=0, padx=5, pady=8, sticky='e')
        self.password_entry = tk.Entry(form, width=30, show='*', font=('Arial', 12))
        self.password_entry.grid(row=1, column=1, padx=5, pady=8)
        self.password_entry.insert(0, "password123")
        
        btn_frame = tk.Frame(inner, bg='#ecf0f1')
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Войти", command=self.login, bg='#3498db', fg='white',
                  font=('Arial', 12), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Регистрация", command=self.register_dialog, bg='#2ecc71', fg='white',
                  font=('Arial', 12), width=15).pack(side=tk.LEFT, padx=10)
        
        self.login_info = tk.Label(inner, text="", bg='#ecf0f1', font=('Arial', 11))
        self.login_info.pack(pady=10)
    
    def login(self):
        response = self.send_request({
            'action': 'login',
            'username': self.username_entry.get(),
            'password': self.password_entry.get()
        })
        
        if response.get('success'):
            self.current_user = response['user']
            self.login_info.config(text=f"Добро пожаловать, {self.current_user['username']} ({self.current_user['role']})", fg='green')
            self.enable_tabs()
            self.notebook.select(1)
            self.load_components()
        else:
            self.login_info.config(text=f"Ошибка: {response.get('error', 'Неверные данные')}", fg='red')
    
    def register_dialog(self):
        dialog = RegisterDialog(self.root)
        if dialog.result:
            response = self.send_request({
                'action': 'register',
                'username': dialog.result['username'],
                'password': dialog.result['password'],
                'role': 'operator'
            })
            if response.get('success'):
                messagebox.showinfo("Успех", f"Пользователь создан (ID: {response.get('user_id')})")
            else:
                messagebox.showerror("Ошибка", response.get('error'))
    
    def setup_components_tab(self, frame):
        toolbar = tk.Frame(frame, bg='#bdc3c7', padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Обновить", command=self.load_components, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Добавить", command=self.add_component, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Редактировать", command=self.edit_component, bg='#f39c12', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Удалить", command=self.delete_component, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        filter_frame = tk.LabelFrame(frame, text="Фильтры", bg='#ecf0f1', font=('Arial', 11))
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Категория:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.comp_category_filter = ttk.Combobox(filter_frame, values=['Все'] + list(CATEGORIES.keys()), width=15, state='readonly')
        self.comp_category_filter.pack(side=tk.LEFT, padx=5)
        self.comp_category_filter.set('Все')
        self.comp_category_filter.bind('<<ComboboxSelected>>', lambda e: self.load_components())
        
        tk.Label(filter_frame, text="Бренд:", bg='#ecf0f1').pack(side=tk.LEFT, padx=(20, 5))
        self.brand_filter = tk.Entry(filter_frame, width=15)
        self.brand_filter.pack(side=tk.LEFT, padx=5)
        
        self.stock_var = tk.BooleanVar()
        tk.Checkbutton(filter_frame, text="Только в наличии", variable=self.stock_var, 
                       bg='#ecf0f1', command=self.load_components).pack(side=tk.LEFT, padx=20)
        
        tk.Button(filter_frame, text="Применить", command=self.load_components, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Сбросить", command=self.reset_comp_filters, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'name', 'brand', 'model', 'category', 'price', 'stock')
        self.components_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col, text, width in zip(columns, 
                                    ('ID', 'Название', 'Бренд', 'Модель', 'Категория', 'Цена продажи', 'На складе'),
                                    (50, 200, 100, 150, 120, 100, 80)):
            self.components_tree.heading(col, text=text)
            self.components_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.components_tree.yview)
        self.components_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.components_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def reset_comp_filters(self):
        self.comp_category_filter.set('Все')
        self.brand_filter.delete(0, tk.END)
        self.stock_var.set(False)
        self.load_components()
    
    def load_components(self):
        filters = {}
        cat = self.comp_category_filter.get()
        if cat != 'Все' and cat in CATEGORIES:
            filters['category_id'] = CATEGORIES[cat]
        brand = self.brand_filter.get().strip()
        if brand:
            filters['brand'] = brand
        if self.stock_var.get():
            filters['in_stock'] = True
        
        response = self.send_request({
            'action': 'component_list',
            'use_orm': self.use_orm,
            'filters': filters if filters else None
        })
        
        if response.get('success'):
            for item in self.components_tree.get_children():
                self.components_tree.delete(item)
            for comp in response.get('data', []):
                self.components_tree.insert('', tk.END, values=(
                    comp['component_id'],
                    comp['component_name'],
                    comp['brand'],
                    comp['model'],
                    comp.get('category_name', ''),
                    f"{float(comp['selling_price']):.2f}",
                    comp['quantity_in_stock']
                ))
    
    def add_component(self):
        dialog = ComponentDialog(self.root, "Добавить комплектующее")
        if dialog.result:
            response = self.send_request({
                'action': 'component_create',
                'use_orm': self.use_orm,
                'data': dialog.result
            })
            if response.get('success'):
                self.load_components()
                messagebox.showinfo("Успех", f"Компонент добавлен (ID: {response['component_id']})")
            else:
                messagebox.showerror("Ошибка", response.get('error'))
    
    def edit_component(self):
        selected = self.components_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите компонент")
            return
        item = self.components_tree.item(selected[0])
        values = item['values']
        dialog = ComponentDialog(self.root, "Редактировать комплектующее", {
            'component_name': values[1],
            'brand': values[2],
            'model': values[3],
            'category_name': values[4]
        })
        if dialog.result:
            response = self.send_request({
                'action': 'component_update',
                'use_orm': self.use_orm,
                'component_id': values[0],
                'data': dialog.result
            })
            if response.get('success'):
                self.load_components()
    
    def delete_component(self):
        selected = self.components_tree.selection()
        if not selected:
            return
        component_id = self.components_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить компонент?"):
            response = self.send_request({
                'action': 'component_delete',
                'use_orm': self.use_orm,
                'component_id': component_id
            })
            if response.get('success'):
                self.load_components()
    
    def setup_clients_tab(self, frame):
        toolbar = tk.Frame(frame, bg='#bdc3c7', padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Обновить", command=self.load_clients, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Добавить", command=self.add_client, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Редактировать", command=self.edit_client, bg='#f39c12', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Удалить", command=self.delete_client, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        filter_frame = tk.LabelFrame(frame, text="Фильтры", bg='#ecf0f1', font=('Arial', 11))
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Фамилия:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.client_last_filter = tk.Entry(filter_frame, width=20)
        self.client_last_filter.pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Найти", command=self.load_clients, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(filter_frame, text="Сбросить", command=self.reset_client_filters, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'first_name', 'last_name', 'email', 'phone', 'date')
        self.clients_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col, text, width in zip(columns,
                                    ('ID', 'Имя', 'Фамилия', 'Email', 'Телефон', 'Дата регистрации'),
                                    (50, 120, 150, 200, 120, 120)):
            self.clients_tree.heading(col, text=text)
            self.clients_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clients_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def reset_client_filters(self):
        self.client_last_filter.delete(0, tk.END)
        self.load_clients()
    
    def load_clients(self):
        filters = {}
        last = self.client_last_filter.get().strip()
        if last:
            filters['last_name'] = last
        
        response = self.send_request({
            'action': 'client_list',
            'use_orm': self.use_orm,
            'filters': filters if filters else None
        })
        
        if response.get('success'):
            for item in self.clients_tree.get_children():
                self.clients_tree.delete(item)
            for client in response.get('data', []):
                reg_date = client.get('registration_date', '')
                if reg_date:
                    reg_date = reg_date[:10]
                self.clients_tree.insert('', tk.END, values=(
                    client['client_id'],
                    client['first_name'],
                    client['last_name'],
                    client.get('email', ''),
                    client.get('phone', ''),
                    reg_date
                ))
    
    def add_client(self):
        dialog = ClientDialog(self.root, "Добавить клиента")
        if dialog.result:
            response = self.send_request({
                'action': 'client_create',
                'use_orm': self.use_orm,
                'data': dialog.result
            })
            if response.get('success'):
                self.load_clients()
                messagebox.showinfo("Успех", f"Клиент добавлен (ID: {response['client_id']})")
            else:
                messagebox.showerror("Ошибка", response.get('error'))
    
    def edit_client(self):
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите клиента")
            return
        item = self.clients_tree.item(selected[0])
        values = item['values']
        dialog = ClientDialog(self.root, "Редактировать клиента", {
            'first_name': values[1],
            'last_name': values[2],
            'email': values[3],
            'phone': values[4]
        })
        if dialog.result:
            response = self.send_request({
                'action': 'client_update',
                'use_orm': self.use_orm,
                'client_id': values[0],
                'data': dialog.result
            })
            if response.get('success'):
                self.load_clients()
    
    def delete_client(self):
        selected = self.clients_tree.selection()
        if not selected:
            return
        client_id = self.clients_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить клиента?"):
            response = self.send_request({
                'action': 'client_delete',
                'use_orm': self.use_orm,
                'client_id': client_id
            })
            if response.get('success'):
                self.load_clients()
    
    def setup_catalog_tab(self, frame):
        toolbar = tk.Frame(frame, bg='#bdc3c7', padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Обновить", command=self.load_builds, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Создать сборку", command=self.create_build, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Просмотр", command=self.view_build, bg='#9b59b6', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Удалить", command=self.delete_build, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'name', 'category', 'base_price', 'markup', 'components', 'total_cost')
        self.builds_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col, text, width in zip(columns,
                                    ('ID', 'Название', 'Категория', 'Базовая цена', 'Наценка %', 'Компонентов', 'Итоговая стоимость'),
                                    (50, 200, 120, 100, 80, 100, 120)):
            self.builds_tree.heading(col, text=text)
            self.builds_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.builds_tree.yview)
        self.builds_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.builds_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_builds(self):
        response = self.send_request({
            'action': 'build_list',
            'use_orm': self.use_orm
        })
        if response.get('success'):
            for item in self.builds_tree.get_children():
                self.builds_tree.delete(item)
            for build in response.get('data', []):
                self.builds_tree.insert('', tk.END, values=(
                    build['build_id'],
                    build['build_name'],
                    build.get('category_name', ''),
                    f"{float(build['base_price']):.2f}",
                    build['markup_percent'],
                    build.get('components_count', 0),
                    f"{float(build.get('total_cost', 0)):.2f}"
                ))
    
    def create_build(self):
        dialog = BuildDialog(self.root, self)
        if dialog.result:
            response = self.send_request({
                'action': 'build_create',
                'use_orm': self.use_orm,
                'data': dialog.result['build_data']
            })
            if response.get('success'):
                build_id = response['build_id']
                for comp in dialog.result['components']:
                    self.send_request({
                        'action': 'build_add_component',
                        'use_orm': self.use_orm,
                        'build_id': build_id,
                        'component_id': comp['component_id'],
                        'quantity': comp['quantity']
                    })
                self.load_builds()
                messagebox.showinfo("Успех", f"Сборка #{build_id} создана")
    
    def view_build(self):
        selected = self.builds_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите сборку")
            return
        build_id = self.builds_tree.item(selected[0])['values'][0]
        response = self.send_request({
            'action': 'build_get',
            'use_orm': self.use_orm,
            'build_id': build_id
        })
        if response.get('success'):
            build = response['data']
            msg = f"Сборка: {build['build_name']}\n"
            msg += f"Категория: {build.get('category_name', 'N/A')}\n"
            msg += f"Базовая цена: {float(build['base_price']):.2f}\n"
            msg += f"Наценка: {build['markup_percent']}%\n"
            msg += f"Итоговая цена: {float(build.get('final_price', 0)):.2f}\n\n"
            msg += "Компоненты:\n"
            for comp in build.get('components', []):
                msg += f"  - {comp['component_name']} ({comp['brand']}) x{comp['quantity']} = {float(comp['selling_price']) * comp['quantity']:.2f}\n"
            messagebox.showinfo("Детали сборки", msg)
    
    def delete_build(self):
        selected = self.builds_tree.selection()
        if not selected:
            return
        build_id = self.builds_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Подтверждение", "Удалить сборку?"):
            response = self.send_request({
                'action': 'build_delete',
                'use_orm': self.use_orm,
                'build_id': build_id
            })
            if response.get('success'):
                self.load_builds()
    
    def setup_configurator_tab(self, frame):
        left = tk.Frame(frame, bg='#ecf0f1')
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(left, text="Доступные компоненты", bg='#ecf0f1', font=('Arial', 13, 'bold')).pack(pady=5)
        
        filter_frame = tk.Frame(left, bg='#ecf0f1')
        filter_frame.pack(fill=tk.X, pady=5)
        tk.Label(filter_frame, text="Категория:", bg='#ecf0f1').pack(side=tk.LEFT)
        self.config_category = ttk.Combobox(filter_frame, values=['Все'] + list(CATEGORIES.keys()), width=15, state='readonly')
        self.config_category.pack(side=tk.LEFT, padx=5)
        self.config_category.set('Все')
        self.config_category.bind('<<ComboboxSelected>>', lambda e: self.load_config_components())
        tk.Button(filter_frame, text="Обновить", command=self.load_config_components, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'name', 'brand', 'price', 'stock')
        self.config_tree = ttk.Treeview(left, columns=columns, show='headings', height=12)
        for col, text, width in zip(columns, ('ID', 'Название', 'Бренд', 'Цена', 'Наличие'), (50, 200, 100, 80, 80)):
            self.config_tree.heading(col, text=text)
            self.config_tree.column(col, width=width, anchor='center')
        self.config_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Button(left, text="Добавить в сборку →", command=self.add_to_config, 
                  bg='#2ecc71', fg='white', font=('Arial', 11)).pack(pady=5)
        
        right = tk.Frame(frame, bg='#ecf0f1')
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tk.Label(right, text="Ваша сборка", bg='#ecf0f1', font=('Arial', 13, 'bold')).pack(pady=5)
        
        columns2 = ('id', 'name', 'brand', 'qty', 'price')
        self.config_build_tree = ttk.Treeview(right, columns=columns2, show='headings', height=10)
        for col, text, width in zip(columns2, ('ID', 'Название', 'Бренд', 'Кол-во', 'Цена'), (50, 200, 100, 60, 80)):
            self.config_build_tree.heading(col, text=text)
            self.config_build_tree.column(col, width=width, anchor='center')
        self.config_build_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.config_total_label = tk.Label(right, text="Итого: 0.00 руб.", bg='#ecf0f1', 
                                           font=('Arial', 16, 'bold'), fg='#2c3e50')
        self.config_total_label.pack(pady=10)
        
        btn_frame = tk.Frame(right, bg='#ecf0f1')
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Удалить", command=self.remove_from_config, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Очистить", command=self.clear_config, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Оформить заказ", command=self.order_from_config, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        
        self.config_items = []
    
    def load_config_components(self):
        filters = {}
        cat = self.config_category.get()
        if cat != 'Все' and cat in CATEGORIES:
            filters['category_id'] = CATEGORIES[cat]
        
        response = self.send_request({
            'action': 'component_list',
            'use_orm': self.use_orm,
            'filters': filters if filters else None
        })
        
        if response.get('success'):
            for item in self.config_tree.get_children():
                self.config_tree.delete(item)
            for comp in response.get('data', []):
                self.config_tree.insert('', tk.END, values=(
                    comp['component_id'],
                    comp['component_name'],
                    comp['brand'],
                    f"{float(comp['selling_price']):.2f}",
                    comp['quantity_in_stock']
                ))
    
    def add_to_config(self):
        selected = self.config_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите компонент")
            return
        item = self.config_tree.item(selected[0])
        values = item['values']
        
        qty = simpledialog.askinteger("Количество", f"Сколько {values[1]} добавить?", initialvalue=1)
        if not qty or qty <= 0:
            return
        if qty > values[4]:
            messagebox.showerror("Ошибка", f"На складе только {values[4]} шт.")
            return
        
        self.config_items.append({
            'component_id': values[0],
            'component_name': values[1],
            'brand': values[2],
            'quantity': qty,
            'unit_price': float(values[3])
        })
        self.refresh_config_build()
    
    def remove_from_config(self):
        selected = self.config_build_tree.selection()
        if not selected:
            return
        idx = self.config_build_tree.index(selected[0])
        del self.config_items[idx]
        self.refresh_config_build()
    
    def clear_config(self):
        self.config_items = []
        self.refresh_config_build()
    
    def refresh_config_build(self):
        for item in self.config_build_tree.get_children():
            self.config_build_tree.delete(item)
        total = 0
        for item in self.config_items:
            self.config_build_tree.insert('', tk.END, values=(
                item['component_id'],
                item['component_name'],
                item['brand'],
                item['quantity'],
                f"{item['unit_price']:.2f}"
            ))
            total += item['unit_price'] * item['quantity']
        self.config_total_label.config(text=f"Итого: {total:.2f} руб.")
    
    def order_from_config(self):
        if not self.config_items:
            messagebox.showwarning("Внимание", "Сборка пуста")
            return
        
        client_id = simpledialog.askinteger("Клиент", "Введите ID клиента:")
        if not client_id:
            return
        
        total = sum(item['unit_price'] * item['quantity'] for item in self.config_items)
        
        response = self.send_request({
            'action': 'order_create',
            'use_orm': self.use_orm,
            'data': {
                'client_id': client_id,
                'order_type': 'custom',
                'total_price': total
            }
        })
        
        if response.get('success'):
            order_id = response['order_id']
            for item in self.config_items:
                self.send_request({
                    'action': 'order_add_item',
                    'use_orm': self.use_orm,
                    'order_id': order_id,
                    'component_id': item['component_id'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price']
                })
            messagebox.showinfo("Успех", f"Заказ #{order_id} оформлен!")
            self.clear_config()
        else:
            messagebox.showerror("Ошибка", response.get('error'))
    
    def setup_orders_tab(self, frame):
        toolbar = tk.Frame(frame, bg='#bdc3c7', padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Обновить", command=self.load_orders, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Создать заказ", command=self.create_order, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Изменить статус", command=self.update_order_status, bg='#f39c12', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Детали", command=self.view_order_details, bg='#9b59b6', fg='white').pack(side=tk.LEFT, padx=5)
        
        filter_frame = tk.LabelFrame(frame, text="Фильтры", bg='#ecf0f1', font=('Arial', 11))
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(filter_frame, text="Статус:", bg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.order_status_filter = ttk.Combobox(filter_frame, values=['Все'] + list(STATUS_MAP.values()), width=12, state='readonly')
        self.order_status_filter.pack(side=tk.LEFT, padx=5)
        self.order_status_filter.set('Все')
        self.order_status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_orders())
        
        tk.Button(filter_frame, text="Сбросить", command=self.reset_order_filters, bg='#95a5a6', fg='white').pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'client', 'type', 'status', 'total', 'date')
        self.orders_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col, text, width in zip(columns, ('ID', 'Клиент', 'Тип', 'Статус', 'Сумма', 'Дата'), (50, 150, 80, 100, 100, 100)):
            self.orders_tree.heading(col, text=text)
            self.orders_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def reset_order_filters(self):
        self.order_status_filter.set('Все')
        self.load_orders()
    
    def load_orders(self):
        filters = {}
        status = self.order_status_filter.get()
        if status != 'Все' and status in RU_TO_EN:
            filters['status'] = RU_TO_EN[status]
        
        response = self.send_request({
            'action': 'order_list',
            'use_orm': self.use_orm,
            'filters': filters if filters else None
        })
        if response.get('success'):
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            for order in response.get('data', []):
                status_text = STATUS_MAP.get(order['status'], order['status'])
                self.orders_tree.insert('', tk.END, values=(
                    order['order_id'],
                    order.get('client_name', order['client_id']),
                    order['order_type'],
                    status_text,
                    f"{float(order['total_price']):.2f}",
                    order['order_date'][:10] if order['order_date'] else ''
                ))
    
    def create_order(self):
        dialog = OrderDialog(self.root)
        if dialog.result:
            response = self.send_request({
                'action': 'order_create',
                'use_orm': self.use_orm,
                'data': dialog.result
            })
            if response.get('success'):
                self.load_orders()
                messagebox.showinfo("Успех", f"Заказ #{response['order_id']} создан")
    
    def update_order_status(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        order_id = self.orders_tree.item(selected[0])['values'][0]
        status = simpledialog.askstring("Статус", "Введите статус (accepted/assembling/ready/issued/cancelled):")
        if status:
            response = self.send_request({
                'action': 'order_update_status',
                'use_orm': self.use_orm,
                'order_id': order_id,
                'status': status
            })
            if response.get('success'):
                self.load_orders()
    
    def view_order_details(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        order_id = self.orders_tree.item(selected[0])['values'][0]
        
        response = self.send_request({
            'action': 'order_get',
            'use_orm': self.use_orm,
            'order_id': order_id
        })
        
        if not response.get('success'):
            return
        
        order = response['data']
        msg = f"Заказ #{order['order_id']}\n"
        msg += f"Клиент: {order.get('client_name', 'Unknown')}\n"
        msg += f"Тип: {order['order_type']}\n"
        msg += f"Статус: {STATUS_MAP.get(order['status'], order['status'])}\n"
        msg += f"Сумма: {float(order['total_price']):.2f}\n"
        msg += f"Дата: {order['order_date'][:10] if order['order_date'] else 'N/A'}\n\n"
        
        items_resp = self.send_request({
            'action': 'order_get_items',
            'use_orm': self.use_orm,
            'order_id': order_id
        })
        
        if items_resp.get('success') and items_resp['data']:
            msg += "Компоненты заказа:\n"
            for item in items_resp['data']:
                msg += f"  - {item['component_name']} ({item['brand']}) x{item['quantity']} = {float(item['unit_price']) * item['quantity']:.2f}\n"
        else:
            msg += "Компоненты: (каталоговый заказ или пустой)"
        
        messagebox.showinfo("Детали заказа", msg)
    
    def setup_finance_tab(self, frame):
        toolbar = tk.Frame(frame, bg='#bdc3c7', padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Обновить", command=self.load_finance, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Сводка", command=self.finance_summary, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Добавить расход", command=self.add_expense, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        columns = ('id', 'order_id', 'type', 'amount', 'description', 'date')
        self.finance_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        for col, text, width in zip(columns, ('ID', 'Заказ', 'Тип', 'Сумма', 'Описание', 'Дата'), (50, 80, 80, 100, 300, 120)):
            self.finance_tree.heading(col, text=text)
            self.finance_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.finance_tree.yview)
        self.finance_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.finance_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_finance(self):
        response = self.send_request({
            'action': 'finance_list',
            'use_orm': self.use_orm
        })
        if response.get('success'):
            for item in self.finance_tree.get_children():
                self.finance_tree.delete(item)
            for rec in response.get('data', []):
                type_text = 'Доход' if rec['record_type'] == 'income' else 'Расход'
                self.finance_tree.insert('', tk.END, values=(
                    rec['record_id'],
                    rec.get('order_id', '-'),
                    type_text,
                    f"{float(rec['amount']):.2f}",
                    rec.get('description', '')[:50],
                    rec['record_date'][:10] if rec['record_date'] else ''
                ))
    
    def finance_summary(self):
        response = self.send_request({
            'action': 'finance_summary',
            'use_orm': self.use_orm
        })
        if response.get('success'):
            data = response['data']
            msg = f"💰 Финансовая сводка\n\n"
            msg += f"Общий доход: {data['total_income']:.2f} руб.\n"
            msg += f"Общий расход: {data['total_expense']:.2f} руб.\n"
            msg += f"Прибыль: {data['profit']:.2f} руб."
            messagebox.showinfo("Финансовая сводка", msg)
    
    def add_expense(self):
        amount = simpledialog.askfloat("Расход", "Введите сумму расхода:")
        if not amount:
            return
        desc = simpledialog.askstring("Описание", "Описание расхода:")
        response = self.send_request({
            'action': 'finance_create',
            'use_orm': self.use_orm,
            'data': {
                'record_type': 'expense',
                'amount': amount,
                'description': desc or 'Расход'
            }
        })
        if response.get('success'):
            self.load_finance()
    
    def setup_admin_tab(self, frame):
        toolbar = tk.Frame(frame, bg='#34495e', padx=5, pady=5)
        toolbar.pack(fill=tk.X)
        
        tk.Button(toolbar, text="Пользователи", command=self.load_users, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Создать пользователя", command=self.admin_create_user, bg='#2ecc71', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Активные сессии", command=self.load_sessions, bg='#9b59b6', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Удалить пользователя", command=self.delete_user, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        self.admin_text = tk.Text(frame, wrap=tk.WORD, padx=10, pady=10, bg='#1e1e1e', fg='#d4d4d4', 
                                  font=('Consolas', 11), height=20)
        scrollbar = ttk.Scrollbar(frame, command=self.admin_text.yview)
        self.admin_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.admin_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def load_users(self):
        response = self.send_request({'action': 'user_list', 'use_orm': self.use_orm})
        if response.get('success'):
            self.admin_text.delete(1.0, tk.END)
            self.admin_text.insert(tk.END, "=== Пользователи системы ===\n\n")
            for user in response.get('data', []):
                created = user['created_at'][:10] if user['created_at'] else 'N/A'
                self.admin_text.insert(tk.END, f"ID: {user['user_id']}, Логин: {user['username']}, Роль: {user['role']}, Создан: {created}\n")
    
    def load_sessions(self):
        response = self.send_request({'action': 'active_sessions'})
        if response.get('success'):
            self.admin_text.delete(1.0, tk.END)
            self.admin_text.insert(tk.END, "=== Активные сессии ===\n\n")
            for session in response.get('data', []):
                self.admin_text.insert(tk.END, f"Сессия: {session['session_id']}\n")
                self.admin_text.insert(tk.END, f"  Пользователь: {session['username'] or 'None'}\n")
                self.admin_text.insert(tk.END, f"  Авторизован: {session['authenticated']}\n\n")
    
    def delete_user(self):
        user_id = simpledialog.askinteger("Удаление", "Введите ID пользователя:")
        if user_id:
            password = simpledialog.askstring("Подтверждение", "Введите ваш пароль:", show='*')
            response = self.send_request({
                'action': 'login',
                'username': self.current_user['username'],
                'password': password
            })
            if response.get('success'):
                del_response = self.send_request({
                    'action': 'user_delete',
                    'use_orm': self.use_orm,
                    'user_id': user_id,
                    'confirmed': True
                })
                if del_response.get('success'):
                    messagebox.showinfo("Успех", "Пользователь удален")
                    self.load_users()
                else:
                    messagebox.showerror("Ошибка", del_response.get('error'))
            else:
                messagebox.showerror("Ошибка", "Неверный пароль")
    
    def admin_create_user(self):
        dialog = AdminCreateUserDialog(self.root)
        if dialog.result:
            response = self.send_request({
                'action': 'user_create',
                'use_orm': self.use_orm,
                'data': dialog.result
            })
            if response.get('success'):
                messagebox.showinfo("Успех", f"Пользователь создан (ID: {response.get('user_id')})")
                self.load_users()
            else:
                messagebox.showerror("Ошибка", response.get('error'))

class ComponentDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x400")
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="Категория:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.category_var = tk.StringVar(value='CPU')
        self.category_combo = ttk.Combobox(self, values=list(CATEGORIES.keys()), textvariable=self.category_var, width=25, state='readonly')
        self.category_combo.grid(row=0, column=1, padx=10, pady=8)
        
        fields = [
            ('component_name', 'Название', data['component_name'] if data else ''),
            ('brand', 'Бренд', data['brand'] if data else ''),
            ('model', 'Модель', data['model'] if data else ''),
            ('specifications', 'Характеристики', data.get('specifications', '') if data else ''),
            ('price', 'Цена закупки', ''),
            ('selling_price', 'Цена продажи', ''),
            ('quantity_in_stock', 'Количество', '0')
        ]
        
        self.entries = {}
        for i, (key, label, value) in enumerate(fields, start=1):
            tk.Label(self, text=label + ":", font=('Arial', 11)).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            entry = tk.Entry(self, width=30, font=('Arial', 11))
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, str(value))
            self.entries[key] = entry
        
        tk.Button(self, text="Сохранить", command=self.save, bg='#2ecc71', fg='white', 
                  font=('Arial', 12), width=15).grid(row=len(fields)+1, column=0, columnspan=2, pady=20)
    
    def save(self):
        try:
            cat_name = self.category_var.get()
            self.result = {
                'category_id': CATEGORIES[cat_name],
                'component_name': self.entries['component_name'].get(),
                'brand': self.entries['brand'].get(),
                'model': self.entries['model'].get(),
                'specifications': self.entries['specifications'].get() or None,
                'price': float(self.entries['price'].get()),
                'selling_price': float(self.entries['selling_price'].get()),
                'quantity_in_stock': int(self.entries['quantity_in_stock'].get())
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")

class ClientDialog(tk.Toplevel):
    def __init__(self, parent, title, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x220")
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="Имя:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.first_name = tk.Entry(self, width=25, font=('Arial', 11))
        self.first_name.grid(row=0, column=1, padx=10, pady=8)
        self.first_name.insert(0, data['first_name'] if data else '')
        
        tk.Label(self, text="Фамилия:", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.last_name = tk.Entry(self, width=25, font=('Arial', 11))
        self.last_name.grid(row=1, column=1, padx=10, pady=8)
        self.last_name.insert(0, data['last_name'] if data else '')
        
        tk.Label(self, text="Email:", font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        self.email = tk.Entry(self, width=25, font=('Arial', 11))
        self.email.grid(row=2, column=1, padx=10, pady=8)
        self.email.insert(0, data['email'] if data else '')
        
        tk.Label(self, text="Телефон:", font=('Arial', 11)).grid(row=3, column=0, padx=10, pady=8, sticky='e')
        self.phone = tk.Entry(self, width=25, font=('Arial', 11))
        self.phone.grid(row=3, column=1, padx=10, pady=8)
        self.phone.insert(0, data['phone'] if data else '')
        
        tk.Button(self, text="Сохранить", command=self.save, bg='#2ecc71', fg='white',
                  font=('Arial', 12), width=15).grid(row=4, column=0, columnspan=2, pady=15)
    
    def save(self):
        self.result = {
            'first_name': self.first_name.get(),
            'last_name': self.last_name.get(),
            'email': self.email.get() or None,
            'phone': self.phone.get() or None
        }
        self.destroy()

class BuildDialog(tk.Toplevel):
    def __init__(self, parent, client):
        super().__init__(parent)
        self.title("Создать сборку")
        self.geometry("500x500")
        self.result = None
        self.client = client
        self.transient(parent)
        self.grab_set()
        self.components = []
        
        tk.Label(self, text="Название сборки:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.build_name = tk.Entry(self, width=30, font=('Arial', 11))
        self.build_name.grid(row=0, column=1, padx=10, pady=8)
        
        tk.Label(self, text="Категория ПК:", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.pc_category = ttk.Combobox(self, values=list(PC_CATEGORIES.keys()), width=27, state='readonly')
        self.pc_category.grid(row=1, column=1, padx=10, pady=8)
        self.pc_category.set('Игровой')
        
        tk.Label(self, text="Описание:", font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        self.description = tk.Entry(self, width=30, font=('Arial', 11))
        self.description.grid(row=2, column=1, padx=10, pady=8)
        
        tk.Label(self, text="Базовая цена:", font=('Arial', 11)).grid(row=3, column=0, padx=10, pady=8, sticky='e')
        self.base_price = tk.Entry(self, width=30, font=('Arial', 11))
        self.base_price.grid(row=3, column=1, padx=10, pady=8)
        self.base_price.insert(0, "0")
        
        tk.Label(self, text="Наценка %:", font=('Arial', 11)).grid(row=4, column=0, padx=10, pady=8, sticky='e')
        self.markup = tk.Entry(self, width=30, font=('Arial', 11))
        self.markup.grid(row=4, column=1, padx=10, pady=8)
        self.markup.insert(0, "15")
        
        tk.Label(self, text="Компоненты сборки:", font=('Arial', 12, 'bold')).grid(row=5, column=0, columnspan=2, pady=10)
        
        self.comp_list = tk.Listbox(self, width=50, height=6, font=('Arial', 11))
        self.comp_list.grid(row=6, column=0, columnspan=2, padx=10, pady=5)
        
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=5)
        tk.Button(btn_frame, text="Добавить компонент", command=self.add_comp, bg='#3498db', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.remove_comp, bg='#e74c3c', fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(self, text="Создать сборку", command=self.save, bg='#2ecc71', fg='white',
                  font=('Arial', 12), width=20).grid(row=8, column=0, columnspan=2, pady=20)
    
    def add_comp(self):
        comp_id = simpledialog.askinteger("Компонент", "ID компонента:", parent=self)
        qty = simpledialog.askinteger("Количество", "Количество:", initialvalue=1, parent=self)
        if comp_id and qty:
            self.components.append({'component_id': comp_id, 'quantity': qty})
            self.comp_list.insert(tk.END, f"ID:{comp_id} x{qty}")
    
    def remove_comp(self):
        sel = self.comp_list.curselection()
        if sel:
            idx = sel[0]
            del self.components[idx]
            self.comp_list.delete(idx)
    
    def save(self):
        try:
            cat_name = self.pc_category.get()
            self.result = {
                'build_data': {
                    'pc_category_id': PC_CATEGORIES[cat_name],
                    'build_name': self.build_name.get(),
                    'description': self.description.get(),
                    'base_price': float(self.base_price.get()),
                    'markup_percent': float(self.markup.get())
                },
                'components': self.components
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")

class OrderDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Создать заказ")
        self.geometry("400x280")
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="ID клиента:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.client_id = tk.Entry(self, width=25, font=('Arial', 11))
        self.client_id.grid(row=0, column=1, padx=10, pady=8)
        self.client_id.insert(0, "1")
        
        tk.Label(self, text="Тип заказа:", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.order_type = ttk.Combobox(self, values=['catalog', 'custom'], width=22, state='readonly')
        self.order_type.grid(row=1, column=1, padx=10, pady=8)
        self.order_type.set('custom')
        
        tk.Label(self, text="ID сборки (для каталога):", font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        self.build_id = tk.Entry(self, width=25, font=('Arial', 11))
        self.build_id.grid(row=2, column=1, padx=10, pady=8)
        
        tk.Label(self, text="Сумма:", font=('Arial', 11)).grid(row=3, column=0, padx=10, pady=8, sticky='e')
        self.total = tk.Entry(self, width=25, font=('Arial', 11))
        self.total.grid(row=3, column=1, padx=10, pady=8)
        self.total.insert(0, "100000")
        
        tk.Button(self, text="Создать", command=self.save, bg='#2ecc71', fg='white',
                  font=('Arial', 12), width=15).grid(row=4, column=0, columnspan=2, pady=20)
    
    def save(self):
        try:
            self.result = {
                'client_id': int(self.client_id.get()),
                'order_type': self.order_type.get(),
                'build_id': int(self.build_id.get()) if self.build_id.get() else None,
                'total_price': float(self.total.get())
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")

class RegisterDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Регистрация")
        self.geometry("350x180")
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="Имя пользователя:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.username = tk.Entry(self, width=25, font=('Arial', 11))
        self.username.grid(row=0, column=1, padx=10, pady=8)
        
        tk.Label(self, text="Пароль:", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.password = tk.Entry(self, width=25, show='*', font=('Arial', 11))
        self.password.grid(row=1, column=1, padx=10, pady=8)
        
        tk.Button(self, text="Создать", command=self.save, bg='#2ecc71', fg='white',
                  font=('Arial', 12), width=15).grid(row=2, column=0, columnspan=2, pady=15)
    
    def save(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Поля не должны быть пустыми")
            return
        self.result = {'username': username, 'password': password}
        self.destroy()

class AdminCreateUserDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Создать пользователя")
        self.geometry("360x220")
        self.result = None
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="Имя пользователя:", font=('Arial', 11)).grid(row=0, column=0, padx=10, pady=8, sticky='e')
        self.username = tk.Entry(self, width=25, font=('Arial', 11))
        self.username.grid(row=0, column=1, padx=10, pady=8)
        
        tk.Label(self, text="Пароль:", font=('Arial', 11)).grid(row=1, column=0, padx=10, pady=8, sticky='e')
        self.password = tk.Entry(self, width=25, show='*', font=('Arial', 11))
        self.password.grid(row=1, column=1, padx=10, pady=8)
        
        tk.Label(self, text="Роль:", font=('Arial', 11)).grid(row=2, column=0, padx=10, pady=8, sticky='e')
        self.role = ttk.Combobox(self, values=['operator', 'manager', 'admin'], width=22, state='readonly')
        self.role.grid(row=2, column=1, padx=10, pady=8)
        self.role.set('operator')
        
        tk.Button(self, text="Создать", command=self.save, bg='#2ecc71', fg='white',
                  font=('Arial', 12), width=15).grid(row=3, column=0, columnspan=2, pady=15)
    
    def save(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        role = self.role.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Поля не должны быть пустыми")
            return
        self.result = {'username': username, 'password': password, 'role': role}
        self.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = PCAssemblyClient(root)
    root.mainloop()