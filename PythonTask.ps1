Add-Type -AssemblyName PresentationCore,PresentationFramework
$msgBody = "The next step will install the SaniTrend Cloud Windows service."
[System.Windows.MessageBox]::Show($msgBody,"Important!", 0,48)

#Create Scheduled Task variables
$sanitrendPath = "$PSScriptRoot\SaniTrendCloud_Lite-main"
$batPath = "$sanitrendPath\sanitrend.bat"
$pythonPath = "$sanitrendPath\python.exe"
$sanitrendFile = "$sanitrendPath\SaniTrend.py" 

New-Item $batPath
Set-Content -Path $batPath -value "call $pythonPath $sanitrendFile"
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host "Creating SaniTrend Cloud Service File..."

Set-Location -Path $sanitrendPath
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host "Installing SaniTrend Cloud Service..."
.\nssm.exe install SaniTrendCloud "$batPath"

Write-Host ""
Write-Host ""
Write-Host ""
Write-Host "Starting SaniTrend Cloud Service..."
.\nssm.exe start SaniTrendCloud

Write-Host ""
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host "SaniTrend Cloud Installation Complete."


$msgBody = "SaniTrend Cloud installation complete."


[System.Windows.MessageBox]::Show($msgBody,"SaniTrend Cloud Installer", 0,0)
Set-ExecutionPolicy Restricted -Scope CurrentUser
# Restart-Computer -Force
Exit