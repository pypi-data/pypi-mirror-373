use ndarray::{Array1, Array2, Array4};
use num::Complex;
use rustfft::{Fft, FftPlanner};
use std::f32::consts::PI;
use std::sync::Arc;

use super::utils::{
    self, crop_pad_audio, log_mel_spectrogram, parse_audio_length, preemphasis, MelParam,
};

const MEL_STEP_IN_FRAME: f32 = 3.2;

pub struct TransformResult {
    result: Option<(Array4<f32>, usize, Option<f32>, bool)>,
}

impl TransformResult {
    pub(crate) fn new(result: Option<(Array4<f32>, usize, Option<f32>, bool)>) -> Self {
        Self { result }
    }

    pub fn to_preprocessed_bytes(self, minimum_element: f32) -> Option<Vec<Vec<u8>>> {
        self.result
            .map(|(result, frame_count, start_idx, first_out)| {
                let shape = result.shape();

                let nframes = shape[3];
                let mut index: f32 = start_idx.unwrap_or(0.0);

                let mut mel_datas = Vec::new();

                for _ in 0..frame_count {
                    let start = index.round() as usize;
                    let end = start + 16;

                    if end > nframes {
                        let padding =
                            ndarray::Array4::from_elem([1, 1, 80, end - nframes], minimum_element);
                        let unit_mel = ndarray::concatenate(
                            ndarray::Axis(3),
                            &[
                                result.slice(ndarray::s![.., .., .., start..nframes]).view(),
                                padding.view(),
                            ],
                        )
                        .expect("Failed to pad mel spectrogram array")
                        .as_standard_layout()
                        .to_owned();
                        let raw_data = unit_mel.as_slice().unwrap();
                        mel_datas.push(bytemuck::cast_slice(raw_data).to_vec());
                    } else {
                        let unit_mel = result
                            .slice(ndarray::s![.., .., .., start..end])
                            .as_standard_layout()
                            .to_owned();
                        let raw_data = unit_mel.as_slice().unwrap();
                        mel_datas.push(bytemuck::cast_slice(raw_data).to_vec());
                    }

                    index += MEL_STEP_IN_FRAME;
                }

                if first_out {
                    if let Some(first_mel) = mel_datas.first().cloned() {
                        let mut new_mel_datas = Vec::with_capacity(mel_datas.len() + 2);
                        new_mel_datas.push(first_mel.clone());
                        new_mel_datas.push(first_mel);
                        new_mel_datas.extend(mel_datas);
                        mel_datas = new_mel_datas;
                    }
                }
                mel_datas
            })
    }

    pub fn to_bytes(self) -> Option<Vec<u8>> {
        self.result.as_ref().map(|(v, _, _, _)| {
            let raw_data = v.as_slice().unwrap();
            bytemuck::cast_slice(raw_data).to_vec()
        })
    }

    pub fn to_ndarray(self) -> Option<Array4<f32>> {
        self.result.map(|v| v.0)
    }
}

pub struct Spectrogram {
    complex_buf: Vec<Complex<f32>>,
    fft: Arc<dyn Fft<f32>>,
    fft_size: usize,
    idx: u64,
    hop_buf: Vec<f32>,
    hop_size: usize,
    scratch_buf: Vec<Complex<f32>>,
    window: Vec<f32>,
}

impl Spectrogram {
    pub fn new(fft_size: usize, hop_size: usize) -> Self {
        let mut planner = FftPlanner::new();
        let fft = planner.plan_fft_forward(fft_size);
        let window: Vec<f32> = (0..fft_size)
            .map(|i| 0.5 * (1.0 - f32::cos((2.0 * PI * i as f32) / fft_size as f32)))
            .collect();
        let idx = 0;

        Self {
            complex_buf: vec![Complex::new(0.0, 0.0); fft_size],
            fft,
            fft_size,
            idx,
            hop_buf: vec![0.0; fft_size],
            hop_size,
            scratch_buf: vec![Complex::new(0.0, 0.0); fft_size],
            window,
        }
    }

    pub fn clear(&mut self) {
        self.idx = 0;

        self.scratch_buf.iter_mut().for_each(|v| {
            *v = Complex::new(0.0, 0.0);
        });
        self.complex_buf.iter_mut().for_each(|v| {
            *v = Complex::new(0.0, 0.0);
        });
        self.hop_buf.iter_mut().for_each(|v| *v = 0.0);
    }

    pub fn add(&mut self, frames: &[f32]) -> Option<Array1<Complex<f32>>> {
        let fft_size = self.fft_size;
        let hop_size = self.hop_size;

        let mut pcm_data: Vec<f32> = frames.iter().cloned().collect();
        let pcm_size = pcm_data.len();
        assert!(pcm_size <= hop_size, "frames must be <= hop_size");

        // zero pad
        if pcm_size < hop_size {
            pcm_data.extend_from_slice(&vec![0.0; hop_size - pcm_size]);
        }

        self.hop_buf.copy_within(hop_size.., 0);
        self.hop_buf[(fft_size - hop_size)..].copy_from_slice(&pcm_data);

        self.idx = self.idx.wrapping_add(pcm_size as u64);

        if self.idx >= fft_size as u64 {
            let windowed_samples: Vec<f32> = self
                .hop_buf
                .iter()
                .enumerate()
                .map(|(j, val)| val * self.window[j])
                .collect();

            self.complex_buf
                .iter_mut()
                .zip(windowed_samples.iter())
                .for_each(|(c, val)| *c = Complex::new(*val, 0.0));

            self.fft
                .process_with_scratch(&mut self.complex_buf, &mut self.scratch_buf);

            Some(Array1::from_vec(self.complex_buf.clone()))
        } else {
            None
        }
    }
}

pub struct Audio2MelSpectrogram {
    pub sample_rate: u32,
    pub fft_size: usize,
    pub hop_size: usize,
    pub center: bool,
    pub preemphasis: Option<f32>,
    pub min_level: f32,
    pub compression_factor: f32,
    pub amplitude_to_db_factor: f32,
    pub ref_level_db: f32,

    //
    spectrogram: Spectrogram,
    mel_banks: Array2<f32>,
}

impl Audio2MelSpectrogram {
    pub fn new(
        sample_rate: u32,
        fft_size: usize,
        hop_size: usize,
        min_level: f32,
        compression_factor: f32,
        amplitude_to_db_factor: f32,
        ref_level_db: f32,
        center: bool,
        preemphasis: Option<f32>,
        mel_params: MelParam,
    ) -> Self {
        let mel_banks = utils::mel(mel_params);
        Self {
            sample_rate,
            fft_size,
            hop_size,
            center,
            preemphasis,
            min_level,
            compression_factor,
            amplitude_to_db_factor,
            ref_level_db,
            spectrogram: Spectrogram::new(fft_size, hop_size),
            mel_banks,
        }
    }

    pub fn transform<F>(
        &mut self,
        audio: Vec<f32>,
        norm_fn: F,
    ) -> Option<(Array4<f32>, usize, Option<f32>, bool)>
    where
        F: Fn(&Array2<f32>) -> Array2<f32>,
    {
        //
        // PRE-PROCESS
        let (wav_length, frame_count) = parse_audio_length(audio.len(), self.sample_rate, 25);
        // Crop or pad the audio samples
        let mut padded_samples = crop_pad_audio(
            audio,
            wav_length,
            if self.center { 0 } else { self.fft_size },
        );

        if self.center {
            // pad (fft_size//2) the padded_samples to the left and right
            let pad_size = self.fft_size / 2;
            let mut left_pad = vec![0.0; pad_size];
            let right_pad = vec![0.0; pad_size];
            left_pad.extend(padded_samples);
            left_pad.extend(right_pad);
            padded_samples = left_pad;
        }

        // Preemphasis
        if let Some(preemp) = self.preemphasis {
            preemphasis(&mut padded_samples, preemp);
        }

        //
        // TRANSFORMS
        //
        // Initialize the Mel spectrogram transformer
        // Compute the Mel spectrogram
        let mut mel_outputs = Vec::new();
        while padded_samples.len() >= self.hop_size {
            let Some(fft) = self
                .spectrogram
                .add(padded_samples.drain(..self.hop_size).as_slice())
            else {
                continue;
            };

            let mel = log_mel_spectrogram(
                &fft,
                &self.mel_banks,
                self.min_level,
                self.compression_factor,
                self.amplitude_to_db_factor,
                self.ref_level_db,
            );
            let mel = norm_fn(&mel);
            mel_outputs.push(mel);
        }

        self.spectrogram.clear();

        if mel_outputs.is_empty() {
            None
        } else {
            let mut stacked_mel = ndarray::Array4::<f32>::zeros((1, 1, 80, mel_outputs.len()));

            for (i, mel) in mel_outputs.into_iter().enumerate() {
                stacked_mel
                    .index_axis_mut(ndarray::Axis(3), i)
                    .assign(&mel.to_shape((80,)).unwrap());
            }
            Some((stacked_mel, frame_count, None, true))
        }
        // // .map(|v| {
        // //     let raw_data = v.as_slice().unwrap();
        // //     cast_slice(raw_data).to_vec()
        // // });

        // mel_bytes
    }
}

pub struct Audio2MelSpectrogramV2RT {
    pub sample_rate: u32,
    pub fft_size: usize,
    pub hop_size: usize,
    pub min_level: f32,
    pub compression_factor: f32,
    pub amplitude_to_db_factor: f32,
    pub ref_level_db: f32,

    //
    spectrogram: Spectrogram,
    mel_banks: Array2<f32>,

    first: bool,
    first_out: bool,
    residual: Option<Vec<f32>>,
    residual_mel: Option<Vec<Array2<f32>>>,
    mel_idx: f32,
}

impl Audio2MelSpectrogramV2RT {
    pub fn new(
        sample_rate: u32,
        fft_size: usize,
        hop_size: usize,
        min_level: f32,
        compression_factor: f32,
        amplitude_to_db_factor: f32,
        ref_level_db: f32,
        mel_params: MelParam,
    ) -> Self {
        let mel_banks = utils::mel(mel_params);
        Self {
            sample_rate,
            fft_size,
            hop_size,
            min_level,
            compression_factor,
            amplitude_to_db_factor,
            ref_level_db,
            spectrogram: Spectrogram::new(fft_size, hop_size),
            mel_banks,
            first: true,
            first_out: true,
            residual: None,
            residual_mel: None,
            mel_idx: 0.0,
        }
    }

    pub fn clear(&mut self) {
        self.spectrogram.clear();
        self.residual = None;
        self.residual_mel = None;
        self.first = true;
        self.first_out = true;
        self.mel_idx = 0.0;
    }

    pub fn transform_with_skipping<F>(
        &mut self,
        mut audio: Vec<f32>,
        norm_fn: F,
    ) -> Option<Vec<Array2<f32>>>
    where
        F: Fn(&Array2<f32>) -> Array2<f32>,
    {
        //
        // PRE-PROCESS
        //let (wav_length, frame_count) = parse_audio_length(audio.len(), self.sample_rate, 25);
        // Crop or pad the audio samples
        if let Some(mut residual) = self.residual.take() {
            residual.extend(audio);
            audio = residual;
        }

        if self.first {
            let pad_size = self.fft_size / 2;

            //
            // Zero padding
            let mut left_pad = vec![0.0; pad_size];

            //
            // reflect padding
            // if audio.len() < pad_size {
            //     self.residual = Some(audio);
            //     return None;
            // }

            // // Reflect padding instead of zero padding
            // let mut left_pad = Vec::with_capacity(pad_size);
            // for i in 0..pad_size {
            //     let idx = std::cmp::min(pad_size - 1 - i, audio.len() - 1);
            //     left_pad.push(audio[idx]);
            // }
            // END reflect padding
            //

            left_pad.extend(audio);
            audio = left_pad;

            self.first = false;
        }

        // TRANSFORMS
        //
        // Initialize the Mel spectrogram transformer
        // Compute the Mel spectrogram
        let mut mel_outputs = Vec::new();
        while audio.len() >= self.hop_size {
            let Some(fft) = self
                .spectrogram
                .add(audio.drain(..self.hop_size).as_slice())
            else {
                continue;
            };

            let mel = log_mel_spectrogram(
                &fft,
                &self.mel_banks,
                self.min_level,
                self.compression_factor,
                self.amplitude_to_db_factor,
                self.ref_level_db,
            );
            let mel = norm_fn(&mel);
            mel_outputs.push(mel);
        }

        if !audio.is_empty() {
            self.residual = Some(audio);
        }

        if mel_outputs.is_empty() {
            None
        } else {
            Some(mel_outputs)
        }
    }

    pub fn transform<F>(
        &mut self,
        mut audio: Vec<f32>,
        norm_fn: F,
    ) -> Option<(Array4<f32>, usize, Option<f32>, bool)>
    where
        F: Fn(&Array2<f32>) -> Array2<f32>,
    {
        //
        // PRE-PROCESS
        //let (wav_length, frame_count) = parse_audio_length(audio.len(), self.sample_rate, 25);
        // Crop or pad the audio samples
        if let Some(mut residual) = self.residual.take() {
            residual.extend(audio);
            audio = residual;
        }

        if self.first {
            let pad_size = self.fft_size / 2;

            //
            // Zero padding
            let mut left_pad = vec![0.0; pad_size];

            //
            // reflect padding
            // if audio.len() < pad_size {
            //     self.residual = Some(audio);
            //     return None;
            // }

            // // Reflect padding instead of zero padding
            // let mut left_pad = Vec::with_capacity(pad_size);
            // for i in 0..pad_size {
            //     let idx = std::cmp::min(pad_size - 1 - i, audio.len() - 1);
            //     left_pad.push(audio[idx]);
            // }
            // END reflect padding
            //

            left_pad.extend(audio);
            audio = left_pad;

            self.first = false;
        }

        // TRANSFORMS
        //
        // Initialize the Mel spectrogram transformer
        // Compute the Mel spectrogram
        let mut mel_outputs = Vec::new();
        while audio.len() >= self.hop_size {
            let Some(fft) = self
                .spectrogram
                .add(audio.drain(..self.hop_size).as_slice())
            else {
                continue;
            };

            let mel = log_mel_spectrogram(
                &fft,
                &self.mel_banks,
                self.min_level,
                self.compression_factor,
                self.amplitude_to_db_factor,
                self.ref_level_db,
            );
            let mel = norm_fn(&mel);
            mel_outputs.push(mel);
        }

        if !audio.is_empty() {
            self.residual = Some(audio);
        }

        if let Some(mut mel) = self.residual_mel.take() {
            mel.extend(mel_outputs);
            mel_outputs = mel;
        }

        if mel_outputs.is_empty() {
            None
        } else {
            let start_idx = self.mel_idx;

            let frame_count =
                utils::calculate_frame_count(mel_outputs.len(), start_idx, MEL_STEP_IN_FRAME, 16);

            if frame_count == 0 {
                self.residual_mel = Some(mel_outputs);
                return None;
            }

            let start_idx_round = (start_idx + 0.5) as usize;
            let frame_end_idx =
                (start_idx_round as f32 + MEL_STEP_IN_FRAME * (frame_count - 1) as f32) as usize
                    + 16;

            let next_idx = start_idx + frame_count as f32 * MEL_STEP_IN_FRAME;
            let lower_next_idx = next_idx.floor() as usize;
            let start_idx = next_idx - lower_next_idx as f32;
            self.residual_mel = Some(mel_outputs[lower_next_idx..].to_vec());

            mel_outputs = mel_outputs[start_idx_round..frame_end_idx].to_vec();

            let mut stacked_mel = ndarray::Array4::<f32>::zeros((1, 1, 80, mel_outputs.len()));

            for (i, mel) in mel_outputs.into_iter().enumerate() {
                stacked_mel
                    .index_axis_mut(ndarray::Axis(3), i)
                    .assign(&mel.to_shape((80,)).unwrap());
            }

            self.mel_idx = start_idx;

            let first_out = self.first_out;
            self.first_out = false;

            // Some((stacked_mel, frame_count, Some(start_idx), first_out))
            // pass with first mel ones.
            Some((stacked_mel, frame_count, Some(0.0), first_out))
        }
        // // .map(|v| {
        // //     let raw_data = v.as_slice().unwrap();
        // //     cast_slice(raw_data).to_vec()
        // // });

        // mel_bytes
    }
}
