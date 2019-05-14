
use std::env;

use cpython::{
    Python, PythonObject,
    PyResult,
    PyString,
    PyList, PythonObjectWithCheckedDowncast,
};

fn main() {
    let gil = Python::acquire_gil();
    let py = gil.python();

    run(py).unwrap();
}

fn run(py: Python) -> PyResult<()> {
    let current_dir = env::current_dir().unwrap();
    let current_dir = PyString::new(py, current_dir.to_str().unwrap());

    let sys = py.import("sys")?;
    let path = PyList::downcast_from(py, sys.get(py, "path")?)?;
    path.insert_item(py, 0, current_dir.into_object());

    let mut argv = vec!();

    for arg in env::args() {
        argv.push(PyString::new(py, &arg).into_object());
    }

    let argv = PyList::new(py, &argv);
    sys.dict(py).set_item(py, "argv", argv)?;

    let textmation = py.import("textmation.__main__")?;
    textmation.call(py, "main", cpython::NoArgs, None)?;

    Ok(())
}
