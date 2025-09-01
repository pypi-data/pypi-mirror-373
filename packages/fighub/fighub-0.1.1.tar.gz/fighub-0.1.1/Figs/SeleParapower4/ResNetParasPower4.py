import sys
import os
import numpy as np
import os, pickle, torch, re, math
import matplotlib.pyplot as plt
import matplotlib as mpl
from collections import defaultdict
from pathlib import Path
import sys
sys.path.append("../../utils")
from utils import colors, marker

print(sys.path)
assert False

class SubPlot:
    def __init__(
        self,
        model_name,
        data_name=[],
        batch_size={},
        epoch=[],
        seed=[1],
        colors_schedule = None,
        marker_schedule = None,
        py_name="Fig",
        category={},
        use_log_scale=True,
        solid_methods=None,
        marker_point = None
    ):
        self.model_name = model_name
        self.data_name = data_name
        self.batch_size = batch_size
        self.label_name_list = []
        self.epoch = epoch
        self.seed = seed
        self.colors_schedule = colors_schedule
        self.marker_schedule = marker_schedule
        self.py_name = py_name
        self.category = category
        self.use_log_scale = use_log_scale
        self.solid_methods = solid_methods if solid_methods else {}

        self.plot_data = defaultdict(lambda: defaultdict(list))

        self.pkl_pth_Per_data = defaultdict(list)
        self.ylabel = {
            "training_loss": "training loss",
            "epoch_loss": "average epoch loss",
            "loss": "epoch loss",
            "grad_norm": "gradient norm",
            "iter_loss": "iteration loss"
        }
        mpl.rcParams['font.family'] = 'Times New Roman'        # 所有字体设为 Times New Roman
        mpl.rcParams['mathtext.fontset'] = 'stix'              # 数学字体设为 Times-like
        mpl.rcParams['mathtext.rm'] = 'Times New Roman'        # 数学 roman 也指定 Times
        mpl.rcParams['axes.unicode_minus'] = False  
        mpl.rcParams["font.size"] = 12

        # color schedule
        if self.colors_schedule != None:
            self.colors_dict = colors.colors_schedule(self.colors_schedule)

        # color schedule
        if self.marker_schedule and marker_point is not None:  
            self.marker_point = marker_point 
            self.marker_dict = marker.marker_schedule(self.marker_schedule)

        # matplotlib settings
        mpl.rcParams["mathtext.fontset"] = "stix"
        mpl.rcParams["axes.unicode_minus"] = False
        mpl.rcParams["font.size"] = 12
        mpl.rcParams["font.family"] = "serif"


    def __extract_data_name(self, pkl_path):
        parts = Path(pkl_path).parts
        model_name_id = parts.index(self.model_name)
        data_name = parts[model_name_id + 1]

        return data_name, parts.index(data_name)

    def __check_info(self, data_name, data_idex, parts):
        # ----------------- check_info -------------------------
        # dataset
        if data_name not in self.data_name:
            print("------------------------------")
            print(f"data_name = {data_name}?")
            print("------------------------------")
            assert False

        # seed
        seed = parts[data_idex - 2]
        if not any(seed == f"seed_{i}" for i in self.seed):
            print("------------------------------")
            print(f"{data_name} --> seed = {seed}?")
            print("------------------------------")
            assert False

        # batch_size
        batch_size = parts[data_idex + 3]
        if f"Batch_size_{self.batch_size[data_name]}" != batch_size:
            print("------------------------------")
            print(f"{data_name} --> batch_size = {batch_size}?")
            print("------------------------------")
            assert False

        # epoch
        epoch = parts[data_idex + 4]
        if epoch != f"epoch_{self.epoch[data_name]}":
            print("------------------------------")
            print(f"{data_name} --> epoch = {self.epoch[data_name]}?")
            print("------------------------------")
            assert False

        # -------------- check_info (over) ------------

    def split_data_info(self, pkl_paths):
        """
        For pkl_pths containing multiple datasets, we will divide them into multiple sub-lists based on the names of the datasets and transfer them to the dictionary
        """
        for pkl_path in pkl_paths:
            data_name, _ = self.__extract_data_name(pkl_path)
            self.pkl_pth_Per_data[data_name].append(pkl_path)

        # for key, value in self.pkl_pth_Per_data.items():
        #     print(key, value)

    def _extract_info(self):
        for data_name, pkl_path in self.pkl_pth_Per_data.items():
            for path in pkl_path:
                if os.path.exists(path):
                    parts = Path(path).parts
                    data_name, data_idex = self.__extract_data_name(path)

                    # ----------------- check_info ----------------
                    self.__check_info(data_name, data_idex, parts)
                    # -------------- check_info (over) ------------

                    with open(path, "rb") as f:
                        out = pickle.load(f)
                        data = out.get(self.category[data_name], None)
                        self.plot_data[data_name][parts[data_idex + 1]].append(data)

                else:
                    print(f"File does not exist:\n {path}")
                    assert False

    def subplot(self, ncols=3, save_name = ""):
        self._extract_info()
        num_datasets = len(self.plot_data)
        num_datasets = len(self.plot_data)
        nrows = math.ceil(num_datasets / ncols)
        fig, axes = plt.subplots(
            nrows, ncols, figsize = (5 * ncols, 4 * nrows), squeeze=False
        )
        axes = axes.flatten()
        for i, (ax, (data_name, optim_dict)) in enumerate(
            zip(axes, self.plot_data.items())
        ):
            
            for optimizer_name, data_list in optim_dict.items():
                for data in data_list:
                    x = range(len(data))
                    if optimizer_name in self.solid_methods:
                        linestyle = "-"
                    else:
                        linestyle = "--"

                    ax.plot(x, data, label=optimizer_name, linestyle=linestyle, color = self.colors_dict[optimizer_name])

                    # mark
                    if self.marker_schedule != None:
                        x = np.array(x)
                        data = np.array(data)
                        ax.plot(x[self.marker_point[data_name]], data[self.marker_point[data_name]], linestyle='', color = self.colors_dict[optimizer_name], marker = self.marker_dict[optimizer_name])

            ax.set_title(data_name, fontsize=12,  fontweight="bold")
            ax.set_xlabel("Parameters")
            # ax.set_ylabel(f"{self.ylabel[self.category[data_name]]}")
            ax.grid(True)

            # This code sets the y-axis label only for the leftmost subplot in a row if all categories are the same, otherwise it shows each subplot's corresponding label.
            unique_values = set(self.category.values())
            if len(unique_values) == 1:
                if i % ncols == 0:
                    ax.set_ylabel(f"{self.ylabel[self.category[data_name]]}")
                else:
                    ax.set_ylabel("")
            else:
                ax.set_ylabel(f"{self.ylabel[self.category[data_name]]}")

            # set log cale
            if "loss" in self.category[data_name].lower():
                ax.set_yscale("log")


        # Delete the resundant subfigures
        for i in range(num_datasets, len(axes)):
            fig.delaxes(axes[i])

        # Uniform Legend
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.5, -0.01),
            ncol=len(handles),
        )

        plt.tight_layout()

        # Saving as PDF
        if save_name == "":
            save_name = f"Figs/{self.model_name}/{self.py_name}.pdf"

        plt.savefig(save_name, bbox_inches="tight")
        print(f"Saved figure as {save_name}")

        plt.close()  # Colse the fig

py_name = os.path.splitext(os.path.basename(__file__))[0]

pkl_paths = [
    "SeleParaPower4_Results/seed_1/ResNet18/CIFAR100/SPBM-TR/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-30_17-14-14/SPBM-TR_M_1e-05_delta_0_cutting_number_10.pkl",
    "SeleParaPower4_Results/seed_1/ResNet18/CIFAR100/SPBM-PF/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-30_17-14-14/SPBM-PF_M_1e-05_delta_0_cutting_number_10.pkl",
    "SeleParaPower4_Results/seed_1/ResNet18/CIFAR100/SGD/train_2000_val_0_test_10000/Batch_size_256/epoch_50/2025-08-30_17-14-14/SGD_alpha_0.pkl"
    
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
    "CIFAR100": [0,2,4,6,8],
}


plot = SubPlot(
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

plot.subplot(ncols=1,save_name=f'Figs/SeleParapower4/{py_name}.pdf')
