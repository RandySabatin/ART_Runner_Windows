@echo off
title py Build Procedure!
echo Generating exe file....
echo ""


call Pyrcc5 -o icons.py icons.qrc

echo ""
echo Job Completed.
echo Press Enter to Exit.
pause