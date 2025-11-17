# Backend Connection Test Suite
# Tests all endpoints systematically (PowerShell 5.1 compatible)

$baseUrl = "https://web-production-0249c.up.railway.app"
$results = @()

# Test 1: Health Endpoint
Write-Host "`n=== Test 1: GET /health ===" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -TimeoutSec 10
    Write-Host "Status: $($response.StatusCode) - OK" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    Write-Host "Response: $($respData | ConvertTo-Json -Compress)" -ForegroundColor Green
    $results += @{ Test = "1. Health"; Status = "PASS"; Code = $response.StatusCode }
} catch {
    Write-Host "Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    $results += @{ Test = "1. Health"; Status = "FAIL"; Code = 0; Error = $_.Exception.Message }
}

# Test 2: Analyze Endpoint - Simple Query
Write-Host "`n=== Test 2: POST /analyze - Simple Query ===" -ForegroundColor Cyan
try {
    $body = @{
        question = "What is data analysis?"
        context = @{}
    } | ConvertTo-Json
    
    Write-Host "Sending: $body" -ForegroundColor Gray
    
    $response = Invoke-WebRequest -Uri "$baseUrl/analyze" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "Status: $($response.StatusCode) - OK" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    Write-Host "Response Fields: $(($respData | Get-Member -MemberType NoteProperty | ForEach-Object { $_.Name }) -join ', ')" -ForegroundColor Green
    Write-Host "Response: $($respData | ConvertTo-Json -Compress)" -ForegroundColor Green
    $results += @{ Test = "2. Analyze-Simple"; Status = "PASS"; Code = $response.StatusCode }
} catch {
    Write-Host "Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    $results += @{ Test = "2. Analyze-Simple"; Status = "FAIL"; Code = 0; Error = $_.Exception.Message }
}

# Test 3: Analyze Endpoint - Math Query
Write-Host "`n=== Test 3: POST /analyze - Math Query ===" -ForegroundColor Cyan
try {
    $body = @{
        question = "Calculate 5 plus 3"
        context = @{}
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/analyze" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "Status: $($response.StatusCode) - OK" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    $preview = if ($respData.explanation) { $respData.explanation.Substring(0, [Math]::Min(100, $respData.explanation.Length)) } else { "N/A" }
    Write-Host "Preview: $preview..." -ForegroundColor Green
    $results += @{ Test = "3. Analyze-Math"; Status = "PASS"; Code = $response.StatusCode }
} catch {
    Write-Host "Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    $results += @{ Test = "3. Analyze-Math"; Status = "FAIL"; Code = 0; Error = $_.Exception.Message }
}

# Test 4: Analyze Endpoint - With Context
Write-Host "`n=== Test 4: POST /analyze - With Context ===" -ForegroundColor Cyan
try {
    $body = @{
        question = "What is machine learning?"
        context = @{ domain = "AI"; level = "beginner" }
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$baseUrl/analyze" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "Status: $($response.StatusCode) - OK" -ForegroundColor Green
    $respData = $response.Content | ConvertFrom-Json
    Write-Host "Response received with fields: $(($respData | Get-Member -MemberType NoteProperty | ForEach-Object { $_.Name }) -join ', ')" -ForegroundColor Green
    $results += @{ Test = "4. Analyze-Context"; Status = "PASS"; Code = $response.StatusCode }
} catch {
    Write-Host "Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    $results += @{ Test = "4. Analyze-Context"; Status = "FAIL"; Code = 0; Error = $_.Exception.Message }
}

# Test 5: Root Endpoint
Write-Host "`n=== Test 5: GET / ===" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/" -Method GET -TimeoutSec 10
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    $preview = $response.Content.Substring(0, [Math]::Min(150, $response.Content.Length))
    Write-Host "Response Preview: $preview..." -ForegroundColor Green
    $results += @{ Test = "5. Root"; Status = "PASS"; Code = $response.StatusCode }
} catch {
    Write-Host "Status: ERROR - $($_.Exception.Message)" -ForegroundColor Red
    $results += @{ Test = "5. Root"; Status = "FAIL"; Code = 0; Error = $_.Exception.Message }
}

# Test 6: Connection Stability - Multiple Requests
Write-Host "`n=== Test 6: Connection Stability ===" -ForegroundColor Cyan
$stableTests = 0
for ($idx = 1; $idx -le 3; $idx++) {
    try {
        $body = @{
            question = "Test $idx"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri "$baseUrl/analyze" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Host "  Request $idx : OK (200)" -ForegroundColor Green
            $stableTests++
        } else {
            Write-Host "  Request $idx : HTTP $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  Request $idx : ERROR" -ForegroundColor Red
    }
}
Write-Host "Stability: $stableTests/3 requests successful" -ForegroundColor $(if ($stableTests -eq 3) { "Green" } else { "Yellow" })
$results += @{ Test = "6. Stability"; Status = if ($stableTests -eq 3) { "PASS" } else { "WARN" }; Code = $stableTests }

# Summary
Write-Host "`n" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Magenta
Write-Host "           BACKEND CONNECTION TEST RESULTS       " -ForegroundColor Magenta
Write-Host "================================================" -ForegroundColor Magenta

Write-Host "`nTotal Tests: $($results.Count)" -ForegroundColor White

$pass = @($results | Where-Object { $_.Status -eq "PASS" }).Count
$warn = @($results | Where-Object { $_.Status -eq "WARN" }).Count
$fail = @($results | Where-Object { $_.Status -eq "FAIL" }).Count

Write-Host "PASS: $pass" -ForegroundColor Green
Write-Host "WARN: $warn" -ForegroundColor Yellow
Write-Host "FAIL: $fail" -ForegroundColor Red

Write-Host "`nDetailed Results:" -ForegroundColor White
$results | ForEach-Object {
    $color = switch ($_.Status) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "White" }
    }
    $codeStr = if ($_.Code -gt 0) { "HTTP $($_.Code)" } else { "No response" }
    Write-Host "  $($_.Test) - $($_.Status) ($codeStr)" -ForegroundColor $color
    if ($_.Error) {
        Write-Host "    Error: $($_.Error)" -ForegroundColor Red
    }
}

# Overall Status
Write-Host "`n" -ForegroundColor White
if ($fail -eq 0 -and $pass -gt 0) {
    Write-Host "🎉 ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Backend connection verified at all endpoints." -ForegroundColor Green
} else {
    Write-Host "⚠️ SOME ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host "Review errors above for details." -ForegroundColor Yellow
}

Write-Host "`n================================================" -ForegroundColor Magenta
Write-Host "✅ Testing Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Magenta
