
use image::GrayImage;
use ndarray::Array2;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CompactMaskModel {
    pub data: Vec<Vec<(u16, u16)>>,
}

pub fn compact_mask(mask: &GrayImage) -> CompactMaskModel {
    let mut compact_data: Vec<Vec<(u16, u16)>> = Vec::new();

    for row in mask.rows() {
        let mut row_compact: Vec<(u16, u16)> = Vec::new();
        let mut previous_value: u8 = 0;

        for (index, pixel) in row.enumerate() {
            let value = pixel[0]; // Extract the grayscale value (Luma<u8>)
            if value != previous_value {
                row_compact.push((index as u16, value as u16));
                previous_value = value;
            }
        }

        compact_data.push(row_compact);
    }

    CompactMaskModel { data: compact_data }
}

pub fn reconstruct_ndarray(
    compact_model: &CompactMaskModel,
    width: usize,
    height: usize,
) -> Array2<u8> {
    let mut result = Array2::<u8>::zeros((height, width));

    // Correct below code
    for (row_index, row_data) in compact_model.data.iter().enumerate() {
        let mut col_start = 0;
        for &(col_index, value) in row_data {
            for col in col_start..(col_index as usize) {
                result[(row_index, col)] = result[(row_index, col_start.saturating_sub(1))];
            }
            result[(row_index, col_index as usize)] = value as u8;
            col_start = (col_index as usize) + 1;
        }

        // Fill remaining columns in the row
        if col_start < width {
            let fill_value = if col_start > 0 {
                result[(row_index, col_start - 1)]
            } else {
                0
            };
            for col in col_start..width {
                result[(row_index, col)] = fill_value;
            }
        }
    }

    result
}

#[cfg(test)]
mod tests {
    use super::*;

    use image::GrayImage;
    use ndarray::Array2;

    #[test]
    fn test_compact_mask() {
        let mask = GrayImage::from_raw(3, 3, vec![0, 0, 0, 0, 255, 255, 255, 255, 255]).unwrap();
        let compact_model = compact_mask(&mask);

        assert_eq!(compact_model.data[0], vec![]);
        assert_eq!(compact_model.data[1], vec![(1, 255)]);
        assert_eq!(compact_model.data[2], vec![(0, 255)]);
    }

    #[test]
    fn test_reconstruct_ndarray() {
        let width = 4;
        let height = 4;
        let compact_model = CompactMaskModel {
            data: vec![
                vec![(0, 255), (1, 0), (2, 225)],
                vec![(1, 255), (3, 0)],
                vec![(2, 255)],
                vec![],
            ],
        };
        let result = reconstruct_ndarray(&compact_model, width, height);
        let expected = Array2::from_shape_vec(
            (height, width),
            vec![
                255u8, 0, 225, 225, 0, 255, 255, 0, 0, 0, 255, 255, 0, 0, 0, 0,
            ],
        )
        .unwrap();

        assert_eq!(result, expected);
    }
}
