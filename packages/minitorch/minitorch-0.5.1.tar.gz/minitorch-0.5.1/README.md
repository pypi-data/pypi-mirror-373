# miniTorch

**miniTorch** adalah framework pembelajaran mesin ringan yang ditulis dalam Python menggunakan NumPy. Framework ini dirancang untuk mendukung autograd, neural network layers, loss functions, dan optimizers, menyerupai fungsionalitas dasar PyTorch namun dengan implementasi yang lebih sederhana untuk keperluan pembelajaran dan eksperimen.

**Versi saat ini: 0.5.1**

## Fitur
- **Tensor dengan Autograd**: Mendukung operasi seperti penjumlahan, pengurangan, perkalian, pembagian, dan perkalian matriks dengan perhitungan gradien otomatis (batch-safe).
- **Layers**:
  - `Linear`: Lapisan linear (fully connected).
  - `Conv2D`: Lapisan konvolusi 2D untuk tugas computer vision.
  - `BatchNorm1D`: Normalisasi batch untuk stabilitas pelatihan.
  - `Flatten`: Meratakan input untuk transisi ke lapisan linear.
  - Aktivasi: `ReLU`, `LeakyReLU`, `Sigmoid`, `Tanh`.
- **Loss Functions**: `MSE`, `L1Loss`, `CrossEntropy`.
- **Optimizers**: `SGD` dan `Adam` (dengan weight decay untuk regularisasi).
- **Module API**: Mendukung pembuatan model modular dengan kelas `Module` dan `Sequential`.
- **DataLoader**: Pemrosesan batch dengan pengacakan data.
- **Device Support**: Saat ini mendukung CPU (dengan placeholder untuk GPU di masa depan).
- **Unit Tests**: Tes otomatis untuk memastikan keandalan operasi Tensor, Linear, dan L1Loss.

## Prasyarat
- Python 3.6 atau lebih tinggi
- NumPy (`pip install numpy`)
- (Opsional) Matplotlib untuk visualisasi loss (`pip install matplotlib`)

## Instalasi
- pip install minitorch

