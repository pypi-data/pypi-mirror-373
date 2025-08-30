use crate::helpers::{DECIMAL, LOWERCASE, SPECIAL_CHARACTERS, UPPERCASE};

#[cfg(feature = "clap")]
use clap::{ArgAction, Parser};

/// A structure to describe password requirements.
#[cfg_attr(
    feature = "clap",
    derive(Parser),
    command(about = "Generate a password comprehensively.", version, long_about = None)
)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PasswordRequirements {
    /// The length of the password.
    #[cfg_attr(feature = "clap", arg(long, short, default_value = "16"))]
    pub length: u16,

    /// How many decimal integer characters should the password contain?
    #[cfg_attr(feature = "clap", arg(long, short, default_value = "1"))]
    pub decimal: u16,

    /// How many special characters should the password contain?
    #[cfg_attr(feature = "clap", arg(long, short, default_value = "1"))]
    pub specials: u16,

    /// Should the first character always be a letter?
    #[cfg_attr(
        feature = "clap",
        arg(
            long = "no-first-is-letter",
            short,
            help = "Do not restrict the first character to only letters.",
            long_help = "Do not restrict the first character to only letters.\
            \n\nBy default, the first character is always a letter.",
            action = ArgAction::SetFalse
        )
    )]
    pub first_is_letter: bool,

    /// Allow characters to be used more than once?
    #[cfg_attr(
        feature = "clap",
        arg(
            short = 'r',
            long,
            help = "Allow character to used more than once.",
            long_help = "Allow character to used more than once.\
            \n\nBy default, each generated character is only used once.\n\
            Allowing repetitions also relaxes the maximum length.",
            action = ArgAction::SetTrue
        )
    )]
    pub allow_repeats: bool,
}

impl PasswordRequirements {
    /// Validates the instance's values.
    ///
    /// This returns a mutated copy of the instance where the values satisfy
    /// "sane minimum requirements" suitable for any password.
    ///
    /// The phrase "sane minimum requirements" implies
    ///
    /// 1. `length` is not less than 10
    /// 2. To avoid repetitions, `length` is not more than
    ///
    ///    - 52 if only letters (no decimal integers or special characters) are used
    ///    - 62 if only letters and decimal integers are used
    ///    - 68 if only letters and special characters are used
    ///    - 78 if letters, decimal integers, and special characters are used
    ///    - [u16::MAX] if repeated characters are allowed
    /// 3. `specials` character count does not overrule the required number of
    ///
    ///    - letters (2; 1 uppercase and 1 lowercase)
    ///    - decimal integers (if `decimal` is specified as non-zero value)
    /// 4. `decimal` character count does not overrule the required number of
    ///
    ///    - letters (2; 1 uppercase and 1 lowercase)
    ///    - special characters (if `specials` is specified as non-zero value)
    ///
    /// # About resolving conflicts
    ///
    /// If this function finds a conflict between the specified number of
    /// `specials` characters and `decimal`, then decimal integers takes precedence.
    ///
    /// For example:
    ///
    /// ```rust
    /// use mk_pass::PasswordRequirements;
    /// let req = PasswordRequirements {
    ///     length: 16,
    ///     specials: 16,
    ///     decimal: 16,
    ///     ..Default::default()
    /// };
    /// let expected = PasswordRequirements {
    ///     length: 16,
    ///     specials: 1,
    ///     decimal: 13,
    ///     ..Default::default()
    /// };
    /// assert_eq!(req.validate(), expected);
    /// ```
    pub fn validate(&self) -> Self {
        let mut len = self.length.max(10);
        if !self.allow_repeats {
            len = len.min(
                UPPERCASE.len() as u16
                    + LOWERCASE.len() as u16
                    + {
                        if self.specials > 0 {
                            SPECIAL_CHARACTERS.len() as u16
                        } else {
                            0
                        }
                    }
                    + {
                        if self.decimal > 0 {
                            DECIMAL.len() as u16
                        } else {
                            0
                        }
                    },
            );
        }
        let non_letter_max_len = len - 2;
        let max_special = if self.specials > 0 {
            non_letter_max_len - self.decimal.min(non_letter_max_len - 1)
        } else {
            0
        };
        let max_decimal = non_letter_max_len - max_special;
        Self {
            length: len,
            decimal: self.decimal.min(max_decimal),
            specials: self.specials.min(max_special),
            first_is_letter: self.first_is_letter,
            allow_repeats: self.allow_repeats,
        }
    }
}

impl Default for PasswordRequirements {
    /// Create default password requirements.
    fn default() -> Self {
        Self {
            length: 16,
            decimal: 1,
            specials: 1,
            first_is_letter: true,
            allow_repeats: false,
        }
    }
}
