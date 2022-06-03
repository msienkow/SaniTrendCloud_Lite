# Installer for SaniTrend™ Cloud Lite

# Set Execution Policy for Powershell Scripts
Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser




function DownloadGitHubRepository 
{ 
    param( 
       [Parameter(Mandatory=$False)] 
       [string] $Name, 
        
       [Parameter(Mandatory=$False)] 
       [string] $Author, 
        
       [Parameter(Mandatory=$False)] 
       [string] $Branch = "main", 
        
       [Parameter(Mandatory=$False)] 
       [string] $Location = "c:\temp" 
    ) 
    
    # Force to create a zip file 
    $ZipFile = "$location\SaniTrendCloud.zip" 
    New-Item $ZipFile -ItemType File -Force

    $RepositoryZipUrl = "https://github.com/msienkow/SaniTrendCloud_Lite/archive/refs/heads/main.zip"

    # download the zip 
    Write-Host 'Downloading SaniTrend Cloud Lite from Github. Please wait...'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-RestMethod -Uri $RepositoryZipUrl -OutFile $ZipFile
    Write-Host 'Download finished'

    #Extract Zip File
    Write-Host 'Starting unziping the GitHub Repository locally'
    Expand-Archive -Path $ZipFile -DestinationPath $location -Force
    Write-Host 'Unzip finished'
    
    # remove zip file
    Remove-Item -Path $ZipFile -Force 
}

function DownloadMicroServer
{ 
    param( 
       [Parameter(Mandatory=$False)] 
       [string] $Name, 
        
       [Parameter(Mandatory=$False)] 
       [string] $Author, 
        
       [Parameter(Mandatory=$False)] 
       [string] $Branch = "main", 
        
       [Parameter(Mandatory=$False)] 
       [string] $Location = "c:\temp" 
    ) 
    
    # Force to create a zip file 
    $ZipFile = "$location\microserver.zip" 
    New-Item $ZipFile -ItemType File -Force

    $RepositoryZipUrl = $serverDownload

    # download the zip 
    Write-Host 'Downloading Edge Microserver. Please wait...'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-RestMethod -Uri $RepositoryZipUrl -OutFile $ZipFile
    Write-Host 'Download finished'

    #Extract Zip File
    Write-Host 'Starting unzipping Edge Microserver...'
    Expand-Archive -Path $ZipFile -DestinationPath $location -Force
    Write-Host 'Unzip finished'
    
    # remove zip file
    Remove-Item -Path $ZipFile -Force 
}

Write-Host ""
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host ""
Write-Host " ____              _ _____                   _    ____ _                 _ "
Write-Host "/ ___|  __ _ _ __ (_)_   _|___ ___ _ __   __| |  / ___| | ___  _   _  __| |"
Write-Host "\___ \ / _  |  _ \| | | ||  __/ _ \  _ \ / _  | | |   | |/ _ \| | | |/ _  |"
Write-Host " ___) | (_| | | | | | | || | |  __/ | | | (_| | | |___| | (_) | |_| | (_| |"
Write-Host "|____/ \__,_|_| |_|_| |_||_|  \___|_| |_|\__,_|  \____|_|\___/ \__,_|\__,_|"
Write-Host ""
Write-Host ""
Write-Host ""
$wshell = New-Object -ComObject Wscript.Shell
$answer = $wshell.Popup("Do you want to install SaniTrend Cloud?",0,"SaniTrend Cloud Installer",64+4)

if ($answer -eq 6) {
    # Get SMI Number from user
    clear
    $choices  = '&Yes', '&No'
    $loop = $true
    DO {
        clear
        $SMINumber = Read-Host -Prompt 'Please Enter the SMI Number: '
        clear
        $title    = ''
        $question = 'Is ' + $SMINumber + ' the correct SMI number?'
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 0)
        if ($decision -eq 0) {
            $loop = $False
        }
    } While ($loop)

    # Get PLC IP Address
    clear
    $loop = $true
    DO {
        clear
        $PLCIP = Read-Host -Prompt 'Please enter the PLC IP Address: '
        clear
        $title    = ''
        $question = 'Is ' + $PLCIP + ' the correct PLC IP Address?'
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 0)
        if ($decision -eq 0) {
            $loop = $False
        }
    } While ($loop)

    # Get Application Key
    clear
    $loop = $true
    DO {
        clear
        $applicationKey = Read-Host -Prompt 'Please enter the application key: '
        clear
        $title    = ''
        $question = 'Is ' + $applicationKey + ' the correct application key?'
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 0)
        if ($decision -eq 0) {
            $loop = $False
        }
    } While ($loop)

    # Select Production or Development Server
    clear
    $loop = $true
    $serverDownload = 'https://sanimatic-dev.cloud.thingworx.com/Thingworx/FileRepositories/Downloads/microserver.zip?appKey=9f09c4f6-14f6-44b7-b90d-73a7e2f0e6ef'
    $server = 'sanimatic-dev.cloud.thingworx.com'
    DO {
        clear
        $title    = ''
        $question = 'Is this for the production server?'
        $decision = $Host.UI.PromptForChoice($title, $question, $choices, 0)
        if ($decision -eq 0) {
            $server = 'sanimatic-prod1.cloud.thingworx.com'
            $serverDownload = 'https://sanimatic-prod1.cloud.thingworx.com/Thingworx/FileRepositories/Downloads/microserver.zip?appKey=6234b184-ad06-470d-b648-55833f414343'
            $loop = $False
        } else {
            $loop = $False
        }
    } While ($loop)

    # Download Github Repository
    [String]$location = Split-Path -Parent $PSCommandPath
    DownloadGithubRepository -Location $location
    [String]$SaniTrendFolder = "$location\SaniTrendCloud_Lite-main"

    # Change directory to respository folder
    cd SaniTrendCloud_Lite-main

    # Download edge microserver
    DownloadMicroServer -Location $pwd
    
    # File cleanup
    Remove-Item .gitignore
    Remove-Item install.sh
    Remove-Item LICENSE
    Remove-Item README.md
    Remove-Item requirements.txt
    Remove-Item sanitrend.service
    Remove-Item SaniTrendCloud.ps1
    Remove-Item ssh.sh
    Remove-Item sudoers.sh
    Move-Item -Path $pwd\SaniTrendCloud.py -Destination $pwd\STC_Lite_Win
    Move-Item -Path $pwd\SaniTrend.py -Destination $pwd\STC_Lite_Win
    Move-Item -Path $pwd\SaniTrendConfig.json -Destination $pwd\STC_Lite_Win

    # SaniTrend Configuration File Setup
    (Get-Content $pwd\STC_Lite_Win\SaniTrendConfig.json) -replace 'PLC_IP_Address', $PLCIP | Set-Content $pwd\STC_Lite_Win\SaniTrendConfig.json
    (Get-Content $pwd\STC_Lite_Win\SaniTrendConfig.json) -replace 'ThingName', $SMINumber | Set-Content $pwd\STC_Lite_Win\SaniTrendConfig.json

    # Edge Microserver Configuration and Setup
    $encrypt = .\microserver\wsems -encrypt $applicationKey
    $keysplit = $encrypt.split()
    $key = $keysplit[3]
    (Get-Content $pwd\microserver\etc\config.json) -replace 'ApplicationKey', $key | Set-Content $pwd\microserver\etc\config.json
    (Get-Content $pwd\microserver\etc\config.json) -replace 'ServerURL', $server | Set-Content $pwd\microserver\etc\config.json
    (Get-Content $pwd\microserver\etc\config.json) -replace 'ThingName', $SMINumber | Set-Content $pwd\microserver\etc\config.json
    $WSEMS_NAME = "Thingworx_WSEMS"
    [String]$binPath = "$pwd\microserver\wsems.exe"
    [String]$configPath = "$pwd\microserver\etc\config.json"
    $service = Get-Service -Name $WSEMS_NAME -ErrorAction SilentlyContinue
    if($service -ne $null)
    {
        cmd /c "sc delete " + $WSEMS_NAME
    }
    cmd /c "sc create " + $WSEMS_NAME + " binPath= " + $binPath + " -service -cfg " + $configPath + " DispalyName= " + $WSEMS_NAME + " start= auto"
    net start $WSEMS_NAME

    
    




    # PowerShell.exe -NoProfile -Command "& {Start-Process PowerShell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""$pwd\PythonTask.ps1""' -Verb RunAs}"

} else {
    
    Exit

}

Exit