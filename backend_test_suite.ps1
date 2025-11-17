# Backend Connection Test Suite
# Tests all endpoints at every level with detailed diagnostics

$baseUrl = "https://web-production-0249c.up.railway.app"
$results = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Path,
        [object]$Body,
        [hashtable]$Headers
    )
    
    $url = "$baseUrl$Path"
    Write-Host "`n=== Testing: $Name ===" -ForegroundColor Cyan
    Write-Host "URL: $url" -ForegroundColor Gray
    Write-Host "Method: $Method" -ForegroundColor Gray
    
    $result = @{
        Name = $Name
        Method = $Method
        Path = $Path
        Status = "UNKNOWN"
        StatusCode = 0
        Duration = 0
        Response = $null
        Error = $null
    }
    
    try {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        
        $params = @{
            Uri = $url
            Method = $Method
            ContentType = "application/json"
            TimeoutSec = 10
        }
        
        if ($Headers) {
            $params["Headers"] = $Headers
        }
        
        if ($Body) {
            $bodyJson = $Body | ConvertTo-Json -Depth 10
            $params["Body"] = $bodyJson
            Write-Host "Body: $bodyJson" -ForegroundColor Gray
        }
        
        $response = Invoke-WebRequest @params -SkipHttpErrorCheck
        $stopwatch.Stop()
        
        $result.StatusCode = $response.StatusCode
        $result.Duration = $stopwatch.ElapsedMilliseconds
        
        # Parse response
        if ($response.Content) {
            try {
                $result.Response = $response.Content | ConvertFrom-Json
            } catch {
                $result.Response = $response.Content
            }
        }
        
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
            $result.Status = "✅ PASS"
            Write-Host "Status: ✅ OK ($($response.StatusCode))" -ForegroundColor Green
            Write-Host "Duration: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Green
            Write-Host "Response: $($result.Response | ConvertTo-Json -Compress)" -ForegroundColor Green
        } else {
            $result.Status = "⚠️ WARNING"
            Write-Host "Status: ⚠️ HTTP $($response.StatusCode)" -ForegroundColor Yellow
            Write-Host "Duration: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Yellow
            Write-Host "Response: $($result.Response | ConvertTo-Json -Compress)" -ForegroundColor Yellow
        }
    } catch {
        $result.Status = "❌ FAIL"
        $result.Error = $_.Exception.Message
        Write-Host "Status: ❌ ERROR" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Details: $($_.Exception | ConvertTo-Json)" -ForegroundColor Red
    }
    
    $results += $result
    return $result
}

# Test 1: Health Endpoint
Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  BACKEND CONNECTION TEST SUITE             ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Magenta

Write-Host "`nPhase 1: Health Check" -ForegroundColor Yellow
Test-Endpoint -Name "GET /health" -Method "GET" -Path "/health"

# Test 2: Analyze Endpoint - Valid Request
Write-Host "`nPhase 2: Analyze Endpoint" -ForegroundColor Yellow
Test-Endpoint -Name "POST /analyze - Valid Query" -Method "POST" -Path "/analyze" -Body @{
    question = "What is data analysis?"
    context = @{}
}

# Test 3: Analyze Endpoint - Another Query
Test-Endpoint -Name "POST /analyze - Math Query" -Method "POST" -Path "/analyze" -Body @{
    question = "Calculate the sum of 5 and 3"
    context = @{}
}

# Test 4: Analyze Endpoint - Empty Query (Should fail)
Write-Host "`nPhase 3: Error Handling" -ForegroundColor Yellow
Test-Endpoint -Name "POST /analyze - Empty Query" -Method "POST" -Path "/analyze" -Body @{
    question = ""
    context = @{}
}

# Test 5: Analyze Endpoint - Missing Context (Should still work)
Test-Endpoint -Name "POST /analyze - Missing Context" -Method "POST" -Path "/analyze" -Body @{
    question = "Test query without context"
}

# Test 6: Root Endpoint
Write-Host "`nPhase 4: Root Endpoint" -ForegroundColor Yellow
Test-Endpoint -Name "GET /" -Method "GET" -Path "/"

# Test 7: File Upload Endpoint (Empty - Should get 400)
Write-Host "`nPhase 5: File Upload Endpoint" -ForegroundColor Yellow
Write-Host "`n=== Testing: POST /api/ - Empty Upload ===" -ForegroundColor Cyan
Write-Host "URL: $baseUrl/api/" -ForegroundColor Gray
Write-Host "Method: POST (multipart/form-data)" -ForegroundColor Gray

try {
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    $formData = @()  # Empty upload
    $response = Invoke-WebRequest -Uri "$baseUrl/api/" -Method POST -Form @{} -SkipHttpErrorCheck -TimeoutSec 10
    
    $stopwatch.Stop()
    
    $uploadResult = @{
        Name = "POST /api/ - Empty Upload"
        Method = "POST"
        Path = "/api/"
        Status = "⚠️ WARNING"
        StatusCode = $response.StatusCode
        Duration = $stopwatch.ElapsedMilliseconds
        Response = if ($response.Content) { $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue } else { "No response body" }
        Error = $null
    }
    
    Write-Host "Status: HTTP $($response.StatusCode)" -ForegroundColor Yellow
    Write-Host "Duration: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Yellow
    
    $results += $uploadResult
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    $results += @{
        Name = "POST /api/ - Empty Upload"
        Method = "POST"
        Path = "/api/"
        Status = "❌ FAIL"
        StatusCode = 0
        Duration = 0
        Response = $null
        Error = $_.Exception.Message
    }
}

# Generate Report
Write-Host "`n" -ForegroundColor White
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  TEST RESULTS SUMMARY                      ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Magenta

$passed = @($results | Where-Object { $_.Status -like "✅*" })
$warnings = @($results | Where-Object { $_.Status -like "⚠️*" })
$failed = @($results | Where-Object { $_.Status -like "❌*" })

Write-Host "`nTotal Tests: $($results.Count)" -ForegroundColor White
Write-Host "✅ Passed: $($passed.Count)" -ForegroundColor Green
Write-Host "⚠️ Warnings: $($warnings.Count)" -ForegroundColor Yellow
Write-Host "❌ Failed: $($failed.Count)" -ForegroundColor Red

Write-Host "`n--- Detailed Results ---" -ForegroundColor White
$results | ForEach-Object {
    Write-Host "`n$($_.Status) $($_.Name)" -ForegroundColor White
    Write-Host "  Method: $($_.Method) $($_.Path)" -ForegroundColor Gray
    Write-Host "  Status Code: $($_.StatusCode)" -ForegroundColor Gray
    Write-Host "  Duration: $($_.Duration)ms" -ForegroundColor Gray
    if ($_.Response) {
        Write-Host "  Response: $($_.Response | ConvertTo-Json -Compress)" -ForegroundColor Gray
    }
    if ($_.Error) {
        Write-Host "  Error: $($_.Error)" -ForegroundColor Red
    }
}

# Save results to file
$resultsJson = $results | ConvertTo-Json -Depth 10
$resultsJson | Out-File -FilePath "backend_test_results.json" -Encoding UTF8
Write-Host "`n✅ Results saved to backend_test_results.json" -ForegroundColor Green

# Determine overall status
if ($failed.Count -eq 0 -and $passed.Count -gt 0) {
    Write-Host "`n🎉 ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ SOME TESTS FAILED - Review results above" -ForegroundColor Yellow
    exit 1
}
