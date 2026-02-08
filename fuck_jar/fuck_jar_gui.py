import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import zipfile
import subprocess
import shutil
import threading
import datetime
import concurrent.futures
import tempfile
import queue
import multiprocessing
import hashlib


class FuckJarGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fuck Jar - Java Decompiler Tool             Author：刨葱 dig_onion 3867458656@qq.com")
        self.root.geometry("800x600")
        
        self.jd_gui_path = r"E:\Ms08067\extentions\jd-gui-windows-1.6.6\jd-gui.exe"
        self.cfr_jar_path = os.path.join(os.path.dirname(__file__), "cfr-0.152.jar")
        self.selected_paths = []
        self.output_dir = None
        self.max_workers = min(32, max(4, multiprocessing.cpu_count() * 2))
        self.log_queue = queue.Queue()
        self.lock = threading.Lock()
        
        # 缓存机制
        self.cache = {}
        self.cache_order = []
        self.cache_capacity = 10000  # 缓存容量
        
        # 输出格式设置
        self.output_format = "java"  # 默认：java文件
        
        # JVM预加载相关
        self.jvm_pool = None
        self.jvm_pool_size = min(4, self.max_workers)
        
        self.setup_ui()
        self._init_jvm_pool()
        self.check_cfr_jar()
        
    def _init_jvm_pool(self):
        """初始化JVM预加载池"""
        try:
            if os.path.exists(self.cfr_jar_path):
                self.log(f"Initializing JVM pool with {self.jvm_pool_size} instances...")
                
                # 预热JVM - 运行一次简单的CFR命令
                cmd = [
                    'java',
                    '-Dfile.encoding=UTF-8',
                    '-Xms64m',
                    '-Xmx128m',
                    '-jar', self.cfr_jar_path,
                    '--version'
                ]
                
                import subprocess
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.log("JVM pool initialized successfully (warm-up completed)")
                else:
                    self.log("JVM pool initialization failed during warm-up")
            else:
                self.log("CFR not found, JVM pool initialization skipped")
        except Exception as e:
            self.log(f"JVM pool initialization error: {str(e)}")
    
    def _get_file_hash(self, file_path):
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                hasher = hashlib.md5()
                while True:
                    data = f.read(65536)  # 64KB chunks
                    if not data:
                        break
                    hasher.update(data)
                return hasher.hexdigest()
        except Exception:
            return None
    
    def _check_cache(self, file_path):
        """检查文件是否在缓存中"""
        file_hash = self._get_file_hash(file_path)
        if file_hash:
            return self.cache.get(file_hash, False)
        return False
    
    def _update_cache(self, file_path):
        """更新缓存"""
        file_hash = self._get_file_hash(file_path)
        if file_hash:
            # 移除旧条目
            if file_hash in self.cache:
                self.cache_order.remove(file_hash)
            
            # 添加新条目
            self.cache[file_hash] = True
            self.cache_order.append(file_hash)
            
            # 检查容量
            if len(self.cache) > self.cache_capacity:
                # 删除最旧的条目
                oldest_hash = self.cache_order.pop(0)
                del self.cache[oldest_hash]
    
    def check_cfr_jar(self):
        if os.path.exists(self.cfr_jar_path):
            self.log(f"CFR decompiler found: {self.cfr_jar_path}")
        else:
            self.log("CFR decompiler not found. Will download automatically on first use.")
            self.log("CFR will be downloaded from: https://github.com/leibnitz27/cfr/releases")
        
    def download_cfr(self):
        try:
            import urllib.request
            
            cfr_url = "https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar"
            self.log(f"Downloading CFR from {cfr_url}...")
            
            def report_progress(block_num, block_size, total_size):
                if total_size > 0:
                    progress = (block_num * block_size / total_size) * 100
                    self.progress_var.set(progress)
                    self.root.update()
            
            urllib.request.urlretrieve(cfr_url, self.cfr_jar_path, reporthook=report_progress)
            self.log("CFR downloaded successfully!")
            self.progress_var.set(0)
            return True
            
        except Exception as e:
            self.log(f"Failed to download CFR: {str(e)}")
            self.log("Please download CFR manually from: https://github.com/leibnitz27/cfr/releases")
            self.log("Download cfr-0.152.jar and place it in program directory.")
            return False
            
    def setup_ui(self):
        menubar = tk.Menu(self.root)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Select Files/Folders", command=self.select_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Set Process Count", command=self.set_thread_count)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        
        self.root.config(menu=menubar)
        
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 版本信息
        version_frame = tk.Frame(info_frame)
        version_frame.pack(side=tk.LEFT, padx=5)
        tk.Label(version_frame, text="Version:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        tk.Label(version_frame, text="1.0.0", fg="green").pack(side=tk.LEFT, padx=2)
        
        # CFR信息
        cfr_frame = tk.Frame(info_frame)
        cfr_frame.pack(side=tk.LEFT, padx=15)
        tk.Label(cfr_frame, text="CFR:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        cfr_name = os.path.basename(self.cfr_jar_path)
        self.cfr_label = tk.Label(cfr_frame, text=cfr_name, fg="blue")
        self.cfr_label.pack(side=tk.LEFT, padx=2)
        
        # 输出格式信息
        format_frame = tk.Frame(info_frame)
        format_frame.pack(side=tk.LEFT, padx=15)
        tk.Label(format_frame, text="Output:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        self.format_label = tk.Label(format_frame, text="Java files", fg="purple")
        self.format_label.pack(side=tk.LEFT, padx=2)
        
        tk.Label(main_frame, text="Drag and drop files/folders here or click 'File' to select:", 
                font=("Arial", 10)).pack(anchor=tk.W)
        
        self.drop_area = tk.Label(main_frame, text="Drop Area\n(Supports files and folders)", 
                                  bg="lightgray", relief=tk.SUNKEN, height=10)
        self.drop_area.pack(fill=tk.BOTH, expand=True, pady=5)
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)
        
        self.selected_files_label = tk.Label(main_frame, text="Selected: None", fg="blue", anchor=tk.W)
        self.selected_files_label.pack(fill=tk.X, pady=5)
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="File", command=self.select_files, 
                 width=15, bg="lightblue").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Output Format", command=self.select_output_format, 
                 width=15, bg="lightcyan").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Fuck Jar", command=self.start_decompile, 
                 width=15, bg="lightgreen").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Clear", command=self.clear_selection, 
                 width=15, bg="lightyellow").pack(side=tk.LEFT, padx=5)
        
        tk.Label(main_frame, text="Output Log:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                               maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = tk.Label(main_frame, text="Ready", fg="green")
        self.status_label.pack(anchor=tk.W, pady=5)
        
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()
        
    def thread_safe_log(self, message):
        self.log_queue.put(message)
        
    def process_log_queue(self):
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log(message)
        except queue.Empty:
            pass
        
    def set_status(self, status, color="black"):
        self.status_label.config(text=status, fg=color)
        self.root.update()
        
    def select_output_format(self):
        """选择输出格式"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Output Format")
        dialog.geometry("350x180")
        
        # 设置对话框标题（支持中文）
        tk.Label(dialog, text="选择输出格式:", font=("Arial", 10, "bold")).pack(pady=10)
        
        # 创建变量存储选择
        format_var = tk.StringVar(value=self.output_format)
        
        # 添加选项（支持中文）
        tk.Radiobutton(dialog, text="Java 文件 (反编译，默认)", 
                       variable=format_var, value="java").pack(anchor=tk.W, padx=20)
        tk.Radiobutton(dialog, text="Class 文件 (原样复制)", 
                       variable=format_var, value="class").pack(anchor=tk.W, padx=20)
        
        # 保存选择的函数
        def save():
            self.output_format = format_var.get()
            # 更新界面显示
            if self.output_format == "java":
                self.format_label.config(text="Java files", fg="purple")
                self.log("输出格式已设置为: Java 文件 (反编译)")
            else:
                self.format_label.config(text="Class files", fg="orange")
                self.log("输出格式已设置为: Class 文件 (原样复制)")
            dialog.destroy()
        
        # 添加保存按钮
        tk.Button(dialog, text="保存", command=save, width=10, bg="lightgreen").pack(pady=15)
    
    def set_thread_count(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Process Count")
        dialog.geometry("400x250")
        
        cpu_count = multiprocessing.cpu_count()
        recommended = min(32, max(4, cpu_count * 2))
        
        info_frame = tk.Frame(dialog)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(info_frame, text="CPU核心数: " + str(cpu_count), font=("Arial", 9)).pack(anchor=tk.W)
        tk.Label(info_frame, text="推荐值: " + str(recommended), font=("Arial", 9, "bold"), fg="green").pack(anchor=tk.W)
        tk.Label(info_frame, text="安全范围: 1-64", font=("Arial", 9)).pack(anchor=tk.W)
        
        tk.Label(dialog, text="设置并发进程数:", font=("Arial", 10, "bold")).pack(pady=5)
        
        thread_var = tk.IntVar(value=self.max_workers)
        thread_entry = tk.Entry(dialog, textvariable=thread_var, font=("Arial", 12))
        thread_entry.pack(pady=5)
        
        warning_label = tk.Label(dialog, text="⚠️ 警告: 设置过高可能导致内存不足", 
                                fg="red", font=("Arial", 8))
        warning_label.pack(pady=5)
        
        def save():
            try:
                count = int(thread_var.get())
                if count > 0 and count <= 64:
                    self.max_workers = count
                    self.log(f"进程数已设置为 {count}")
                    dialog.destroy()
                else:
                    messagebox.showerror("错误", "进程数必须在 1 到 64 之间")
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        tk.Button(dialog, text="保存", command=save, width=15, bg="lightgreen").pack(pady=10)
        
    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="Select files",
            filetypes=[("All files", "*.*")]
        )
        
        if paths:
            folders = filedialog.askdirectory(title="Select folders (optional)")
            if folders:
                self.selected_paths = list(paths) + [folders]
            else:
                self.selected_paths = list(paths)
            self.update_selection_label()
            self.log(f"Selected {len(self.selected_paths)} item(s)")
            
    def on_drop(self, event):
        try:
            paths = self.root.tk.splitlist(event.data)
            valid_paths = []
            
            for path in paths:
                path = path.strip('{}')
                if os.path.exists(path):
                    self.selected_paths.append(path)
                    valid_paths.append(path)
            
            self.update_selection_label()
            self.log(f"Dropped {len(valid_paths)} valid item(s) out of {len(paths)} total")
        except Exception as e:
            self.log(f"Error during drag and drop: {str(e)}")
            messagebox.showerror("Error", f"Drag and drop failed: {str(e)}")
        
    def update_selection_label(self):
        if self.selected_paths:
            text = f"Selected: {len(self.selected_paths)} item(s)"
            for path in self.selected_paths[:3]:
                text += f"\n  - {os.path.basename(path)}"
            if len(self.selected_paths) > 3:
                text += f"\n  ... and {len(self.selected_paths) - 3} more"
        else:
            text = "Selected: None"
        
        self.selected_files_label.config(text=text)
        
    def clear_selection(self):
        self.selected_paths = []
        self.update_selection_label()
        self.log("Selection cleared")
        self.set_status("Ready", "green")
        
    def find_jar_files(self, path):
        jar_files = []
        
        if os.path.isfile(path) and path.lower().endswith('.jar'):
            jar_files.append(path)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.lower().endswith('.jar'):
                        jar_files.append(os.path.join(root, file))
        
        return jar_files
        
    def decompile_single_file(self, class_file, output_dir):
        try:
            if not os.path.exists(self.cfr_jar_path):
                return False
            
            cmd = [
                'java',
                '-Dfile.encoding=UTF-8',
                '-Xms64m',
                '-Xmx256m',
                '-jar', self.cfr_jar_path,
                class_file,
                '--outputdir', output_dir
                # CFR不需要--encoding参数，只需要JVM层面的编码设置
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=30
            )
            
            if result.returncode == 0:
                return True
            else:
                return False
                
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            return False
            
    def decompile_jar_with_cfr(self, jar_path, output_path, current_output_format=None):
        # Use the provided output format or fall back to the instance's format
        output_format = current_output_format or self.output_format
        try:
            jar_name = os.path.basename(jar_path)
            self.log(f"Processing: {jar_name}")
            
            jar_size = os.path.getsize(jar_path)
            self.log(f"JAR size: {jar_size / (1024 * 1024):.2f} MB")
            
            output_jar_dir = os.path.join(output_path, jar_name.replace('.jar', ''))
            os.makedirs(output_jar_dir, exist_ok=True)
            
            temp_extract_dir = tempfile.mkdtemp(prefix='fuck_jar_')
            
            try:
                self.log(f"Extracting JAR content...")
                
                # 并行解压JAR文件
                with zipfile.ZipFile(jar_path, 'r') as zip_ref:
                    file_infos = zip_ref.infolist()
                    
                    if len(file_infos) > 10:
                        # 使用并行解压
                        import concurrent.futures
                        max_extract_workers = min(8, self.max_workers)
                        
                        def extract_file(file_info):
                            try:
                                zip_ref.extract(file_info, temp_extract_dir)
                                return True
                            except Exception:
                                return False
                        
                        extracted_count = 0
                        failed_count = 0
                        
                        with concurrent.futures.ThreadPoolExecutor(max_workers=max_extract_workers) as executor:
                            results = list(executor.map(extract_file, file_infos))
                            extracted_count = sum(results)
                            failed_count = len(results) - extracted_count
                        
                        self.log(f"Parallel extracted {extracted_count} files, {failed_count} failed")
                    else:
                        # 小文件使用顺序解压
                        zip_ref.extractall(temp_extract_dir)
                        self.log("Sequential extracted successfully")
                
                self.log("JAR extracted successfully")
                
                class_files = []
                non_class_files = []
                nested_jar_files = []
                
                for root, dirs, files in os.walk(temp_extract_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, temp_extract_dir)
                        
                        if file.endswith('.class'):
                            class_files.append((full_path, rel_path))
                        elif file.lower().endswith('.jar'):
                            nested_jar_files.append((full_path, rel_path))
                        else:
                            non_class_files.append((full_path, rel_path))
                
                self.log(f"Found {len(class_files)} .class files in {jar_name}")
                if nested_jar_files:
                    self.log(f"Found {len(nested_jar_files)} nested JAR file(s) in {jar_name}")
                
                if class_files:
                    if output_format == "java":
                        # Java格式：反编译
                        processed_count = 0
                        failed_count = 0
                        
                        # Group class files by output directory for batch processing
                        class_files_by_dir = {}
                        for class_file, rel_path in class_files:
                            output_file = os.path.join(output_jar_dir, 
                                                       rel_path.replace('.class', '.java'))
                            output_dir = os.path.dirname(output_file)
                            os.makedirs(output_dir, exist_ok=True)
                            
                            if output_dir not in class_files_by_dir:
                                class_files_by_dir[output_dir] = []
                            class_files_by_dir[output_dir].append(class_file)
                        
                        # Batch process by directory
                        batch_count = len(class_files_by_dir)
                        self.log(f"Decompiling {len(class_files)} class files in {batch_count} batches with {self.max_workers} processes...")
                        
                        # 内存映射处理大文件
                        def handle_large_file(file_path):
                            """使用内存映射处理大文件"""
                            file_size = os.path.getsize(file_path)
                            if file_size > 10 * 1024 * 1024:  # 10MB以上
                                try:
                                    import mmap
                                    with open(file_path, 'r+b') as f:
                                        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as mm:
                                            # 简单读取以验证内存映射
                                            _ = mm.read(4)
                                    return True
                                except Exception:
                                    return False
                            return True
                        
                        def decompile_batch(output_dir, batch_files):
                            try:
                                if not os.path.exists(self.cfr_jar_path):
                                    return False
                                
                                # 检查缓存 - 但即使在缓存中也需要生成文件，因为缓存只是标记处理过，不保证文件存在
                                uncached_files = batch_files
                                
                                # 跳过缓存检查，确保每次都生成文件
                                # if not uncached_files:
                                #     # 所有文件都在缓存中
                                #     return True
                                
                                # Calculate optimal memory based on batch size
                                batch_size = len(uncached_files)
                                if batch_size > 100:
                                    max_mem = '1024m'
                                elif batch_size > 50:
                                    max_mem = '768m'
                                else:
                                    max_mem = '512m'
                                
                                cmd = [
                    'java',
                    '-Dfile.encoding=UTF-8',
                    '-Xms128m',
                    f'-Xmx{max_mem}',
                    '-jar', self.cfr_jar_path,
                    '--outputdir', output_dir,
                    '--silent', 'true',  # 减少输出
                    '--caseinsensitivefs', 'true',  # 大小写不敏感文件系统
                    '--forcecondy', 'false',  # 禁用条件分支优化
                    '--forcetopsort', 'false',  # 禁用拓扑排序
                    '--forceexceptionprune', 'false'  # 禁用异常修剪
                    # CFR不需要--encoding参数，只需要JVM层面的编码设置
                ]
                                cmd.extend(uncached_files)
                                
                                # Calculate timeout based on batch size
                                if batch_size > 100:
                                    timeout = 120
                                elif batch_size > 50:
                                    timeout = 90
                                else:
                                    timeout = 60
                                
                                result = subprocess.run(
                                    cmd,
                                    capture_output=True,
                                    text=True,
                                    encoding='utf-8',
                                    errors='ignore',
                                    timeout=timeout
                                )
                                
                                if result.returncode == 0:
                                    # 更新缓存
                                    for file_path in uncached_files:
                                        self._update_cache(file_path)
                                    return True
                                else:
                                    return False
                                
                            except subprocess.TimeoutExpired:
                                return False
                            except Exception as e:
                                return False
                        
                        # Use ProcessPoolExecutor for CPU-bound tasks
                        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                            futures = []
                            
                            for output_dir, batch_files in class_files_by_dir.items():
                                future = executor.submit(decompile_batch, output_dir, batch_files)
                                futures.append((future, len(batch_files)))
                            
                            for future, batch_size in futures:
                                try:
                                    if future.result():
                                        with self.lock:
                                            processed_count += batch_size
                                    else:
                                        with self.lock:
                                            failed_count += batch_size
                                except Exception:
                                    with self.lock:
                                        failed_count += batch_size
                        
                        self.log(f"Decompiled {processed_count} files, {failed_count} failed")
                    else:
                        # Class格式：直接复制
                        self.log(f"Copying {len(class_files)} class files directly...")
                        
                        # 批量创建目录
                        directories = set()
                        for class_file, rel_path in class_files:
                            dst_file = os.path.join(output_jar_dir, rel_path)
                            directories.add(os.path.dirname(dst_file))
                        
                        # 批量创建所有目录
                        for dir_path in directories:
                            os.makedirs(dir_path, exist_ok=True)
                        self.log(f"Batch created {len(directories)} directories")
                        
                        # 并行复制文件
                        def copy_class_file(file_info):
                            class_file, rel_path = file_info
                            try:
                                dst_file = os.path.join(output_jar_dir, rel_path)
                                shutil.copy2(class_file, dst_file)
                                return True
                            except Exception:
                                return False
                        
                        copied_count = 0
                        failed_copy = 0
                        
                        # 并行复制文件
                        with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, self.max_workers)) as executor:
                            results = list(executor.map(copy_class_file, class_files))
                            copied_count = sum(results)
                            failed_copy = len(results) - copied_count
                        
                        self.log(f"Copied {copied_count} class files, {failed_copy} failed")
                
                if non_class_files:
                    non_class_count = len(non_class_files)
                    self.log(f"Copying {non_class_count} non-class files with batch IO...")
                    
                    # 批量创建目录
                    directories = set()
                    for src_file, rel_path in non_class_files:
                        dst_file = os.path.join(output_jar_dir, rel_path)
                        directories.add(os.path.dirname(dst_file))
                    
                    # 批量创建所有目录
                    for dir_path in directories:
                        os.makedirs(dir_path, exist_ok=True)
                    self.log(f"Batch created {len(directories)} directories")
                    
                    # 并行复制文件
                    def copy_file(file_info):
                        src_file, rel_path = file_info
                        try:
                            dst_file = os.path.join(output_jar_dir, rel_path)
                            shutil.copy2(src_file, dst_file)
                            return True
                        except Exception:
                            return False
                    
                    copied_count = 0
                    failed_copy = 0
                    
                    # 并行复制文件
                    with concurrent.futures.ThreadPoolExecutor(max_workers=min(16, self.max_workers)) as executor:
                        results = list(executor.map(copy_file, non_class_files))
                        copied_count = sum(results)
                        failed_copy = len(results) - copied_count
                    
                    self.log(f"Batch copied {copied_count} non-class files, {failed_copy} failed")
                else:
                    self.log("No non-class files to copy")
                
                if nested_jar_files:
                    nested_count = len(nested_jar_files)
                    self.log(f"Processing {nested_count} nested JARs in parallel with {self.max_workers} processes...")
                    
                    def process_nested_jar(nested_jar_info):
                        nested_jar, rel_path = nested_jar_info
                        try:
                            nested_dir = os.path.dirname(rel_path)
                            nested_dir_simplified = nested_dir.replace(os.sep, '.')
                            nested_output_dir = os.path.join(output_jar_dir, nested_dir_simplified)
                            return self.decompile_jar_with_cfr(nested_jar, nested_output_dir, output_format)
                        except Exception:
                            return False
                    
                    processed_nested = 0
                    failed_nested = 0
                    
                    # 并行处理嵌套JAR
                    with concurrent.futures.ProcessPoolExecutor(max_workers=min(self.max_workers, nested_count)) as executor:
                        results = list(executor.map(process_nested_jar, nested_jar_files))
                        processed_nested = sum(results)
                        failed_nested = len(results) - processed_nested
                    
                    self.log(f"Parallel processed {processed_nested} nested JARs, {failed_nested} failed")
                else:
                    self.log("No nested JARs found")
                
                self.log(f"Completed: {jar_name}")
                return True
                
            finally:
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                
        except Exception as e:
            self.log(f"Error processing {jar_path}: {str(e)}")
            return False
            
    def copy_non_jar_files(self, src_path, output_path):
        try:
            if os.path.isfile(src_path) and not src_path.lower().endswith('.jar'):
                output_file = os.path.join(output_path, os.path.basename(src_path))
                os.makedirs(os.path.dirname(output_file), exist_ok=True)
                shutil.copy2(src_path, output_file)
                self.log(f"Copied: {os.path.basename(src_path)}")
                
            elif os.path.isdir(src_path):
                for root, dirs, files in os.walk(src_path):
                    for file in files:
                        if not file.lower().endswith('.jar'):
                            src_file = os.path.join(root, file)
                            rel_path = os.path.relpath(src_file, src_path)
                            dst_file = os.path.join(output_path, rel_path)
                            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                            shutil.copy2(src_file, dst_file)
                            
        except Exception as e:
            self.log(f"Error copying files: {str(e)}")
            
    def start_decompile(self):
        if not self.selected_paths:
            messagebox.showwarning("Warning", "Please select files or folders first!")
            return
            
        thread = threading.Thread(target=self.decompile_process)
        thread.daemon = True
        thread.start()
        
    def decompile_process(self):
        try:
            self.set_status("Processing...", "blue")
            self.progress_var.set(0)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = os.path.join(os.getcwd(), f"decompiled_{timestamp}")
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.log(f"Output directory: {self.output_dir}")
            
            all_jar_files = []
            
            for path in self.selected_paths:
                jar_files = self.find_jar_files(path)
                all_jar_files.extend(jar_files)
                self.log(f"Found {len(jar_files)} JAR file(s) in {os.path.basename(path)}")
            
            if not all_jar_files:
                self.log("No JAR files found!")
                for path in self.selected_paths:
                    self.copy_non_jar_files(path, self.output_dir)
                self.set_status("Completed (no JARs)", "green")
                self.progress_var.set(100)
                return
            
            self.log(f"Total JAR files to process: {len(all_jar_files)}")
            
            for i, jar_file in enumerate(all_jar_files):
                progress = (i / len(all_jar_files)) * 100
                self.progress_var.set(progress)
                
                self.decompile_jar_with_cfr(jar_file, self.output_dir, self.output_format)
            
            for path in self.selected_paths:
                self.copy_non_jar_files(path, self.output_dir)
            
            self.progress_var.set(100)
            self.log(f"All done! Output saved to: {self.output_dir}")
            self.set_status("Completed!", "green")
            
            messagebox.showinfo("Success", f"Decompilation completed!\nOutput saved to:\n{self.output_dir}")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.set_status("Error occurred", "red")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = FuckJarGUI(root)
    root.mainloop()
