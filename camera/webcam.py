import platform

_os = platform.system()

if _os == "Linux":

    from .backend.linux import backend

elif _os == "Windows":

    from .backend.windows import backend

else:

    raise RuntimeError(
        f"Unsupported operating system: {_os}"
    )


open_camera = backend.open_camera
get_camera_list = backend.get_camera_list
get_current_camera = backend.get_current_camera
read = backend.read
release = backend.release