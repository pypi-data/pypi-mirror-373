setlocal
call %~dp0setup_venv.bat

:: NOTE: need to create .pypirc in HOME directory containing
:: repository details... See https://packaging.python.org/specifications/pypirc/

pushd %~dp0..

if not exist dist (
    echo Dist does not exist -- run build_dist.bat first
)

twine upload --repository testpypi dist/*

popd