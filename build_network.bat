@echo off
echo Building SUMO Network for Phnom Penh Intersection...
"C:\Program Files (x86)\Eclipse\Sumo\bin\netconvert.exe" --node-files phnom_penh.nod.xml --edge-files phnom_penh.edg.xml -o phnom_penh.net.xml
echo Done! Please ensure you have SUMO installed in your PATH.
pause
