# Reproducible, non-destructive native 4X endurance test: six factions,
# independent seeds, deterministic campaign progression and economy screenshots.
# This is a survival/UI smoke test, NOT a proof of AI expansion or balance.
param(
    [Parameter(Mandatory=$true)][string]$PackageDir,
    [int]$Turns = 500,
    [string]$OutputDir = ""
)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$PackageDir = (Resolve-Path $PackageDir).Path
if ($Turns -lt 100 -or $Turns -gt 2000) { throw 'Turns must be 100..2000' }
if (-not (Test-Path (Join-Path $PackageDir 'VOIDREIGN.exe'))) { throw 'Native VOIDREIGN.exe not found in stage' }
if (-not (Test-Path (Join-Path $PackageDir 'game-data\Data\Components.txt'))) { throw 'Bundled native game-data missing' }
if (-not $OutputDir) { $OutputDir = Join-Path $env:TEMP ('voidreign-faction-soak-' + $Turns) }
$full = [IO.Path]::GetFullPath($OutputDir).TrimEnd('\')
if ($full.StartsWith($root.TrimEnd('\') + '\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Use an output directory outside the repository, to keep screenshots untracked'
}
New-Item -ItemType Directory -Path $full -Force | Out-Null
$source = [IO.File]::ReadAllText((Join-Path $root 'tests\input\voidreign-native-longgame.script'))
$cases = @(
    @{Faction='Aurelian'; Seed=7},
    @{Faction='Veyran'; Seed=11},
    @{Faction='Khepri'; Seed=13},
    @{Faction='Meridian'; Seed=17},
    @{Faction='Outer'; Seed=19},
    @{Faction='Helion'; Seed=23}
)
$scripts = @()
foreach($case in $cases) {
    $name = $case.Faction.ToLowerInvariant()
    $body = $source.Replace('--turns=100',('--turns=' + $Turns)).
        Replace('assert-turn 100',('assert-turn ' + $Turns)).
        Replace('--quick-start=Aurelian',('--quick-start=' + $case.Faction)).
        Replace('--seed=7',('--seed=' + $case.Seed)).
        Replace('voidreign-century',('voidreign-' + $Turns + '-' + $name)).
        Replace('100-turn','long-running')
    $path = Join-Path $full ('soak-' + $name + '.script')
    [IO.File]::WriteAllText($path, $body, [Text.UTF8Encoding]::new($false))
    $scripts += $path
    Write-Output ('SCENARIO ' + $case.Faction + ' seed=' + $case.Seed + ' turns=' + $Turns)
}
$watch = [Diagnostics.Stopwatch]::StartNew()
& python (Join-Path $root 'tools\run_input_tests.py') --exe (Join-Path $PackageDir 'VOIDREIGN.exe') --data-dir (Join-Path $PackageDir 'game-data') --renderer opengl --jobs 1 --timeout 180 --output (Join-Path $full 'results') @scripts
$status = $LASTEXITCODE
$watch.Stop()
Write-Output ('SIMULATED_TURNS_REQUESTED=' + ($Turns * $cases.Count))
Write-Output ('WALL_SECONDS=' + [Math]::Round($watch.Elapsed.TotalSeconds,2))
Write-Output ('FACTION_SOAK_EXIT=' + $status)
Write-Output 'NOTE: Inspect resource overflow, expansion, AI decisions and balance separately; passing these scripts alone does not prove them.'
exit $status
