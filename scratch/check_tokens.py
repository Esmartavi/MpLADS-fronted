import subprocess

cmd = r'''
$e = $null
$t = $null
[System.Management.Automation.Language.Parser]::ParseFile("start.ps1", [ref]$t, [ref]$e) | Out-Null
foreach ($tok in $t) {
    if ($tok.Kind -eq "StringExpandable" -or $tok.Kind -eq "StringLiteral") {
        if ($tok.Extent.StartLineNumber -gt 315) {
            Write-Host "Line" $tok.Extent.StartLineNumber "-" $tok.Extent.EndLineNumber ":" $tok.Extent.Text
        }
    }
}
if ($e) {
    Write-Host "ERRORS:"
    $e | ForEach-Object { Write-Host $_.Extent.StartLineNumber $_.Extent.StartColumnNumber $_.Message }
}
'''

res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)
