# OpenCV Studio

A small Streamlit web app built on the OpenCV notebook concepts. Upload any image and use the four tabs:

| Tab | Notebook concept | Controls |
|---|---|---|
| ☀️ Brightness & Contrast | Image arithmetic: `cv2.add`, `cv2.subtract`, `cv2.multiply`, `np.clip` | Brightness and contrast sliders, plus a clipping checkbox that lets you watch overflow wrap around past 255 |
| ⚫ Document Cleaner | Thresholding: global, inverse, Otsu, adaptive mean, adaptive Gaussian | Method dropdown, threshold slider, block size and C sliders |
| ✂️ Background Remover | Alpha channels and masks: `cv2.threshold`, `cv2.bitwise_not`, `cv2.merge` | Light/dark background, threshold slider or Otsu, transparency slider, download a transparent PNG |
| ✏️ Caption & Highlight | Drawing and annotation: `cv2.putText`, `cv2.rectangle`, `cv2.circle` | Caption text, font, size, color, position, and a rectangle or circle highlight |

Every tab shows the original and the processed image side by side, and every result can be downloaded as a PNG.

## Files
- `app.py`: the Streamlit interface
- `processing.py`: all the OpenCV image processing
- `requirements.txt`: Python packages
- `.streamlit/config.toml`: the color theme

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
