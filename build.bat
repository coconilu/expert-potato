@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo    Expert Potato 构建脚本
echo ==========================================
echo.

:: 检查是否在正确的目录
if not exist "src\main.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    echo 当前目录: %CD%
    echo 预期文件: src\main.py
    pause
    exit /b 1
)

:: 显示菜单
echo 请选择构建选项:
echo.
echo 1. 构建单文件版本 (推荐，优化大小)
echo 2. 构建文件夹版本 (启动更快)
echo 3. 传统构建方法 (备选方案)
echo 4. 清理构建文件
echo 5. 安装 PyInstaller
echo 6. 退出
echo.
echo 说明:
echo   选项1: 使用优化的spec文件，排除模型缓存，文件更小
echo   选项2: 文件夹版本，启动速度快，但文件数量多
echo   选项3: 传统方法，可能包含模型缓存，文件较大
echo.
set /p choice="请输入选项 (1-6): "

if "%choice%"=="1" goto build_single
if "%choice%"=="2" goto build_folder
if "%choice%"=="3" goto build_legacy
if "%choice%"=="4" goto clean_build
if "%choice%"=="5" goto install_pyinstaller
if "%choice%"=="6" goto end
echo 无效选项，请重新选择
goto menu

:build_single
echo.
echo 🚀 开始单文件构建...
echo.
python build.py build
goto check_result

:build_folder
echo.
echo 🚀 开始文件夹构建...
echo.
python build.py folder
goto check_result

:build_legacy
echo.
echo 🚀 开始传统构建...
echo.
python build.py legacy
goto check_result

:clean_build
echo.
echo 🧹 清理构建文件...
echo.
python build.py clean
echo.
echo ✅ 清理完成！
pause
exit /b 0

:install_pyinstaller
echo.
echo 📦 安装 PyInstaller...
echo.
python build.py install
echo.
echo 安装完成，请重新运行构建
pause
exit /b 0

:check_result
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ 构建成功！
    echo.
    echo 📦 输出位置:
    if exist "dist\Expert Potato.exe" (
        echo    单文件: dist\Expert Potato.exe
    )
    if exist "dist\Expert Potato\Expert Potato.exe" (
        echo    文件夹: dist\Expert Potato\
    )
    echo.
    echo 🎯 你现在可以:
    echo    1. 测试运行生成的程序
    echo    2. 将程序分发给其他用户
    echo    3. 创建安装程序 (可选)
) else (
    echo.
    echo ❌ 构建失败！
    echo.
    echo 💡 可能的解决方案:
    echo    1. 确保已安装 uv: pip install uv
    echo    2. 确保已安装依赖: uv sync
    echo    3. 确保已安装 PyInstaller: python build.py install
    echo    4. 检查错误信息并修复问题
)

echo.
pause

:end
echo 再见！