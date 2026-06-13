@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo Animal Detection - Final CUDA Validation
echo ========================================
echo.

set "PYTHON=%~dp0.venv_cuda\Scripts\python.exe"
set "PIP_CACHE_DIR=E:\pip_cache"
set "TORCH_HOME=%~dp0.torch"
set "YOLO_CONFIG_DIR=%~dp0ultralytics_config"

if not exist "%TORCH_HOME%" mkdir "%TORCH_HOME%"
if not exist "%YOLO_CONFIG_DIR%" mkdir "%YOLO_CONFIG_DIR%"
if not exist "outputs" mkdir "outputs"

REM Check CUDA virtual environment
"%PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: CUDA virtual environment not found: %PYTHON%
    echo Create it with: python -m venv .venv_cuda
    pause
    exit /b 1
)

REM Check CUDA availability
"%PYTHON%" -c "import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: CUDA is not available in .venv_cuda.
    echo Reinstall CUDA PyTorch in this environment before running validation.
    pause
    exit /b 1
)

echo.
set "MODEL=runs\detect\runs\detect\animal_dataset_6sp_20cls_finetune\weights\best.pt"
set "OUTPUT=outputs\valset_predictions_6sp_20cls_finetuned_suppressed_balanced.json"

if not exist "%MODEL%" (
    echo ERROR: Final model not found: %MODEL%
    pause
    exit /b 1
)

echo Running final 20-class YOLO model on val_set with CUDA...
echo.

"%PYTHON%" scripts\evaluate.py --image-dir val_set --output "%OUTPUT%" --model "%MODEL%" --conf 0.25 --iou 0.45 --imgsz 640 --device 0

echo.
echo Done! Check %OUTPUT% for results.
pause
