use ndarray::{s, Array1, Array2, Axis};
use num::Complex;

pub fn calculate_frame_count(
    length: usize,
    start_idx: f32,
    step_size: f32,
    window_size: usize,
) -> usize {
    if length < window_size {
        return 0;
    }

    let mut count = 0;
    let mut current_pos = start_idx;

    while ((current_pos + 0.5) as usize + window_size) <= length {
        count += 1;
        current_pos += step_size;
    }

    count
}

pub fn crop_pad_audio(mut wav: Vec<f32>, mut audio_length: usize, pad_size: usize) -> Vec<f32> {
    audio_length += pad_size;
    if wav.len() > audio_length {
        wav = wav[..audio_length].to_vec();
    } else if wav.len() < audio_length {
        wav.extend(vec![0.0; audio_length - wav.len()]);
    }
    wav
}

pub fn parse_audio_length(audio_length: usize, sr: u32, fps: u32) -> (usize, usize) {
    let bits_per_frame = sr as f32 / fps as f32;
    let num_frames = (audio_length as f32 / bits_per_frame) as usize;
    let adjusted_audio_length = (num_frames as f32 * bits_per_frame) as usize;
    (adjusted_audio_length, num_frames)
}

pub fn preemphasis(wav: &mut Vec<f32>, k: f32) {
    let mut previous_sample = 0.0;
    for sample in wav.iter_mut() {
        let current_sample = *sample;
        *sample = current_sample - k * previous_sample;
        previous_sample = current_sample;
    }
}
pub struct MelParam {
    pub sr: f32,
    pub n_fft: usize,
    pub n_mels: usize,
    pub f_min: Option<f32>,
    pub f_max: Option<f32>,
    pub htk: bool,
    pub norm: bool,
}

pub fn mel(params: MelParam) -> Array2<f32> {
    let MelParam {
        sr,
        n_fft,
        n_mels,
        f_min,
        f_max,
        htk,
        norm,
    } = params;

    let fftfreqs = fft_frequencies(sr, n_fft);
    let f_min = f_min.unwrap_or(0.0); // Minimum frequency
    let f_max = f_max.unwrap_or(sr / 2.0); // Maximum frequency
    let mel_f = mel_frequencies(n_mels + 2, f_min, f_max, htk);

    // calculate the triangular mel filter bank weights for mel-frequency cepstral coefficient (MFCC) computation
    let fdiff = &mel_f.slice(s![1..n_mels + 2]) - &mel_f.slice(s![..n_mels + 1]);
    let ramps = &mel_f.slice(s![..n_mels + 2]).insert_axis(Axis(1)) - &fftfreqs;

    let mut weights = Array2::zeros((n_mels, n_fft / 2 + 1));

    for i in 0..n_mels {
        let lower = -&ramps.row(i) / fdiff[i];
        let upper = &ramps.row(i + 2) / fdiff[i + 1];

        weights
            .row_mut(i)
            .assign(&lower.mapv(|x| x.max(0.0).min(1.0)));

        weights
            .row_mut(i)
            .zip_mut_with(&upper.mapv(|x| x.max(0.0).min(1.0)), |a, &b| {
                *a = (*a).min(b);
            });
    }

    if norm {
        // Slaney-style mel is scaled to be approx constant energy per channel
        let enorm = 2.0 / (&mel_f.slice(s![2..n_mels + 2]) - &mel_f.slice(s![..n_mels]));
        weights *= &enorm.insert_axis(Axis(1));
    }

    weights
}

pub fn fft_frequencies(sr: f32, n_fft: usize) -> Array1<f32> {
    let step = sr / n_fft as f32;
    let freqs: Array1<f32> = Array1::from_shape_fn(n_fft / 2 + 1, |i| step * i as f32);
    freqs
}

pub fn hz_to_mel(frequency: f32, htk: bool) -> f32 {
    if htk {
        return 2595.0 * (1.0 + frequency / 700.0).log10();
    }

    let f_min: f32 = 0.0;
    let f_sp: f32 = 200.0 / 3.0;
    let min_log_hz: f32 = 1000.0;
    let min_log_mel: f32 = (min_log_hz - f_min) / f_sp;
    let logstep: f32 = (6.4f32).ln() / 27.0;

    if frequency >= min_log_hz {
        min_log_mel + ((frequency / min_log_hz).ln() / logstep)
    } else {
        (frequency - f_min) / f_sp
    }
}

pub fn mel_to_hz(mel: f32, htk: bool) -> f32 {
    if htk {
        return 700.0 * (10.0f32.powf(mel / 2595.0) - 1.0);
    }

    let f_min: f32 = 0.0;
    let f_sp: f32 = 200.0 / 3.0;
    let min_log_hz: f32 = 1000.0;
    let min_log_mel: f32 = (min_log_hz - f_min) / f_sp;
    let logstep: f32 = (6.4f32).ln() / 27.0;

    if mel >= min_log_mel {
        min_log_hz * (logstep * (mel - min_log_mel)).exp()
    } else {
        f_min + f_sp * mel
    }
}

pub fn mels_to_hz(mels: Array1<f32>, htk: bool) -> Array1<f32> {
    mels.mapv(|mel| mel_to_hz(mel, htk))
}

pub fn mel_frequencies(n_mels: usize, fmin: f32, fmax: f32, htk: bool) -> Array1<f32> {
    let min_mel = hz_to_mel(fmin, htk);
    let max_mel = hz_to_mel(fmax, htk);

    let mels = Array1::linspace(min_mel, max_mel, n_mels);
    mels_to_hz(mels, htk)
}

pub fn log_mel_spectrogram(
    stft: &Array1<Complex<f32>>,
    mel_filters: &Array2<f32>,
    epsilon: f32,
    compression_factor: f32,
    amplitude_to_db_factor: f32,
    ref_leve_db: f32,
) -> Array2<f32> {
    // magnitudes
    let mag = stft
        .iter()
        .map(|v| (v.norm_sqr() + 1e-9).sqrt())
        .take(stft.len() / 2 + 1)
        .collect::<Vec<_>>();
    // print the column by column of the magnitudes
    // magnitudes_padded.push(0.0);
    // println!("{:?}", mag);

    let mag_shaped = Array2::from_shape_vec((1, mag.len()), mag).unwrap();

    let mel_spec = mel_filters.dot(&mag_shaped.t()).mapv(|v| {
        ((v.max(epsilon) * compression_factor).log10() * amplitude_to_db_factor) - ref_leve_db
    });

    // print method arguments
    mel_spec
}

pub fn norm_mean_std(mel_spec: &Array2<f32>, mel_spec_mean: f32, mel_spec_std: f32) -> Array2<f32> {
    mel_spec.mapv(|x| (x - mel_spec_mean) / mel_spec_std)
}

pub fn norm_mel(mel_spec: &Array2<f32>, max_abs_value: f32, min_level_db: f32) -> Array2<f32> {
    let v = 2.0 * max_abs_value;

    let clamped: Array2<f32> = mel_spec.mapv(|x| {
        (v * ((x - min_level_db) / -min_level_db) - max_abs_value)
            .max(-max_abs_value)
            .min(max_abs_value)
    });

    clamped
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_calculate_frame_count() {
        // length: usize,
        // start_idx: f32,
        // step_size: f32,
        // mut window_size: usize,
        // 0.0, 160.0, 320.0, 480.0(~880.0)
        assert_eq!(calculate_frame_count(1000, 0.0, 160.0, 400), 4);

        //
        assert_eq!(calculate_frame_count(100, 0.0, 160.0, 200), 0);

        //
        assert_eq!(calculate_frame_count(1000, 700.0, 160.0, 400), 0);

        // 0.0
        assert_eq!(calculate_frame_count(400, 0.0, 160.0, 400), 1);

        // 0.0, 100.0, 200.0
        assert_eq!(calculate_frame_count(400, 0.0, 100.0, 200), 3);
    }
}
