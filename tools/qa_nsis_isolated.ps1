# Build and exercise a non-elevated, isolated variant of the production NSIS
# installer. Production script and installed applications are NEVER modified.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File tools/qa_nsis_isolated.ps1 -PackageDir <stage> [-RunGameplay]
param(
    [Parameter(Mandatory=$true)][string]$PackageDir,
    [string]$OutputDir = "",
    [switch]$RunGameplay
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$PackageDir = (Resolve-Path $PackageDir).Path
$makensis = 'C:\Program Files (x86)\NSIS\makensis.exe'
if (-not (Test-Path $makensis)) { throw 'NSIS makensis.exe not installed' }
if (-not (Test-Path (Join-Path $PackageDir 'VOIDREIGN.exe'))) { throw 'Incomplete native stage' }
if (-not $OutputDir) { $OutputDir = Join-Path $env:TEMP 'voidreign-nsis-isolated-qa' }
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$id = [guid]::NewGuid().ToString('N').Substring(0,10)
$qaName = 'VOIDREIGN-NSIS-QA-' + $id
$qaRoot = Join-Path $OutputDir $qaName
New-Item -ItemType Directory -Force -Path $qaRoot | Out-Null
$testInstaller = Join-Path $qaRoot ($qaName + '-setup.exe')
$testScript = Join-Path $qaRoot 'qa-installer.nsi'
$installed = Join-Path $env:TEMP $qaName
$uninstallKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\' + $qaName
$settingsKey = 'HKCU:\Software\' + $qaName
$startShortcut = Join-Path ([Environment]::GetFolderPath('Programs')) ($qaName + '.lnk')
$desktopShortcut = Join-Path ([Environment]::GetFolderPath('Desktop')) ($qaName + '.lnk')
$source = Get-Content -LiteralPath (Join-Path $repo 'packaging\windows\opense4.nsi') -Raw
$qa = $source.Replace('RequestExecutionLevel admin','RequestExecutionLevel user')
$qa = $qa.Replace('SetShellVarContext all','SetShellVarContext current')
$qa = $qa.Replace('HKLM','HKCU')
$qa = $qa.Replace('!define APP_NAME "VOIDREIGN"',('!define APP_NAME "' + $qaName + '"'))
$qa = $qa.Replace('Software\Microsoft\Windows\CurrentVersion\Uninstall\VOIDREIGN',('Software\Microsoft\Windows\CurrentVersion\Uninstall\' + $qaName))
$qa = $qa.Replace('Software\VOIDREIGN',('Software\' + $qaName))
$qa = $qa.Replace('$PROGRAMFILES64\VOIDREIGN',('$TEMP\' + $qaName))
$icon = Join-Path $repo 'packaging\windows\voidreign.ico'
$side = Join-Path $repo 'packaging\windows\installer-side.bmp'
foreach ($symbol in @('MUI_ICON','MUI_UNICON')) {
    $qa = $qa.Replace(('!define ' + $symbol + ' "voidreign.ico"'),('!define ' + $symbol + ' "' + $icon + '"'))
}
foreach ($symbol in @('MUI_WELCOMEFINISHPAGE_BITMAP','MUI_UNWELCOMEFINISHPAGE_BITMAP')) {
    $qa = $qa.Replace(('!define ' + $symbol + ' "installer-side.bmp"'),('!define ' + $symbol + ' "' + $side + '"'))
}
if ($qa -match 'RequestExecutionLevel admin|\bHKLM\b|SetShellVarContext all|\$PROGRAMFILES64\\VOIDREIGN') {
    throw 'QA installer still contains a production installation privilege/path'
}
if ($qa -notmatch [regex]::Escape($qaName)) { throw 'QA identity replacement missing' }
[IO.File]::WriteAllText($testScript, $qa, [Text.UTF8Encoding]::new($false))
Write-Output ('QA_ID=' + $qaName)
Write-Output ('QA_SCRIPT=' + $testScript)
Write-Output 'Compiling isolated QA installer from production NSIS source'
& $makensis '/V2' '-DVERSION=0.1.0-qa' '-DVERSION_NUMBER=0.1.0' ('-DSTAGE=' + $PackageDir) ('-DOUTFILE=' + $testInstaller) $testScript
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $testInstaller)) { throw 'Isolated NSIS compile failed' }
Write-Output ('QA_SETUP_BYTES=' + (Get-Item $testInstaller).Length)
if ((Test-Path $installed) -or (Test-Path $uninstallKey) -or (Test-Path $settingsKey)) {
    throw 'QA destination or registry keys already exist, refusing to overwrite'
}
# An independently named sentinel in normal per-user saves detects accidental
# cleanup without changing or deleting existing user saves.
$saveDir = Join-Path $env:APPDATA 'VOIDREIGN\saves'
New-Item -ItemType Directory -Force -Path $saveDir | Out-Null
$sentinel = Join-Path $saveDir ($qaName + '.gam')
if (Test-Path $sentinel) { throw 'QA sentinel collision' }
[IO.File]::WriteAllText($sentinel,'VOIDREIGN isolated NSIS save preservation sentinel')
try {
    Write-Output 'Installing QA build silently in user TEMP (no UAC / no production keys)'
    $installProcess = Start-Process -FilePath $testInstaller -ArgumentList '/S' -Wait -PassThru
    if ($installProcess.ExitCode -ne 0) { throw ('QA install exit '+$installProcess.ExitCode) }
    foreach ($name in @('VOIDREIGN.exe','VOIDREIGN-datacheck.exe','VOIDREIGN-server.exe','VOIDREIGN-sdk.exe','game-data\Data\Components.txt','uninstall.exe')) {
        if (-not (Test-Path (Join-Path $installed $name))) { throw ('QA install missing '+$name) }
    }
    if (-not (Test-Path $uninstallKey)) { throw 'QA uninstall key missing in HKCU' }
    if (-not (Test-Path $settingsKey)) { throw 'QA settings key missing in HKCU' }
    if (-not (Test-Path $startShortcut)) { throw 'QA Start-menu shortcut missing' }
    $stagedHash = (Get-FileHash (Join-Path $PackageDir 'VOIDREIGN.exe') -Algorithm SHA256).Hash
    $installedHash = (Get-FileHash (Join-Path $installed 'VOIDREIGN.exe') -Algorithm SHA256).Hash
    if ($stagedHash -ne $installedHash) { throw 'Installed executable differs from packaged executable' }
    $dataOutput = & (Join-Path $installed 'VOIDREIGN-datacheck.exe') (Join-Path $installed 'game-data\Data') 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0 -or $dataOutput -notmatch '0 errors, 0 warnings') { throw 'Installed game-data invalid' }
    Write-Output 'PASS: isolated NSIS install, registry, shortcut, exact binary, native data'
    $app = $null
    try {
        $app = Start-Process -FilePath (Join-Path $installed 'VOIDREIGN.exe') -ArgumentList '--quick-start=Aurelian --systems=24 --empires=3 --seed=7 --no-audio --size=1280x800' -WorkingDirectory $installed -PassThru
        $window = $false
        for ($i = 0; $i -lt 30; $i++) {
            Start-Sleep -Milliseconds 500
            $app.Refresh()
            if ($app.HasExited) { throw 'Installed game exited before opening its window' }
            if ($app.MainWindowHandle -ne 0 -and $app.Responding) { $window = $true; break }
        }
        if (-not $window) { throw 'No responsive native application window appeared' }
        Write-Output ('PASS: installed native application window, title='+$app.MainWindowTitle)
    } finally {
        if ($app -and -not $app.HasExited) {
            try { $null=$app.CloseMainWindow(); if (-not $app.WaitForExit(4000)) { $app.Kill() } }
            catch { try {$app.Kill()} catch {} }
        }
    }
    if ($RunGameplay) {
        $smokes = @('voidreign-native-startup','voidreign-native-veyran','voidreign-native-khepri','voidreign-native-fleet-control','voidreign-native-save-load','voidreign-native-ai-turns')
        & python (Join-Path $repo 'tools\run_input_tests.py') --exe (Join-Path $installed 'VOIDREIGN.exe') --data-dir (Join-Path $installed 'game-data') --renderer opengl --jobs 1 --output (Join-Path $qaRoot 'gameplay') @smokes
        if ($LASTEXITCODE -ne 0) { throw 'Installed native gameplay scripts failed' }
        Write-Output 'PASS: six installed native gameplay scripts'
    }
    Write-Output 'Uninstalling isolated QA build silently'
    $uninstaller = Join-Path $installed 'uninstall.exe'
    $uninstallProcess = Start-Process -FilePath $uninstaller -ArgumentList '/S' -Wait -PassThru
    if ($uninstallProcess.ExitCode -ne 0) { throw ('QA uninstall exit '+$uninstallProcess.ExitCode) }
    for($i=0; $i -lt 50 -and ((Test-Path $installed) -or (Test-Path $uninstallKey)); $i++) { Start-Sleep -Milliseconds 300 }
    if ((Test-Path $installed) -or (Test-Path $uninstallKey) -or (Test-Path $settingsKey)) { throw 'QA uninstall left install files or registry keys' }
    if (Test-Path $startShortcut) { throw 'QA uninstall left Start-menu shortcut' }
    if (Test-Path $desktopShortcut) { throw 'QA uninstall left desktop shortcut' }
    if ((-not (Test-Path $sentinel)) -or ([IO.File]::ReadAllText($sentinel) -ne 'VOIDREIGN isolated NSIS save preservation sentinel')) {
        throw 'Uninstaller modified per-user saves'
    }
    Write-Output 'PASS: isolated NSIS uninstall is clean and preserves per-user saves'
    Write-Output 'QA_RESULT=SUCCESS'
} finally {
    if (Test-Path $sentinel) { Remove-Item -LiteralPath $sentinel -Force }
}
