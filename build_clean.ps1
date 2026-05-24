# 清理并重新编译 Beamer deck
# 用法: .\build_clean.ps1 [deck-name]   (默认: cvgdiff-beamer)
#      .\build_clean.ps1 template-lib-demo
#      .\build_clean.ps1 all            (编译所有 .tex 文件)

param(
    [string]$Deck = "cvgdiff-beamer"
)

$ErrorActionPreference = "Stop"

# ── 确定要编译的文件 ─────────────────────────────────────────────────────────
$texFiles = @()
if ($Deck -eq "all") {
    $texFiles = Get-ChildItem *.tex | Where-Object { $_.Name -notmatch "^cvgdiff-minimal" } | Select-Object -ExpandProperty FullName
    if ($texFiles.Count -eq 0) {
        Write-Error "No .tex files found in current directory."
        exit 1
    }
} else {
    $texPath = "$Deck.tex"
    if (-not (Test-Path $texPath)) {
        Write-Error "File not found: $texPath"
        exit 1
    }
    $texFiles = @((Resolve-Path $texPath).Path)
}

# ── 清理函数 ─────────────────────────────────────────────────────────────────
function Clean-BuildFiles($stem) {
    Write-Host "=== Cleaning intermediate files for $stem ===" -ForegroundColor Cyan
    $exts = @("aux", "nav", "snm", "toc", "log", "out", "fls", "fdb_latexmk", "xdv")
    foreach ($ext in $exts) {
        $f = "build\$stem.$ext"
        if (Test-Path $f) {
            Remove-Item $f -Force
            Write-Host "  Removed: $f"
        }
    }
}

# ── 编译函数 ─────────────────────────────────────────────────────────────────
function Build-Deck($texFile) {
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($texFile)
    Clean-BuildFiles $stem

    for ($pass = 1; $pass -le 2; $pass++) {
        Write-Host ""
        Write-Host "=== $stem : Pass $pass/2 ===" -ForegroundColor Cyan
        xelatex -output-directory=build -interaction=nonstopmode "$texFile"
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Pass $pass exited with code $LASTEXITCODE (may be harmless appendixnumberbeamer errors)"
        }
    }

    # 复制到项目根目录
    $pdfSrc = "build\$stem.pdf"
    $pdfDst = "$stem.pdf"
    if (Test-Path $pdfSrc) {
        Copy-Item $pdfSrc $pdfDst -Force
        Write-Host "  Copied: $pdfDst" -ForegroundColor Green
    }

    # 检查 Overfull \vbox
    $logFile = "build\$stem.log"
    if (Test-Path $logFile) {
        $overflows = Select-String -Path $logFile -Pattern "Overfull \\vbox" | Select-Object -First 5
        if ($overflows) {
            Write-Host "  WARNING: Overfull \vbox detected:" -ForegroundColor Yellow
            $overflows | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
        } else {
            Write-Host "  No Overfull \vbox detected." -ForegroundColor Green
        }
    }

    Write-Host ""
}

# ── 主循环 ───────────────────────────────────────────────────────────────────
foreach ($tex in $texFiles) {
    Build-Deck $tex
}

Write-Host "=== Build complete ===" -ForegroundColor Green
Write-Host "=== Checking for Overfull \vbox ===" -ForegroundColor Cyan
$overfull = Select-String -Path "build\cvgdiff-beamer.log" -Pattern "Overfull \\vbox"
if ($overfull) {
    Write-Warning "Found Overfull \vbox:"
    $overfull | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "  No Overfull \vbox found." -ForegroundColor Green
}

Write-Host ""
Write-Host "=== Done ===" -ForegroundColor Green
