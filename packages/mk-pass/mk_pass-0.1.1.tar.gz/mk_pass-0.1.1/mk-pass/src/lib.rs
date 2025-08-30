#![doc = include_str!("../README.md")]
#![doc(
    html_logo_url = "https://raw.githubusercontent.com/2bndy5/mk-pass/main/docs/docs/images/logo-square.png"
)]
#![doc(
    html_favicon_url = "https://github.com/2bndy5/mk-pass/raw/main/docs/docs/images/favicon.ico"
)]
use rand::prelude::*;
mod helpers;
use helpers::{CharKind, CountTypesUsed};
pub use helpers::{DECIMAL, LOWERCASE, SPECIAL_CHARACTERS, UPPERCASE};
mod config;
pub use config::PasswordRequirements;

#[cfg(feature = "clap")]
pub use clap;

/// Generate a password given the constraints specified by `config`.
///
/// This function will invoke [`PasswordRequirements::validate()`] to
/// ensure basic password requirements are met.
pub fn generate_password(config: PasswordRequirements) -> String {
    let config = config.validate();
    let len = config.length as usize;
    let mut rng = rand::rng();
    let mut password = String::with_capacity(len);

    let mut used_types = CountTypesUsed::default();
    let mut available_types = vec![CharKind::Uppercase, CharKind::Lowercase];
    if config.specials > 0 {
        available_types.push(CharKind::Special);
    }
    if config.decimal > 0 {
        available_types.push(CharKind::Decimal);
    }
    let max_letters = len as u16 - config.decimal - config.specials;
    let max_lowercase = max_letters / 2;
    let max_uppercase = max_letters - max_lowercase;
    #[cfg(test)]
    {
        println!("max_lowers: {max_lowercase}, max_uppers: {max_uppercase}");
    }

    let mut pass_chars = vec!['\n'; len];

    let start = if config.first_is_letter {
        let letter_types = [CharKind::Lowercase, CharKind::Uppercase];
        let sample_kind = letter_types[rng.random_range(0..letter_types.len())];
        let sample_set = sample_kind.into_sample();
        pass_chars[0] = sample_set[rng.random_range(0..LOWERCASE.len())];
        match sample_kind {
            CharKind::Lowercase => {
                used_types.lowercase += 1;
                if used_types.lowercase == max_lowercase {
                    available_types = CharKind::pop_kind(available_types, &sample_kind);
                }
            }
            _ => {
                used_types.uppercase += 1;
                if used_types.uppercase == max_uppercase {
                    available_types = CharKind::pop_kind(available_types, &sample_kind);
                }
            }
        }
        1
    } else {
        0
    };
    let mut positions = (start..len).collect::<Vec<usize>>();

    for _ in start..len {
        debug_assert!(!available_types.is_empty());
        // pick a sample set from which to pick a character
        let kind = available_types[rng.random_range(0..available_types.len())];
        match kind {
            CharKind::Lowercase => {
                used_types.lowercase += 1;
                #[cfg(test)]
                {
                    println!("used lowers: {}", used_types.lowercase);
                }
                if used_types.lowercase == max_lowercase {
                    available_types = CharKind::pop_kind(available_types, &kind);
                }
            }
            CharKind::Uppercase => {
                used_types.uppercase += 1;
                #[cfg(test)]
                {
                    println!("used uppers: {}", used_types.uppercase);
                }
                if used_types.uppercase == max_uppercase {
                    available_types = CharKind::pop_kind(available_types, &kind);
                }
            }
            CharKind::Decimal => {
                used_types.number += 1;
                if used_types.number == config.decimal {
                    available_types = CharKind::pop_kind(available_types, &kind);
                }
            }
            CharKind::Special => {
                used_types.special += 1;
                if used_types.special == config.specials {
                    available_types = CharKind::pop_kind(available_types, &kind);
                }
            }
        }

        // now generate character from selected sample set
        let sample = kind.into_sample();
        let mut rand_index = rng.random_range(0..sample.len());
        if !config.allow_repeats {
            while pass_chars.contains(&sample[rand_index]) {
                rand_index = rng.random_range(0..sample.len());
            }
        }

        // now pick an index in the password that hasn't been used
        let rnd_pos = rng.random_range(0..positions.len());
        let pos = positions.remove(rnd_pos);
        pass_chars[pos] = sample[rand_index];
    }

    for ch in pass_chars {
        password.push(ch);
    }
    password
}

#[cfg(test)]
mod test {
    use super::{PasswordRequirements, generate_password};
    use crate::helpers::{DECIMAL, LOWERCASE, SPECIAL_CHARACTERS, UPPERCASE};

    fn count(output: &str) -> (usize, usize, usize, usize, usize) {
        let (mut uppers, mut lowers, mut decimal, mut specials) = (0, 0, 0, 0);
        let mut repeats = vec![];
        for (i, ch) in output.char_indices() {
            if LOWERCASE.contains(&ch) {
                lowers += 1;
            } else if UPPERCASE.contains(&ch) {
                uppers += 1;
            } else if DECIMAL.contains(&ch) {
                decimal += 1;
            } else if SPECIAL_CHARACTERS.contains(&ch) {
                specials += 1;
            }
            if output[0..i].contains(ch) && !repeats.contains(&ch) {
                repeats.push(ch);
            }
        }
        let repeats = repeats.len();
        println!(
            "decimal: {decimal}, uppercase: {uppers}, lowercase: {lowers}, special: {specials}, repeats: {repeats}"
        );
        (uppers, lowers, decimal, specials, repeats)
    }

    fn gen_pass(config: PasswordRequirements) {
        let password = generate_password(config);
        println!("Generated password: {password}");
        assert_eq!(password.len(), config.length as usize);
        let (uppers, lowers, decimal, specials, repeats) = count(&password);
        assert_eq!(decimal, config.decimal as usize);
        assert_eq!(specials, config.specials as usize);
        let letters = (config.length - config.specials - config.decimal) as usize;
        assert_eq!(letters, uppers + lowers);
        assert_eq!(repeats > 0, config.allow_repeats);
        if config.first_is_letter {
            let first = password.chars().next().unwrap();
            assert!(LOWERCASE.contains(&first) || UPPERCASE.contains(&first));
        }
    }

    #[test]
    fn special_4() {
        let config = PasswordRequirements {
            specials: 4,
            ..Default::default()
        };
        gen_pass(config);
    }

    #[test]
    fn no_special() {
        let config = PasswordRequirements {
            specials: 0,
            ..Default::default()
        };
        gen_pass(config);
    }

    #[test]
    fn no_first_is_letter() {
        // NOTE: there's no way to adequately test the randomness of the first char.
        let config = PasswordRequirements {
            first_is_letter: false,
            ..Default::default()
        };
        gen_pass(config);
    }

    #[test]
    fn no_decimal() {
        let config = PasswordRequirements {
            decimal: 0,
            ..Default::default()
        };
        gen_pass(config);
    }

    #[test]
    fn allow_repeats() {
        let config = PasswordRequirements {
            allow_repeats: true,
            decimal: 18,
            length: 20,
            specials: 0,
            ..Default::default()
        };
        gen_pass(config);
    }

    /// This is a hacky way to ensure complete coverage about the first character kind.
    ///
    /// It basically keeps generating a password until the first random letter is either
    /// [`UPPERCASE`] or [`LOWERCASE`] as specified by the `lower` parameter.
    ///
    /// Theoretically, this could cause an infinite loop or just run a long time because
    /// we are relying on randomness. However, the condition being tested means the
    /// probability of the randomness is 50:50.
    fn till_first_is(lower: bool) {
        let config = PasswordRequirements {
            specials: 8,
            decimal: 0,
            length: 10,
            ..Default::default()
        };
        let sample_set: &[char] = if lower { &LOWERCASE } else { &UPPERCASE };

        let mut password = generate_password(config);
        while !sample_set.contains(&password.chars().next().unwrap()) {
            password = generate_password(config);
        }
    }

    #[test]
    fn gen_first_lower() {
        till_first_is(true);
    }

    #[test]
    fn gen_first_upper() {
        till_first_is(false);
    }
}
