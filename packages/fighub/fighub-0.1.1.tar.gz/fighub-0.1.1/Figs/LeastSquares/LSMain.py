import sys
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(root_path)
from utils import fighub

py_name = os.path.splitext(os.path.basename(__file__))[0]

pkl_paths = [
    # ADAM - CIFAR100
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/ADAM/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/ADAM_alpha_0.0005_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/ALR-SMAG/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/ALR-SMAG_c_5_eta_max_16_beta_0.9.pkl',
    # Bundle
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/Bundle/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/Bundle_delta_0.5_cutting_number_10.pkl',
    # SGD
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/SGD/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/SGD_alpha_0.1.pkl',
    #SPSmax
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/SPSmax/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/SPSmax_c_10_gamma_1.pkl',
    # PF
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/SPBM-PF/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/SPBM-PF_M_1e-05_delta_0.5_cutting_number_10.pkl',
    # TR
    'SeleParasResults/seed_1/LeastSquares/CIFAR100/SPBM-TR/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-50-26/SPBM-TR_M_1e-05_delta_128_cutting_number_10.pkl',


    # ADAM - CALTECH101_Resize_32
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/ADAM/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/ADAM_alpha_0.0005_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/ALR-SMAG/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/ALR-SMAG_c_0.1_eta_max_0.125_beta_0.9.pkl',
    # Bundle
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/Bundle/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/Bundle_delta_0.25_cutting_number_10.pkl',
    # SGD
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/SGD/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/SGD_alpha_0.1.pkl',
    #SPSmax
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/SPSmax/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/SPSmax_c_5_gamma_128.pkl',
    # PF
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/SPBM-PF/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/SPBM-PF_M_1e-05_delta_0.25_cutting_number_10.pkl',
    # TR
    'SeleParasResults/seed_1/LeastSquares/CALTECH101_Resize_32/SPBM-TR/train_5000_val_0_test_1500/Batch_size_256/epoch_10/2025-08-20_17-50-26/SPBM-TR_M_1e-05_delta_128_cutting_number_10.pkl',


    # ADAM - MNIST
    'SeleParasResults/seed_1/LeastSquares/MNIST/ADAM/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG
    'SeleParasResults/seed_1/LeastSquares/MNIST/ALR-SMAG/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/ALR-SMAG_c_0.1_eta_max_2_beta_0.9.pkl',
    # Bundle
    'SeleParasResults/seed_1/LeastSquares/MNIST/Bundle/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/Bundle_delta_4_cutting_number_10.pkl',
    # SGD
    'SeleParasResults/seed_1/LeastSquares/MNIST/SGD/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/SGD_alpha_1.pkl',
    #SPSmax
    'SeleParasResults/seed_1/LeastSquares/MNIST/SPSmax/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/SPSmax_c_0.1_gamma_2.pkl',
    # PF
    'SeleParasResults/seed_1/LeastSquares/MNIST/SPBM-PF/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/SPBM-PF_M_1e-05_delta_4_cutting_number_10.pkl',
    # TR
    'SeleParasResults/seed_1/LeastSquares/MNIST/SPBM-TR/train_5000_val_0_test_5000/Batch_size_256/epoch_10/2025-08-20_17-49-42/SPBM-TR_M_1e-05_delta_64_cutting_number_10.pkl'
    
    

]

model_name = "LeastSquares"
data_name = [
    "CALTECH101_Resize_32",
    "MNIST",
    "Ijcnn",
    "Duke",
    "w8a",
    "RCV1",
    "MNIST",
    "CIFAR100"
]
batch_size = {
    "CALTECH101_Resize_32": 256,
    "MNIST": 256,
    "Ijcnn": 64,
    "Duke": 10,
    "w8a": 128,
    "RCV1": 256,
    "MNIST": 256,
    "CIFAR100": 256
}

epoch = {
    "CALTECH101_Resize_32": 10,
    "MNIST": 10,
    "Ijcnn": 10,
    "Duke": 10,
    "w8a": 10,
    "RCV1": 10,
    "MNIST": 10,
    "CIFAR100": 10
}

category_dict = {
    "CALTECH101_Resize_32": "training_loss",
    "MNIST": "training_loss",
    "Ijcnn": "training_loss",
    "Duke": "training_loss",
    "w8a": "training_loss",
    "RCV1": "training_loss",
    "MNIST": "training_loss",
    "CIFAR100": "training_loss"
}

solid_methods = ["SPBM-TR", "SPBM-PF"]

marker_point = {
    "CALTECH101_Resize_32": [0, 2, 4, 6, 8],
    "MNIST": [0, 2, 4, 6, 8],
    "Ijcnn": [0, 2, 4, 6, 8],
    "Duke": [0, 2, 4, 6, 8],
    "w8a": [0, 2, 4, 6, 8],
    "RCV1": [0, 2, 4, 6, 8],
    "MNIST": [0, 2, 4, 6, 8],
    "CIFAR100": [0, 2, 4, 6, 8]
}


plot = fighub.SubPlot(model_name, data_name, batch_size, 
                      category=category_dict, epoch=epoch,
                      seed=[1],
                      solid_methods = solid_methods,
                      colors_schedule = "SPBM",
                      marker_schedule = "SPBM",
                      marker_point = marker_point,
                      py_name=py_name
                      )

plot.split_data_info(pkl_paths)

plot.subplot()