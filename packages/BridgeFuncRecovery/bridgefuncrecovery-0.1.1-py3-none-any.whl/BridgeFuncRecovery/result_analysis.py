import matplotlib.pyplot as plt
import numpy as np


def empirical_ccdf(samplevalue, assessedtimes):
    return [(np.sum(np.array(samplevalue) >= val)) / len(samplevalue) for val in assessedtimes]


## Arguments for the functions below:
"""
Parameters:
data (dict): Dictionary containing 'RepairClass_dict' as one of the keys.
comp_name (str): The component name to plot.
show (bool): Whether to call plt.show()
"""

## Repair class distribution for a single component in 'RepairClass_dict'
def plot_repair_class_distribution_single(data, comp_name, show=True):
    RC = data['RepairClass_dict']

    if comp_name not in RC:
        print(f"Component '{comp_name}' not found in RepairClass_dict.")
        return
    
    rc_values = RC[comp_name]
    num_rlz = len(rc_values)

    prop_vals = [rc_values.count(i) / num_rlz for i in range(1, 6)]

    plt.figure(figsize=(8, 4))
    index = np.arange(1, 6)
    plt.bar(index, prop_vals, width=0.3, label=comp_name)
    plt.xticks(index)
    plt.xlabel(f'{comp_name} Repair Class')
    plt.ylabel('Proportion')
    plt.title(f'Repair Class Distribution: {comp_name}')
    plt.legend()

    if show:
        plt.show()


## Repair class distributions for all components in 'RepairClass_dict'
def plot_all_repair_class_distributions(data, show_each=True): 
    RC = data['RepairClass_dict']
    for comp_name in RC:
        plot_repair_class_distribution_single(data, comp_name, show=show_each)


## Initial response phase Functionality State (FS) distribution
def plot_fs_initial(data, show=True):
    num_rlz = len(data['FS_rlz'])
    prop_FS_initial = [data['FS_rlz'].count(i) / num_rlz for i in [0, 1, 2, 3, 7]]
    categories = ['Fully Repaired', 'FS1', 'FS2', 'FS3', 'FS7']
    plt.figure(figsize=(10, 5))
    bar_width = .1
    index = np.arange(len(categories))
    plt.bar(index, prop_FS_initial, bar_width, label='Initial Phase Functionality State')
    plt.xticks(index, categories)
    plt.xlabel('Functionality State (Initial phase)')
    plt.ylabel('Proportion')
    plt.legend(loc='best')
    plt.title('Initial Response Phase Functionality State')
    if show:
        plt.show()


## Reopening phase Functionality State (FS) distribution
def plot_fs_reopening(data, show=True):
    num_rlz = len(data['FS_rlz_Reopening'])
    prop_FS_reopening = [data['FS_rlz_Reopening'].count(i) / num_rlz for i in range(0, 8)]
    categories = ['FS0', 'FS1', 'FS2', 'FS3', 'FS4', 'FS5', 'FS6', 'FS7']
    plt.figure(figsize=(10, 5))
    bar_width = .1
    index = np.arange(len(categories))
    plt.bar(index, prop_FS_reopening, bar_width, label='Reopening Phase FS')
    plt.xticks(index, categories)
    plt.xlabel('Functionality State (Reopening)')
    plt.ylabel('Proportion')
    plt.legend(loc='best')
    plt.title('Reopening Phase Functionality State')
    if show:
        plt.show()


## Closed lane distribution at initial phase
def plot_closed_lane_initial(data, show=True):
    num_rlz = len(data['ClosedLaneNum_Initial'])
    prop_closedlane_initial = [data['ClosedLaneNum_Initial'].count(i) / num_rlz for i in [0, 1, 2, 3, 4]]
    categories = ['0', '1', '2', '3', '4']
    plt.figure(figsize=(10, 5))
    bar_width = .1
    index = np.arange(len(categories))
    plt.bar(index, prop_closedlane_initial, bar_width, label='Closed Lanes at Initial Phase')
    plt.xticks(index, categories)
    plt.xlabel('Closed Lanes (Initial)')
    plt.ylabel('Proportion')
    plt.legend(loc='best')
    plt.title('Closed Lane Number at Initial Phase')
    if show:
        plt.show()


## Empirical CCDF of total impeding time delays
def plot_total_impeding_ccdf(data, show=True):
    assessedtimes = np.linspace(0, 300, num=100)
    TotalDelay = data['IF_sum_list']
    ccdf = empirical_ccdf(TotalDelay, assessedtimes)
    plt.figure()
    plt.plot(assessedtimes, ccdf, label='Impeding Time Delays')
    plt.xlabel('Duration (days)')
    plt.ylabel('Probability of Exceedance')
    plt.xlim([0, 300])
    plt.legend(loc='upper right')
    plt.title('Empirical CCDF of Total Time Delay')
    if show:
        plt.show()


## Empirical CCDF of total repair/replacement durations
def plot_total_repair_ccdf(data, show=True):
    assessedtimes = np.linspace(0, 300, num=100)
    TotalRep = data['RepDur_sum_rlz']
    ccdf_vals = empirical_ccdf(TotalRep, assessedtimes)
    plt.figure()
    plt.plot(assessedtimes, ccdf_vals, label='Repair/Replacement Durations')
    plt.xlabel('Duration (days)')
    plt.ylabel('Probability of Exceedance')
    plt.xlim([0, 200])
    plt.legend(loc='upper right')
    plt.title('Empirical CCDF of Total Repair/Replacement Duration')
    if show:
        plt.show()


## Impeding factors (median) printout
def print_impeding_medians(data):
    print("--- Median Impeding Factors ---")
    for k in ['IniInsp', 'InDepInsp', 'Financing', 'Design', 'Permitting', 'Contractor']:
        print(f"{k}: {np.median(data['IF_sampled_list'][k]):.2f} days")
    print(f"Total Delay: {np.median(data['IF_sum_list']):.2f} days")


## Repair durations (median) printout
def print_repair_durations(data):
    print("--- Median Repair Durations (days) ---")
    comp_lists = {
        'Col': [], 'Seat_ab': [], 'Super': [], 'ColFnd': [], 'AbFnd': [],
        'Backwall': [], 'Bearing_ab': [], 'Key_ab': [], 'ApproSlab': [], 'JointSeal_ab': []
    }
    for entry in data['RepDur_sampled_comp_rlz']:
        if entry == 'Complete':
            continue
        for k in comp_lists:
            comp_lists[k].append(entry[k])
    for k, v in comp_lists.items():
        if v:
            print(f"{k}: {np.median(v):.2f} days")



## Show all results in a single function
def show_all_results(data):

    print_impeding_medians(data)
    print_repair_durations(data)

    plot_all_repair_class_distributions(data, show=False)
    plot_fs_initial(data, show=False)
    plot_fs_reopening(data, show=False)
    plot_closed_lane_initial(data, show=False)
    plot_total_impeding_ccdf(data, show=False)
    plot_total_repair_ccdf(data, show=False)

    plt.show()