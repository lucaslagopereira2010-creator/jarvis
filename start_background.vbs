' ============================================================
'  Arranca JARVIS en SEGUNDO PLANO, sin ventana de consola.
'  Haz doble clic para iniciarlo, o pon un acceso directo a
'  este archivo en la carpeta de Inicio para que arranque solo
'  al encender el ordenador (ejecuta:  shell:startup).
' ============================================================
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")

carpeta = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = carpeta

' Usa el Python del entorno virtual si existe; si no, el del sistema.
If fso.FileExists(carpeta & "\.venv\Scripts\pythonw.exe") Then
    py = carpeta & "\.venv\Scripts\pythonw.exe"
Else
    py = "pythonw.exe"
End If

' El 0 final oculta la ventana; False = no esperar a que termine.
sh.Run """" & py & """ """ & carpeta & "\jarvis_clap.py""", 0, False
