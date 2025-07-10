@echo on

cd /d %~dp0\..\Archipelago
python BizHawkClient.py --connect Player1:None@localhost:38281
