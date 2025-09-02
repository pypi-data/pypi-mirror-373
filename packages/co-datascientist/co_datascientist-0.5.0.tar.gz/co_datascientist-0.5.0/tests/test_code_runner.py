from co_datascientist.workflow_runner import _get_python_libraries


def test_get_python_libraries():
    # dont crash plz
    libraries = _get_python_libraries("python")
    print(libraries)
