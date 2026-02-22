# $port="COM3" # CHANGE THIS to match com port on PC
# $baud=115200
# mode $port BAUD=$baud PARITY=n DATA=8 STOP=1 | Out-Null
# "FWD 200`n" | Out-File -Encoding ascii -NoNewline "\\.\$port"d

$portName = "COM3"
$baudRate = 115200

# $port = New-Object System.IO.Ports.SerialPort $portName, $baudRate, None, 8, one
# $port.Open()
# $port.WriteLine("FWD 200")
# $port.Close()

$port = New-Object System.IO.Ports.SerialPort
$port.PortName = $portName
$port.BaudRate = $baudRate
$port.Parity = [System.IO.Ports.Parity]::None
$port.DataBits = 8
$port.StopBits = [System.IO.Ports.StopBits]::One

$port.Open()
Start-Sleep -Milliseconds 200
$port.WriteLine("FWD")
Start-Sleep -Milliseconds 100
$port.Close()