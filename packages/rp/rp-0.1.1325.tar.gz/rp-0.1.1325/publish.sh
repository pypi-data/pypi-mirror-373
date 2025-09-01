#Run "sh publish.sh" to publish a new version of rp from site packages
cd /Users/Ryan/PycharmProjects/QuickPython
echo Preparing to upload rp...

echo Removing the previous dist files...
#I'm providing the global paths of things I'm going to delete just to be safe...
rm -f /Users/Ryan/PycharmProjects/QuickPython/dist/*
echo Removing the outdated rp folder...
rm -rf /Users/Ryan/PycharmProjects/QuickPython/rp
echo Copying the rp folder from site packages into this directory...
cp -r /Library/Frameworks/Python.framework/Versions/3.5/lib/python3.5/site-packages/rp rp

python3 increment_version.py
cp version.py rp/version.py

echo "Updating list_of_modules.txt..."
python3 update_module_paths.py
echo 'Done updating list_of_modules.txt.'

echo running setup.py...
python3 setup.py sdist
echo uploading the distribution...
twine upload dist/*
echo ...done publishing rp! Version:
cat rp/version.py
