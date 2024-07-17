import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
import os
import sys
import winshell
from win32com.client import Dispatch
import shutil

def get_app_dir():
    return os.path.join(os.environ['LOCALAPPDATA'], 'TODO List by CHUKEPC')

def create_shortcut():
    app_dir = get_app_dir()
    desktop = winshell.desktop()
    path = os.path.join(desktop, "TODO List.lnk")
    target = os.path.join(app_dir, "TODO_App.exe")
    wDir = app_dir
    icon = target

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()

def setup_app():
    app_dir = get_app_dir()
    os.makedirs(app_dir, exist_ok=True)

    if getattr(sys, 'frozen', False):
        # Если это exe файл
        exe_path = sys.executable
        exe_name = os.path.basename(exe_path)
        new_exe_path = os.path.join(app_dir, exe_name)
        
        # Копируем exe файл в новую директорию, если его там еще нет
        if not os.path.exists(new_exe_path):
            shutil.copy2(exe_path, new_exe_path)
        
        # Создаем ярлык на рабочем столе
        create_shortcut()
        
        # Если текущий путь не совпадает с целевым, перезапускаем приложение
        if exe_path.lower() != new_exe_path.lower():
            os.startfile(new_exe_path)
            sys.exit()

    return app_dir

class ModernTreeview(ttk.Treeview):
    def __init__(self, master, **kw):
        super().__init__(master, style="Modern.Treeview", **kw)

class TodoApp:
    def __init__(self, master):
        self.master = master
        self.master.title("TODO List by CHUKEPC")
        self.master.geometry("1500x600")
        self.master.configure(bg='#f0f0f0')

        # Цветовая схема
        self.colors = {
            'bg': '#f0f0f0',
            'fg': '#333333',
            'accent': '#4a90e2',
            'button': '#5cb85c',
            'button_active': '#4cae4c'
        }

        # Путь к базе данных
        self.app_dir = setup_app()
        self.db_path = os.path.join(self.app_dir, 'todo.db')

        # Подключение к базе данных
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

        # Переменные для сортировки
        self.sort_column = "priority"
        self.sort_order = "DESC"

        # Настройка стилей
        self.setup_styles()

        # Создание и размещение виджетов
        self.create_widgets()
        self.update_task_list()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS tasks
                          (id INTEGER PRIMARY KEY, task TEXT, priority INTEGER, 
                           due_date TEXT, completed INTEGER)''')
        self.conn.commit()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TFrame", background=self.colors['bg'])
        style.configure("TLabel", background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure("TButton", background=self.colors['button'], foreground='white', 
                        padding=(10, 5), font=('Helvetica', 10))
        style.map("TButton", background=[('active', self.colors['button_active'])])

        style.configure("Modern.Treeview",
            background="white",
            foreground=self.colors['fg'],
            rowheight=25,
            fieldbackground="white"
        )
        style.map("Modern.Treeview",
            background=[('selected', self.colors['accent'])],
            foreground=[('selected', 'white')]
        )

        style.configure("Modern.Treeview.Heading",
            background=self.colors['accent'],
            foreground="white",
            relief="flat"
        )
        style.map("Modern.Treeview.Heading",
            background=[('active', self.colors['accent'])]
        )

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Фрейм для ввода задачи
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        self.task_entry = ttk.Entry(input_frame, width=40, font=('Helvetica', 12))
        self.task_entry.grid(row=0, column=0, padx=(0, 10))

        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(input_frame, textvariable=self.priority_var, 
                                      values=["Низкий", "Средний", "Высокий"], width=10, font=('Helvetica', 12))
        priority_combo.grid(row=0, column=1, padx=(0, 10))
        priority_combo.set("Средний")

        self.date_entry = DateEntry(input_frame, width=12, background=self.colors['accent'],
                                    foreground='white', borderwidth=2, font=('Helvetica', 12))
        self.date_entry.grid(row=0, column=2, padx=(0, 10))

        add_button = ttk.Button(input_frame, text="Добавить задачу", command=self.add_task)
        add_button.grid(row=0, column=3)

        # Фрейм для списков задач
        lists_frame = ttk.Frame(main_frame)
        lists_frame.pack(fill=tk.BOTH, expand=True)

        # Список активных задач
        active_frame = ttk.LabelFrame(lists_frame, text="Активные задачи", padding="10")
        active_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.active_tree = ModernTreeview(active_frame, columns=("Task", "Priority", "Due Date"), 
                                          show="headings", height=10)
        self.active_tree.heading("Task", text="Задача", command=lambda: self.sort_tasks("task"))
        self.active_tree.heading("Priority", text="Приоритет", command=lambda: self.sort_tasks("priority"))
        self.active_tree.heading("Due Date", text="Срок", command=lambda: self.sort_tasks("due_date"))
        self.active_tree.column("Task", width=250)
        self.active_tree.column("Priority", width=100)
        self.active_tree.column("Due Date", width=100)
        self.active_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        active_scrollbar = ttk.Scrollbar(active_frame, orient="vertical", command=self.active_tree.yview)
        active_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.active_tree.configure(yscrollcommand=active_scrollbar.set)

        # Список выполненных задач
        completed_frame = ttk.LabelFrame(lists_frame, text="Выполненные задачи", padding="10")
        completed_frame.grid(row=0, column=1, sticky="nsew")

        self.completed_tree = ModernTreeview(completed_frame, columns=("Task", "Priority", "Due Date"), 
                                             show="headings", height=10)
        self.completed_tree.heading("Task", text="Задача", command=lambda: self.sort_tasks("task", completed=True))
        self.completed_tree.heading("Priority", text="Приоритет", command=lambda: self.sort_tasks("priority", completed=True))
        self.completed_tree.heading("Due Date", text="Срок", command=lambda: self.sort_tasks("due_date", completed=True))
        self.completed_tree.column("Task", width=250)
        self.completed_tree.column("Priority", width=100)
        self.completed_tree.column("Due Date", width=100)
        self.completed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        completed_scrollbar = ttk.Scrollbar(completed_frame, orient="vertical", command=self.completed_tree.yview)
        completed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.completed_tree.configure(yscrollcommand=completed_scrollbar.set)

        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)
        lists_frame.grid_rowconfigure(0, weight=1)

        # Привязка событий
        self.active_tree.bind("<ButtonRelease-1>", self.show_task_options)
        self.completed_tree.bind("<ButtonRelease-1>", self.show_task_options)

    def add_task(self):
        task = self.task_entry.get()
        priority = self.priority_var.get()
        due_date = self.date_entry.get()
        if task and priority and due_date:
            priority_map = {"Низкий": 1, "Средний": 2, "Высокий": 3}
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO tasks (task, priority, due_date, completed) VALUES (?, ?, ?, 0)", 
                           (task, priority_map[priority], due_date))
            self.conn.commit()
            self.task_entry.delete(0, tk.END)
            self.priority_var.set("Средний")
            self.date_entry.set_date(datetime.now())
            self.update_task_list()
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля")

    def complete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        self.conn.commit()
        self.update_task_list()

    def uncomplete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE tasks SET completed = 0 WHERE id = ?", (task_id,))
        self.conn.commit()
        self.update_task_list()

    def edit_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cursor.fetchone()

        edit_window = tk.Toplevel(self.master)
        edit_window.title("Редактировать задачу")

        ttk.Label(edit_window, text="Задача:").grid(row=0, column=0, padx=5, pady=5)
        task_entry = ttk.Entry(edit_window, width=40)
        task_entry.grid(row=0, column=1, padx=5, pady=5)
        task_entry.insert(0, task[1])

        ttk.Label(edit_window, text="Приоритет:").grid(row=1, column=0, padx=5, pady=5)
        priority_var = tk.StringVar(value=["Низкий", "Средний", "Высокий"][task[2]-1])
        priority_combo = ttk.Combobox(edit_window, textvariable=priority_var, 
                                      values=["Низкий", "Средний", "Высокий"], width=10)
        priority_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(edit_window, text="Срок:").grid(row=2, column=0, padx=5, pady=5)
        date_entry = DateEntry(edit_window, width=12, background='darkblue',
                               foreground='white', borderwidth=2)
        date_entry.grid(row=2, column=1, padx=5, pady=5)
        date_entry.set_date(task[3])

        def save_changes():
            new_task = task_entry.get()
            new_priority = priority_var.get()
            new_due_date = date_entry.get()
            if new_task and new_priority and new_due_date:
                priority_map = {"Низкий": 1, "Средний": 2, "Высокий": 3}
                cursor = self.conn.cursor()
                cursor.execute("UPDATE tasks SET task = ?, priority = ?, due_date = ? WHERE id = ?", 
                               (new_task, priority_map[new_priority], new_due_date, task_id))
                self.conn.commit()
                self.update_task_list()
                edit_window.destroy()
            else:
                messagebox.showwarning("Предупреждение", "Пожалуйста, заполните все поля")

        save_button = ttk.Button(edit_window, text="Сохранить", command=save_changes)
        save_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

    def delete_task(self, task_id):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту задачу?"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            self.update_task_list()

    def sort_tasks(self, column, completed=False):
        if column == self.sort_column:
            self.sort_order = "ASC" if self.sort_order == "DESC" else "DESC"
        else:
            self.sort_column = column
            self.sort_order = "DESC"
        
        self.update_task_list()

    def update_task_list(self):
        self.active_tree.delete(*self.active_tree.get_children())
        self.completed_tree.delete(*self.completed_tree.get_children())
        
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM tasks ORDER BY {self.sort_column} {self.sort_order}")
        tasks = cursor.fetchall()
        
        priority_map = {1: "Низкий", 2: "Средний", 3: "Высокий"}
        for task in tasks:
            values = (task[1], priority_map[task[2]], task[3], task[0])
            if task[4]:  # Выполненная задача
                self.completed_tree.insert("", "end", values=values)
            else:  # Активная задача
                self.active_tree.insert("", "end", values=values)

        # Обновление заголовков с индикаторами сортировки
        for tree in [self.active_tree, self.completed_tree]:
            for col in ["Task", "Priority", "Due Date"]:
                if col.lower().replace(" ", "_") == self.sort_column:
                    tree.heading(col, text=f"{col} {'↑' if self.sort_order == 'ASC' else '↓'}")
                else:
                    tree.heading(col, text=col)

    def show_task_options(self, event):
        tree = event.widget
        region = tree.identify_region(event.x, event.y)
        if region == "cell":
            item = tree.identify_row(event.y)
            tree.selection_set(item)
            task_id = tree.item(item)['values'][3]
            
            popup = tk.Menu(self.master, tearoff=0)
            if tree == self.active_tree:
                popup.add_command(label="Отметить выполненной", 
                                  command=lambda: self.complete_task(task_id))
            else:
                popup.add_command(label="Отменить выполнение", 
                                  command=lambda: self.uncomplete_task(task_id))
            popup.add_command(label="Редактировать", 
                              command=lambda: self.edit_task(task_id))
            popup.add_command(label="Удалить", 
                              command=lambda: self.delete_task(task_id))
            
            popup.tk_popup(event.x_root, event.y_root)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()