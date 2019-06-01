
use std::env;
use std::process;

#[macro_use]
extern crate cpython;

use cpython::{
    Python, PythonObject,
    ObjectProtocol,
    PyClone,
    PyResult,
    exc::SystemExit,
    PyString,
    PyList, PythonObjectWithCheckedDowncast,
    PyDict,
    PyModule,
};

mod rect;
mod drawing;
mod rasterizer;

use rasterizer::{
    PyImage,
    PyFont,
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

    let module = PyModule::new(py, "rasterizer")?;
    // module.add_class::<PyImage>(py)?;
    // module.add_class::<PyFont>(py)?;
    module.add(py, "Image", py.get_type::<PyImage>())?;
    module.add(py, "Font", py.get_type::<PyFont>())?;

    let modules = PyDict::downcast_from(py, sys.get(py, "modules")?)?;
    modules.set_item(py, "rasterizer", module)?;

    let mut argv = vec![];

    for arg in env::args() {
        argv.push(PyString::new(py, &arg).into_object());
    }

    let argv = PyList::new(py, &argv);
    sys.dict(py).set_item(py, "argv", argv)?;

    let textmation = py.import("textmation.__main__")?;
    textmation.call(py, "main", cpython::NoArgs, None)?;

    Ok(())
}
