Set WshShell = CreateObject("WScript.Shell")
Set args = WScript.Arguments

slot = "morning"
If args.Count > 0 Then
    slot = args(0)
End If

projectDir = "D:\Gemini\AI_Agent_FB_Page_Maira"
cmd = Chr(34) & projectDir & "\run_slot.bat" & Chr(34) & " " & slot

' Run hidden (0) and wait for completion (True)
WshShell.Run cmd, 0, True
