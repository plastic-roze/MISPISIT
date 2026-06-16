"""
Tkinter GUI Client for PC Assembly System.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import socket
import json
import threading

# Status translations: English <-> Russian
STATUS_MAP = {
    'accepted': 'Принят',
    'assembling': 'В сборке',
    'ready': 'Готов',
    'issued': 'Выдан',
    'cancelled': 'Отменён'
}
RU_TO_EN = {v: k for k, v in STATUS_MAP.items()}

class PCAssemblyClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Система сборки компьютеров на заказ")
        self.root.geometry("900x700")
        self.root.configure(bg="#ececec")

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
            # Don't show modal error here; allow user to use UI in offline mode
            self.socket = None
            self.status_var.set("Нет подключения")

    def send_request(self, request):
        try:
            if not self.socket:
                return {'success': False, 'error': 'Нет подключения к серверу'}
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self.socket.recv(4096)
            return json.loads(response.decode('utf-8'))
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def setup_ui(self):
        # Header bar
        header = tk.Frame(self.root, bg='#2f4958', height=50)
        header.pack(side=tk.TOP, fill=tk.X)
        tk.Label(header, text="Система сборки компьютеров на заказ", bg='#2f4958', fg='white', font=(None, 14, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)

        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Подключиться", command=self.connect_to_server)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        mode_menu = tk.Menu(menubar, tearoff=0)
        self.orm_var = tk.BooleanVar(value=True)
        mode_menu.add_checkbutton(label="ORM режим", variable=self.orm_var, command=lambda: self.set_mode(self.orm_var.get()))
        menubar.add_cascade(label="Режим", menu=mode_menu)

        # Status bar (footer)
        self.status_var = tk.StringVar(value="Не подключено")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bg='#2f4958', fg='white', relief=tk.FLAT)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # keep a Style instance and ensure button text is black
        self.style = ttk.Style()
        self.style.configure('TButton', foreground='black')

        # Notebook (tabs) inside a content frame to emulate screenshots
        content_frame = tk.Frame(self.root, bg='#ececec')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10,0))

        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Login tab
        self.login_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.login_frame, text="Авторизация")
        self.setup_login_tab()

        # Components tab
        self.components_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.components_frame, text="Комплектующие")
        self.setup_components_tab()

        # Orders tab
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="Заказы")
        self.setup_orders_tab()

        # Admin tab
        self.admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_frame, text="Администрирование")
        self.setup_admin_tab()

        # Disable tabs until login
        self.notebook.tab(1, state='disabled')
        self.notebook.tab(2, state='disabled')
        self.notebook.tab(3, state='disabled')

    def set_mode(self, use_orm):
        self.use_orm = use_orm
        self.status_var.set(f"Режим: {'ORM' if use_orm else 'SQL'}")

    def setup_login_tab(self):
        frame = ttk.Frame(self.login_frame, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Имя пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)
        self.username_entry.insert(0, "admin")

        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.password_entry = ttk.Entry(frame, width=30, show='*')
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)
        self.password_entry.insert(0, "password123")

        ttk.Button(frame, text="Войти", command=self.login).grid(row=2, column=0, padx=10, pady=20)
        ttk.Button(frame, text="Регистрация", command=self.register).grid(row=2, column=1, padx=10, pady=20)

        self.login_info = ttk.Label(frame, text="")
        self.login_info.grid(row=3, column=0, columnspan=2)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        response = self.send_request({
            'action': 'login',
            'username': username,
            'password': password
        })

        if response.get('success'):
            self.current_user = response['user']
            self.login_info.config(text=f"Добро пожаловать, {self.current_user['username']} ({self.current_user['role']})")
            self.notebook.tab(1, state='normal')
            self.notebook.tab(2, state='normal')
            if self.current_user['role'] == 'admin':
                self.notebook.tab(3, state='normal')
            self.notebook.select(1)
        else:
            messagebox.showerror("Ошибка", response.get('error', 'Ошибка авторизации'))

    def register(self):
        dialog = RegisterDialog(self.root, "Регистрация пользователей")
        if dialog.result:
            username = dialog.result['username']
            password = dialog.result['password']
            # users cannot choose role; default to 'operator'
            role = 'operator'
            response = self.send_request({
                'action': 'register',
                'username': username,
                'password': password,
                'role': role
            })
            if response.get('success'):
                messagebox.showinfo("Успех", f"Пользователь создан (ID: {response.get('user_id')})")
            else:
                messagebox.showerror("Ошибка", response.get('error', 'Не удалось зарегистрировать'))

    def setup_components_tab(self):
        style = ttk.Style()
        style.configure('Blue.TButton', background='#3498db', foreground='black')
        style.map('Blue.TButton', background=[('active', '#2980b9')])
        style.configure('Green.TButton', background='#2ecc71', foreground='black')
        style.map('Green.TButton', background=[('active', '#27ae60')])
        style.configure('Red.TButton', background='#e74c3c', foreground='black')
        style.map('Red.TButton', background=[('active', '#c0392b')])

        toolbar = tk.Frame(self.components_frame, bg='#f6f6f6')
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Обновить", command=self.load_components, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Добавить", command=self.add_component, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Редактировать", command=self.edit_component, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Удалить", command=self.delete_component, style='Red.TButton').pack(side=tk.LEFT, padx=6)

        filter_frame = tk.LabelFrame(self.components_frame, text="Фильтры", padx=5, pady=5, bg='#f6f6f6')
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="Бренд:").pack(side=tk.LEFT, padx=2)
        self.brand_filter = ttk.Entry(filter_frame, width=15)
        self.brand_filter.pack(side=tk.LEFT, padx=2)
        ttk.Button(filter_frame, text="Применить", command=self.load_components, style='Green.TButton').pack(side=tk.LEFT, padx=5)

        columns = ('id', 'name', 'brand', 'model', 'price', 'stock')
        self.components_tree = ttk.Treeview(self.components_frame, columns=columns, show='headings')
        for col, text in zip(columns, ('ID', 'Название', 'Бренд', 'Модель', 'Цена', 'На складе')):
            self.components_tree.heading(col, text=text)
            self.components_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(self.components_frame, orient=tk.VERTICAL, command=self.components_tree.yview)
        self.components_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.components_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_components(self):
        filters = {}
        brand = self.brand_filter.get()
        if brand:
            filters['brand'] = brand

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
                    comp['selling_price'],
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
        component_id = item['values'][0]

        dialog = ComponentDialog(self.root, "Редактировать комплектующее", item['values'])
        if dialog.result:
            response = self.send_request({
                'action': 'component_update',
                'use_orm': self.use_orm,
                'component_id': component_id,
                'data': dialog.result
            })
            if response.get('success'):
                self.load_components()

    def delete_component(self):
        selected = self.components_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите компонент")
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

    def setup_orders_tab(self):
        toolbar = tk.Frame(self.orders_frame, bg='#f6f6f6')
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Обновить", command=self.load_orders, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Создать заказ", command=self.create_order, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Изменить статус", command=self.update_order_status, style='Blue.TButton').pack(side=tk.LEFT, padx=6)

        columns = ('id', 'client', 'type', 'status', 'total', 'date')
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=columns, show='headings')
        for col, text in zip(columns, ('ID', 'Клиент', 'Тип', 'Статус', 'Сумма', 'Дата')):
            self.orders_tree.heading(col, text=text)
            self.orders_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(self.orders_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_orders(self):
        response = self.send_request({
            'action': 'order_list',
            'use_orm': self.use_orm
        })
        if response.get('success'):
            for item in self.orders_tree.get_children():
                self.orders_tree.delete(item)
            for order in response.get('data', []):
                status_text = STATUS_MAP.get(order['status'], order['status'])
                self.orders_tree.insert('', tk.END, values=(
                    order['order_id'],
                    order['client_id'],
                    order['order_type'],
                    status_text,
                    order['total_price'],
                    order['order_date'][:10] if order['order_date'] else ''
                ))

    def create_order(self):
        dialog = OrderDialog(self.root, "Создать заказ")
        if dialog.result:
            response = self.send_request({
                'action': 'order_create',
                'use_orm': self.use_orm,
                'data': dialog.result
            })
            if response.get('success'):
                self.load_orders()
                messagebox.showinfo("Успех", f"Заказ создан (ID: {response['order_id']})")

    def update_order_status(self):
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ")
            return
        order_id = self.orders_tree.item(selected[0])['values'][0]
        # Ask user for a status in Russian, map back to English for the server
        choices = ", ".join(STATUS_MAP.values())
        new_status_ru = simpledialog.askstring("Статус", f"Введите статус ({choices}):")
        if not new_status_ru:
            return
        new_status_ru = new_status_ru.strip()
        # map Russian to English; if user entered English, accept it
        if new_status_ru in RU_TO_EN:
            status_to_send = RU_TO_EN[new_status_ru]
        elif new_status_ru in STATUS_MAP:
            # user entered English key
            status_to_send = new_status_ru
        else:
            messagebox.showerror("Ошибка", "Неизвестный статус")
            return

        response = self.send_request({
            'action': 'order_update_status',
            'use_orm': self.use_orm,
            'order_id': order_id,
            'status': status_to_send
        })
        if response.get('success'):
            self.load_orders()

    def setup_admin_tab(self):
        toolbar = tk.Frame(self.admin_frame, bg='#334a57')
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Пользователи", command=self.load_users, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Создать пользователя", command=self.admin_create_user, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Активные сессии", command=self.load_sessions, style='Blue.TButton').pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Удалить пользователя", command=self.delete_user, style='Red.TButton').pack(side=tk.LEFT, padx=6)

        self.admin_text = tk.Text(self.admin_frame, wrap=tk.WORD, padx=10, pady=10, bg='#1e1e1e', fg='#d4d4d4', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(self.admin_frame, command=self.admin_text.yview)
        self.admin_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.admin_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_users(self):
        response = self.send_request({
            'action': 'user_list',
            'use_orm': self.use_orm
        })
        if response.get('success'):
            self.admin_text.delete(1.0, tk.END)
            for user in response.get('data', []):
                self.admin_text.insert(tk.END, f"ID: {user['user_id']}, Логин: {user['username']}, Роль: {user['role']}, Создан: {user['created_at'][:10] if user['created_at'] else 'N/A'}\n")

    def load_sessions(self):
        response = self.send_request({'action': 'active_sessions'})
        if response.get('success'):
            self.admin_text.delete(1.0, tk.END)
            for session in response.get('data', []):
                self.admin_text.insert(tk.END, f"Сессия: {session['session_id']}, Пользователь: {session['username']}, Авторизован: {session['authenticated']}\n")

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
        dialog = AdminCreateUserDialog(self.root, "Создать пользователя")
        if dialog.result:
            data = dialog.result
            response = self.send_request({
                'action': 'user_create',
                'use_orm': self.use_orm,
                'data': data
            })
            if response.get('success'):
                messagebox.showinfo("Успех", f"Пользователь создан (ID: {response.get('user_id')})")
                self.load_users()
            else:
                messagebox.showerror("Ошибка", response.get('error', 'Не удалось создать пользователя'))

class ComponentDialog(tk.Toplevel):
    def __init__(self, parent, title, values=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x350")
        self.result = None

        fields = [
            ('category_id', 'ID категории', values[0] if values else '1'),
            ('component_name', 'Название', values[1] if values else ''),
            ('brand', 'Бренд', values[2] if values else ''),
            ('model', 'Модель', values[3] if values else ''),
            ('price', 'Цена закупки', ''),
            ('selling_price', 'Цена продажи', ''),
            ('quantity_in_stock', 'Количество', '0')
        ]

        self.entries = {}
        for i, (key, label, value) in enumerate(fields):
            ttk.Label(self, text=label).grid(row=i, column=0, padx=5, pady=5, sticky='e')
            entry = ttk.Entry(self, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entry.insert(0, str(value))
            self.entries[key] = entry

        ttk.Button(self, text="Сохранить", command=self.save).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def save(self):
        try:
            self.result = {
                'category_id': int(self.entries['category_id'].get()),
                'component_name': self.entries['component_name'].get(),
                'brand': self.entries['brand'].get(),
                'model': self.entries['model'].get(),
                'price': float(self.entries['price'].get()),
                'selling_price': float(self.entries['selling_price'].get()),
                'quantity_in_stock': int(self.entries['quantity_in_stock'].get())
            }
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверные данные: {e}")


class RegisterDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("350x160")
        self.result = None

        ttk.Label(self, text="Имя пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.username = ttk.Entry(self, width=25)
        self.username.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Пароль:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.password = ttk.Entry(self, width=25, show='*')
        self.password.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Создать", command=self.save).grid(row=2, column=0, columnspan=2, pady=15)

    def save(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Поля не должны быть пустыми")
            return
        self.result = {'username': username, 'password': password}
        self.destroy()


class AdminCreateUserDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("360x200")
        self.result = None

        ttk.Label(self, text="Имя пользователя:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.username = ttk.Entry(self, width=25)
        self.username.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Пароль:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.password = ttk.Entry(self, width=25, show='*')
        self.password.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Роль:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.role = ttk.Combobox(self, values=['operator', 'manager', 'admin'], width=22)
        self.role.grid(row=2, column=1, padx=5, pady=5)
        self.role.set('operator')

        ttk.Button(self, text="Создать", command=self.save).grid(row=3, column=0, columnspan=2, pady=15)

    def save(self):
        username = self.username.get().strip()
        password = self.password.get().strip()
        role = self.role.get().strip()
        if not username or not password:
            messagebox.showerror("Ошибка", "Поля не должны быть пустыми")
            return
        self.result = {'username': username, 'password': password, 'role': role}
        self.destroy()

class OrderDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x250")
        self.result = None

        ttk.Label(self, text="ID клиента:").grid(row=0, column=0, padx=5, pady=5)
        self.client_id = ttk.Entry(self, width=30)
        self.client_id.grid(row=0, column=1, padx=5, pady=5)
        self.client_id.insert(0, "1")

        ttk.Label(self, text="Тип заказа:").grid(row=1, column=0, padx=5, pady=5)
        self.order_type = ttk.Combobox(self, values=['catalog', 'custom'], width=27)
        self.order_type.grid(row=1, column=1, padx=5, pady=5)
        self.order_type.set('custom')

        ttk.Label(self, text="ID сборки (для каталога):").grid(row=2, column=0, padx=5, pady=5)
        self.build_id = ttk.Entry(self, width=30)
        self.build_id.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Сумма:").grid(row=3, column=0, padx=5, pady=5)
        self.total = ttk.Entry(self, width=30)
        self.total.grid(row=3, column=1, padx=5, pady=5)
        self.total.insert(0, "100000")

        ttk.Button(self, text="Создать", command=self.save).grid(row=4, column=0, columnspan=2, pady=20)

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

if __name__ == '__main__':
    root = tk.Tk()
    app = PCAssemblyClient(root)
    root.mainloop()
