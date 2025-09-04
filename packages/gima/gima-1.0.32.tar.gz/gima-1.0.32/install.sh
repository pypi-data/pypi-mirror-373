#rm gim
#pyinstaller --onefile gim.py
#cp ./dist/gim .
#rm -rf build dist gim.spec

#rm -rf build dist gim.egg-info gima.egg-info
#python setup.py sdist bdist_wheel
#cd dist
#twine upload *
#cd ..

python3 -m build
twine upload dist/*
pip install gima --break-system-packages --upgrade
pip install gima --break-system-packages --upgrade