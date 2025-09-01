
def colors_schedule(colors_schedule = None):

    if colors_schedule == "SPBM":
        based_color = {
            "ADAM": "#7f7f7f",  # gray
            "ALR-SMAG": "#8fbc8f",  # olive
            "Bundle": "#17becf",  # cyan
            "SGD": "#2ca02c",  # green
            "SPSmax": "#BA6262",  # brown
            "SPBM-PF": "#1f77b4",  # blue
            "SPBM-TR": "#d62728",  # red
        }
    else:
        based_color = {
        "ADAM": "#1f77b4",  
        "ALR-SMAG": '#ff7f0e',  
        "Bundle": '#2ca02c',  
        "SGD": '#d62728',  
        "SPSmax": '#9467bd',  
        "SPBM-PF": '#8c564b',  
        "SPBM-TR": '#e377c2',  
        "dddd": '#7f7f7f',  
        "xxx": '#bcbd22',  
        "ED": '#17becf'  
    }
    return based_color