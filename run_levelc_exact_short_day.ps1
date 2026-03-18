[CmdletBinding()]
param(
    [string]$DayLabel = "day2",
    [string]$Backend = "ibm_fez",
    [string]$Depths = "1,2,3,4",
    [int]$Trials = 3,
    [int]$Shots = 4000,
    [double]$TargetMae = 0.05,
    [string]$RuntimeMetric = "quantum_seconds",
    [switch]$DryRun
)

$targetScript = Join-Path (Split-Path -Parent $PSCommandPath) "run_q14_only_exact_short_day.ps1"
if (-not (Test-Path $targetScript)) {
    throw "Missing target script: $targetScript"
}

Write-Warning "run_levelc_exact_short_day.ps1 now forwards to the active q14-only benchmark runner."

$forward = @{
    DayLabel = $DayLabel
    Backend = $Backend
    Depths = $Depths
    Trials = $Trials
    Shots = $Shots
    TargetMae = $TargetMae
    RuntimeMetric = $RuntimeMetric
}
if ($DryRun) {
    $forward.DryRun = $true
}

& $targetScript @forward
exit $LASTEXITCODE
