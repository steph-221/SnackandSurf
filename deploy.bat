@echo off
echo ===================================================
echo     Mise a jour du site Snack and Surf
echo ===================================================
echo.
echo 1. Preparation des fichiers...
git add .

echo 2. Validation des changements...
git commit -m "Mise a jour depuis le script auto"

echo 3. Envoi vers le serveur en ligne...
git push

echo.
echo ===================================================
echo Termine ! Le site se mettra a jour tout seul
echo dans quelques secondes.
echo ===================================================
pause
