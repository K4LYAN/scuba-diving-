# Dev-only: mobile Lighthouse run against the local server (python tools/serve.py).
#   powershell -File tools/qa/lighthouse.ps1 -Page index -Out C:\temp\lh.json
param([string]$Page = 'index', [string]$Out = "$env:TEMP\lh-$Page.json", [int]$Port = 8123, [switch]$Desktop)
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$prof = Join-Path $env:TEMP ('lh-prof-' + [guid]::NewGuid())
$p = Start-Process $edge -ArgumentList '--headless=new', '--remote-debugging-port=9333', "--user-data-dir=$prof", '--no-first-run', 'about:blank' -PassThru
Start-Sleep 3
try {
    npx -y lighthouse@12 "http://127.0.0.1:$Port/$Page.html" --port=9333 --quiet $(if ($Desktop) { "--preset=desktop" }) --output=json --output-path=$Out 2>$null | Out-Null
} finally {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    Get-Process msedge -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*$prof*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Remove-Item $prof -Recurse -Force -ErrorAction SilentlyContinue
}
