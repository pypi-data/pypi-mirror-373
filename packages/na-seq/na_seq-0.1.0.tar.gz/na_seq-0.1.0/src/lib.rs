mod amino_acid;
pub mod element;
pub mod nucleotide;

use element::*;
use na_seq_rs::{
    AtomTypeInRes as RsAtomTypeInRes, Element as RsElement, Nucleotide as RsNucleotide,
    NucleotideGeneral as RsNucleotideGeneral,
};
use nucleotide::*;
use pyo3::{
    Bound, Py, PyResult, Python, exceptions::PyValueError, prelude::*, pymodule, types::PyType,
};

fn map_io<T>(r: std::io::Result<T>) -> PyResult<T> {
    r.map_err(|e| PyValueError::new_err(e.to_string()))
}

#[pymodule]
fn na_seq(py: Python<'_>, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Nucleotide>()?;
    m.add_class::<NucleotideGeneral>()?;
    m.add_class::<Element>()?;
    m.add_class::<AtomTypeInRes>()?;

    let element_obj = m.getattr("Element")?;
    let element_type = element_obj.downcast::<PyType>()?;
    let nt_obj = m.getattr("Nucleotide")?;
    let nt_type = nt_obj.downcast::<PyType>()?;
    let ntg_obj = m.getattr("NucleotideGeneral")?;
    let ntg_type = ntg_obj.downcast::<PyType>()?;
    let atir_obj = m.getattr("AtomTypeInRes")?;
    let atir_type = atir_obj.downcast::<PyType>()?;

    macro_rules! set_variant {
        ($class:expr, $Wrapper:ident, $RsEnum:ident, $name:ident, $alias:expr) => {{
            let obj = Py::new(
                py,
                $Wrapper {
                    inner: $RsEnum::$name,
                },
            )?;
            $class.setattr(stringify!($name), obj.clone_ref(py))?;
            let sym: String = $alias;
            $class.setattr(&sym, obj)?;
        }};
    }

    // Element + symbol aliases ("C", "Fe", ...)
    set_variant!(
        element_type,
        Element,
        RsElement,
        Hydrogen,
        RsElement::Hydrogen.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Carbon,
        RsElement::Carbon.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Oxygen,
        RsElement::Oxygen.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Nitrogen,
        RsElement::Nitrogen.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Fluorine,
        RsElement::Fluorine.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Sulfur,
        RsElement::Sulfur.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Phosphorus,
        RsElement::Phosphorus.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Iron,
        RsElement::Iron.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Copper,
        RsElement::Copper.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Calcium,
        RsElement::Calcium.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Potassium,
        RsElement::Potassium.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Aluminum,
        RsElement::Aluminum.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Lead,
        RsElement::Lead.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Gold,
        RsElement::Gold.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Silver,
        RsElement::Silver.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Mercury,
        RsElement::Mercury.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Tin,
        RsElement::Tin.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Zinc,
        RsElement::Zinc.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Magnesium,
        RsElement::Magnesium.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Manganese,
        RsElement::Manganese.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Iodine,
        RsElement::Iodine.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Chlorine,
        RsElement::Chlorine.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Tungsten,
        RsElement::Tungsten.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Tellurium,
        RsElement::Tellurium.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Selenium,
        RsElement::Selenium.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Bromine,
        RsElement::Bromine.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Rubidium,
        RsElement::Rubidium.to_letter()
    );
    set_variant!(
        element_type,
        Element,
        RsElement,
        Other,
        RsElement::Other.to_letter()
    );

    // Nucleotide + alias "A","C","G","T"
    set_variant!(
        nt_type,
        Nucleotide,
        RsNucleotide,
        A,
        RsNucleotide::A.to_str_upper()
    );
    set_variant!(
        nt_type,
        Nucleotide,
        RsNucleotide,
        C,
        RsNucleotide::C.to_str_upper()
    );
    set_variant!(
        nt_type,
        Nucleotide,
        RsNucleotide,
        G,
        RsNucleotide::G.to_str_upper()
    );
    set_variant!(
        nt_type,
        Nucleotide,
        RsNucleotide,
        T,
        RsNucleotide::T.to_str_upper()
    );

    // NucleotideGeneral + alias "A","C","G","T","N","W","S","Y","R","M","K"
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        A,
        RsNucleotideGeneral::A.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        C,
        RsNucleotideGeneral::C.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        G,
        RsNucleotideGeneral::G.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        T,
        RsNucleotideGeneral::T.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        N,
        RsNucleotideGeneral::N.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        W,
        RsNucleotideGeneral::W.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        S,
        RsNucleotideGeneral::S.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        Y,
        RsNucleotideGeneral::Y.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        R,
        RsNucleotideGeneral::R.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        M,
        RsNucleotideGeneral::M.to_str_upper()
    );
    set_variant!(
        ntg_type,
        NucleotideGeneral,
        RsNucleotideGeneral,
        K,
        RsNucleotideGeneral::K.to_str_upper()
    );

    // AtomTypeInRes (fixed variants only)
    macro_rules! at {
        ($v:ident) => {
            set_variant!(
                atir_type,
                AtomTypeInRes,
                RsAtomTypeInRes,
                $v,
                RsAtomTypeInRes::$v.to_string()
            );
        };
    }
    at!(C);
    at!(CA);
    at!(CB);
    at!(CD);
    at!(CD1);
    at!(CD2);
    at!(CE);
    at!(CE1);
    at!(CE2);
    at!(CE3);
    at!(CG);
    at!(CG1);
    at!(CG2);
    at!(CH2);
    at!(CH3);
    at!(CZ);
    at!(CZ1);
    at!(CZ2);
    at!(CZ3);
    at!(O);
    at!(OD1);
    at!(OD2);
    at!(OE1);
    at!(OE2);
    at!(OG);
    at!(OH);
    at!(OXT);
    at!(N);
    at!(ND1);
    at!(ND2);
    at!(NE);
    at!(NZ);
    at!(NH1);
    at!(NH2);
    at!(NE1);
    at!(NE2);
    at!(OG1);
    at!(OG2);
    at!(SD);
    at!(SE);
    at!(SG);

    Ok(())
}
