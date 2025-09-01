use super::constants::BLOCK_SIZE;

pub type Block = [u8; BLOCK_SIZE];
pub type Word = [u8; 4];
pub type State = [Word; 4];