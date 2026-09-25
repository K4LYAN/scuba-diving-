# Dev-only: headless Edge screenshots of settled pages.
#   powershell -File tools\qa\shoot.ps1 -Page index -Width 1440 -Height 7400 -Theme dark -Out shot.png
param(
    [string]$Page = 'index',
    [int]$Width = 1440,
    [int]$Height = 7400,
    [string]$Theme = 'dark',
    [string]$Out = "$env:TEMP\dive-adda-$Page-$Theme-$Width.png"
)
$edge = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
$profile = Join-Path $env:TEMP "dive-adda-shot-$Theme-$Width"
$url = "http://localhost:8123/tools/qa/shot.html?page=$Page&w=$Width&h=$Height&theme=$Theme"
$args = @('--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
          "--user-data-dir=$profile", "--window-size=$Width,$Height", '--virtual-time-budget=25000',
          "--screenshot=$Out", $url)
Start-Process -FilePath $edge -ArgumentList $args -Wait -NoNewWindow -RedirectStandardError "$env:TEMP\dive-adda-shot.log" | Out-Null
if (Test-Path $Out) { "saved $Out" } else { "no screenshot written" }
