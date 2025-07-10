@echo on

cd /d %~dp0\..\Archipelago
python -m worlds.crash2.Crash2Client --connect Player1:None@localhost:38281
