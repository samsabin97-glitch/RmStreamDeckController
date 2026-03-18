# $port="COM3" # CHANGE THIS
# $baud=115200
# mode $port BAUD=$baud PARITY=n DATA=8 STOP=1 | Out-Null
# "STOP`n" | Out-File -Encoding ascii -NoNewline "\\.\$port"

$portName = "COM3"
$baudRate = 115200

$port = New-Object System.IO.Ports.SerialPort $portName, $baudRate, None, 8, one
$port.Open()
$port.WriteLine("STOP")
$port.Close()