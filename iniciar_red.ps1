param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Ip,

    [Parameter(Position = 1)]
    [ValidateRange(1, 65535)]
    [int]$Port = 8000
)

$parsedAddress = $null
if (
    -not [System.Net.IPAddress]::TryParse($Ip, [ref]$parsedAddress) -or
    $parsedAddress.AddressFamily -ne [System.Net.Sockets.AddressFamily]::InterNetwork
) {
    throw "Ingresá una dirección IPv4 válida. Ejemplo: .\iniciar_red.ps1 192.168.1.25"
}

Set-Location -LiteralPath $PSScriptRoot

# Estas variables existen solamente mientras se ejecuta este servidor.
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1,testserver,$Ip"
$env:PUBLIC_BASE_URL = "http://${Ip}:$Port"

Write-Host ""
Write-Host "AmpereStore disponible en: $env:PUBLIC_BASE_URL" -ForegroundColor Green
Write-Host "Los enlaces enviados por email usarán esa misma dirección."
Write-Host "Para detener el servidor presioná Ctrl+C."
Write-Host ""

python manage.py runserver "0.0.0.0:$Port"
