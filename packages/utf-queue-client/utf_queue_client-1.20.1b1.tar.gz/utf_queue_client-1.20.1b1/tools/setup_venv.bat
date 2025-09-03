pushd %~dp0..
if not exist venv (
   python -m venv venv
)
call venv\scripts\activate
pip install wheel
pip install -r test-requirements.txt
popd