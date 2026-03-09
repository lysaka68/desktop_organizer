#!/usr/bin/env python3
"""
Desktop Organizer - Автоматично подреждане на файлове на десктопа
"""

import os
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json

class DesktopOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Desktop Organizer 🗂️ - Created by Lyudmil Tonchev")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Стандартен път до десктопа
        self.desktop_path = str(Path.home() / "Desktop")
        
        # Категории файлове
        self.file_categories = {
            'Изображения': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp'],
            'Документи': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
            'Видео': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Аудио': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
            'Архиви': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            'Код': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go', '.rs'],
            'Изпълними': ['.exe', '.msi', '.app', '.deb', '.rpm', '.dmg'],
            'Други': []
        }
        
        self.create_widgets()
        self.load_settings()
        
    def create_widgets(self):
        # Заглавие
        title_frame = tk.Frame(self.root, bg='#2c3e50', pady=15)
        title_frame.pack(fill='x')
        
        title = tk.Label(title_frame, text="📁 Desktop Organizer", 
                        font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title.pack()
        
        subtitle = tk.Label(title_frame, text="Автоматично подреждане на файловете на десктопа", 
                           font=('Arial', 10), bg='#2c3e50', fg='#ecf0f1')
        subtitle.pack()
        
        # Главна рамка
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Избор на път
        path_frame = tk.LabelFrame(main_frame, text="📂 Път до десктопа", 
                                   font=('Arial', 11, 'bold'), padx=10, pady=10)
        path_frame.pack(fill='x', pady=(0, 15))
        
        path_inner = tk.Frame(path_frame)
        path_inner.pack(fill='x')
        
        self.path_var = tk.StringVar(value=self.desktop_path)
        path_entry = tk.Entry(path_inner, textvariable=self.path_var, 
                             font=('Arial', 10), state='readonly')
        path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_inner, text="Избери", command=self.browse_folder,
                              bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                              cursor='hand2', relief='flat', padx=15)
        browse_btn.pack(side='right')
        
        # Опции за организиране
        options_frame = tk.LabelFrame(main_frame, text="⚙️ Опции за организиране", 
                                     font=('Arial', 11, 'bold'), padx=10, pady=10)
        options_frame.pack(fill='x', pady=(0, 15))
        
        self.organize_type = tk.StringVar(value="category")
        
        radio_category = tk.Radiobutton(options_frame, text="По тип файл (Изображения, Документи и др.)",
                                       variable=self.organize_type, value="category",
                                       font=('Arial', 10), cursor='hand2')
        radio_category.pack(anchor='w', pady=5)
        
        radio_date = tk.Radiobutton(options_frame, text="По дата на модификация",
                                   variable=self.organize_type, value="date",
                                   font=('Arial', 10), cursor='hand2')
        radio_date.pack(anchor='w', pady=5)
        
        radio_extension = tk.Radiobutton(options_frame, text="По разширение на файла",
                                        variable=self.organize_type, value="extension",
                                        font=('Arial', 10), cursor='hand2')
        radio_extension.pack(anchor='w', pady=5)
        
        # Допълнителни опции
        extras_frame = tk.LabelFrame(main_frame, text="🔧 Допълнителни настройки", 
                                    font=('Arial', 11, 'bold'), padx=10, pady=10)
        extras_frame.pack(fill='x', pady=(0, 15))
        
        self.ignore_folders = tk.BooleanVar(value=True)
        ignore_check = tk.Checkbutton(extras_frame, text="Игнорирай съществуващи папки",
                                     variable=self.ignore_folders, font=('Arial', 10))
        ignore_check.pack(anchor='w', pady=3)
        
        self.create_backup = tk.BooleanVar(value=False)
        backup_check = tk.Checkbutton(extras_frame, text="Създай резервно копие преди организиране",
                                     variable=self.create_backup, font=('Arial', 10))
        backup_check.pack(anchor='w', pady=3)
        
        # Статус
        self.status_label = tk.Label(main_frame, text="Готов за организиране", 
                                    font=('Arial', 10), fg='#27ae60')
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress.pack(pady=10)
        
        # Бутони
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        organize_btn = tk.Button(button_frame, text="🚀 Организирай сега", 
                                command=self.organize_desktop,
                                bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                cursor='hand2', relief='flat', padx=30, pady=10)
        organize_btn.pack(side='left', padx=5)
        
        preview_btn = tk.Button(button_frame, text="👁️ Преглед", 
                               command=self.preview_changes,
                               bg='#f39c12', fg='white', font=('Arial', 12, 'bold'),
                               cursor='hand2', relief='flat', padx=30, pady=10)
        preview_btn.pack(side='left', padx=5)
        
        # Информация
        info_frame = tk.LabelFrame(main_frame, text="ℹ️ Информация", 
                                  font=('Arial', 10, 'bold'), padx=10, pady=10)
        info_frame.pack(fill='both', expand=True)
        
        info_text = tk.Text(info_frame, height=6, wrap='word', font=('Arial', 9),
                           bg='#f8f9fa', relief='flat')
        info_text.pack(fill='both', expand=True)
        info_text.insert('1.0', 
            "Това приложение организира файловете на десктопа в папки.\n\n"
            "• По тип файл: Групира по категории (изображения, документи и др.)\n"
            "• По дата: Създава папки по година и месец\n"
            "• По разширение: Създава папка за всяко разширение (.jpg, .pdf и др.)\n\n"
            "Съществуващите папки няма да бъдат преместени.")
        info_text.config(state='disabled')
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.desktop_path)
        if folder:
            self.desktop_path = folder
            self.path_var.set(folder)
            
    def get_file_category(self, extension):
        """Определя категорията на файла според разширението"""
        for category, extensions in self.file_categories.items():
            if extension.lower() in extensions:
                return category
        return 'Други'
        
    def preview_changes(self):
        """Показва какви промени ще бъдат направени"""
        if not os.path.exists(self.desktop_path):
            messagebox.showerror("Грешка", "Избраният път не съществува!")
            return
            
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Преглед на промените")
        preview_window.geometry("600x400")
        
        tk.Label(preview_window, text="Файлове, които ще бъдат организирани:", 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        text_frame = tk.Frame(preview_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        text_widget = tk.Text(text_frame, yscrollcommand=scrollbar.set, 
                             font=('Courier', 9))
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)
        
        organize_type = self.organize_type.get()
        changes = {}
        
        for item in os.listdir(self.desktop_path):
            item_path = os.path.join(self.desktop_path, item)
            
            if os.path.isdir(item_path) and self.ignore_folders.get():
                continue
                
            if os.path.isfile(item_path):
                _, ext = os.path.splitext(item)
                
                if organize_type == "category":
                    target_folder = self.get_file_category(ext)
                elif organize_type == "date":
                    mod_time = os.path.getmtime(item_path)
                    date = datetime.fromtimestamp(mod_time)
                    target_folder = f"{date.year}/{date.strftime('%B')}"
                else:  # extension
                    target_folder = ext[1:].upper() if ext else "БЕЗ_РАЗШИРЕНИЕ"
                    
                if target_folder not in changes:
                    changes[target_folder] = []
                changes[target_folder].append(item)
        
        if not changes:
            text_widget.insert('1.0', "Няма файлове за организиране.")
        else:
            for folder, files in sorted(changes.items()):
                text_widget.insert('end', f"\n📁 {folder}/ ({len(files)} файла)\n")
                for file in sorted(files):
                    text_widget.insert('end', f"   → {file}\n")
                    
        text_widget.config(state='disabled')
        
        tk.Button(preview_window, text="Затвори", command=preview_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                 cursor='hand2', relief='flat', padx=20, pady=5).pack(pady=10)
        
    def organize_desktop(self):
        """Главна функция за организиране на десктопа"""
        if not os.path.exists(self.desktop_path):
            messagebox.showerror("Грешка", "Избраният път не съществува!")
            return
            
        # Потвърждение
        result = messagebox.askyesno("Потвърждение", 
                                    "Сигурни ли сте, че искате да организирате файловете?\n\n"
                                    "Файловете ще бъдат преместени в нови папки.")
        if not result:
            return
            
        # Резервно копие
        if self.create_backup.get():
            self.create_backup_folder()
            
        self.status_label.config(text="Организиране...", fg='#f39c12')
        self.root.update()
        
        organize_type = self.organize_type.get()
        files_moved = 0
        errors = []
        
        items = [item for item in os.listdir(self.desktop_path)]
        total_items = len(items)
        self.progress['maximum'] = total_items
        
        for index, item in enumerate(items):
            item_path = os.path.join(self.desktop_path, item)
            
            # Пропускане на папки
            if os.path.isdir(item_path) and self.ignore_folders.get():
                self.progress['value'] = index + 1
                self.root.update()
                continue
                
            if os.path.isfile(item_path):
                try:
                    _, ext = os.path.splitext(item)
                    
                    # Определяне на целева папка
                    if organize_type == "category":
                        target_folder = self.get_file_category(ext)
                    elif organize_type == "date":
                        mod_time = os.path.getmtime(item_path)
                        date = datetime.fromtimestamp(mod_time)
                        target_folder = os.path.join(str(date.year), date.strftime('%B'))
                    else:  # extension
                        target_folder = ext[1:].upper() if ext else "БЕЗ_РАЗШИРЕНИЕ"
                    
                    # Създаване на целева папка
                    target_path = os.path.join(self.desktop_path, target_folder)
                    os.makedirs(target_path, exist_ok=True)
                    
                    # Преместване на файла
                    dest_path = os.path.join(target_path, item)
                    
                    # Ако файлът съществува, добави номер
                    counter = 1
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(item)
                        dest_path = os.path.join(target_path, f"{name}_{counter}{ext}")
                        counter += 1
                    
                    shutil.move(item_path, dest_path)
                    files_moved += 1
                    
                except Exception as e:
                    errors.append(f"{item}: {str(e)}")
            
            self.progress['value'] = index + 1
            self.root.update()
        
        # Край
        self.progress['value'] = 0
        self.status_label.config(text="Готово!", fg='#27ae60')
        
        if errors:
            error_msg = f"Организирани {files_moved} файла.\n\nГрешки:\n" + "\n".join(errors[:5])
            messagebox.showwarning("Завършено с грешки", error_msg)
        else:
            messagebox.showinfo("Успех!", f"Успешно организирани {files_moved} файла! 🎉")
            
    def create_backup_folder(self):
        """Създава резервно копие на десктопа"""
        backup_name = f"Desktop_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(Path.home(), backup_name)
        
        try:
            shutil.copytree(self.desktop_path, backup_path)
            messagebox.showinfo("Резервно копие", f"Резервно копие създадено в:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Грешка", f"Не може да се създаде резервно копие:\n{str(e)}")
            
    def load_settings(self):
        """Зарежда запазени настройки"""
        settings_file = os.path.join(Path.home(), '.desktop_organizer_settings.json')
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.organize_type.set(settings.get('organize_type', 'category'))
                    self.ignore_folders.set(settings.get('ignore_folders', True))
            except:
                pass
                
    def save_settings(self):
        """Запазва настройките"""
        settings_file = os.path.join(Path.home(), '.desktop_organizer_settings.json')
        settings = {
            'organize_type': self.organize_type.get(),
            'ignore_folders': self.ignore_folders.get()
        }
        try:
            with open(settings_file, 'w') as f:
                json.dump(settings, f)
        except:
            pass

def main():
    root = tk.Tk()
    app = DesktopOrganizer(root)
    
    # Запазване на настройки при затваряне
    def on_closing():
        app.save_settings()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
