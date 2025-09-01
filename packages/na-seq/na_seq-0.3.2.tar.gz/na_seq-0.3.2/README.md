 # Python bindings for the na_seq crate
 
See [na_seq](https://github.com/david-oconnor/na_seq) for details.
 
# todo: Add this directly to na_seq's repo instead of its own?

## Compiling
Maturin is required to compile. To install: `pip install maturin`.

To compile to a wheel: Run `maturin build --release`. To test locally, then run `pip install .`
(The `install` script does this)

To publish to PyPi, run `maturin publish`.