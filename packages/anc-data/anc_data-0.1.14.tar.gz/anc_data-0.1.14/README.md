# anc_data

## build & upload pip

Bump up version number in pyproject.toml

`pip install build`

to clean up older builds, run `rm dist/*`

then `python -m build`

`pip install twine`

`twine upload dist/*` or pick specific versions to upload

You will be prompted for your PyPI username and password (token). Refer to the email sent to dev_infra@anuttacon.com if you have access to it.

