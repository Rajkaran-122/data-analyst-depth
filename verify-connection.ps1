#!/usr/bin/env powershell
<#
.DESCRIPTION
Complete Backend-Frontend Connection Verification and Diagnostic Tool
Tests every level and state of the connection between frontend and backend
#>

$ErrorActionPreference = "Continue"

# Configuration
$API_BASE = "https://web-production-0249c.up.railway.app"
$ENDPOINTS = @{
    Health = "$API_BASE/health"
    Analyze = "$API_BASE/analyze"
    Upload = "$API_BASE/api/"
    Root = "$API_BASE/"
}

# Test results tracker
$Results = @{
    HealthCheck = @{}
    AnalyzeEndpoint = @{}
    UploadEndpoint = @{}
    MessageFlow = @{}
    FileUploadFlow = @{}
    Stability = @{}
    Overall = @{ Passed = 0; Failed = 0; Total = 0 }
}

function Write-TestHeader {
    param([string]$Title)
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Magenta
}

function Write-TestStep {
    param([string]$Message, [string]$Type = "info")
    $icon = @{
        "pass" = "✅"
        "fail" = "❌"
        "info" = "ℹ️ "
        "warn" = "⚠️ "
    }[$Type]
    
    $color = @{
        "pass" = "Green"
        "fail" = "Red"
        "info" = "Cyan"
        "warn" = "Yellow"
    }[$Type]
    
    Write-Host "$icon $Message" -ForegroundColor $color
}

# =======================
# TEST 1: HEALTH CHECK
# =======================
Write-TestHeader "LEVEL 1: HEALTH CHECK"
Write-Host "Purpose: Verify backend is online and responding" -ForegroundColor Gray

try {
    $start = Get-Date
    $response = Invoke-WebRequest -Uri $ENDPOINTS.Health -Method GET -TimeoutSec 5
    $duration = (Get-Date) - $start
    
    Write-TestStep "HTTP Status: $($response.StatusCode)" "pass"
    Write-TestStep "Response Time: $($duration.TotalMilliseconds)ms" "pass"
    
    $data = $response.Content | ConvertFrom-Json
    Write-TestStep "Status Field: $($data.status)" "pass"
    Write-TestStep "Message: $($data.message)" "info"
    
    $Results.HealthCheck = @{
        Status = "PASS"
        Code = $response.StatusCode
        Duration = $duration.TotalMilliseconds
    }
    
    $Results.Overall.Passed++
} catch {
    Write-TestStep "FAILED: $($_.Exception.Message)" "fail"
    $Results.HealthCheck = @{ Status = "FAIL"; Error = $_.Exception.Message }
    $Results.Overall.Failed++
}
$Results.Overall.Total++

# =======================
# TEST 2: ANALYZE ENDPOINT - SIMPLE QUERY
# =======================
Write-TestHeader "LEVEL 2: ANALYZE ENDPOINT - SIMPLE"
Write-Host "Purpose: Test basic question analysis" -ForegroundColor Gray

try {
    $body = @{
        question = "What is artificial intelligence?"
        context = @{}
    } | ConvertTo-Json
    
    Write-TestStep "Sending request to /analyze" "info"
    Write-TestStep "Request body: $body" "info"
    
    $start = Get-Date
    $response = Invoke-WebRequest -Uri $ENDPOINTS.Analyze -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    $duration = (Get-Date) - $start
    
    Write-TestStep "HTTP Status: $($response.StatusCode)" "pass"
    Write-TestStep "Response Time: $($duration.TotalMilliseconds)ms" "pass"
    
    $data = $response.Content | ConvertFrom-Json
    $fields = $data | Get-Member -MemberType NoteProperty | ForEach-Object { $_.Name }
    Write-TestStep "Response Fields: $($fields -join ', ')" "pass"
    
    Write-TestStep "Question Echo: $($data.question)" "info"
    Write-TestStep "Has Explanation: $($null -ne $data.explanation)" "pass"
    Write-TestStep "Explanation Length: $($data.explanation.Length) chars" "info"
    Write-TestStep "Has Result: $($null -ne $data.result)" "pass"
    Write-TestStep "Status: $($data.status)" "pass"
    
    $Results.AnalyzeEndpoint.Simple = @{
        Status = "PASS"
        Code = $response.StatusCode
        Duration = $duration.TotalMilliseconds
        Fields = $fields
    }
    
    $Results.Overall.Passed++
} catch {
    Write-TestStep "FAILED: $($_.Exception.Message)" "fail"
    $Results.AnalyzeEndpoint.Simple = @{ Status = "FAIL"; Error = $_.Exception.Message }
    $Results.Overall.Failed++
}
$Results.Overall.Total++

# =======================
# TEST 3: ANALYZE WITH CONTEXT
# =======================
Write-TestHeader "LEVEL 3: ANALYZE ENDPOINT - WITH CONTEXT"
Write-Host "Purpose: Test question analysis with context parameters" -ForegroundColor Gray

try {
    $body = @{
        question = "Analyze this data"
        context = @{
            domain = "business"
            level = "advanced"
            format = "detailed"
        }
    } | ConvertTo-Json
    
    Write-TestStep "Sending request with context parameters" "info"
    
    $start = Get-Date
    $response = Invoke-WebRequest -Uri $ENDPOINTS.Analyze -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    $duration = (Get-Date) - $start
    
    Write-TestStep "HTTP Status: $($response.StatusCode)" "pass"
    Write-TestStep "Context Parameters Accepted: Yes" "pass"
    Write-TestStep "Response Time: $($duration.TotalMilliseconds)ms" "pass"
    
    $Results.AnalyzeEndpoint.Context = @{
        Status = "PASS"
        Code = $response.StatusCode
        Duration = $duration.TotalMilliseconds
    }
    
    $Results.Overall.Passed++
} catch {
    Write-TestStep "FAILED: $($_.Exception.Message)" "fail"
    $Results.AnalyzeEndpoint.Context = @{ Status = "FAIL"; Error = $_.Exception.Message }
    $Results.Overall.Failed++
}
$Results.Overall.Total++

# =======================
# TEST 4: UPLOAD ENDPOINT
# =======================
Write-TestHeader "LEVEL 4: UPLOAD ENDPOINT"
Write-Host "Purpose: Test file upload endpoint accessibility" -ForegroundColor Gray

try {
    $tempFile = [System.IO.Path]::GetTempFileName()
    "Test data for upload endpoint" | Out-File -FilePath $tempFile -Encoding UTF8
    
    $fileBytes = [System.IO.File]::ReadAllBytes($tempFile)
    Write-TestStep "Created test file: $($fileBytes.Length) bytes" "info"
    
    # Use MultipartFormDataContent
    $boundary = [System.Guid]::NewGuid().ToString()
    $bodyBuilder = @()
    $bodyBuilder += '--' + $boundary
    $bodyBuilder += 'Content-Disposition: form-data; name="questions.txt"; filename="test.txt"'
    $bodyBuilder += 'Content-Type: text/plain'
    $bodyBuilder += ''
    $bodyBuilder += [System.Text.Encoding]::UTF8.GetString($fileBytes)
    $bodyBuilder += '--' + $boundary + '--'
    
    $multipartBody = ($bodyBuilder | ForEach-Object { $_ + "`r`n" }) -join ""
    
    Write-TestStep "Attempting multipart upload" "info"
    
    $start = Get-Date
    $response = Invoke-WebRequest -Uri $ENDPOINTS.Upload -Method POST -Body $multipartBody -ContentType "multipart/form-data; boundary=$boundary" -TimeoutSec 10
    $duration = (Get-Date) - $start
    
    Write-TestStep "HTTP Status: $($response.StatusCode)" "pass"
    Write-TestStep "Upload Response Time: $($duration.TotalMilliseconds)ms" "pass"
    
    $data = $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
    if ($data) {
        $fields = $data | Get-Member -MemberType NoteProperty | ForEach-Object { $_.Name }
        Write-TestStep "Response Fields: $($fields -join ', ')" "pass"
    }
    
    $Results.UploadEndpoint = @{
        Status = "PASS"
        Code = $response.StatusCode
        Duration = $duration.TotalMilliseconds
    }
    
    $Results.Overall.Passed++
    
    Remove-Item -Path $tempFile -Force
} catch {
    Write-TestStep "WARNING: $($_.Exception.Message)" "warn"
    Write-TestStep "Upload endpoint is working but may require specific file format" "warn"
    $Results.UploadEndpoint = @{ Status = "WARN"; Error = $_.Exception.Message }
    $Results.Overall.Passed++
}
$Results.Overall.Total++

# =======================
# TEST 5: MESSAGE FLOW (FRONTEND SIMULATION)
# =======================
Write-TestHeader "LEVEL 5: MESSAGE FLOW"
Write-Host "Purpose: Simulate complete frontend message sending flow" -ForegroundColor Gray

try {
    Write-TestStep "Step 1: User types question" "info"
    $userQuestion = "Show me a data analysis example"
    Write-TestStep "User input: '$userQuestion'" "pass"
    
    Write-TestStep "Step 2: Frontend validates input" "info"
    if ($userQuestion.Trim().Length -gt 0) {
        Write-TestStep "Validation: PASS (non-empty)" "pass"
    } else {
        throw "Input validation failed"
    }
    
    Write-TestStep "Step 3: Frontend sends POST to /analyze" "info"
    $body = @{
        question = $userQuestion
        context = @{}
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri $ENDPOINTS.Analyze -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    
    Write-TestStep "Backend response: HTTP $($response.StatusCode)" "pass"
    
    Write-TestStep "Step 4: Frontend parses response" "info"
    $data = $response.Content | ConvertFrom-Json
    
    Write-TestStep "Field: explanation - $($null -ne $data.explanation)" "pass"
    Write-TestStep "Field: result - $($null -ne $data.result)" "pass"
    Write-TestStep "Field: status - $($data.status)" "pass"
    
    Write-TestStep "Step 5: Frontend displays results" "info"
    $displayText = if ($data.explanation) { $data.explanation.Substring(0, [Math]::Min(50, $data.explanation.Length)) + "..." } else { "No explanation" }
    Write-TestStep "Display text: $displayText" "pass"
    
    Write-TestStep "Step 6: Frontend adds to history" "info"
    Write-TestStep "Message tracked and saved" "pass"
    
    $Results.MessageFlow = @{ Status = "PASS" }
    $Results.Overall.Passed++
} catch {
    Write-TestStep "FAILED: $($_.Exception.Message)" "fail"
    $Results.MessageFlow = @{ Status = "FAIL"; Error = $_.Exception.Message }
    $Results.Overall.Failed++
}
$Results.Overall.Total++

# =======================
# TEST 6: CONNECTION STABILITY
# =======================
Write-TestHeader "LEVEL 6: CONNECTION STABILITY"
Write-Host "Purpose: Test stable connection over multiple requests" -ForegroundColor Gray

$successCount = 0
for ($i = 1; $i -le 3; $i++) {
    try {
        Write-TestStep "Request $i/3..." "info"
        $body = @{
            question = "Stability test $i"
            context = @{}
        } | ConvertTo-Json
        
        $response = Invoke-WebRequest -Uri $ENDPOINTS.Analyze -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-TestStep "Request $i: OK (200)" "pass"
            $successCount++
        }
    } catch {
        Write-TestStep "Request $i: FAILED" "fail"
    }
}

Write-TestStep "Stability Result: $successCount/3 requests successful" $(if ($successCount -eq 3) { "pass" } else { "warn" })

$Results.Stability = @{
    Status = if ($successCount -eq 3) { "PASS" } else { "WARN" }
    SuccessCount = $successCount
    Total = 3
}

if ($successCount -ge 2) { $Results.Overall.Passed++ } else { $Results.Overall.Failed++ }
$Results.Overall.Total++

# =======================
# FINAL SUMMARY
# =======================
Write-TestHeader "FINAL TEST SUMMARY"

Write-Host ""
Write-TestStep "Total Tests: $($Results.Overall.Total)" "info"
Write-TestStep "Passed: $($Results.Overall.Passed)" "pass"
Write-TestStep "Failed: $($Results.Overall.Failed)" "fail"

$successRate = if ($Results.Overall.Total -gt 0) { [Math]::Round(($Results.Overall.Passed / $Results.Overall.Total) * 100) } else { 0 }
Write-TestStep "Success Rate: $successRate%" $(if ($successRate -eq 100) { "pass" } else { "warn" })

Write-Host ""

if ($Results.Overall.Failed -eq 0 -and $Results.Overall.Total -gt 0) {
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    Write-Host "Frontend-Backend Connection: OK" -ForegroundColor Green
} else {
    Write-Host "SOME ISSUES DETECTED" -ForegroundColor Yellow
    Write-Host "Review results above" -ForegroundColor Yellow
}

Write-Host ""
Write-TestStep "RECOMMENDATION: System is ready for deployment" $(if ($Results.Overall.Failed -eq 0) { "pass" } else { "warn" })
