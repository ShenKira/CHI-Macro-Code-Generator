@echo off
setlocal EnableExtensions DisableDelayedExpansion

rem Usage: build.bat [version] [both^|standalone^|onefile]
rem Set NUITKA_PYTHON to the python.exe that has Nuitka and PySide6 installed.
if /i "%~1"=="--help" goto :usage
if /i "%~1"=="-h" goto :usage

cd /d "%~dp0" || goto :project_error

set "APP_VERSION=%~1"
if not defined APP_VERSION set /p "APP_VERSION=Build version (for example 1.7.0): "
if not defined APP_VERSION goto :version_error
powershell -NoProfile -Command "if ($env:APP_VERSION -cmatch '^[0-9]+(\.[0-9]+){0,3}(-[0-9A-Za-z]+(\.[0-9A-Za-z]+)*)?$' -and $env:APP_VERSION.Length -le 40) { exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 goto :version_error

set "BUILD_MODE=%~2"
if not defined BUILD_MODE set "BUILD_MODE=both"
if /i not "%BUILD_MODE%"=="both" if /i not "%BUILD_MODE%"=="standalone" if /i not "%BUILD_MODE%"=="onefile" goto :mode_error
if not "%~3"=="" goto :usage_error

set "PYTHON_EXE=python"
if defined NUITKA_PYTHON (
  set "PYTHON_EXE=%NUITKA_PYTHON%"
) else (
  rem Prefer an already activated environment. The original build environment
  rem may instead live under the user's Conda envs directory.
  python -c "import nuitka, PySide6" >nul 2>&1
  if errorlevel 1 (
    if exist "%USERPROFILE%\.conda\envs\nuitka_pack\python.exe" (
      set "PYTHON_EXE=%USERPROFILE%\.conda\envs\nuitka_pack\python.exe"
    ) else if exist "%ProgramData%\anaconda3\envs\nuitka_pack\python.exe" (
      set "PYTHON_EXE=%ProgramData%\anaconda3\envs\nuitka_pack\python.exe"
    )
  )
)
set "RELEASE_DIR=%CD%\release\v%APP_VERSION%"
if /i "%BUILD_MODE%"=="both" if exist "%RELEASE_DIR%" goto :release_exists
if /i "%BUILD_MODE%"=="standalone" if exist "%RELEASE_DIR%\standalone" goto :release_exists
if /i "%BUILD_MODE%"=="onefile" if exist "%RELEASE_DIR%\onefile" goto :release_exists
if not defined NUITKA_CACHE_DIR set "NUITKA_CACHE_DIR=%CD%\release\.nuitka-cache"

if not exist "main.py" goto :source_error
if not exist "config\experiments.json" goto :source_error
if not exist "docs\TECHNIQUE_MAPPING.md" goto :source_error

echo [INFO] Python: "%PYTHON_EXE%"
echo [INFO] Nuitka cache: "%NUITKA_CACHE_DIR%"
"%PYTHON_EXE%" -c "import nuitka, PySide6" >nul 2>&1
if errorlevel 1 goto :python_error
"%PYTHON_EXE%" -m nuitka --version
if errorlevel 1 goto :python_error

echo [INFO] Running project tests...
"%PYTHON_EXE%" -m unittest discover -s tests -q
if errorlevel 1 goto :tests_error

if /i "%BUILD_MODE%"=="both" goto :build_both
if /i "%BUILD_MODE%"=="standalone" goto :build_standalone
goto :build_onefile

:build_both
call :build_standalone
if errorlevel 1 exit /b 1
call :build_onefile
if errorlevel 1 exit /b 1
goto :finished

:build_standalone
echo [INFO] Building standalone in "%RELEASE_DIR%\standalone"...
"%PYTHON_EXE%" -m nuitka main.py ^
  --standalone ^
  --msvc=latest ^
  --enable-plugin=pyside6 ^
  --include-package=core ^
  --include-package=gui ^
  --include-package=utils ^
  --include-data-files=config/experiments.json=config/experiments.json ^
  --include-data-files=docs/TECHNIQUE_MAPPING.md=docs/TECHNIQUE_MAPPING.md ^
  --windows-console-mode=disable ^
  --assume-yes-for-downloads ^
  --output-filename=CHIMacroGenerator.exe ^
  --output-dir="%RELEASE_DIR%\standalone"
if errorlevel 1 goto :build_error
if not exist "%RELEASE_DIR%\standalone\main.dist\CHIMacroGenerator.exe" goto :artifact_error
if not exist "%RELEASE_DIR%\standalone\main.dist\config\experiments.json" goto :artifact_error
if not exist "%RELEASE_DIR%\standalone\main.dist\docs\TECHNIQUE_MAPPING.md" goto :artifact_error
echo [OK] Standalone: "%RELEASE_DIR%\standalone\main.dist"
exit /b 0

:build_onefile
echo [INFO] Building onefile in "%RELEASE_DIR%\onefile"...
"%PYTHON_EXE%" -m nuitka main.py ^
  --onefile ^
  --msvc=latest ^
  --enable-plugin=pyside6 ^
  --include-package=core ^
  --include-package=gui ^
  --include-package=utils ^
  --include-data-files=config/experiments.json=config/experiments.json ^
  --include-data-files=docs/TECHNIQUE_MAPPING.md=docs/TECHNIQUE_MAPPING.md ^
  --include-onefile-external-data=config/* ^
  --include-onefile-external-data=docs/* ^
  --windows-console-mode=disable ^
  --assume-yes-for-downloads ^
  --output-filename=CHIMacroGenerator.exe ^
  --output-dir="%RELEASE_DIR%\onefile"
if errorlevel 1 goto :build_error
if not exist "%RELEASE_DIR%\onefile\CHIMacroGenerator.exe" goto :artifact_error
if not exist "%RELEASE_DIR%\onefile\config\experiments.json" goto :artifact_error
if not exist "%RELEASE_DIR%\onefile\docs\TECHNIQUE_MAPPING.md" goto :artifact_error
echo [OK] Onefile: "%RELEASE_DIR%\onefile\CHIMacroGenerator.exe"
exit /b 0

:finished
echo [OK] Build completed: "%RELEASE_DIR%"
exit /b 0

:usage
echo Usage: build.bat [version] [both^|standalone^|onefile]
echo Example: build.bat 1.7.0 both
echo Set NUITKA_PYTHON to a python.exe with Nuitka and PySide6 installed.
exit /b 0

:usage_error
echo [ERROR] Too many arguments.
goto :failed
:project_error
echo [ERROR] Cannot open the project directory.
goto :failed
:version_error
echo [ERROR] Version must be numeric, with optional dot components and prerelease suffix.
goto :failed
:mode_error
echo [ERROR] Mode must be both, standalone, or onefile.
goto :failed
:release_exists
echo [ERROR] Requested build already exists under: "%RELEASE_DIR%"
echo [ERROR] Choose a new version or build a different mode to preserve existing settings.
goto :failed
:source_error
echo [ERROR] Missing main.py, config\experiments.json, or docs\TECHNIQUE_MAPPING.md.
goto :failed
:python_error
echo [ERROR] "%PYTHON_EXE%" cannot import Nuitka and PySide6.
echo [ERROR] Activate the build environment, or set NUITKA_PYTHON to its python.exe.
goto :failed
:tests_error
echo [ERROR] Project tests failed; build was not started.
goto :failed
:build_error
echo [ERROR] Nuitka build failed.
exit /b 1
:artifact_error
echo [ERROR] Nuitka returned success, but the executable, config, or documentation is missing.
exit /b 1
:failed
exit /b 1
