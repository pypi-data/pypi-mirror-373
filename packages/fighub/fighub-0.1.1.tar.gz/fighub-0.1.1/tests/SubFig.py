from fighub import draw
import os
py_name = os.path.splitext(os.path.basename(__file__))[0]

pkl_paths = [
    # ADAM - CALTECH101_Resize_32
    "SeleParasResults/seed_1/ResNet18/CALTECH101_Resize_32/ADAM/train_2000_val_0_test_2604/Batch_size_128/epoch_50/2025-08-24_16-14-05/ADAM_alpha_0.0005_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl",
    

    # ADAM - MNIST
    'SeleParasResults/seed_1/ResNet18/MNIST/ADAM/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/ADAM_alpha_0.001_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',

    # ---------------------------------------------------------
    # ADAM - CIFAR100
    "SeleParasResults/seed_1/ResNet18/CIFAR100/ADAM/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/ADAM_alpha_0.0005_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl",
    "SeleParasResults/seed_1/ResNet18/CIFAR100/ADAM/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl",

    # ALR-SMAG
    "SeleParasResults/seed_1/ResNet18/CIFAR100/ALR-SMAG/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/ALR-SMAG_c_0.1_eta_max_0.25_beta_0.9.pkl",

    # bundle
    "SeleParasResults/seed_1/ResNet18/CIFAR100/Bundle/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/Bundle_delta_0.5_cutting_number_10.pkl",

    # SPBM-PF
    "SeleParasResults/seed_1/ResNet18/CIFAR100/SPBM-PF/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-24_16-14-05/SPBM-PF_M_1e-05_delta_256_cutting_number_10.pkl",

    # SPBM-TR
    "SeleParasResults/seed_1/ResNet18/CIFAR100/SPBM-TR/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-30_22-01-54/SPBM-TR_M_1e-05_delta_65536_cutting_number_10.pkl"
    
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

epochs = {
    "CALTECH101_Resize_32": 50,
    "MNIST": 50,
    "Ijcnn": 10,
    "Duke": 10,
    "w8a": 10,
    "RCV1": 10,
    "CIFAR100": 50,
}

sample_number = {
    "CALTECH101_Resize_32": (2000, 0, 2604),
    "MNIST": (2000, 0, 10000),
    "Ijcnn": 10,
    "Duke": 10,
    "w8a": 10,
    "RCV1": 10,
    "CIFAR100": (2000, 0, 10000),
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

seed = [1]


plots = draw.ParasPlot(model_name, epochs, batch_size, seed, category_dict, sample_number, colors_schedule="SPBM", marker_schedule = "SPBM", marker_point = marker_point, py_name=py_name)

plots.load_data(pkl_paths)

plots.subplot(solid_methods)

