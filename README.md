# Fuck Jar - 批量反编译jar（Java Decompiler Tool）

## 作者信息

- **刨葱 dig_onion**
- **联系作者** 3867458656@qq.com

## 功能说明
在对java项目逆向分析的时候，Intellij IDEA 无法对class文件进行索引，十分恶心，而JD-gui 每次只能处理一个jar包，相当难受，于是，该项目应运而生：

这是一个基于Python的Windows图形化工具，用于批量反编译JAR文件，使用CFR反编译器生成真正的Java源代码。



## 快速开始

## 依赖项

### 推荐：
- **Python 3.11.9**
- **Java运行环境（JRE/JDK）java 23.0.1** - 用于运行CFR反编译器

### Python包：
- tkinter（通常随Python安装）
- tkinterdnd2（用于拖拽功能）

### 方法1：一键启动（推荐）

**双击 `run.bat`** 即可启动程序
- 自动检查Python和Java环境
- 自动安装缺失的Python依赖
- 自动下载CFR反编译器（首次运行时）

### 方法2：手动启动

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**：
   ```bash
   python fuck_jar_gui.py
   ```

## 使用步骤

1. **选择文件/文件夹**：
   - 点击"File"菜单选择文件或文件夹
   - 或者直接将文件/文件夹拖入灰色区域

2. **设置线程数（可选）**：
   - 点击"Settings"菜单
   - 选择"Set Thread Count"
   - 设置并发线程数（根据CPU调整）

3. **选择输出格式**（可选）：
   - 点击"Output Format"按钮
   - 选择"Java 文件 (反编译，默认)"或"Class 文件 (原样复制)"
   - 点击"保存"按钮应用

4. **开始处理**：
   - 点击"Fuck Jar"按钮开始处理
   - 查看日志输出了解处理进度

5. **查看结果**：
   - 处理完成后，结果会保存在工作目录下的 `decompiled_YYYYMMDD_HHMMSS` 文件夹中
   - 每个.class文件会被反编译为.java文件（默认模式）
   - 其他文件（如.properties、.xml等）会保留原样

### 功能优势（图形化操作与极速体验）：
- **文件选择**：可以通过"File"菜单选择文件或文件夹
- **拖拽支持**：支持将文件或文件夹直接拖入工作区
- **递归扫描**：自动递归扫描所选目录下的所有JAR文件
- **批量处理**：一键处理所有找到的JAR文件
- **多线程处理**：支持并行反编译，大幅提高处理速度
- **真正的Java反编译**：使用CFR反编译器生成.java文件，而不是简单的解压
- **目录结构保留**：输出结果保持与源文件相同的目录结构
- **非JAR文件保留**：非JAR文件会原样复制到输出目录
- **输出格式选择**：支持选择Java文件（反编译）或Class文件（原样复制）
- **缓存机制**：缓存已处理的文件，提高重复处理速度
- **并行处理嵌套JAR**：同时处理多个嵌套JAR文件
- **批量IO操作**：批量创建目录和复制文件，提高IO效率
<img width="1186" height="959" alt="image" src="https://github.com/user-attachments/assets/294f84fd-2b7b-45f9-a1e0-e181fad45641" />


## 注意事项

- 确保Java环境已正确安装并配置
- 确保有足够的磁盘空间用于输出
- 大量JAR文件处理可能需要较长时间
- 建议根据CPU核心数调整线程数以获得最佳性能

## 文件结构

```
fuck_jar/
├── fuck_jar_gui.py      # 主程序
├── cfr-0.152.jar        # CFR反编译器（已包含）
├── requirements.txt      # Python依赖
├── run.bat              # 启动脚本（包含所有安装功能）
└── README.md            # 使用说明
```

## 许可证

本工具仅供学习和研究使用。
