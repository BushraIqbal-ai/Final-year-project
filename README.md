# BrainMap XAI — NeuroScan AI

**Explainable Deep Learning Framework for Parkinson's Disease Stage Classification from Brain MRI**

> Final Year Project — BS (Information Technology)
> Institute of Computing, MNS-University of Agriculture, Multan, Pakistan
> Session 2022–2026

---

## 👥 Team

| Name | Registration No. |
|---|---|
| Helia Karim | 2022-UAM-2208 |
| Bushra Iqbal | 2022-UAM-2224 |
| Muhammad Zulqarnain | 2022-UAM-2248 |

**Supervisor:** Mr. Muhammad Shehzad
**Director, Institute of Computing:** Prof. Dr. Salman Qadri

---

## 📌 Overview

**C3BAM-SE-XAI v2** is a deep learning framework that classifies Parkinson's disease stages from brain MRI images while remaining interpretable to clinicians. It combines a CNN backbone (EfficientNet-B3) with a **dual attention mechanism** — **CBAM** (Convolutional Block Attention Module) + **Squeeze-and-Excitation (SE)** — and integrates **Grad-CAM** based Explainable AI so predictions come with visual heatmaps showing *which brain regions* influenced the decision, instead of a black-box output.

The trained model is served through a web application, **NeuroScan AI**, that lets healthcare professionals upload an MRI scan, get a five-class prediction with confidence scores, and view the Grad-CAM overlay alongside a downloadable clinical report.

### Problem it solves
- Late/inaccurate clinical diagnosis of Parkinson's disease
- Over-reliance on specialist expertise
- Existing automated systems have low accuracy, poor generalization, and limited datasets
- Most deep learning models are black boxes with no explainability
- Lack of multi-class (staged) classification — most prior systems are binary

---

## 🧠 Classification Classes

The model performs **five-class** classification:

1. Non-Demented
2. Very-Mild-Demented
3. Mild-Demented
4. Moderate-Demented
5. Severe-Demented

---

## 🏗️ Model Architecture — C3BAM-SE-XAI v2 (Implemented)

```
Input Image (224×224 RGB)
        ↓
EfficientNet-B3 backbone (pretrained ImageNet features)
        ↓
CBAM + SE refinement (combined in one block)
        ↓
GAP + GMP dual pooling → concat (3072-d feature vector)
        ↓
Deep classification head: 1024 → 512 → 256 → 5 classes
        ↓
Output (5-class prediction) + Grad-CAM (XAI)
```

| Component | Purpose |
|---|---|
| **EfficientNet-B3 backbone** | Pretrained feature extractor (replaces the plain custom CNN used in the base paper) |
| **CBAM + SE (combined block)** | Single fused attention block — channel + spatial attention (CBAM) refined further by Squeeze-and-Excitation (SE) channel recalibration |
| **Dual Pooling (GAP + GMP)** | Global Average Pooling and Global Max Pooling are computed in parallel and concatenated (→ 3072-d) instead of a simple flatten, capturing both average and peak activation signals |
| **Deep Classification Head** | Fully connected layers 1024 → 512 → 256 → 5, replacing the base paper's single flatten→dense classifier |
| **Nadam Optimizer** | Stable convergence during training (lr = 0.00015, momentum = 0.6001) |
| **Test-Time Augmentation (TTA ×5)** | Averages predictions over 5 augmented versions of each test image for robustness |
| **Grad-CAM (XAI Module)** | Generates gradient-weighted heatmaps explaining predictions |
| **Label Smoothing Loss** | Improves generalization and reduces overconfidence |

> **Note:** This differs from the base/reference paper architecture, which used a custom CNN (Conv→MaxPool→ReLU) with 3 separate CBAM blocks and a simple flatten→dense classifier. The implemented version upgrades the backbone to EfficientNet-B3, fuses CBAM+SE into one refinement block, and adds dual (GAP+GMP) pooling before a deeper classification head.

**Preprocessing/Augmentation:** rotation (±20°), horizontal flip, shear, zoom, width/height shift, resizing to 150×150 (training) / 224×224 (inference), normalization — used to fix severe class imbalance (each class balanced to 1,000 training samples).

---

## 📊 Results

**Trained for 72 epochs** on the Parkinson's Disease Dementia MRI dataset (Kaggle).

| Metric | Train | Validation | Validation (TTA ×5) |
|---|---|---|---|
| Accuracy | 98.72% | 94.71% | **95.06%** |
| Loss | 0.2754 | 0.1960 | — |

**Per-Class Report (Validation):**

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| Mild-Demented | 0.887 | 0.885 | 0.886 | 293 |
| Moderate-Demented | 0.975 | 0.987 | 0.981 | 239 |
| Non-Demented | 0.871 | 0.948 | 0.908 | 192 |
| Severe-Demented | 1.000 | 0.750 | 0.857 | 4 |
| Very-Mild-Demented | 1.000 | 1.000 | 1.000 | 142 |
| **Weighted Avg** | **0.948** | **0.947** | **0.947** | 870 |

> Severe-Demented has low support (only 4 validation samples) — a dataset limitation, not a model weakness. Mild-Demented is the hardest class due to boundary overlap with Non-Demented.

---

## 🛠️ Tech Stack

### Model / Training (Python)
- **Python 3.10+**
- **PyTorch 2.x** — core deep learning framework
- **TorchVision 0.15+** — pretrained EfficientNet-B3 backbone, transforms
- **Albumentations 1.3+** — advanced augmentation pipeline
- **OpenCV (cv2) 4.x** — image processing, Grad-CAM overlay rendering
- **NumPy 1.24+**, **Scikit-learn 1.2+** — metrics, class weights, confusion matrix
- **Matplotlib / Seaborn** — training curves, confusion matrix heatmaps

### Development Environment
- Jupyter Notebook
- Google Colab (GPU) / Local CUDA GPU
- Git (version control)

### Web Application (NeuroScan AI)
- **Client-side:** HTML5, CSS3, JavaScript (dynamic/asynchronous UI updates without page reload)
- **Server-side:** **Flask (Python)** — hosts the `/predict` inference API, session management, logging/audit trail
- Model loaded directly inside the Flask app (same Python/PyTorch runtime as training)
- Flask handles image upload, server-side preprocessing (resize/normalize), inference, Grad-CAM generation, and returns JSON (class, confidence, Grad-CAM image as base64)

> **Note:** The original plan (per the thesis document) was an ASP.NET + VB.NET server-side stack. This was later changed to a **Flask** backend, which integrates more naturally with the PyTorch model since both training and serving run in Python.

### Hardware Requirements (Training)
- NVIDIA CUDA-capable GPU, ≥ 8 GB VRAM recommended
- 16 GB+ RAM
- SSD storage recommended
- CUDA 11.x / 12.x

### Web App System Requirements (End User)
| Requirement | Minimum | Recommended |
|---|---|---|
| Browser | Chrome 90+ / Firefox 88+ | Chrome 120+ / Edge 120+ |
| Screen Resolution | 1280×720 | 1920×1080+ |
| Internet | Required | Broadband ≥ 10 Mbps |
| MRI Format | JPG / PNG | PNG, 512×512+ |
| File Size | ≤ 16 MB | 1–5 MB |

---

## ✨ Features (NeuroScan AI Web App)

- Secure login/registration (authentication)
- MRI upload with client-side + server-side validation (format, file size)
- Five-class Parkinson's stage prediction with confidence scores
- Grad-CAM heatmap overlay on the uploaded MRI
- Downloadable/structured Analysis Result Report
- Analysis History with search & filter
- Dashboard with analytics summary
- Pages: Login, Home, How It Works, About, Dashboard, Analyze, History

---

## 🔄 How It Works (Pipeline)

1. Clinician uploads an MRI scan via the UI
2. UI validates format and forwards image to the Preprocessing Module
3. Image is resized (150×150), normalized, and TTA ×5 variants generated
4. Preprocessed tensor batch passed to the C3BAM-SE-XAI model
5. Model applies Channel Attention (CBAM) → Spatial Attention (CBAM) → SE recalibration → Softmax (5-class output)
6. If confidence is below threshold, a low-confidence warning is shown
7. Grad-CAM engine computes the gradient-weighted heatmap for the predicted class
8. UI renders prediction, confidence scores, and Grad-CAM overlay
9. A structured classification report is generated and saved

---

## 📁 Suggested Repository Structure

```
BrainMap-XAI/
├── notebooks/
│   └── Architecture.ipynb          # model architecture, training, GPU setup
├── models/
│   └── best_model.pt               # trained model weights
├── src/
│   ├── dataset.py                  # SmartDataset pipeline
│   ├── attention.py                # CBAM + SE blocks
│   ├── model.py                    # C3BAMSEXAIv2 architecture
│   ├── train.py                    # training loop / config
│   ├── losses.py                   # Label Smoothing Loss
│   ├── gradcam.py                  # Grad-CAM XAI module
│   └── tta.py                      # Test-Time Augmentation
├── webapp/
│   ├── static/ & templates/         # HTML5, CSS3, JS (Flask frontend)
│   └── app.py                      # Flask backend — /predict inference API
├── reports/
│   └── project_report.docx         # full thesis document
└── README.md
```

*(Adjust to match your actual folder layout.)*

---

```

```bash
# 5. Run the web app (Flask)
cd webapp
pip install flask
python app.py
# app runs the /predict endpoint — open the local URL shown in the terminal (e.g. http://127.0.0.1:5000)
```

---

## 🔮 Future Work

- Expand dataset size and diversity (multi-hospital data)
- Integrate multi-modal medical data (e.g., clinical/EEG data alongside MRI)
- Advanced/quantitative validation of explainability (not just qualitative Grad-CAM)
- Real-time clinical deployment (optimize inference speed & compute cost)
- Early disease prediction and progression analysis
- Explore Transformer-based architectures
- Mobile and Edge AI deployment for wider accessibility

---

## 📄 License / Academic Note

This project was submitted in partial fulfillment of the requirements for the degree of **BS (Information Technology)** at the **Institute of Computing, MNS-University of Agriculture, Multan, Pakistan**. For full technical details, UML diagrams, code listings, and screenshots, see the complete project report and slides below.

- 📄 [Full Project Report](https://docs.google.com/document/d/127SANNZztVKjUyjDaM_FvV42UiXguREh/edit?usp=sharing&ouid=117639944094007826260&rtpof=true&sd=true)
- 📊 [Project Slides](https://drive.google.com/file/d/174ACBALLqKP3r-Lyu2VqW4qoLC8wjuMm/view?usp=sharing)
