#!/bin/bash

set -e

# 标题和作者信息
echo ""
echo "========================================"
echo "   Fuck Jar - Java Decompiler Tool"
echo "========================================"
echo "  Author: dig_onion (刨葱)"
echo "  Version: 1.0.0"
echo "========================================"
echo ""

# 检查Python环境
echo "[1/4] Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "[SUCCESS] Python installed: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "[SUCCESS] Python installed: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    echo ""
    echo "[ERROR] Python not found!"
    echo "Please install Python 3.6 or higher"
    echo "Download: https://www.python.org/downloads/"
    echo ""
    echo "After installation, make sure Python is in PATH"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""

# 检查Java环境
echo "[2/4] Checking Java environment..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java --version 2>&1 | head -1)
    echo "[SUCCESS] Java installed: $JAVA_VERSION"
else
    echo "[WARNING] Java not found!"
    echo "Java is required for CFR decompiler"
    echo "Download: https://www.oracle.com/java/technologies/downloads/"
    echo ""
    read -p "Continue anyway? (y/n): " CONTINUE
    if [[ ! $CONTINUE =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# 检查Python依赖
echo "[3/4] Checking Python dependencies..."

# 升级pip
echo "[INFO] Upgrading pip..."
$PYTHON_CMD -m pip install --upgrade pip > /dev/null 2>&1 || echo "[WARNING] Failed to upgrade pip, continuing..."

# 检查tkinterdnd2
echo "[INFO] Checking tkinterdnd2 dependency..."
if $PYTHON_CMD -m pip show tkinterdnd2 > /dev/null 2>&1; then
    echo "[SUCCESS] Dependencies installed"
else
    echo "[INFO] Dependencies not installed, installing..."
    echo ""
    echo "[INFO] Installing from requirements.txt..."
    if $PYTHON_CMD -m pip install -r requirements.txt; then
        echo "[SUCCESS] Dependencies installed"
    else
        echo ""
        echo "[ERROR] Dependency installation failed!"
        echo "Please check network or install manually:"
        echo "  $PYTHON_CMD -m pip install -r requirements.txt"
        echo ""
        echo "Alternative: Try offline installation:"
        echo "  1. Download dependencies on another machine"
        echo "  2. Copy packages folder to this machine"
        echo "  3. Run: $PYTHON_CMD -m pip install --no-index --find-links=./packages -r requirements.txt"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo ""

# 检查CFR decompiler
echo "[4/4] Checking CFR decompiler..."
if [ -f "cfr-0.152.jar" ]; then
    echo "[SUCCESS] CFR decompiler found"
else
    echo "[INFO] CFR decompiler not found"
    echo "[INFO] Attempting to download automatically..."
    echo ""
    
    # 尝试下载CFR
    if command -v curl &> /dev/null; then
        echo "[INFO] Using curl to download CFR..."
        if curl -o cfr-0.152.jar https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar; then
            echo "[SUCCESS] CFR decompiler downloaded successfully"
        else
            echo "[WARNING] Failed to download CFR with curl!"
            echo "Will be downloaded automatically on first run"
        fi
    elif command -v wget &> /dev/null; then
        echo "[INFO] Using wget to download CFR..."
        if wget -O cfr-0.152.jar https://github.com/leibnitz27/cfr/releases/download/0.152/cfr-0.152.jar; then
            echo "[SUCCESS] CFR decompiler downloaded successfully"
        else
            echo "[WARNING] Failed to download CFR with wget!"
            echo "Will be downloaded automatically on first run"
        fi
    else
        echo "[WARNING] Neither curl nor wget found!"
        echo "CFR will be downloaded automatically by the program on first run"
        echo "Download: https://github.com/leibnitz27/cfr/releases"
    fi
fi

echo ""

# 启动程序
echo "========================================"
echo "   All checks passed, starting program..."
echo "========================================"
echo ""
echo "Tips:"
echo "   - Drag files/folders to the gray area"
echo "   - Or click 'File' menu to select files"
echo "   - Click 'Output Format' to choose output format"
echo "   - Click 'Fuck Jar' to start decompilation"
echo "   - Adjust thread count in 'Settings'"
echo ""
echo "========================================"
echo ""

# 运行程序
$PYTHON_CMD fuck_jar_gui.py

# 检查程序执行结果
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "[ERROR] Program execution failed!"
    echo "========================================"
    echo ""
    echo "Please check the following:"
    echo ""
    echo "1. Python environment"
    echo "   Run: $PYTHON_CMD --version"
    echo ""
    echo "2. Dependencies installed"
    echo "   Run: $PYTHON_CMD -m pip list | grep tkinterdnd2"
    echo ""
    echo "3. Java environment"
    echo "   Run: java --version"
    echo ""
    echo "4. CFR decompiler exists"
    echo "   Check: cfr-0.152.jar"
    echo ""
    echo "5. View detailed error"
    echo "   Run: $PYTHON_CMD fuck_jar_gui.py"
    echo ""
    echo "For help, see README.md"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

echo ""
echo "[SUCCESS] Program exited normally"
read -p "Press Enter to exit..."
