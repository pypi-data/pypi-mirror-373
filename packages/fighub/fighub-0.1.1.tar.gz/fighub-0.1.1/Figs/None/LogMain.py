import sys
import os
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(root_path)
from utils import fighub

py_name = os.path.splitext(os.path.basename(__file__))[0]

pkl_paths = [
    # ADAM - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/ADAM/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/ALR-SMAG/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/ALR-SMAG_c_0.1_eta_max_0.0078125_beta_0.9.pkl',
    # Bundle - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/Bundle/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/Bundle_delta_0.03125_cutting_number_10.pkl',
    # SGD - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/SGD/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/SGD_alpha_0.01.pkl',
    #SPSmax - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/SPSmax/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/SPSmax_c_10_gamma_0.25.pkl',
    # PF - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/SPBM-PF/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/SPBM-PF_M_1e-05_delta_0.25_cutting_number_10.pkl',
    # TR - CIFAR100
    'SeleParasResults/seed_1/LogRegressionBinaryL2/CIFAR100/SPBM-TR/train_1000_val_0_test_200/Batch_size_256/epoch_10/2025-08-17_00-03-34/SPBM-TR_M_1e-05_delta_1_cutting_number_10.pkl',
    
    # ---------------------------------------------------------
    # SGD - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/ADAM/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/ALR-SMAG/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/ALR-SMAG_c_0.1_eta_max_4_beta_0.9.pkl',
    # Bundle - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/Bundle/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/Bundle_delta_64_cutting_number_10.pkl',
    # SGD - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/SGD/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/SGD_alpha_1.pkl',
    #SPSmax - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/SPSmax/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/SPSmax_c_10_gamma_8.pkl',
    # PF - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/SPBM-PF/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/SPBM-PF_M_1e-05_delta_128_cutting_number_10.pkl',
    # TR - RCV1
    'SeleParasResults/seed_1/LogRegressionBinaryL2/RCV1/SPBM-TR/train_14169_val_0_test_6073/Batch_size_256/epoch_10/2025-08-17_00-04-35/SPBM-TR_M_1e-05_delta_4_cutting_number_10.pkl',

    # ---------------------------------------------------------
    # ADAM - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/ADAM/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/ALR-SMAG/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/ALR-SMAG_c_0.1_eta_max_1_beta_0.9.pkl',
    # Bundle - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/Bundle/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/Bundle_delta_1_cutting_number_10.pkl',
    # SGD - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/SGD/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/SGD_alpha_1.pkl',
    #SPSmax - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/SPSmax/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/SPSmax_c_0.1_gamma_2.pkl',
    # PF - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/SPBM-PF/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/SPBM-PF_M_1e-05_delta_4_cutting_number_10.pkl',
    # TR - w8a
    'SeleParasResults/seed_1/LogRegressionBinaryL2/w8a/SPBM-TR/train_49749_val_0_test_14951/Batch_size_128/epoch_10/2025-08-17_00-04-35/SPBM-TR_M_1e-05_delta_2_cutting_number_10.pkl',

    # ---------------------------------------------------------
    # ADAM - Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/ADAM/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG- Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/ALR-SMAG/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/ALR-SMAG_c_0.1_eta_max_0.0625_beta_0.9.pkl',
    # Bundle- Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/Bundle/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/Bundle_delta_0.03125_cutting_number_10.pkl',
    # SGD- Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/SGD/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/SGD_alpha_0.1.pkl',
    #SPSmax- Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/SPSmax/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/SPSmax_c_0.1_gamma_0.03125.pkl',
    # PF- Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/SPBM-PF/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/SPBM-PF_M_1e-05_delta_32_cutting_number_10.pkl',
    # TR- Duke
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Duke/SPBM-TR/train_38_val_0_test_4/Batch_size_10/epoch_10/2025-08-16_17-33-07/SPBM-TR_M_1e-05_delta_8_cutting_number_10.pkl',


    # ADAM - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/ADAM/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/ALR-SMAG/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/ALR-SMAG_c_0.1_eta_max_1_beta_0.9.pkl',
    # Bundle - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/Bundle/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/Bundle_delta_0.25_cutting_number_10.pkl',
    # SGD - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/SGD/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/SGD_alpha_1.pkl',
    #SPSmax - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/SPSmax/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/SPSmax_c_0.1_gamma_4.pkl',
    # PF - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/SPBM-PF/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/SPBM-PF_M_1e-05_delta_4_cutting_number_10.pkl',
    # TR - Ijcnn
    'SeleParasResults/seed_1/LogRegressionBinaryL2/Ijcnn/SPBM-TR/train_35000_val_0_test_91701/Batch_size_64/epoch_10/2025-08-17_00-04-35/SPBM-TR_M_1e-05_delta_1_cutting_number_10.pkl',

    # -------------------------- MNIST -------------------------
    # ADAM - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/ADAM/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/ADAM_alpha_0.002_epsilon_1e-08_beta1_0.9_beta2_0.999.pkl',
    # ALR-SMAG - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/ALR-SMAG/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/ALR-SMAG_c_0.1_eta_max_1_beta_0.9.pkl',
    # Bundle - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/Bundle/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/Bundle_delta_1_cutting_number_10.pkl',
    # SGD - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/SGD/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/SGD_alpha_1.pkl',
    #SPSmax - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/SPSmax/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/SPSmax_c_0.1_gamma_1.pkl',
    # PF - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/SPBM-PF/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/SPBM-PF_M_1e-05_delta_32_cutting_number_10.pkl',
    # TR - MNIST
    'SeleParasResults/seed_1/LogRegressionBinaryL2/MNIST/SPBM-TR/train_12665_val_0_test_2115/Batch_size_256/epoch_10/2025-08-17_00-03-34/SPBM-TR_M_1e-05_delta_4_cutting_number_10.pkl'

]

model_name = "LogRegressionBinaryL2"
data_name = [
    "MNIST",
    "Ijcnn",
    "Duke",
    "w8a",
    "RCV1",
    "MNIST",
    "CIFAR100"
]
batch_size = {
    "MNIST": 256,
    "Ijcnn": 64,
    "Duke": 10,
    "w8a": 128,
    "RCV1": 256,
    "MNIST": 256,
    "CIFAR100": 256
}

epoch = {
    "MNIST": 10,
    "Ijcnn": 10,
    "Duke": 10,
    "w8a": 10,
    "RCV1": 10,
    "MNIST": 10,
    "CIFAR100": 10
}

category_dict = {
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