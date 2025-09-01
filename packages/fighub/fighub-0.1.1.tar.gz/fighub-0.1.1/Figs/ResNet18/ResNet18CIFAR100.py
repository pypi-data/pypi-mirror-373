import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(root_path)
from utils import fighub

py_name = os.path.splitext(os.path.basename(__file__))[0]

pkl_paths = [
    # ---------------------------------------------------------
    # ADAM - CIFAR100
    "SeleParasResults/seed_1/ResNet18/CIFAR100/ADAM/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/ADAM_alpha_0.001_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl",
    # # ALR-SMAG
    # "SeleParasResults/seed_1/ResNet18/CIFAR100/ALR-SMAG/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/ALR-SMAG_c_0.1_eta_max_0.25_beta_0.9.pkl",
    # # Bundle
    # "SeleParasResults/seed_1/ResNet18/CIFAR100/Bundle/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/Bundle_delta_0.25_cutting_number_10.pkl",
    # SGD
    "SeleParasResults/seed_1/ResNet18/CIFAR100/SGD/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-31_09-45-20/SGD_alpha_0.25.pkl",
    # #SPSmax
    # "SeleParasResults/seed_1/ResNet18/CIFAR100/SPSmax/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/SPSmax_c_0.1_gamma_0.25.pkl",
    # PF
    "SeleParasResults/seed_1/ResNet18/CIFAR100/SPBM-PF/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/SPBM-PF_M_1e-05_delta_256_cutting_number_10.pkl",
    # TR
    "SeleParasResults/seed_1/ResNet18/CIFAR100/SPBM-TR/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-30_22-01-54/SPBM-TR_M_1e-05_delta_65536_cutting_number_10.pkl",
]

model_name = "ResNet18"
data_name = [
    "CALTECH101_Resize_32",
    "MNIST",
    "Ijcnn",
    "Duke",
    "w8a",
    "RCV1",
    "MNIST",
    "CIFAR100",
]
batch_size = {
    "CALTECH101_Resize_32": 128,
    "MNIST": 256,
    "Ijcnn": 64,
    "Duke": 10,
    "w8a": 128,
    "RCV1": 256,
    "MNIST": 256,
    "CIFAR100": 256,
}

epoch = {
    "CALTECH101_Resize_32": 50,
    "MNIST": 50,
    "Ijcnn": 10,
    "Duke": 10,
    "w8a": 10,
    "RCV1": 10,
    "CIFAR100": 50,
}

category_dict = {
    "CALTECH101_Resize_32": "training_loss",
    "MNIST": "training_loss",
    "Ijcnn": "training_loss",
    "Duke": "training_loss",
    "w8a": "training_loss",
    "RCV1": "training_loss",
    "MNIST": "training_loss",
    "CIFAR100": "training_loss",
}

solid_methods = ["SPBM-TR", "SPBM-PF"]

marker_point = {
    "CALTECH101_Resize_32": [0, 10, 20, 30, 40],
    "MNIST": [0, 10, 20, 30, 40],
    "Ijcnn": [0, 10, 20, 30, 40],
    "Duke": [0, 10, 20, 30, 40],
    "w8a": [0, 10, 20, 30, 40],
    "RCV1": [0, 10, 20, 30, 40],
    "MNIST": [0, 10, 20, 30, 40],
    "CIFAR100": [0, 10, 20, 30, 40],
}


plot = fighub.SubPlot(
    model_name,
    data_name,
    batch_size,
    category=category_dict,
    epoch=epoch,
    seed=[1],
    solid_methods=solid_methods,
    colors_schedule="SPBM",
    marker_schedule="SPBM",
    marker_point=marker_point,
    py_name=py_name,
)

plot.split_data_info(pkl_paths)

plot.subplot(ncols=1)
