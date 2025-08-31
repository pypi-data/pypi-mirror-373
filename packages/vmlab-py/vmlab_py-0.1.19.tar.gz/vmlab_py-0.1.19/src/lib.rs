pub mod audio;
pub mod compact_mask;

use audio::transforms::{Audio2MelSpectrogramV2RT, TransformResult};
use audio::utils::{norm_mean_std, MelParam};
use audio::{PreAudio2ExpTrait, PreAudio2ExpV1, PreAudio2ExpV2, MINIMUM_MEL_V1, MINIMUM_MEL_V2};
use compact_mask::reconstruct_ndarray;
use image::GrayImage;
use ndarray::{Array1, Array2};
use numpy::{PyArray1, PyArray2, PyArrayMethods};
use pyo3::types::PyBytes;
use pyo3::{exceptions::PyValueError, prelude::*};

#[pyfunction]
#[pyo3(signature = (bytes, width, height, scale=None))]
/// Reconstructs a grayscale mask from a serialized CompactMaskModel.
///
/// # Arguments
/// - `bytes` (`PyBytes`): The serialized CompactMaskModel.
/// - `width` (`usize`): The width of the output image.
/// - `height` (`usize`): The height of the output image.
/// - `scale` (`f32`, 'str'): The scale to be resized and filtertype of resizing.
///
/// ## FilterType
/// - NEAREST: "nearest" or "lowest"
/// - LINEAR: "linear" or "triangle" or "low"
/// - CATMULLROM: "catmullrom" or "cubic" or "medium"
/// - GAUSSIAN: "gaussian" or "high"
/// - LANZOS: "lanzos" or "highest"
///
/// # Returns
/// A `numpy.ndarray` representing the reconstructed mask.
pub fn reconstruct_mask(
    bytes: &Bound<'_, PyBytes>,
    width: usize,
    height: usize,
    scale: Option<(f32, String)>,
) -> PyResult<Py<PyArray2<f32>>> {
    let b = bytes.as_bytes();
    // decode the msgpack from b
    let Ok(compact_model) = rmp_serde::from_slice(b) else {
        return Err(PyErr::new::<PyValueError, _>(
            "Failed to deserialize CompactMaskModel",
        ));
    };

    // Logic to reconstruct the mask
    let result: Array2<u8> = reconstruct_ndarray(&compact_model, width, height);

    // resize using image crate the result if scale is provided and scale it not 1.0
    // and convert result type into f32
    if let Some((scale, filter_type)) = scale {
        //let result = image::imageops::resize(&image::ImageBuffer::from_raw(width as u32, height as u32, result.to_vec()).unwrap(), (scale * width as f32) as u32, (scale * height as f32) as u32, image::imageops::FilterType::Nearest);
        //let result = Array2::from_shape_vec((result.len() / width, width), result).unwrap();
        let (result, _) = result.into_raw_vec_and_offset();

        let img = GrayImage::from_raw(width as u32, height as u32, result).unwrap();
        let resized = image::imageops::resize(
            &img,
            (scale * width as f32) as u32,
            (scale * height as f32) as u32,
            match filter_type.as_str() {
                "nearest" | "lowest" => image::imageops::FilterType::Nearest,
                "linear" | "triangle" | "low" => image::imageops::FilterType::Triangle,
                "catmullrom" | "cubic" | "medium" => image::imageops::FilterType::CatmullRom,
                "gaussian" | "high" => image::imageops::FilterType::Gaussian,
                "lanzos" | "highest" => image::imageops::FilterType::CatmullRom,
                _ => image::imageops::FilterType::Triangle,
            },
        );

        // convert u8 into Array2<f32> result
        let resized_height = resized.height() as usize;
        let resized_width = resized.width() as usize;
        let result: Array2<f32> = Array2::from_shape_vec(
            (resized_height, resized_width),
            resized.pixels().map(|p| p[0] as f32 / 255.0).collect(),
        )
        .unwrap();

        return Ok(Python::with_gil(|py| {
            PyArray2::from_owned_array(py, result).into()
        }));
    }

    // Convert u8 into f32
    let result: Array2<f32> = result.mapv(|x| x as f32 / 255.0);
    Ok(Python::with_gil(|py| {
        PyArray2::from_owned_array(py, result).into()
    }))
}

/// Dummy function for warmup.
///
/// # Returns
/// A dummy value of 0.
#[pyfunction]
pub fn dummy_func(py: Python) -> PyResult<u32> {
    Ok(0)
}

/// Converts a wav file to a mel spectrogram in bytes for the Audio2Exp V1 model.
///
/// # Arguments
/// - `wav` (`numpy.ndarray`): The wav file as a numpy array.
/// - 'sample_rate' (`u32`): The sample rate of given wav.
///
/// # Returns
/// A list of bytes representing the mel spectrogram.
#[pyfunction]
pub fn a2ev1_melspectrogram(
    py: Python,
    wav: &Bound<'_, PyAny>,
    sample_rate: u32,
) -> PyResult<Vec<Py<PyBytes>>> {
    let transformer = PreAudio2ExpV1::new();
    process_melspectrogram(py, wav, sample_rate, transformer, MINIMUM_MEL_V1)
}

/// Converts a wav file to a mel spectrogram in bytes for the Audio2Exp V2 model.
///
/// # Arguments
/// - `wav` (`numpy.ndarray`): The wav file as a numpy array.
/// - 'sample_rate' (`u32`): The sample rate of given wav.
///
/// # Returns
/// A list of bytes representing the mel spectrogram.
#[pyfunction]
pub fn a2ev2_melspectrogram(
    py: Python,
    wav: &Bound<'_, PyAny>,
    sample_rate: u32,
) -> PyResult<Vec<Py<PyBytes>>> {
    let transformer = PreAudio2ExpV2::new();
    process_melspectrogram(py, wav, sample_rate, transformer, MINIMUM_MEL_V2)
}

fn process_melspectrogram(
    py: Python,
    wav: &Bound<'_, PyAny>,
    sample_rate: u32,
    mut transformer: impl PreAudio2ExpTrait + std::marker::Send,
    minimum: f32,
) -> PyResult<Vec<Py<PyBytes>>> {
    // Convert input numpy array to ndarray Array1<f32>

    let wav = wav.downcast::<PyArray1<f32>>().map_err(|_| {
        pyo3::exceptions::PyTypeError::new_err("Expected a NumPy ndarray of type float32")
    })?;

    let wav = wav.readonly().as_array().to_owned();
    let wav_vec: Vec<f32> = wav.to_vec();


    let chunks: Vec<Vec<u8>> = py.allow_threads(move || {
        // Resample to 16000 Hz if needed (nearest-neighbor as in original)
        let resampled: Vec<f32> = if sample_rate == 44100 {
            let ratio = 16000.0 / 44100.0;
            let new_len = (wav_vec.len() as f32 * ratio).round() as usize;
            let mut out = Vec::with_capacity(new_len);
            for i in 0..new_len {
                let nearest_index =
                    ((i as f32 / ratio).round() as usize).min(wav_vec.len().saturating_sub(1));
                out.push(wav_vec[nearest_index]);
            }
            out
        } else {
            wav_vec
        };

        // Transform + preprocessing
        transformer
            .transform(resampled)
            .to_preprocessed_bytes(minimum)
            .unwrap_or_default()
    });

    // Create Python bytes with the GIL
    let result = chunks
        .into_iter()
        .map(|chunk| {
            let bytes = bytemuck::cast_slice(chunk.as_slice());
            PyBytes::new(py, bytes).into()
        })
        .collect();

    Ok(result)
}

#[pyclass]
pub struct RTMelV2 {
    transformer: Audio2MelSpectrogramV2RT,
    sample_rate: u32,
    last_step: f32,
}

#[pymethods]
impl RTMelV2 {
    #[new]
    fn new(sample_rate: u32) -> Self {
        RTMelV2 {
            sample_rate,
            last_step: 0.0,
            transformer: Audio2MelSpectrogramV2RT::new(
                16000,
                800,
                200,
                1e-5,
                1.0,
                1.0,
                0.0,
                MelParam {
                    sr: 16000.0,
                    n_fft: 800,
                    n_mels: 80,
                    f_min: Some(55.0),
                    f_max: Some(7600.0),
                    htk: false,
                    norm: true,
                },
            ),
        }
    }

    fn clear(&mut self) {
        self.last_step = 0.0;
        self.transformer.clear();
    }

    /// Example method for the RTMelV2 class.
    /// This method can be called from Python.
    fn transform(&mut self, py: Python, wav: &Bound<'_, PyAny>) -> PyResult<Vec<Py<PyBytes>>> {
        let wav = wav.downcast::<PyArray1<f32>>().map_err(|_| {
            pyo3::exceptions::PyTypeError::new_err("Expected a NumPy ndarray of type float32")
        })?;

        let wav = wav.readonly().as_array().to_owned();
        let wav_vec =  wav.to_vec();
        let sample_rate =   self.sample_rate;

        let chunks: Vec<Vec<u8>> = py.allow_threads(|| {
            let audio = if sample_rate != 16000 {
                let out_len = (wav_vec.len() as f32 * 16000.0 / sample_rate as f32).ceil() as usize;
                let step = sample_rate as f32 / 16000.0;
                let mut cur_idx = self.last_step;
                let mut resampled_wav = Vec::with_capacity(out_len + 1);

                // Nearest neighbor resampling (as in original)
                while cur_idx <= (wav_vec.len() - 1) as f32 {
                    let nearest_idx = (cur_idx.round() as usize).min(wav_vec.len() - 1);
                    resampled_wav.push(wav_vec[nearest_idx]);
                    cur_idx += step;
                }

                // Update last_step to only the fractional part
                //self.last_step = cur_idx - (cur_idx as usize) as f32;
                self.last_step = cur_idx - wav_vec.len() as f32;

                // Convert resampled wav into ndarray
                resampled_wav
            } else {
                wav.to_vec()
            };

            let transformed = self.transformer.transform(audio, |v| {
                norm_mean_std(v, -2.123307466506958, 1.0819180011749268)
            });

            if transformed.is_none() {
                Vec::new()
            } else {
                TransformResult::new(transformed)
                    .to_preprocessed_bytes(MINIMUM_MEL_V2)
                    .unwrap_or_default()
            }
        });

        let result = chunks.into_iter().map(|chunk| {
            let bytes = bytemuck::cast_slice(chunk.as_slice()); // Convert chunk to bytes
            PyBytes::new(py, bytes).into() // Convert to PyBytes and store in Vec
        }).collect();

        Ok(result)
    }
}

#[pymodule(name = "vmlab_py")]
fn vmlab_module(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(dummy_func, m)?)?;
    m.add_function(wrap_pyfunction!(reconstruct_mask, m)?)?;
    m.add_function(wrap_pyfunction!(a2ev1_melspectrogram, m)?)?;
    m.add_function(wrap_pyfunction!(a2ev2_melspectrogram, m)?)?;
    m.add_class::<RTMelV2>()?;
    Ok(())
}
