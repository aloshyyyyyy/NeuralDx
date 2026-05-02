# Setup Notes

## Model File
The `model_VGG.keras` file is not pushed to GitHub (too large).
To generate it, run the training script after downloading the dataset.

## Dataset
Dataset not included. Structure needed:
```
Covid19-dataset/
├── train/
│   ├── Covid/
│   ├── Normal/
│   └── Viral Pneumonia/
└── test/
    ├── Covid/
    ├── Normal/
    └── Viral Pneumonia/
```

## Mac M-Series Setup
For Apple Silicon GPU acceleration:
```bash
pip install tensorflow-macos tensorflow-metal
```

## Environment
Python 3.9 recommended.
