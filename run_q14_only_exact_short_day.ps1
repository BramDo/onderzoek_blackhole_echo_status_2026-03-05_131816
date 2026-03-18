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

$ErrorActionPreference = "Stop"

function Convert-WindowsPathToWsl {
    param([Parameter(Mandatory = $true)][string]$Path)

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    if ($fullPath -notmatch "^[A-Za-z]:\\") {
        throw "Unsupported Windows path for WSL conversion: $fullPath"
    }

    $drive = $fullPath.Substring(0, 1).ToLowerInvariant()
    $rest = $fullPath.Substring(2).Replace("\", "/")
    return "/mnt/$drive$rest"
}

function Convert-WallClockToSeconds {
    param([Parameter(Mandatory = $true)][string]$Value)

    $parts = $Value.Trim().Split(":")
    switch ($parts.Count) {
        2 {
            $minutes = [double]$parts[0]
            $seconds = [double]$parts[1]
            return ($minutes * 60.0) + $seconds
        }
        3 {
            $hours = [double]$parts[0]
            $minutes = [double]$parts[1]
            $seconds = [double]$parts[2]
            return ($hours * 3600.0) + ($minutes * 60.0) + $seconds
        }
        default {
            throw "Unsupported wall clock format: $Value"
        }
    }
}

function Get-ClassicalBaselineSeconds {
    param([Parameter(Mandatory = $true)][int]$Qubits)

    $timePath = Join-Path $script:RepoWin ("results\benchmark\classical\time_black_hole_scrambling_q{0}_exact_short.txt" -f $Qubits)
    if (-not (Test-Path $timePath)) {
        throw "Missing classical timing file: $timePath"
    }

    $match = Select-String -Path $timePath -Pattern 'Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*(.+)$' | Select-Object -First 1
    if (-not $match) {
        throw "Could not parse classical wall time from: $timePath"
    }

    $wallClock = $match.Matches[0].Groups[1].Value.Trim()
    return Convert-WallClockToSeconds $wallClock
}

function Get-PerturbedMae {
    param([Parameter(Mandatory = $true)][string]$JsonPath)

    if (-not (Test-Path $JsonPath)) {
        throw "Missing hardware output JSON: $JsonPath"
    }

    $doc = Get-Content $JsonPath -Raw | ConvertFrom-Json
    $runs = @($doc.runs)
    if ($runs.Count -eq 0) {
        throw "No runs found in hardware output JSON: $JsonPath"
    }

    $values = foreach ($run in $runs) {
        [double]$run.raw.perturbed_abs_error_vs_exact
    }

    if ($values.Count -eq 0) {
        throw "No perturbed_abs_error_vs_exact values found in: $JsonPath"
    }

    return (($values | Measure-Object -Average).Average)
}

function Get-HardwareRuntimeInfo {
    param([Parameter(Mandatory = $true)][string]$JsonPath)

    if (-not (Test-Path $JsonPath)) {
        throw "Missing hardware output JSON: $JsonPath"
    }

    $doc = Get-Content $JsonPath -Raw | ConvertFrom-Json
    $rt = $doc.runtime
    $jobMeta = $rt.hardware_job_metadata
    if ($null -eq $jobMeta) {
        return [pscustomobject]@{
            quantum_seconds = $null
            billed_seconds = $null
            usage_estimate_qs = $null
            created_timestamp = $null
            running_timestamp = $null
            finished_timestamp = $null
            status = $null
        }
    }

    return [pscustomobject]@{
        quantum_seconds = $jobMeta.metrics.usage.quantum_seconds
        billed_seconds = $jobMeta.metrics.bss.seconds
        usage_estimate_qs = $jobMeta.usage_estimation.quantum_seconds
        created_timestamp = $jobMeta.metrics.timestamps.created
        running_timestamp = $jobMeta.metrics.timestamps.running
        finished_timestamp = $jobMeta.metrics.timestamps.finished
        status = $jobMeta.status
    }
}

function Invoke-HardwareRun {
    param([Parameter(Mandatory = $true)][int]$Qubits)

    $outputRel = "results/hardware/benchmark_q${Qubits}_raw_exact_short_${DayLabel}.json"
    $outputWin = Join-Path $script:RepoWin ($outputRel.Replace("/", "\"))
    $timingWin = Join-Path $script:RepoWin ("results\hardware\time_benchmark_q{0}_raw_exact_short_{1}.txt" -f $Qubits, $DayLabel)
    $stdoutLogWin = Join-Path $script:RepoWin ("results\hardware\stdout_benchmark_q{0}_raw_exact_short_{1}.log" -f $Qubits, $DayLabel)

    $innerCmd = @(
        "cd '$script:RepoWsl' &&"
        "/home/bram/.venvs/qiskit/bin/python qiskit_black_hole_hardware_runner.py"
        "--backend $Backend"
        "--qubits $Qubits"
        "--depths $Depths"
        "--trials $Trials"
        "--shots $Shots"
        "--output-json $outputRel"
    ) -join " "

    if ($DryRun) {
        return [pscustomobject]@{
            qubits = $Qubits
            command = $innerCmd
            output_json = $outputWin
            timing_file = $timingWin
            stdout_log = $stdoutLogWin
            classical_seconds = [math]::Round((Get-ClassicalBaselineSeconds -Qubits $Qubits), 2)
        }
    }

    $startedUtc = (Get-Date).ToUniversalTime().ToString("o")
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    & wsl -e bash -lc "$innerCmd" *> $stdoutLogWin
    $exitCode = $LASTEXITCODE
    $stopwatch.Stop()
    $completedUtc = (Get-Date).ToUniversalTime().ToString("o")

    if ($exitCode -ne 0) {
        throw "Hardware run for q$Qubits failed with exit code $exitCode. See $stdoutLogWin"
    }

    $elapsedSeconds = [math]::Round($stopwatch.Elapsed.TotalSeconds, 2)
    $classicalSeconds = [math]::Round((Get-ClassicalBaselineSeconds -Qubits $Qubits), 2)
    $mae = [math]::Round((Get-PerturbedMae -JsonPath $outputWin), 6)
    $hwInfo = Get-HardwareRuntimeInfo -JsonPath $outputWin
    $gateSeconds = $elapsedSeconds
    $gateMetricUsed = "elapsed_seconds"
    if ($RuntimeMetric -eq "quantum_seconds" -and $null -ne $hwInfo.quantum_seconds) {
        $gateSeconds = [double]$hwInfo.quantum_seconds
        $gateMetricUsed = "quantum_seconds"
    }

    @(
        "started_utc=$startedUtc"
        "completed_utc=$completedUtc"
        "elapsed_seconds=$elapsedSeconds"
        "classical_baseline_seconds=$classicalSeconds"
        "perturbed_echo_mae=$mae"
        "target_mae=$TargetMae"
        "backend=$Backend"
        "output_json=$outputRel"
        "job_status=$($hwInfo.status)"
        "quantum_seconds=$($hwInfo.quantum_seconds)"
        "billed_seconds=$($hwInfo.billed_seconds)"
        "usage_estimate_qs=$($hwInfo.usage_estimate_qs)"
        "runtime_gate_metric=$gateMetricUsed"
        "runtime_gate_seconds=$gateSeconds"
        "ibm_created_timestamp=$($hwInfo.created_timestamp)"
        "ibm_running_timestamp=$($hwInfo.running_timestamp)"
        "ibm_finished_timestamp=$($hwInfo.finished_timestamp)"
    ) | Set-Content $timingWin

    return [pscustomobject]@{
        qubits = $Qubits
        output_json = $outputWin
        timing_file = $timingWin
        stdout_log = $stdoutLogWin
        elapsed_seconds = $elapsedSeconds
        classical_seconds = $classicalSeconds
        perturbed_mae = $mae
        quantum_seconds = $hwInfo.quantum_seconds
        billed_seconds = $hwInfo.billed_seconds
        usage_estimate_qs = $hwInfo.usage_estimate_qs
        runtime_gate_metric = $gateMetricUsed
        runtime_gate_seconds = $gateSeconds
        pass_mae = ($mae -le $TargetMae)
        pass_runtime = ($gateSeconds -lt $classicalSeconds)
    }
}

$SnapshotRoot = Split-Path -Parent $PSCommandPath
$RepoWin = Join-Path $SnapshotRoot "files\quantum-math-lab"
$RepoWsl = Convert-WindowsPathToWsl -Path $RepoWin

Write-Host "Q14-only exact-short raw day runner"
Write-Host "Day label: $DayLabel"
Write-Host "Backend: $Backend"
Write-Host "Repo: $RepoWin"

$q14 = Invoke-HardwareRun -Qubits 14
if ($DryRun) {
    Write-Host ""
    Write-Host "Dry-run q14 command:"
    Write-Host $q14.command
    Write-Host ("q14 classical baseline: {0}s" -f $q14.classical_seconds)
    exit 0
}

Write-Host ""
Write-Host ("q14 finished: MAE={0}, hardware_wall={1}s, classical_wall={2}s, quantum_seconds={3}, gate_metric={4}, gate_seconds={5}" -f $q14.perturbed_mae, $q14.elapsed_seconds, $q14.classical_seconds, $q14.quantum_seconds, $q14.runtime_gate_metric, $q14.runtime_gate_seconds)

if (-not $q14.pass_mae) {
    Write-Warning "q14 finished but missed the MAE target."
    exit 12
}

if (-not $q14.pass_runtime) {
    Write-Warning "q14 finished but the runtime gate is not below the q14 classical baseline."
    exit 13
}

Write-Host ""
Write-Host "Day run passed the q14-only gates."
exit 0
