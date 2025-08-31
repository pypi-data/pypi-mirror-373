use super::{
    transforms::{Audio2MelSpectrogram, TransformResult},
    utils::{norm_mean_std, norm_mel, MelParam},
};

pub const MINIMUM_MEL_V1: f32 = -4.0;
pub const MINIMUM_MEL_V2: f32 = -2.6588821;

pub trait PreAudio2ExpTrait {
    fn transform(&mut self, audio: Vec<f32>) -> TransformResult;
}
pub struct PreAudio2ExpV2 {
    transformer: Audio2MelSpectrogram,
}

impl PreAudio2ExpV2 {
    pub fn new() -> Self {
        Self {
            transformer: Audio2MelSpectrogram::new(
                16000,
                800,
                200,
                1e-5,
                1.0,
                1.0,
                0.0,
                true,
                None,
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
}

impl PreAudio2ExpTrait for PreAudio2ExpV2 {
    fn transform(&mut self, audio: Vec<f32>) -> TransformResult {
        TransformResult::new(self.transformer.transform(audio, |v| {
            norm_mean_std(v, -2.123307466506958, 1.0819180011749268)
        }))
    }
}

pub struct PreAudio2ExpV1 {
    min_db: f32,
    transformer: Audio2MelSpectrogram,
}

impl PreAudio2ExpV1 {
    pub fn new() -> Self {
        let min_db = -100.0;
        let min_level = (min_db / 20.0 * f32::ln(10.0)).exp();
        let ref_level_db = 20.0;
        Self {
            min_db,
            transformer: Audio2MelSpectrogram::new(
                16000,
                800,
                200,
                min_level,
                1.0,
                20.0,
                ref_level_db,
                false,
                Some(0.97),
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
}

impl PreAudio2ExpTrait for PreAudio2ExpV1 {
    fn transform(&mut self, audio: Vec<f32>) -> TransformResult {
        TransformResult::new(
            self.transformer
                .transform(audio, |v| norm_mel(v, 4.0, self.min_db)),
        )
    }
}

//pub struct PreAudio2ExpV1RT {
//    min_db: f32,
//    transformer: Audio2MelSpectrogramRT,
//}
//
//impl PreAudio2ExpV1RT {
//    pub fn new() -> Self {
//        let min_db = -100.0;
//        let min_level = (min_db / 20.0 * f32::ln(10.0)).exp();
//        let ref_level_db = 20.0;
//        Self {
//            min_db,
//            transformer: Audio2MelSpectrogramRT::new(
//                16000,
//                800,
//                200,
//                min_level,
//                1.0,
//                20.0,
//                ref_level_db,
//                false,
//                Some(0.97),
//                MelParam {
//                    sr: 16000.0,
//                    n_fft: 800,
//                    n_mels: 80,
//                    f_min: Some(55.0),
//                    f_max: Some(7600.0),
//                    htk: false,
//                    norm: true,
//                },
//            ),
//        }
//    }
//    pub fn intialize(&mut self, audio: Vec<f32>, chunks: usize) -> usize {
//        self.transformer.initialize(audio, chunks)
//    }
//
//    pub fn next(&mut self) -> TransformResult {
//        TransformResult::new(self.transformer.next(|v| norm_mel(v, 4.0, self.min_db)))
//    }
//}
