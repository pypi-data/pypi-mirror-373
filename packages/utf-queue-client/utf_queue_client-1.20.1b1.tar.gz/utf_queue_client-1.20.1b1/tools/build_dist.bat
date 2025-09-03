setlocal
call %~dp0setup_venv.bat

pushd ..

rd /s /q build
rd /s /q dist
rd /s /q utf_queue_client.egg-info

pip install wheel
pip install -r test-requirements.txt --index-url https://artifactory.silabs.net/artifactory/api/pypi/infrasw-python-virtual/simple
python -m build

popd
