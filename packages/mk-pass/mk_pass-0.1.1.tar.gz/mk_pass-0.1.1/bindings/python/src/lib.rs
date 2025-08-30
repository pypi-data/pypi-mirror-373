use pyo3::prelude::*;

/// A python package binding the mk-pass library written in rust.
#[pymodule]
pub mod mk_pass {
    use pyo3::prelude::*;

    /// The function used as an entrypoint for the executable script.
    ///
    /// This function takes no parameters because
    /// they are parsed directly from `sys.argv`.
    #[pyfunction]
    pub fn main(py: Python) -> PyResult<()> {
        use ::mk_pass::clap::Parser;
        let args = py
            .import("sys")?
            .getattr("argv")?
            .extract::<Vec<String>>()?;
        let config = ::mk_pass::PasswordRequirements::parse_from(args);
        let password = generate_password(&config.into());
        println!("{password}");
        Ok(())
    }

    /// A structure to describe password requirements.
    #[derive(Debug, Clone, Copy, PartialEq, Eq)]
    #[pyclass(module = "mk_pass", get_all, frozen, eq)]
    pub struct PasswordRequirements {
        /// The length of the password.
        pub length: u16,

        /// How many numeric characters should the password contain?
        pub decimal: u16,

        /// How many special characters should the password contain?
        pub specials: u16,

        /// Should the first character always be a letter?
        pub first_is_letter: bool,

        /// Allow characters to be used more than once?
        pub allow_repeats: bool,
    }

    #[pymethods]
    impl PasswordRequirements {
        #[new]
        #[pyo3(
        signature = (length = 16, decimal=1, specials=1, first_is_letter = true, allow_repeats = false)
    )]
        pub fn new(
            length: Option<i32>,
            decimal: Option<i32>,
            specials: Option<i32>,
            first_is_letter: Option<bool>,
            allow_repeats: Option<bool>,
        ) -> Self {
            Self {
                length: length.unwrap_or(16) as u16,
                decimal: decimal.unwrap_or(1) as u16,
                specials: specials.unwrap_or(1) as u16,
                first_is_letter: first_is_letter.unwrap_or(true),
                allow_repeats: allow_repeats.unwrap_or_default(),
            }
        }

        pub fn __repr__(&self) -> String {
            format!("{self:?}")
        }

        /// Validates the instance's values.
        ///
        /// This returns a mutated clone of the instance where the values satisfy
        /// "sane minimum requirements" suitable for any password.
        ///
        /// The phrase "sane minimum requirements" implies
        ///
        /// 1. `length` is not less than 10
        /// 2. To avoid repetitions, `length` is not more than
        ///     - 52 if only letters (no decimal integers or special characters) are used
        ///     - 62 if only letters and decimal integers are used
        ///     - 68 if only letters and special characters are used
        ///     - 78 if letters, decimal integers, and special characters are used
        ///     - 65535 if repeated characters are allowed
        /// 3. `specials` character count does not overrule the required number of
        ///     - letters (2; 1 uppercase and 1 lowercase)
        ///     - decimal integers (if `decimal` is specified as non-zero value)
        /// 4. `decimal` character count does not overrule the required number of
        ///     - letters (2; 1 uppercase and 1 lowercase)
        ///     - special characters (if `specials` is specified as non-zero value)
        ///
        /// Note:
        ///     If this function finds a conflict between the specified number of
        ///     ``specials`` characters and ``decimal``, then decimal integers takes precedence.
        ///
        ///     For example:
        ///
        ///     ```python
        ///     >>> from comp_gen_pass import PasswordRequirements
        ///     >>> req = PasswordRequirements(length=16, specials=16, decimal=16)
        ///     >>> req
        ///     PasswordRequirements { length: 16, decimal: 16, specials: 16, first_is_letter: true }
        ///     >>> req.validate()
        ///     PasswordRequirements { length: 16, decimal: 13, specials: 1, first_is_letter: true }
        ///     ```
        pub fn validate(&self) -> Self {
            let config: ::mk_pass::PasswordRequirements = self.into();
            config.validate().into()
        }
    }

    impl From<::mk_pass::PasswordRequirements> for PasswordRequirements {
        fn from(value: ::mk_pass::PasswordRequirements) -> Self {
            Self {
                length: value.length,
                decimal: value.decimal,
                specials: value.specials,
                first_is_letter: value.first_is_letter,
                allow_repeats: value.allow_repeats,
            }
        }
    }

    impl From<&PasswordRequirements> for ::mk_pass::PasswordRequirements {
        fn from(value: &PasswordRequirements) -> Self {
            Self {
                length: value.length,
                decimal: value.decimal,
                specials: value.specials,
                first_is_letter: value.first_is_letter,
                allow_repeats: value.allow_repeats,
            }
        }
    }

    /// Generate a password given the constraints specified by `config`.
    ///
    /// This function will invoke
    /// [`PasswordRequirements.validate()`][mk_pass.PasswordRequirements.validate]
    /// to ensure basic password requirements are met.
    #[pyfunction]
    pub fn generate_password(config: &PasswordRequirements) -> String {
        ::mk_pass::generate_password(config.into())
    }

    #[pymodule_export]
    const SPECIAL_CHARACTERS: [char; 16] = ::mk_pass::SPECIAL_CHARACTERS;

    #[pymodule_export]
    const DECIMAL: [char; 10] = ::mk_pass::DECIMAL;

    #[pymodule_export]
    const LOWERCASE: [char; 26] = ::mk_pass::LOWERCASE;

    #[pymodule_export]
    const UPPERCASE: [char; 26] = ::mk_pass::UPPERCASE;
}
