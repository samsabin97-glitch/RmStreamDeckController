param(
[string]$Port = "COM3",
[ValidateSet("START","STOP","FWD","REV")]
[string]$Cmd = "STOP",
[int]$Baud = 115200
)

$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, "None", 8, "One"
$sp.NewLine = "`n"

try {
$sp.Open()

# Give the Arduino a moment if it auto-resets when the port opens
Start-Sleep -Milliseconds 1000

# Send command with newline (many sketches use readStringUntil('\n') or Serial.readLine style logic)
$sp.WriteLine($Cmd)

} finally {
if ($sp.IsOpen) { $sp.Close() }
$sp.Dispose()
}
