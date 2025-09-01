use crate::utils::constants::{LOOKUP_TABLE, S_BOX};
use crate::utils::types::{Block, Word};

pub fn get_first_key(key: &Block, rounds: u8) -> Block {
    let mut key_state: [Word; 4] = [[0, 0, 0, 0]; 4];
    let mut previous_key_state: [Word; 4] = [[0, 0, 0, 0]; 4];
    for i in 0..4 {
        for j in 0..4 {
            key_state[i][j] = key[i * 4 + j]
        }
    }

    for i in (1..rounds).rev() {
        for j in 1..4 {
            previous_key_state[j] = xor(&key_state[j - 1], &key_state[j])
        }
        let rot = rot_word(&previous_key_state[3]);
        let sub = sub_word(&rot);
        let xored = xor(&key_state[0], &r_con(i as usize));
        previous_key_state[0] = xor(&xored, &sub);
        key_state = previous_key_state
    }
    let mut first_key = [0; 16];
    for i in 0..4 {
        for j in 0..4 {
            first_key[i * 4 + j] = key_state[i][j]
        }
    }
    first_key
}

fn rot_word(word: &Word) -> Word {
    [word[1], word[2], word[3], word[0]]
}

fn sub_word(word: &Word) -> Word {
    [
        S_BOX[word[0] as usize],
        S_BOX[word[1] as usize],
        S_BOX[word[2] as usize],
        S_BOX[word[3] as usize],
    ]
}

fn xor(w1: &Word, w2: &Word) -> Word {
    [w1[0] ^ w2[0], w1[1] ^ w2[1], w1[2] ^ w2[2], w1[3] ^ w2[3]]
}

fn r_con(n: usize) -> Word {
    [LOOKUP_TABLE[n], 0, 0, 0]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_rot_word() {
        let word: Word = [0, 1, 2, 3];
        assert_eq!(rot_word(&word), [1, 2, 3, 0]);
    }

    #[test]
    fn test_sub_word() {
        let word: Word = [0, 1, 2, 3];
        assert_eq!(sub_word(&word), [99, 124, 119, 123])
    }

    #[test]
    fn test_xor() {
        let new_word = xor(&[0, 1, 2, 3], &[0, 1, 2, 3]);
        assert_eq!(new_word, [0, 0, 0, 0])
    }

    #[test]
    fn test_r_con() {
        assert_eq!(r_con(0), [141, 0, 0, 0])
    }

    #[test]
    fn test_get_first_key() {
        let key = [
            71, 247, 247, 188, 149, 53, 62, 3, 249, 108, 50, 188, 253, 5, 141, 253,
        ];
        assert_eq!(
            get_first_key(&key, 5),
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        );
    }
}