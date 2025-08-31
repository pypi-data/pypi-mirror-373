# vmlab-py-package

pypi link : [vmlab_py](https://pypi.org/project/vmlab-py/)

Rust 기반으로 구현된 Python 패키지 **`vmlab-py`**

## 목표

- Native 언어로 구현하여 python내에서 성능 효율성 높이기

### **프로젝트 정보**

- 현재 버전 **0.1.14**
- GitHub Repository: [vmlab-py-package](https://github.com/VMONSTER-AI/vmlab-py-package)
- PyPI: [vmlab-py](https://pypi.org/project/vmlab-py/)

## 설치

```bash
pip install vmlab-py==0.1.19
```

### 모듈에 포함된 함수

### 1. **a2ev1_melspectrogram**

- **설명**: Audio2Exp V1 모델을 위한 Mel Spectrogram 생성 (샘플레이트가 다를 경우 16000으로 변환)
- **입력**:
    - `wav` (`numpy.ndarray`): numpy.ndarray 형태의 WAV 데이터
    - `sample_rate` (`u32`): `wav` 의 sample rate
- **출력**:
    - Mel Spectrogram을 바이트 리스트로 반환

---

### 2. **a2ev2_melspectrogram**

- **설명**: Audio2Exp V2 모델을 위한 Mel Spectrogram 생성 (샘플레이트가 다를 경우 16000으로 변환)
- **입력**:
    - `wav` (`numpy.ndarray`): numpy.ndarray 형태의 WAV 데이터
    - `sample_rate` (`u32`): `wav` 의 sample rate
- **출력**:
    - Mel Spectrogram을 바이트 리스트로 반환

---

### 3. **dummy_func**

- **설명**: 초기화를 위한 더미 함수
- **출력**:
    - 더미 값 `0` 반환

---

### 4. **reconstruct_mask**

- **설명**: CompactMaskModel로부터 그레이스케일 마스크 복원
- **입력**:
    - `bytes` (`PyBytes`): CompactMaskModel의 직렬화된 데이터
    - `width` (`usize`): 출력 이미지의 너비
    - `height` (`usize`): 출력 이미지의 높이
    - `scale` (`Tuple(f32, str)`): 마스크의 크기 조정 비율 및 리사이징 필터 타입 (옵션)
        - **FilterType**:
            - **NEAREST**: "nearest" 또는 "lowest"
            - **LINEAR**: "linear", "triangle", "low"
            - **CATMULLROM**: "catmullrom", "cubic", "medium"
            - **GAUSSIAN**: "gaussian", "high"
            - **LANZOS**: "lanzos", "highest"
- **출력**:
    - 복원된 마스크를 `numpy.ndarray` 형태로 반환 (H, W)


## Publish

### Requirements

```bash
pip install maturin
```

### Build the python package

```bash
maturin build --release
```

### Test in locally

```
pip install target/wheels/{GENERATED_WHEELS_NAME}.whl
```

### Publish to PyPI

```
maturin publish
```

### Build for arm and upload file

manylinux에서 빌드. (manylinux는 다양한 리눅스 배포판에서 동작할 수 있는 **바이너리 파이썬 패키지(whl 파일)**를 제공하기 위해 만들어짐.)

Dockerfile에서 빌드 및 업로드까지 해결. ( FROM quay.io/pypa/manylinux_2_28_aarch64 )

**Build (on x86 host)**:

- 변수 PASS에 토큰 입력 필요

```bash
docker buildx build --platform linux/arm64 --build-arg PASS=<token> -t maturin-arm-builder .
```

