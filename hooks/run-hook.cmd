: << 'CMDBLOCK'
@echo off
REM Polyglot launcher for the sdd-convention Stop hook.
REM On Windows cmd.exe runs this batch block; POSIX shells skip it (the first
REM line is a no-op heredoc in sh). Fails open (exit 0) when no Python is
REM available: the hook is a reminder, not a gate - CI carries enforcement.
where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -3 "%~dp0check-docs-updated.py"
    exit /b 0
)
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python "%~dp0check-docs-updated.py"
    exit /b 0
)
exit /b 0
CMDBLOCK

# POSIX: prefer python3, fall back to python, else fail open.
DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then exec python3 "$DIR/check-docs-updated.py"; fi
if command -v python >/dev/null 2>&1; then exec python "$DIR/check-docs-updated.py"; fi
exit 0
