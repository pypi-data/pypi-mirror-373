import matplotlib as mpl
import matplotlib.pyplot as plt
from fighub import colors, marker
from pathlib import Path
import os, pickle, math 
from collections import defaultdict
import numpy as np


class ParasPlot:
    def __init__(
        self,
        model_name: str,
        epochs: dict,
        batch_size: dict,
        seed: list,
        category_dict: dict,
        sample_number: dict,
        py_name,
        colors_schedule = None,
        marker_schedule = None,
        marker_point = None
    ):
        self.model_name = model_name
        self.py_name = py_name
        self.epochs = epochs
        self.batch_size = batch_size
        self.seed = seed
        self.category_dict = category_dict
        self.sample_number = sample_number
        self.ylabel = {
            "training_loss": "training loss",
            "epoch_loss": "average epoch loss",
            "loss": "epoch loss",
        }
        self.colors_schedule = colors_schedule
        self.marker_schedule = marker_schedule


        # (seed, data_name, optimizer)
        self.fig_value = defaultdict(lambda: defaultdict(list))

        mpl.rcParams["font.family"] = "Times New Roman"  # 所有字体设为 Times New Roman
        mpl.rcParams["mathtext.fontset"] = "stix"  # 数学字体设为 Times-like
        mpl.rcParams["mathtext.rm"] = "Times New Roman"  # 数学 roman 也指定 Times
        mpl.rcParams["axes.unicode_minus"] = False
        mpl.rcParams["font.size"] = 12

        # color schedule
        if self.colors_schedule != None:
            self.colors_dict = colors.colors_schedule(self.colors_schedule)
        
        # marker schedule
        if self.marker_schedule and marker_point is not None:  
            self.marker_point = marker_point 
            self.marker_dict = marker.marker_schedule(self.marker_schedule)

    def _check_info(self, pkl_path):
        parts = Path(pkl_path).parts
        model_name_id = parts.index(self.model_name)
        data_name = parts[model_name_id + 1]
        data_idex = parts.index(data_name)

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
        if epoch != f"epoch_{self.epochs[data_name]}":
            print("------------------------------")
            print(f"{data_name} --> epoch = {self.epochs[data_name]}?")
            print("------------------------------")
            assert False

        # sample_number
        sample_str_list = parts[data_idex + 2].split("_")
        sample_number = (
            int(sample_str_list[1]),
            int(sample_str_list[3]),
            int(sample_str_list[5]),
        )
        if sample_number != self.sample_number[data_name]:
            print("------------------------------")
            print(
                f"{data_name}-{sample_number} --> sample_number = {self.sample_number[data_name]}?"
            )
            print("------------------------------")
            assert False

    def _extract_info(self, pkl_path):
        parts = Path(pkl_path).parts
        model_name_id = parts.index(self.model_name)
        data_name = parts[model_name_id + 1]
        seed_str = parts[model_name_id - 1].split("_")[1]
        optimizer_name = parts[model_name_id + 2]

        info = {
            "data_name": data_name,
            "seed_str": seed_str,
            "optimizer_name": optimizer_name,
        }
        # print(info)
        # assert False
        return info

    def load_data(self, pkl_paths):
        for pkl_path in pkl_paths:
            if os.path.exists(pkl_path):
                self._check_info(pkl_path)
                self.info = self._extract_info(pkl_path)
                # load data
                with open(pkl_path, "rb") as f:
                    out = pickle.load(f)
                    data = out.get(self.category_dict[self.info["data_name"]], None)

                    self.fig_value[self.info["data_name"]][
                        self.info["optimizer_name"]
                    ].append(data)
            else:
                print(f"{pkl_path} ---> error")

    def draw_one(self, solid_methods = None, ncol = 1, save_name = ""):
        plt.figure(figsize=(9, 6))
        # data: dict , for example: data["GSD"]
        for i, (data_name, data) in enumerate(self.fig_value.items()):
            for optimizer_name, curves_value in data.items():
                # print(optimizer_name)
                # print(len(curves_value))
                min_len = min(len(c) for c in curves_value)
                data_array = np.array([c[:min_len] for c in curves_value])
                mean_curve = data_array.mean(axis=0)
                std_curve = data_array.std(axis=0)

                # setting
                linestyle = "-" if optimizer_name in solid_methods else "--"


                x = np.arange(min_len)
                if self.colors_schedule != None:
                    plt.plot(x, mean_curve, linestyle,
                        color = self.colors_dict[optimizer_name],
                        label=optimizer_name
                        )
                    plt.fill_between(
                        x,
                        mean_curve - std_curve,
                        mean_curve + std_curve,
                        alpha=0.3,
                        color = self.colors_dict[optimizer_name],
                        # label=optimizer_name
                    )
                else:
                    plt.plot(x, mean_curve, linestyle, label=optimizer_name)

                    plt.fill_between(
                        x,
                        mean_curve - std_curve,
                        mean_curve + std_curve,
                        alpha=0.3,
                        # label=optimizer_name
                    )
                
                if self.marker_schedule:
                    x = np.array(x)
                    data = np.array(mean_curve)
                    plt.plot(x[self.marker_point[data_name]], data[self.marker_point[data_name]], linestyle='', color = self.colors_dict[optimizer_name], marker = self.marker_dict[optimizer_name])

            plt.yscale('log')
            plt.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.15),
                ncol = ncol
                )
            plt.xlabel("epochs")
            plt.grid(True)
            plt.ylabel(self.ylabel[self.category_dict[data_name]])
            plt.title(f"{data_name}")
            # Saving as PDF
            if save_name == "":
                save_name = f"Figs/{self.model_name}/{self.py_name}.pdf"
            plt.savefig(save_name, bbox_inches="tight")
            print(f"Saved figure as {save_name}")
            plt.close()

    def subplot(self, solid_methods = None, ncols = 3, save_name = ""):
        num_datasets = len(self.fig_value.keys())
        nrows = math.ceil(num_datasets / ncols)
        fig, axes = plt.subplots(
            nrows, ncols, figsize = (5 * ncols, 4 * nrows), squeeze=False
        )
        axes = axes.flatten()

        for i, (ax, (data_name , data)) in enumerate(zip(axes, self.fig_value.items())):
            for optimizer_name, curves_value in data.items():

                min_len = min(len(c) for c in curves_value)
                data_array = np.array([c[:min_len] for c in curves_value])
                mean_curve = data_array.mean(axis=0)
                std_curve = data_array.std(axis=0)

                # setting
                linestyle = "-" if optimizer_name in solid_methods else "--"
                # print(data_name, optimizer_name, linestyle)

                x = np.arange(min_len)
                if self.colors_schedule != None:
                    ax.plot(x, mean_curve, linestyle,
                        color = self.colors_dict[optimizer_name],
                        label=optimizer_name
                        )
                    ax.fill_between(
                        x,
                        mean_curve - std_curve,
                        mean_curve + std_curve,
                        alpha=0.3,
                        color = self.colors_dict[optimizer_name],
                        # label=optimizer_name
                    )
                else:
                    ax.plot(x, mean_curve, linestyle, label=optimizer_name)

                    ax.fill_between(
                        x,
                        mean_curve - std_curve,
                        mean_curve + std_curve,
                        alpha=0.3,
                        # label=optimizer_name
                    )
                
                if self.marker_schedule:
                    x = np.array(x)
                    data = np.array(mean_curve)
                    ax.plot(x[self.marker_point[data_name]], data[self.marker_point[data_name]], linestyle='', color = self.colors_dict[optimizer_name], marker = self.marker_dict[optimizer_name])

                # set log cale
                if "loss" in self.category_dict[data_name].lower():
                    ax.set_yscale("log")

                unique_values = set(self.category_dict.values())
                if len(unique_values) == 1:
                    if i % ncols == 0:
                        ax.set_ylabel(f"{self.ylabel[self.category_dict[data_name]]}")
                    else:
                        ax.set_ylabel("")
                else:
                    ax.set_ylabel(f"{self.ylabel[self.category_dict[data_name]]}")
                
                ax.set_title(data_name, fontsize=12,  fontweight="bold")
                ax.set_xlabel("epochs")
                # ax.set_ylabel(f"{self.ylabel[self.category[data_name]]}")
                ax.grid(True)

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