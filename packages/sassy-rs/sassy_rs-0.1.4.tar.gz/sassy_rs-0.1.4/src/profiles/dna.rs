use crate::profiles::Profile;
use std::{
    simd::cmp::SimdPartialEq,
    simd::{Simd, u8x32},
};

/// DNA alphabet: ACGT.
///
/// Input sequences are assuming to only consist of these bases.
/// This can be verified using [`Dna::valid_seq`].
#[derive(Clone, Debug)]
pub struct Dna {
    bases: Vec<u8>,
}

impl Profile for Dna {
    type A = u8;
    type B = [u64; 4];

    fn encode_pattern(a: &[u8]) -> (Self, Vec<Self::A>) {
        let bases = vec![b'A', b'C', b'T', b'G'];
        let query_profile = a.iter().map(|c| (c >> 1) & 3).collect();
        (Dna { bases }, query_profile)
    }

    #[inline(always)]
    fn encode_ref(&self, b: &[u8; 64], out: &mut Self::B) {
        unsafe {
            let chunk0 = u8x32::from_array(b[0..32].try_into().unwrap());
            let chunk1 = u8x32::from_array(b[32..64].try_into().unwrap());
            let chunk0_shifted = chunk0 >> 1;
            let chunk1_shifted = chunk1 >> 1;
            let masked0 = chunk0_shifted & u8x32::splat(0x03);
            let masked1 = chunk1_shifted & u8x32::splat(0x03);
            for (i, code) in CODES.iter().enumerate() {
                let eq0 = masked0.simd_eq(*code);
                let eq1 = masked1.simd_eq(*code);
                let low = eq0.to_bitmask();
                let high = eq1.to_bitmask();
                *out.get_unchecked_mut(i) = (high << 32) | low;
            }
        };
    }

    #[inline(always)]
    fn eq(ca: &u8, cb: &[u64; 4]) -> u64 {
        unsafe { *cb.get_unchecked(*ca as usize) }
    }

    #[inline(always)]
    fn is_match(char1: u8, char2: u8) -> bool {
        (char1 | 0x20) == (char2 | 0x20)
    }

    #[inline(always)]
    fn alloc_out() -> Self::B {
        [0; 4]
    }

    #[inline(always)]
    fn n_bases(&self) -> usize {
        self.bases.len()
    }

    #[inline(always)]
    fn valid_seq(seq: &[u8]) -> bool {
        // we’ll do 32-byte chunks
        const LANES: usize = 32;
        type V = Simd<u8, LANES>;

        let len = seq.len();
        let mut i = 0;

        // Split in 32-byte chunks (u8 * 32)
        while i + LANES <= len {
            let chunk = V::from_slice(&seq[i..i + LANES]);
            // lowercase, setting 5th bit, might transform some ascii to
            // other ascii but that's fine
            let lowered = chunk | V::splat(0x20);
            let is_a = lowered.simd_eq(V::splat(b'a'));
            let is_c = lowered.simd_eq(V::splat(b'c'));
            let is_g = lowered.simd_eq(V::splat(b'g'));
            let is_t = lowered.simd_eq(V::splat(b't'));
            let ok = is_a | is_c | is_g | is_t;
            if !ok.all() {
                return false;
            }

            i += LANES;
        }

        // Whatever non 32 tail is left
        while i < len {
            println!("Tail check");
            let c = seq[i] | 0x20; // lowercase
            if c != b'a' && c != b'c' && c != b'g' && c != b't' {
                return false;
            }
            i += 1;
        }

        true
    }

    fn reverse_complement(query: &[u8]) -> Vec<u8> {
        query.iter().rev().map(|&c| RC[c as usize]).collect()
    }

    fn complement(query: &[u8]) -> Vec<u8> {
        query.iter().map(|&c| RC[c as usize]).collect()
    }
}

// Same order as iupac
const CODES: [u8x32; 4] = [
    u8x32::splat(0u8), // A
    u8x32::splat(1u8), // C
    u8x32::splat(2u8), // T
    u8x32::splat(3u8), // G
];

const RC: [u8; 256] = {
    let mut rc = [0; 256];
    let mut i = 0;
    while i < 256 {
        rc[i] = i as u8;
        i += 1;
    }
    rc[b'A' as usize] = b'T';
    rc[b'C' as usize] = b'G';
    rc[b'T' as usize] = b'A';
    rc[b'G' as usize] = b'C';
    rc
};

#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_dna_is_match() {
        assert!(Dna::is_match(b'A', b'A'));
        assert!(Dna::is_match(b'c', b'c'));
        assert!(Dna::is_match(b'C', b'c'));
        assert!(Dna::is_match(b'c', b'C'));
        assert!(!Dna::is_match(b'X', b'A'));
        assert!(!Dna::is_match(b'X', b'A'));
        assert!(!Dna::is_match(b'X', b'T'));
        assert!(!Dna::is_match(b'X', b'G'));
        assert!(!Dna::is_match(b'X', b'C'));
        assert!(!Dna::is_match(b'A', b'N'));
        assert!(!Dna::is_match(b'C', b't'));
    }

    fn get_match_positions(out: &[u64; 4]) -> Vec<Vec<usize>> {
        let mut positions = vec![vec![]; 4];
        for (i, _) in CODES.iter().enumerate() {
            let bits = out[i];
            for j in 0..64 {
                if (bits & (1u64 << j)) != 0 {
                    positions[i].push(j);
                }
            }
        }
        positions
    }

    #[test]
    fn test_dna_u64_search() {
        let mut seq = [b'G'; 64];
        seq[0] = b'A';
        seq[1] = b'A';
        seq[63] = b'C';
        let mut out = [0u64; 4];
        {
            let seq: &[u8; 64] = &seq;
            let out: &mut [u64; 4] = &mut out;
            unsafe {
                let chunk0 = u8x32::from_array(seq[0..32].try_into().unwrap());
                let chunk1 = u8x32::from_array(seq[32..64].try_into().unwrap());
                let chunk0_shifted = chunk0 >> 1;
                let chunk1_shifted = chunk1 >> 1;
                let masked0 = chunk0_shifted & u8x32::splat(0x03);
                let masked1 = chunk1_shifted & u8x32::splat(0x03);
                for (i, code) in CODES.iter().enumerate() {
                    let eq0 = masked0.simd_eq(*code);
                    let eq1 = masked1.simd_eq(*code);
                    let low = eq0.to_bitmask();
                    let high = eq1.to_bitmask();
                    *out.get_unchecked_mut(i) = (high << 32) | low;
                }
            }
        }; // A, C, T, G
        let positions = get_match_positions(&out);
        assert_eq!(positions[0], vec![0, 1]);
        assert_eq!(positions[1], vec![63]);
        assert_eq!(positions[2], Vec::<usize>::new());
        assert_eq!(positions[3], (2..63).collect::<Vec<_>>());
    }

    #[test]
    fn test_dna_u64_case_insensitive() {
        let mut seq = [b'G'; 64];
        seq[0] = b'a';
        seq[1] = b'A';
        let mut out = [0u64; 4];
        {
            let seq: &[u8; 64] = &seq;
            let out: &mut [u64; 4] = &mut out;
            unsafe {
                let chunk0 = u8x32::from_array(seq[0..32].try_into().unwrap());
                let chunk1 = u8x32::from_array(seq[32..64].try_into().unwrap());
                let chunk0_shifted = chunk0 >> 1;
                let chunk1_shifted = chunk1 >> 1;
                let masked0 = chunk0_shifted & u8x32::splat(0x03);
                let masked1 = chunk1_shifted & u8x32::splat(0x03);
                for (i, code) in CODES.iter().enumerate() {
                    let eq0 = masked0.simd_eq(*code);
                    let eq1 = masked1.simd_eq(*code);
                    let low = eq0.to_bitmask();
                    let high = eq1.to_bitmask();
                    *out.get_unchecked_mut(i) = (high << 32) | low;
                }
            }
        };
        let positions = get_match_positions(&out);
        assert_eq!(positions[0], vec![0, 1]);
    }

    fn non_actg_bytes(n: isize) -> Vec<u8> {
        // Create a vector of all bytes that are not DNA bases
        let non_dna_chars = (0u8..=255)
            .filter(|&b| !matches!(b.to_ascii_uppercase(), b'A' | b'C' | b'G' | b'T'))
            .collect::<Vec<u8>>();

        if n == -1 {
            // return all (unqiue) non dna bytes
            non_dna_chars
        } else {
            let mut seq = vec![0u8; n as usize];
            for i in 0..n as usize {
                seq[i] = non_dna_chars[rand::random_range(0..non_dna_chars.len())];
            }
            seq
        }
    }

    #[test]
    fn test_dna_valid_seq_empty() {
        assert!(Dna::valid_seq(b"")); // Not sure if this should be valid or not
    }

    #[test]
    fn test_dna_valid_seq() {
        // scalar, dna (as <32); valid
        assert!(Dna::valid_seq(b"ACGTactg"));

        // scalar, non-dna; invalid
        // -1 is all ascii which are not dna
        let non_actg = non_actg_bytes(-1);
        assert!(!Dna::valid_seq(&non_actg));

        // 32-byte chunks, dna; valid
        let seq = [b'A', b'C', b'T', b'G', b'a', b'c', b't', b'g'].repeat(32);
        assert!(Dna::valid_seq(&seq));

        // 32-byte chunks, non-dna; invalid
        let seq = non_actg_bytes(256);
        assert!(!Dna::valid_seq(&seq));
    }
}
