$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)

Start-Process "http://localhost:8501"

.\python\python.exe main.py