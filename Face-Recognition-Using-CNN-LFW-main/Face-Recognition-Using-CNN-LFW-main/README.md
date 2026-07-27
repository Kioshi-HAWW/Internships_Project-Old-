# Face-Recognition-Using-CNN-LFW
# 👤 Face Recognition Using CNN

A Face Recognition System developed using a **Convolutional Neural Network (CNN)** on the **Labeled Faces in the Wild (LFW)** dataset. This project demonstrates multi-class face classification using deep learning techniques.

---

## 📖 Project Overview

The objective of this project is to recognize and classify human faces using a Convolutional Neural Network (CNN). The model is trained on the **Labeled Faces in the Wild (LFW)** dataset and incorporates modern deep learning techniques such as data augmentation, batch normalization, dropout, L2 regularization, learning rate scheduling, and early stopping to improve model performance.

---

## 🚀 Features

- Face Recognition using CNN
- LFW Dataset
- Image Preprocessing
- Data Augmentation
- Batch Normalization
- Dropout Regularization
- L2 Regularization
- Class Weight Balancing
- Early Stopping
- Learning Rate Scheduler
- Model Checkpoint
- Confusion Matrix
- Classification Report
- Accuracy and Loss Visualization

---

## 🗂️ Dataset

**Dataset:** Labeled Faces in the Wild (LFW)

The dataset is loaded directly using Scikit-learn.

```python
from sklearn.datasets import fetch_lfw_people

lfw = fetch_lfw_people(
    min_faces_per_person=100,
    resize=0.6,
    color=False
)
```

Dataset Characteristics:

- Grayscale Face Images
- Multiple Person Classes
- Automatically downloaded through Scikit-learn

---

## 🧠 CNN Architecture

Input Image

↓

Conv2D (32 Filters)

↓

Batch Normalization

↓

Conv2D (32 Filters)

↓

MaxPooling

↓

Dropout

↓

Conv2D (64 Filters)

↓

Batch Normalization

↓

Conv2D (64 Filters)

↓

MaxPooling

↓

Dropout

↓

Conv2D (128 Filters)

↓

Batch Normalization

↓

Conv2D (128 Filters)

↓

MaxPooling

↓

Dropout

↓

Global Average Pooling

↓

Dense (256)

↓

Dropout

↓

Output Layer (Softmax)

---

## 🛠️ Technologies Used

- Python
- TensorFlow
- Keras
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Pandas
- Google Colab

---

## 📁 Project Structure

```
Face-Recognition-Using-CNN/
│
├── Face_Recognition_CNN.ipynb
├── README.md
├── requirements.txt
├── LICENSE
├── best_model.keras
└── report/
    ├── Mini_Project_Report.pdf
    └── Project_Presentation.pptx
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/Face-Recognition-Using-CNN.git
```

Move into the project folder:

```bash
cd Face-Recognition-Using-CNN
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Project

Open the notebook:

```
Face_Recognition_CNN.ipynb
```

Run all cells sequentially in:

- Google Colab
- Jupyter Notebook

---

## 📊 Model Evaluation

The project evaluates the model using:

- Test Accuracy
- Training Accuracy
- Validation Accuracy
- Loss Curves
- Confusion Matrix
- Classification Report

---

## 📈 Results

The CNN model performs multi-class face classification on the LFW dataset.

Performance depends on the selected classes, preprocessing, hyperparameters, and training configuration.

---

## 🔮 Future Improvements

- Improve CNN architecture
- Hyperparameter tuning
- Real-time webcam face recognition
- Face detection before recognition
- Deploy as a web application

---

## 👨‍💻 Author

**Prathmesh Chedge**

