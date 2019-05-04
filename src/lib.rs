#[macro_use]
extern crate cpython;

py_module_initializer!(rasterizer, initrasterizer, PyInit_rasterizer, |py, m| {
    m.add(py, "__doc__", "Rasterizer module implemented in Rust")?;

    Ok(())
});
