/// The list of possible special characters used when generating a password.
pub const SPECIAL_CHARACTERS: [char; 16] = [
    '-', '.', '/', '\\', ':', '\'', '+', '&', ',', '@', '$', '!', '_', '#', '%', '~',
];

/// The list of possible decimal used when generating a password.
pub const DECIMAL: [char; 10] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

/// The list of possible uppercase letters used when generating a password.
pub const UPPERCASE: [char; 26] = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S',
    'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
];

/// The list of possible lowercase letters used when generating a password.
pub const LOWERCASE: [char; 26] = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
    't', 'u', 'v', 'w', 'x', 'y', 'z',
];

#[derive(Debug, PartialEq, Eq, Clone, Copy, Hash)]
pub enum CharKind {
    Uppercase,
    Lowercase,
    Decimal,
    Special,
}

impl CharKind {
    pub fn into_sample(self) -> &'static [char] {
        match self {
            CharKind::Uppercase => &UPPERCASE,
            CharKind::Lowercase => &LOWERCASE,
            CharKind::Decimal => &DECIMAL,
            CharKind::Special => &SPECIAL_CHARACTERS,
        }
    }

    pub fn pop_kind(available: Vec<Self>, kind: &Self) -> Vec<Self> {
        available
            .iter()
            .filter_map(|v| if *v == *kind { None } else { Some(*v) })
            .collect::<Vec<CharKind>>()
    }
}

#[derive(Debug, Default)]
pub struct CountTypesUsed {
    pub uppercase: u16,
    pub lowercase: u16,
    pub number: u16,
    pub special: u16,
}
