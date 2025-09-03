@setlocal
@set LIBTBX_PREFIX=%~dp0
@set LIBTBX_PREFIX=%LIBTBX_PREFIX:~0,-1%
@for %%F in ("%LIBTBX_PREFIX%") do @set LIBTBX_PREFIX=%%~dpF
@set LIBTBX_PREFIX=%LIBTBX_PREFIX:~0,-1%
@set LIBTBX_BUILD=%LIBTBX_PREFIX%\..\Library\share\cctbx
@set LIBTBX_DISPATCHER_NAME=%~nx0
@set LIBTBX_PYEXE=python.exe
@"%LIBTBX_PYEXE%" "%~dp0\..\..\..\mmtbx\command_line\distance_difference.py" %*
