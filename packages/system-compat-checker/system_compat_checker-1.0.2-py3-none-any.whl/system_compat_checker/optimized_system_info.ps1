# Optimized System Information Collection Script for Windows
# This script collects comprehensive system information and outputs it as JSON

# Function to safely get WMI information
function Get-SafeWMIObject {
    param(
        [string]$ClassName,
        [string]$Property = $null
    )
    
    try {
        $obj = Get-WmiObject -Class $ClassName -ErrorAction Stop
        if ($Property) {
            return $obj.$Property
        }
        return $obj
    }
    catch {
        return $null
    }
}

# Function to safely get CIM information
function Get-SafeCIMInstance {
    param(
        [string]$ClassName,
        [string]$Property = $null
    )
    
    try {
        $obj = Get-CimInstance -ClassName $ClassName -ErrorAction Stop
        if ($Property) {
            return $obj.$Property
        }
        return $obj
    }
    catch {
        return $null
    }
}

# Function to format bytes to human readable
function Format-Bytes {
    param([long]$Bytes)
    
    if ($Bytes -eq 0) { return "0 B" }
    
    $sizes = @("B", "KB", "MB", "GB", "TB")
    $index = [Math]::Floor([Math]::Log($Bytes, 1024))
    $size = [Math]::Round($Bytes / [Math]::Pow(1024, $index), 2)
    
    return "$size $($sizes[$index])"
}

# Initialize the system information object
$systemInfo = @{}

# Operating System Information
try {
    $os = Get-SafeCIMInstance -ClassName "Win32_OperatingSystem"
    if ($os) {
        $systemInfo.OperatingSystem = @{
            Name = $os.Caption
            Version = $os.Version
            Architecture = $os.OSArchitecture
            BuildNumber = $os.BuildNumber
            InstallDate = $os.InstallDate
            LastBootUpTime = $os.LastBootUpTime
            TotalVisibleMemorySize = if ($os.TotalVisibleMemorySize) { Format-Bytes ($os.TotalVisibleMemorySize * 1KB) } else { "Unknown" }
            FreePhysicalMemory = if ($os.FreePhysicalMemory) { Format-Bytes ($os.FreePhysicalMemory * 1KB) } else { "Unknown" }
        }
    } else {
        $systemInfo.OperatingSystem = @{
            Name = $env:OS
            Version = [System.Environment]::OSVersion.Version.ToString()
            Architecture = [System.Environment]::GetEnvironmentVariable("PROCESSOR_ARCHITECTURE")
        }
    }
}
catch {
    $systemInfo.OperatingSystem = @{
        Name = "Windows (Detection Failed)"
        Version = "Unknown"
        Architecture = "Unknown"
    }
}

# CPU Information
try {
    $cpu = Get-SafeCIMInstance -ClassName "Win32_Processor" | Select-Object -First 1
    if ($cpu) {
        $systemInfo.CPU = @{
            Name = $cpu.Name
            Manufacturer = $cpu.Manufacturer
            Architecture = $cpu.Architecture
            NumberOfCores = $cpu.NumberOfCores
            NumberOfLogicalProcessors = $cpu.NumberOfLogicalProcessors
            MaxClockSpeed = if ($cpu.MaxClockSpeed) { "$($cpu.MaxClockSpeed) MHz" } else { "Unknown" }
            CurrentClockSpeed = if ($cpu.CurrentClockSpeed) { "$($cpu.CurrentClockSpeed) MHz" } else { "Unknown" }
            L2CacheSize = if ($cpu.L2CacheSize) { Format-Bytes ($cpu.L2CacheSize * 1KB) } else { "Unknown" }
            L3CacheSize = if ($cpu.L3CacheSize) { Format-Bytes ($cpu.L3CacheSize * 1KB) } else { "Unknown" }
        }
    } else {
        $systemInfo.CPU = @{
            Name = $env:PROCESSOR_IDENTIFIER
            Manufacturer = "Unknown"
            NumberOfCores = $env:NUMBER_OF_PROCESSORS
        }
    }
}
catch {
    $systemInfo.CPU = @{
        Name = "CPU (Detection Failed)"
        Manufacturer = "Unknown"
        NumberOfCores = "Unknown"
    }
}

# Memory Information
try {
    $memory = Get-SafeCIMInstance -ClassName "Win32_PhysicalMemory"
    if ($memory) {
        $totalMemory = ($memory | Measure-Object -Property Capacity -Sum).Sum
        $memoryModules = $memory | ForEach-Object {
            @{
                Capacity = Format-Bytes $_.Capacity
                Speed = if ($_.Speed) { "$($_.Speed) MHz" } else { "Unknown" }
                Manufacturer = $_.Manufacturer
                PartNumber = $_.PartNumber
                SerialNumber = $_.SerialNumber
            }
        }
        
        $systemInfo.Memory = @{
            TotalPhysicalMemory = Format-Bytes $totalMemory
            NumberOfModules = $memory.Count
            Modules = $memoryModules
        }
    } else {
        # Fallback using ComputerInfo
        try {
            $computerInfo = Get-ComputerInfo -Property TotalPhysicalMemory -ErrorAction Stop
            $systemInfo.Memory = @{
                TotalPhysicalMemory = Format-Bytes $computerInfo.TotalPhysicalMemory
                NumberOfModules = "Unknown"
            }
        }
        catch {
            $systemInfo.Memory = @{
                TotalPhysicalMemory = "Unknown"
                NumberOfModules = "Unknown"
            }
        }
    }
}
catch {
    $systemInfo.Memory = @{
        TotalPhysicalMemory = "Memory (Detection Failed)"
        NumberOfModules = "Unknown"
    }
}

# Graphics Information
try {
    $graphics = Get-SafeCIMInstance -ClassName "Win32_VideoController"
    if ($graphics) {
        $graphicsCards = $graphics | Where-Object { $_.Name -notlike "*Basic*" -and $_.Name -notlike "*Generic*" } | ForEach-Object {
            @{
                Name = $_.Name
                AdapterRAM = if ($_.AdapterRAM) { Format-Bytes $_.AdapterRAM } else { "Unknown" }
                DriverVersion = $_.DriverVersion
                VideoProcessor = $_.VideoProcessor
            }
        }
        
        $systemInfo.Graphics = @{
            Cards = $graphicsCards
        }
    } else {
        $systemInfo.Graphics = @{
            Cards = @(@{ Name = "Graphics (Detection Failed)" })
        }
    }
}
catch {
    $systemInfo.Graphics = @{
        Cards = @(@{ Name = "Graphics (Detection Failed)" })
    }
}

# Storage Information
try {
    # Get logical disks (partitions/volumes) for usage information
    $logicalDisks = Get-SafeCIMInstance -ClassName "Win32_LogicalDisk"
    # Get physical disks for hardware information
    $physicalDisks = Get-SafeCIMInstance -ClassName "Win32_DiskDrive"
    
    $partitionInfo = @()
    
    if ($logicalDisks) {
        # Process logical disks for partition information
        $logicalDisks | ForEach-Object {
            if ($_.Size -and $_.Size -gt 0) {
                $totalBytes = [long]$_.Size
                $freeBytes = [long]$_.FreeSpace
                $usedBytes = $totalBytes - $freeBytes
                $percentUsed = if ($totalBytes -gt 0) { ($usedBytes / $totalBytes) * 100 } else { 0 }
                
                # Try to get the physical disk model for this logical disk
                $deviceModel = "Unknown"
                if ($physicalDisks) {
                    # For simplicity, use the first physical disk model
                    # In a more complex scenario, you'd map logical to physical disks
                    $firstDisk = $physicalDisks | Select-Object -First 1
                    if ($firstDisk -and $firstDisk.Model) {
                        $deviceModel = $firstDisk.Model
                    }
                }
                
                $partitionInfo += @{
                    device = $deviceModel
                    mountpoint = $_.DeviceID
                    total = $totalBytes
                    used = $usedBytes
                    free = $freeBytes
                    percent_used = $percentUsed
                    filesystem = $_.FileSystem
                    volume_label = $_.VolumeName
                }
            }
        }
    }
    
    # If no logical disks found, fall back to physical disk info
    if ($partitionInfo.Count -eq 0 -and $physicalDisks) {
        $physicalDisks | ForEach-Object {
            $partitionInfo += @{
                device = $_.Model
                mountpoint = "N/A"
                total = if ($_.Size) { [long]$_.Size } else { 0 }
                used = 0
                free = if ($_.Size) { [long]$_.Size } else { 0 }
                percent_used = 0
                filesystem = "Unknown"
                volume_label = "Unknown"
            }
        }
    }
    
    $systemInfo.Storage = @{
        partitions = $partitionInfo
    }
}
catch {
    $systemInfo.Storage = @{
        partitions = @(@{ 
            device = "Storage (Detection Failed)"
            mountpoint = "N/A"
            total = 0
            used = 0
            free = 0
            percent_used = 0
        })
    }
}

# Network Information
try {
    $network = Get-SafeCIMInstance -ClassName "Win32_NetworkAdapter" | Where-Object { $_.NetConnectionStatus -eq 2 -and $_.AdapterType -notlike "*Loopback*" }
    if ($network) {
        $networkAdapters = $network | ForEach-Object {
            @{
                Name = $_.Name
                MACAddress = $_.MACAddress
                Speed = if ($_.Speed) { Format-Bytes $_.Speed } else { "Unknown" }
                AdapterType = $_.AdapterType
            }
        }
        
        $systemInfo.Network = @{
            Adapters = $networkAdapters
        }
    } else {
        $systemInfo.Network = @{
            Adapters = @(@{ Name = "Network (Detection Failed)" })
        }
    }
}
catch {
    $systemInfo.Network = @{
        Adapters = @(@{ Name = "Network (Detection Failed)" })
    }
}

# System Information
try {
    $computer = Get-SafeCIMInstance -ClassName "Win32_ComputerSystem"
    if ($computer) {
        $systemInfo.System = @{
            Manufacturer = $computer.Manufacturer
            Model = $computer.Model
            SystemType = $computer.SystemType
            Domain = $computer.Domain
            Workgroup = $computer.Workgroup
            UserName = $computer.UserName
        }
    } else {
        $systemInfo.System = @{
            Manufacturer = "Unknown"
            Model = "Unknown"
            SystemType = "Unknown"
        }
    }
}
catch {
    $systemInfo.System = @{
        Manufacturer = "System (Detection Failed)"
        Model = "Unknown"
        SystemType = "Unknown"
    }
}

# Convert to JSON and output
try {
    $jsonOutput = $systemInfo | ConvertTo-Json -Depth 10 -Compress
    Write-Output $jsonOutput
}
catch {
    # Fallback minimal JSON output
    $fallbackInfo = @{
        OperatingSystem = @{ Name = "Windows"; Version = "Unknown" }
        CPU = @{ Name = "Unknown CPU" }
        Memory = @{ TotalPhysicalMemory = "Unknown" }
        Error = "JSON conversion failed"
    }
    Write-Output ($fallbackInfo | ConvertTo-Json -Compress)
}