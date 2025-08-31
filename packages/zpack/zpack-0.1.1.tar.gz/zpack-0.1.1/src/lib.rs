use pyo3::prelude::*;

pub mod package;
pub mod spec;
pub mod util;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn zpack(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<package::version::Version>()?;

    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    Ok(())
}
