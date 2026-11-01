"""OpenCV Studio: a small Streamlit app built on the OpenCV notebook concepts.

Run locally:  streamlit run app.py
"""
import cv2
import numpy as np
import streamlit as st

import processing as P

st.set_page_config(page_title='OpenCV Studio', page_icon='🎨', layout='wide')

# ---------------- Look and feel ----------------
st.markdown("""
<style>
/* Page background: a soft pastel wash */
.stApp {
    background: linear-gradient(180deg, #F5F3FF 0%, #FFFFFF 35%, #ECFEFF 100%);
}
.block-container { padding-top: 2rem; max-width: 1300px; }

/* Hero banner */
.hero {
    background: linear-gradient(120deg, #7C3AED 0%, #DB2777 50%, #F59E0B 100%);
    border-radius: 22px; padding: 28px 32px; color: white;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25); margin-bottom: 18px;
}
.hero h1 { color: white; font-size: 2.4rem; margin: 0 0 6px 0; padding: 0; }
.hero p  { color: rgba(255,255,255,0.95); font-size: 1.08rem; margin: 0; }
.chips { margin-top: 14px; }
.chip {
    display: inline-block; background: rgba(255,255,255,0.22); color: white;
    border: 1px solid rgba(255,255,255,0.45); border-radius: 999px;
    padding: 4px 12px; margin: 4px 6px 0 0; font-size: 0.88rem; font-weight: 600;
}

/* Step cards on the welcome screen */
.steps { display: flex; gap: 14px; flex-wrap: wrap; margin: 6px 0 10px 0; }
.step {
    flex: 1 1 200px; border-radius: 18px; padding: 18px; color: #1F1B2E;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
}
.step .num { font-size: 1.6rem; }
.step b { display: block; font-size: 1.05rem; margin: 4px 0; }
.s1 { background: #EDE9FE; } .s2 { background: #FCE7F3; }
.s3 { background: #FEF3C7; } .s4 { background: #CFFAFE; }

/* Tabs: big, rounded, colorful */
.stTabs [data-baseweb="tab-list"] { gap: 8px; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] {
    background: #FFFFFF; border: 2px solid #E9D5FF; border-radius: 14px;
    padding: 10px 18px; height: auto; font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(120deg, #7C3AED, #DB2777); color: white !important;
    border-color: transparent;
}
.stTabs [aria-selected="true"] p { color: white !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }

/* Colored panel at the top of each tab */
.panel {
    border-radius: 16px; padding: 14px 18px; margin: 12px 0 14px 0;
    border-left: 6px solid; font-size: 0.98rem;
}
.panel h3 { margin: 0 0 4px 0; padding: 0; font-size: 1.25rem; }
.p-sun  { background: #FEF3C7; border-color: #F59E0B; }
.p-doc  { background: #E0E7FF; border-color: #4F46E5; }
.p-cut  { background: #DCFCE7; border-color: #16A34A; }
.p-pen  { background: #FCE7F3; border-color: #DB2777; }

/* Before / After labels */
.badge {
    display: inline-block; border-radius: 999px; padding: 4px 14px;
    font-weight: 700; font-size: 0.9rem; margin-bottom: 6px;
}
.before { background: #E5E7EB; color: #374151; }
.after  { background: linear-gradient(120deg, #7C3AED, #DB2777); color: white; }

/* Image frames */
[data-testid="stImage"] img {
    border-radius: 14px; box-shadow: 0 6px 18px rgba(0,0,0,0.10);
}

/* Download button */
.stDownloadButton button {
    background: linear-gradient(120deg, #16A34A, #0EA5E9); color: white;
    border: none; border-radius: 12px; font-weight: 700; padding: 0.5rem 1.2rem;
}
.stDownloadButton button:hover { filter: brightness(1.08); color: white; }

/* Upload box */
[data-testid="stFileUploader"] section {
    border: 2px dashed #A78BFA; border-radius: 16px; background: #FAF5FF;
}

.footer { text-align: center; color: #6B7280; font-size: 0.9rem; padding: 10px 0 4px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🎨 OpenCV Studio</h1>
  <p>Upload a photo and play with it: fix the lighting, clean up documents,
     remove backgrounds, and add captions. Every control updates the picture instantly.</p>
  <div class="chips">
    <span class="chip">☀️ Image arithmetic</span>
    <span class="chip">⚫ Thresholding</span>
    <span class="chip">✂️ Alpha channels</span>
    <span class="chip">✏️ Drawing & text</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- Sidebar guide ----------------
with st.sidebar:
    st.markdown('## 🧭 Quick guide')
    st.markdown("""
**1. Upload** a JPG or PNG at the top.

**2. Pick a tab** for what you want to do.

**3. Move the controls**: the result updates right away.

**4. Download** your result as a PNG.
""")
    st.markdown('---')
    st.markdown('### 💡 Which photo works best?')
    st.markdown("""
- ☀️ **Brightness**: any photo, ideally with bright skies or white walls
- ⚫ **Document Cleaner**: notes or sheet music with shadows
- ✂️ **Background Remover**: an object on a plain white or black background
- ✏️ **Caption**: any photo you want to label
""")

# ---------------- Upload ----------------
uploaded = st.file_uploader('📤 Upload an image (JPG or PNG)', type=['jpg', 'jpeg', 'png', 'bmp', 'webp'])
if uploaded is None:
    st.markdown("""
<div class="steps">
  <div class="step s1"><div class="num">📤</div><b>1. Upload</b>Drop any photo into the box above.</div>
  <div class="step s2"><div class="num">🗂️</div><b>2. Choose a tool</b>Four tabs, one for each OpenCV skill.</div>
  <div class="step s3"><div class="num">🎚️</div><b>3. Adjust</b>Sliders and buttons change the result live.</div>
  <div class="step s4"><div class="num">💾</div><b>4. Download</b>Save the result as a PNG.</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div class="footer">Built with OpenCV and Streamlit</div>', unsafe_allow_html=True)
    st.stop()

data = np.frombuffer(uploaded.getvalue(), np.uint8)
img = cv2.imdecode(data, cv2.IMREAD_COLOR)
if img is None:
    st.error("😕 Couldn't read that file as an image. Try a JPG or PNG.")
    st.stop()
img = P.fit(img)
h, w = img.shape[:2]
st.success(f'✅ Loaded **{uploaded.name}** ({w} × {h} px). Pick a tab below to get started.')


def rgb(bgr):
    """OpenCV stores BGR; Streamlit shows RGB."""
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def png_bytes(image):
    ok, buf = cv2.imencode('.png', image)
    return buf.tobytes()


def panel(css_class, title, body):
    st.markdown(f'<div class="panel {css_class}"><h3>{title}</h3>{body}</div>', unsafe_allow_html=True)


def side_by_side(processed, caption, download_name, download_img=None):
    left, right = st.columns(2)
    with left:
        st.markdown('<span class="badge before">BEFORE</span>', unsafe_allow_html=True)
        st.image(rgb(img), caption='Original')
    with right:
        st.markdown('<span class="badge after">AFTER</span>', unsafe_allow_html=True)
        st.image(rgb(processed), caption=caption)
        st.download_button('💾 Download result (PNG)',
                           png_bytes(download_img if download_img is not None else processed),
                           file_name=download_name, mime='image/png', key=download_name)


tab_adjust, tab_thresh, tab_bg, tab_caption = st.tabs(
    ['☀️ Brightness & Contrast', '⚫ Document Cleaner', '✂️ Background Remover', '✏️ Caption & Highlight'])

# ---------------- Tab 1: image arithmetic ----------------
with tab_adjust:
    panel('p-sun', '☀️ Brightness & Contrast',
          'Brightness uses <code>cv2.add</code> / <code>cv2.subtract</code>, contrast uses '
          '<code>cv2.multiply</code>. 🧪 <b>Try this:</b> untick <b>Clip values</b> and push contrast up. '
          'Bright areas go past 255 and wrap around into dark, strange colors.')
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        brightness = c1.slider('🔆 Brightness', -150, 150, 0, step=5)
        contrast = c2.slider('🌗 Contrast (scale factor)', 0.2, 3.0, 1.0, step=0.05)
        clip = c3.checkbox('✂️ Clip values to 0–255 (np.clip)', value=True)
        if not clip:
            c3.warning('Overflow mode: bright pixels will wrap around!')
    out = P.adjust(img, brightness, contrast, clip)
    side_by_side(out, f'Brightness {brightness:+d}, contrast ×{contrast:.2f}, '
                      f'{"clipped" if clip else "NOT clipped (overflow!)"}', 'adjusted.png')

# ---------------- Tab 2: thresholding ----------------
with tab_thresh:
    panel('p-doc', '⚫ Document Cleaner',
          'Turns a photo of notes or sheet music into clean black and white. <b>Global</b> uses one cutoff '
          'for the whole page, so shadows ruin it. <b>Adaptive</b> picks a cutoff for each pixel from its '
          'neighborhood, so it handles uneven lighting. <b>Otsu</b> finds the best global cutoff for you.')
    with st.container(border=True):
        c1, c2 = st.columns([1, 2])
        method = c1.selectbox('🧰 Method', P.THRESH_METHODS, index=4)
        thresh_val, block, cval = 127, 25, 10
        if method in ('Global', 'Global (inverse)'):
            thresh_val = c2.slider('🎚️ Threshold', 0, 255, 127)
        elif method.startswith('Adaptive'):
            cc1, cc2 = c2.columns(2)
            block = cc1.slider('🔲 Neighborhood size (block size, odd)', 3, 101, 25, step=2)
            cval = cc2.slider('➖ C (subtracted from the local mean)', -20, 40, 10)
        else:
            c2.info('🤖 Otsu picks the threshold automatically, so there is nothing to tune.')
    out, used = P.threshold(img, method, thresh_val, block, cval)
    if used is not None:
        st.metric('Threshold used', f'{used:.0f}')
    label = f'{method}' + (f', threshold = {used:.0f}' if used is not None else f', block {block}, C {cval}')
    side_by_side(out, label, 'cleaned.png')

# ---------------- Tab 3: alpha channel ----------------
with tab_bg:
    panel('p-cut', '✂️ Background Remover',
          'A threshold finds the background, <code>cv2.bitwise_not</code> flips it into a mask, and '
          '<code>cv2.merge</code> attaches the mask as the 4th (alpha) channel. Works best on an object '
          'against a plain light or dark background. The checkerboard shows the see-through parts.')
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        bg_type = c1.radio('🖼️ Background is…', ['Light', 'Dark'], horizontal=True)
        auto = c1.checkbox('🤖 Pick threshold automatically (Otsu)')
        bg_thresh = c2.slider('🎚️ Background threshold', 0, 255, 230 if bg_type == 'Light' else 40,
                              disabled=auto)
        transparency = c3.slider('👻 Background transparency (%)', 0, 100, 100)
    opacity = round(255 * transparency / 100)
    bgra, mask = P.remove_background(img, bg_thresh, bg_type == 'Light', auto, opacity)
    preview = P.composite(bgra, P.checkerboard(img.shape))
    side_by_side(preview, f'Transparent PNG (background alpha = {255 - opacity})',
                 'transparent.png', download_img=bgra)
    with st.expander('🔍 Show the mask'):
        st.image(mask, caption='Alpha mask: white = kept, black = transparent')

# ---------------- Tab 4: drawing and annotation ----------------
with tab_caption:
    panel('p-pen', '✏️ Caption & Highlight',
          'Adds centered text with <code>cv2.putText</code> and highlights part of the picture with '
          '<code>cv2.rectangle</code> or <code>cv2.circle</code>.')
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        c1.markdown('**📝 Text**')
        text = c1.text_input('Caption', 'My photo')
        font = c1.selectbox('🔤 Font', list(P.FONTS))
        position = c1.radio('📍 Position', ['Top', 'Middle', 'Bottom'], index=2, horizontal=True)
        c2.markdown('**🎨 Style**')
        default_scale = round(max(0.5, w / 700), 1)
        scale = c2.slider('🔠 Text size', 0.3, 6.0, float(min(default_scale, 6.0)), step=0.1)
        thick = c2.slider('🖊️ Line thickness', 1, 12, max(1, int(w / 400)))
        color = c2.color_picker('🌈 Text color', '#FFFFFF')
        c3.markdown('**🔲 Highlight**')
        shape = c3.radio('Shape', ['None', 'Rectangle', 'Circle'], horizontal=True, index=1)
        box_color = c3.color_picker('🌈 Highlight color', '#FF00FF')
        box = circle = None
        if shape == 'Rectangle':
            xs = c3.slider('↔️ Box left / right (%)', 0, 100, (25, 75))
            ys = c3.slider('↕️ Box top / bottom (%)', 0, 100, (20, 70))
            box = (xs[0] / 100, ys[0] / 100, xs[1] / 100, ys[1] / 100)
        elif shape == 'Circle':
            cx = c3.slider('↔️ Center x (%)', 0, 100, 50)
            cy = c3.slider('↕️ Center y (%)', 0, 100, 45)
            r = c3.slider('⭕ Radius (%)', 1, 70, 20)
            circle = (cx / 100, cy / 100, r / 100)
    out = P.annotate(img, text, font, scale, color, thick, position, box, box_color, circle)
    side_by_side(out, 'Annotated', 'captioned.png')

st.markdown('<div class="footer">🎨 Built with OpenCV and Streamlit · image arithmetic · thresholding · '
            'alpha channels & masks · drawing & annotation</div>', unsafe_allow_html=True)
