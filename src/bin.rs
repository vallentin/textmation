
use std::env;
use std::process;

use cpython::{
    Python, PythonObject,
    ObjectProtocol,
    PyClone,
    PyResult,
    exc::SystemExit,
    PyString,
    PyList, PythonObjectWithCheckedDowncast,
};

fn main() {
    let gil = Python::acquire_gil();
    let py = gil.python();

    if let Err(err) = run(py) {
        if let Some(err_val) = err.clone_ref(py).pvalue {
            if let Ok(sys_exit) = SystemExit::downcast_from(py, err_val) {
                let sys_exit = sys_exit.into_object();

                let code = sys_exit.getattr(py, "code").unwrap();
                let code = code.extract::<i32>(py).unwrap();

                process::exit(code);
            }
        }

        err.print(py);

        process::exit(-1);
    }
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
