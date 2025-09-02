import platform

get_os = platform.system()

ispc = get_os == "Windows"
ismac = get_os == "Darwin"
islinux = get_os == "Linux"
