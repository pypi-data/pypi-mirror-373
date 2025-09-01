## Temporary pycrysfml installation process (pyenv python 3.12, macOS 14, Apple Silicon):

- Install from local wheel
  ```bash
  pip install deps/pycrysfml-0.1.6-py312-none-macosx_14_0_arm64.whl
  ```
- Try to import the module
  ```bash
  python -c "from pycrysfml import cfml_py_utilities"
  ```
- If previous step failed, check the linked libraries
  ```bash
  otool -L .venv/lib/python3.12/site-packages/pycrysfml/crysfml08lib.so
  ```
- If the library is linked to the wrong Python version, you can fix it with:
  ```bash
  install_name_tool -change `python3-config --prefix`/Python `python3-config --prefix`/lib/libpython3.12.dylib .venv/lib/python3.12/site-packages/pycrysfml/crysfml08lib.so
  ```
- Check again the linked Python library
  ```bash
  otool -L .venv/lib/python3.12/site-packages/pycrysfml/crysfml08lib.so
  ```
- Try to import the module again
  ```bash
  python -c "from pycrysfml import cfml_py_utilities"
  ```
