mod attack;
mod utils;
mod first_step;
mod second_step;
mod key_expansion;

use crate::attack::attack;

use pyo3::prelude::*;
use crate::utils::types::Block;


#[pyfunction]
fn crack_key(normal_cipher_text: Block, faulty_cipher_text: Block, nb_threads: u8) -> PyResult<Vec<Block>> {
    let keys = attack(&normal_cipher_text, &faulty_cipher_text, nb_threads);
    Ok(keys)
}

/// A Python module implemented in Rust.
#[pymodule]
fn aes_dfa(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(crack_key, m)?)?;
    Ok(())
}
