#[cfg(not(test))]
use std::env;

use clap::Parser;
use mk_pass::{PasswordRequirements, generate_password};

fn main() {
    let config = PasswordRequirements::parse_from(
        #[cfg(test)]
        vec!["mk-pass"],
        #[cfg(not(test))]
        env::args(),
    );
    let password = generate_password(config);
    println!("{password}");
}

#[cfg(test)]
mod test {
    use super::main;

    #[test]
    fn run() {
        // basically this test just ensures it does not panic.
        main()
    }
}
