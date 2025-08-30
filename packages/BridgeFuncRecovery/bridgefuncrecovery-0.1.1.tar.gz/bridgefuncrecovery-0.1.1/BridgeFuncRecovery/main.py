print("Running BridgeFuncRecovery analysis...", flush=True)

from .utils import *

def run(
            
    IM_fixed,
    num_span,
    CompQty,
    WorkerAllo_percrew,
    Worker_Replace,
    num_rlz=1000,
    w=[0, 0, 1],
    height=35,
    num_lanes_before=4,
    ColSuperMatType_dict=None,
    NumCrew_percomp=None,
    WorkHour_repairable=8,
    WorkHour_replacement=8,
    num_concrete_pour_replacement=1,
    dispersion_assigned=0.3,
    CompFra_dict=None,
    return_data = False   
):

    if ColSuperMatType_dict is None:
        ColSuperMatType_dict = {'Col': 'concrete', 'Super': 'concrete'}


    if NumCrew_percomp is None:
        NumCrew_percomp = {
            'Col': 1, 'Seat_ab': 1, 'Super': 1, 'ColFnd': 1, 'AbFnd': 1, 'Backwall': 1,
            'Bearing_ab': 1, 'Key_ab': 1, 'ApproSlab': 1, 'JointSeal_ab': 1,
            'Seat_super':1,  'Bearing_super':1, 'Key_super':1,  'JointSeal_super': 1
        }
    
    if CompFra_dict is None:
        Col_S = (.11, .59); Col_M = (.53, .59); Col_E = (1.14, .59); Col_C = (1.75, .59)
        Seat_S = (.12, .56); Seat_M = (.52, .67); Seat_E = (1.14, .56); Seat_C = (1.7, .56)
        AbAct_S = (.55, .60); AbAct_M = (1.15, .60)
        AbPass_S = (1.02, .53); AbPass_M = (2.65, .53)
        AbTran_S = (.25, .49); AbTran_M = (.71, .49)
        Bearing_S = (.10, .54); Bearing_M = (.50, .54)
        Deck_S = (.36, .54); Deck_M = (1.11, .54)
        FndRot_S = (99, .001); FndRot_M = (99, .001)
        FndTran_S = (6.31, 1.07); FndTran_M = (99, .001)
        Key_S = (0.33, 0.61); Key_M = (0.55, 0.64)
        Settle_S = (1.16, .86); Settle_M = (1.51, .97)
        JointSeal_S = (.23, .56); JointSeal_M = (8.27, .56)

        CompFra_dict = {
            'CompFra': {
                'Col': [Col_S, Col_M, Col_E, Col_C],
                'Seat_ab': [Seat_S, Seat_M, Seat_E, Seat_C],
                'Seat_super': [Seat_S, Seat_M, Seat_E, Seat_C],
                'AbAct': [AbAct_S, AbAct_M],
                'AbPass': [AbPass_S, AbPass_M],
                'AbTran': [AbTran_S, AbTran_M],
                'Bearing_ab': [Bearing_S, Bearing_M],
                'Bearing_super': [Bearing_S, Bearing_M],
                'Deck': [Deck_S, Deck_M],
                'FndRot': [FndRot_S, FndRot_M],
                'FndTran': [FndTran_S, FndTran_M],
                'Key_ab': [Key_S, Key_M],
                'Key_super': [Key_S, Key_M],
                'Settle': [Settle_S, Settle_M],
                'JointSeal_ab': [JointSeal_S, JointSeal_M],
                'JointSeal_super': [JointSeal_S, JointSeal_M]
            }
        }

    # %%
    import random, time
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.stats import lognorm
    import pandas as pd
    import math
    from collections import Counter

    from .utils import (sample_damage_correlated_baker,formalize_CountDamagedQty,map_comp_RC, 
        sample_order_IF, sample_replacementdur, sample_comp_repairdur, 
        order_comp_repairdur, decisiontree_reopeningFS, rd_num_byMean, sample_closedlanenum)

    # %%
    # Embedded database:
    ## Map from CompName to Comp

    # Define all the possible CompName and corresponding determinant CompModelName
    CompName_List = ['Col', 'Seat_ab','Super', 'ColFnd', 'AbFnd', 'Backwall', 'Bearing_ab', 'Key_ab','ApproSlab','JointSeal_ab','JointSeal_super', 'Seat_super', 'Bearing_super', 'Key_super']
    CompModelName_List = ['Col', 'Seat_ab','Seat_super', 'Deck', 'FndRot', 'FndTran', 'AbAct', 'AbTran', 'AbPass', 'Bearing_ab', 'Bearing_super',  'Key_ab', 'Key_super', 'Settle','JointSeal_ab', 'JointSeal_super']

    # Define a rule mapping from CompName to CompModelName
    mapping = { # map from Comp to CompModel
        'ColFnd': ['FndRot', 'FndTran'], #Column Foundation
        'AbFnd': ['AbAct','AbPass', 'AbTran'],
        'Backwall': ['AbAct','AbPass'],
        'Super': ['Deck'],
        'ApproSlab': ['AbAct','AbPass','Settle']
    }

    #CompModelQty is a dict to record how many qty of CompName is required. This is the # of lists in the damage sampling
    CompModelQty = {CompModelName: 0 for CompModelName in CompModelName_List}

    for CompName, qty in CompQty.items():
        # check if Comp in mapping
        if CompName in mapping:
            for mapped_CompModel in mapping[CompName]:
                # Update the Comp Model Qty by maximizing its request number among all Comps
                CompModelQty[mapped_CompModel] = max(qty, CompModelQty[mapped_CompModel])
        else:
            #CompModelName_QtyList.extend([comp] * qty)
            CompModelQty[CompName] = max(qty, CompModelQty[CompName])

    # %%
    CompFra_dict = {'CompFra':{'Col':[Col_S,Col_M,Col_E,Col_C], 'Seat_ab':[Seat_S,Seat_M,Seat_E,Seat_C],  'Seat_super':[Seat_S,Seat_M,Seat_E,Seat_C], 
                               'AbAct':[AbAct_S, AbAct_M], 'AbPass':[AbPass_S,AbPass_M], 'AbTran':[AbTran_S,AbTran_M],
                              'Bearing_ab':[Bearing_S,Bearing_M],'Bearing_super':[Bearing_S,Bearing_M],
                               'Deck':[Deck_S,Deck_M], 'FndRot':[FndRot_S,FndRot_M], 'FndTran':[FndTran_S,FndTran_M],
                              'Key_ab':[Key_S, Key_M], 'Key_super':[Key_S, Key_M],
                            'Settle':[Settle_S,Settle_M], 'JointSeal_ab' : [JointSeal_S, JointSeal_M],  'JointSeal_super' : [JointSeal_S, JointSeal_M]}
                   }

    # %%
    # --- Mapping of Repair Class (RC) to Functionality State (FS) and system DS and its description
    # --- Format: Worst-case RC: (FS#, FS name)
    RC_to_FS = {
        1: (0, 'Fully Repaired'), 
        2: (1, 'Fully Functional'), 
        3: (2, 'Moderate Lane Closure'),
        4: (3, 'Extensive Lane Closure'),
        5: (7, 'Complete Closure'),
        # The followings are exclusive for reopneing FS so the key (worst-case RC) is meaningless
        996: (4, 'Partially Reopen with Weight Restriction'),
        997: (5, 'Partially Reopen with Minor Lane Closure'),
        998: (6, 'Partially Reopen with Weight Restrictions and Minor Lane Closure')
    }


    # --- Format: Worst-case RC: (systemDS #, systemDS name)
    RC_to_sysDS = {
        1: (0, 'No Damage'), #RC: (sysDS#, Description)
        2: (1, 'Slight Damage'),
        3: (2, 'Moderate Damage'),
        4: (3, 'Extensive Damage'),
        5: (4, 'Complete Damage')
    }


    # --- Initial and Reopening FS lane closure #
    # (Updated 240402)  I've deleted the original dict, and directly put the closed lane numbers and their probabilities in the function 'sample_closedlanenum'


    # --- Reopneing FS probability 
    DecTreeProb_SuperAppro = [.2,.1,.7]  # Prob of [FS6,7,and 8] if superstructure or approach slab in RC3
    DecTreeProb_AbutRelated = [.6,.2,.2] # Prob of [FS6,7,and 8] if abutment-related components in RC3


    # --- Impeding factor (unit:day)
    # Structure: SysDS: {IFName:[LowerBound, UpperBound]}
    #Impeding_dataset = {
    #    1:{'IniInsp':[0.02,0.25], 'InDepInsp':[3,7], 'Financing':[180,720],'Design':[0,0], 'Permitting':[42,90],'Contractor':[360,720]},
    #    2:{'IniInsp':[0.02,0.25], 'InDepInsp':[3,7], 'Financing':[30,180],'Design':[30,60], 'Permitting':[42,90],'Contractor':[90,180]},
    #    3:{'IniInsp':[0.02,0.25], 'InDepInsp':[.083,1.5], 'Financing':[0,0],'Design':[7,60], 'Permitting':[1,7],'Contractor':[0.25,2]},
    #    4:{'IniInsp':[0.02,0.25], 'InDepInsp':[0,0], 'Financing':[0,0],'Design':[14,60], 'Permitting':[1,7],'Contractor':[0.25,2]}
    #} # unit: day

    # sequence: {IFName: [ EP not triggered, not affect functionality ], [EP not triggered, affect functionality], [EP triggered, bridge not in complete DS], [EP triggered, bridge in complete DS]} }
    Impeding_dataset = {
        'IniInsp': [[0.02,0.25], [0.02,0.25], [0.02,0.25], [0.02,0.25]],
        'InDepInsp': [ [3,7], [3,7], [.083,1.5], [0,0]  ],
        'Financing': [ [180,720], [30,60], [0,0],[0,0] ],
        'Design': [ [0,0], [30,60], [7,60], [14,60] ],
        'Permitting': [ [42,90],[42,90],[1,7],[1,7] ],
        'Contractor': [ [360,720], [90,180], [0.25,2],[0.25,2] ]

    } # unit: day


    # --- Bridge Replacement Duration & Req'd worker
    #  NOTE: these times *do not include* curing time
    # [MinDur, MaxDur]
    RepDur_bridge_singlespan = [28, 58]
    RepDur_bridge_twospan = [40, 86]
    RepDur_bridge_multispan_l30 = [40, 86]
    RepDur_bridge_multispan_g30_l100 = [40 + 30 * (num_span-2), 86 + 30 + (num_span-2)]
    RepDur_bridge_multispan_g100 = [40 + 180 * (num_span-2), 86 + 180 + (num_span-2)]
    # Max Worker corresponds to the MinDur, Min Worker corrsponds to the MaxDur
    RepDur_bridge_singlespan_WorkerBound = [20,5]
    RepDur_bridge_twospan_WorkerBound = [30,10]
    RepDur_bridge_multispan_l30_WorkerBound = [35,20]
    RepDur_bridge_multispan_g30_l100_WorkerBound = [35 + 15*(num_span-2), 20 + 15*(num_span-2)]
    RepDur_bridge_multispan_g100_WorkerBound = [35 + 15*(num_span-2), 20 + 15*(num_span-2)]


    # -- Component repair duration & Req'd worker # dataset 
    # date type: {'CompName':[ [MinDur for DS0, Max for DS0], [MinDur for DS1, Max for DS1],[etc.] } - not include Complete Damage
    #  NOTE: these times *include* curing time
    RepDur_comp_dict = {'Col': [ [1e-5,1e-4], [3 , 5], [3, 10], [34.5,48] ],
              'Seat_ab': [ [1e-5,1e-4], [1e-5,1e-4], [4, 11], [10 , 23] ],
              'Seat_super': [ [1e-5,1e-4], [1e-5,1e-4], [4, 11], [10 , 23] ],
              'Super': [ [1e-5,1e-4], [3, 5], [3, 10] ],
              'ColFnd': [ [1e-5,1e-4],[1e-5, 1e-5], [6, 17] ], 
              'AbFnd': [ [1e-5,1e-4], [1e-5, 1e-4], [4, 12] ],
              'Bearing_ab':[ [1e-5,1e-4], [1e-5,1e-4], [2,7] ],
              'Bearing_super':[ [1e-5,1e-4], [1e-5,1e-4], [2,7] ],
              'Key_ab': [ [1e-5,1e-4], [3, 5], [11.5, 22] ], 
              'Key_super': [ [1e-5,1e-4], [3, 5], [11.5, 22] ], 
              'Backwall': [ [1e-5,1e-4], [4, 9], [12.5, 26] ],
              'ApproSlab': [[1e-5,1e-4], [1, 4], [2, 8] ],
              'JointSeal_ab': [[1e-5,1e-4], [2, 4], [2, 4]],
              'JointSeal_super': [[1e-5,1e-4], [2, 4], [2, 4]]
                       }

    RepDur_WorkerBound_dict = {'Col': [ [1,1], [6,1], [6,2], [6,3] ], # Max Worker corresponds to the MinDur, Min Worker corrsponds to the MaxDur
              'Seat_ab': [ [1,1], [6,1], [6,3], [6,3] ],
              'Seat_super': [ [1,1], [6,1], [6,3], [6,3] ],
              'Super': [ [1,1], [6,4], [6,4]],
              'ColFnd': [ [1,1], [6,3], [6,3] ], 
              'AbFnd': [ [1,1],  [6,3], [6,3] ],
              'Bearing_ab':[ [1,1],  [6,2],[6,2] ],
              'Bearing_super':[ [1,1],  [6,2],[6,2] ],
              'Key_ab': [ [1,1],  [6,1], [6,3] ], 
              'Key_super': [ [1,1],  [6,1], [6,3] ], 
              'Backwall': [ [1,1],  [6,2], [6,2] ],
              'ApproSlab': [ [1,1],  [7,4], [7,4] ],
              'JointSeal_ab': [ [1,1],  [6,4], [6,4]],
              'JointSeal_super': [ [1,1],  [6,4], [6,4]]                 
                              }

    # -- Indicate what component and under what DS, what's the concrete curing time
    # {'CompName':[ [Curing time for DS0], [Curing time for DS1], etc. } - not include Complete Damage
    ConcreteCuringTime_comp_dict = {'Col': [ 0, 0, 0, 28],
              'Seat_ab': [ 0, 0, 0, 0],
              'Seat_super': [ 0, 0, 0, 0],
              'Super': [ 0, 0, 0 ],
              'ColFnd':  [0, 0, 0 ], 
              'AbFnd': [ 0, 0, 0 ],
              'Bearing_ab':[ 0, 0, 0 ],
              'Bearing_super':[ 0, 0, 0 ],
              'Key_ab': [ 0, 0, 7 ], 
              'Key_super': [ 0, 0, 7 ],
              'Backwall': [ 0, 0, 7 ],
              'ApproSlab': [0, 0, 0 ],
              'JointSeal_ab': [0, 0, 0],
               'JointSeal_super': [0, 0, 0]}

    # %%
    # Sampling component damage
    # 1) completely independent: independent sampling across different component types and quantity
    # 2) independent sampling across different component, perfect correlation within the same component type
    # 3) independent sampling across different component, partial correlation across the same component type
    
    # Major Outputs: 
    # `DamageSample_CompModel_Qty`: A dict with lists of lists containg damage sample for each nonlinear models that model component damage behavior, distinguishing the number of components. 
    # `DamageSample_Comp_Qty`: Map the `DamageSample_CompModel_Qty` into damage of component.
    # `Percent_Damage_CompModel_Qty` and `Percent_Damage_Comp_Qty` are frequencies of each component (distinguishin quantity) to check the proportion of falling into each of the damage tag 

    # %%
    random.seed(1223)
    np.random.seed(1223)

    # Sample correlated damage

    # Determine what CompModelNames are regarded to be in a same group
    # key: sys, value: subsys
    IntraGroupRule = {'Substructure':['Col','FndTran','FndRot','Seat_super', 'Bearing_super', 'Key_super', 'JointSeal_super'],
                      'Abutment':['Seat_ab','JointSeal_ab','AbAct','AbPass','AbTran','Settle','Key_ab','Bearing_ab'],
                       'Supersructure':['Deck']}

    # - DamageSample_CompModel_Qty - row num = comp num; col num = rlz num
    DamageSample_CompModel_Qty = sample_damage_correlated_baker(IM_fixed, CompModelName_List, CompModelQty, 
                                        IntraGroupRule, CompFra_dict, 
                                       w, num_rlz)


    # %%
    ##--- Map the sampled damage result from CompModel to Comp
    # - row num = comp num; col num = rlz num
    DamageSample_Comp_Qty =  {CompName:None for CompName in CompName_List} # Map CompModel-level damage to CompName level (following the mapping rule)

    for CompName_this,qty in CompQty.items():
        # If need to map from CompName?
        #print(CompName_this)
        if CompName_this in mapping:
            DSCompare_dict = {CompModelCompare: DamageSample_CompModel_Qty.get(CompModelCompare)[0:qty] for CompModelCompare in mapping[CompName_this]}
            DSCompare_array = [np.array(values) for values in DSCompare_dict.values()]
            DSCompare_array_stacked = np.stack(DSCompare_array)
            maxDS = np.max(DSCompare_array_stacked, axis=0)
            DamageSample_Comp_Qty[CompName_this] = maxDS.tolist()

        else:
            DamageSample_Comp_Qty[CompName_this] = DamageSample_CompModel_Qty[CompName_this][0:qty]

    # %%
    # Get the porportion of damage count per comp
    Percent_Damage_CompModel_Qty = {key:None for key in DamageSample_CompModel_Qty.keys()}
    Percent_Damage_Comp_Qty = {key:None for key in DamageSample_Comp_Qty.keys()}

    for CompModelName in Percent_Damage_CompModel_Qty.keys():
        DamageSample_current =  DamageSample_CompModel_Qty[CompModelName]
        num_comp = len(DamageSample_current)
        possible_DS = 4 if CompModelName.lower() in ['col', 'seat'] else 2
        DSSample_count = [ [None]*possible_DS for _ in range(num_comp)]
        for compnum_idx in range(num_comp):
            DS_count_compnum = Counter(DamageSample_current[compnum_idx])
            DS_freq_compnum = [DS_count_compnum.get(ds,0)/num_rlz for ds in range(possible_DS+1)]
            DSSample_count[compnum_idx] = DS_freq_compnum
        Percent_Damage_CompModel_Qty[CompModelName] = DSSample_count

    for CompName in Percent_Damage_Comp_Qty.keys():
        DamageSample_current =  DamageSample_Comp_Qty[CompName]
        num_comp = len(DamageSample_current)
        possible_DS = 4 if CompName.lower() in ['col', 'seat'] else 2
        DSSample_count = [ [None]*possible_DS for _ in range(num_comp)]
        for compnum_idx in range(num_comp):
            DS_count_compnum = Counter(DamageSample_current[compnum_idx])
            DS_freq_compnum = [DS_count_compnum.get(ds,0)/num_rlz for ds in range(possible_DS+1)]
            DSSample_count[compnum_idx] = DS_freq_compnum
        Percent_Damage_Comp_Qty[CompName] = DSSample_count

    # %%
    # only retrieve the entries with non-empty (meaning, non-zero comp quantity) in the list
    NonEmptyCompModelName_List = [key for key, value in DamageSample_CompModel_Qty.items() if value]
    NonEmptyCompName_List = [key for key, value in DamageSample_Comp_Qty.items() if value]

    DamageSample_CompModel_Qty = {key: DamageSample_CompModel_Qty[key] for key in NonEmptyCompModelName_List} # not needed further
    Percent_Damage_Comp_Qty = {key: Percent_Damage_Comp_Qty[key] for key in NonEmptyCompName_List}
    DamageSample_Comp_Qty = {key: DamageSample_Comp_Qty[key] for key in NonEmptyCompName_List}


    # Mapping Sampled Component Damage & Damaged Qty to Component-Repair Class
    
    # `function name`: map_comp_RC() 
    # `Description`: Determine repair classes for each component type based on the embedded damage-repair class relationships 
    # `inputs`:
    # - **count_DS_comp**: a count list from 'CountDamagedQty' that records DS counts (per rlz, per DS )
    # `outputs`:
    # - **RepairClass_dict**    

    # %%
    ##---- Convert 'DamageSample_Comp_Qty' (sampled scattered DS per qty, per rlz) into a count dict 'CountDamagedQty' (per rlz, per DS )
    CountDamagedQty = formalize_CountDamagedQty(NonEmptyCompName_List,DamageSample_Comp_Qty)
    # row: num_rlz; col: DS. Value in (idx_row, idx_col) indicate how many components have DS {idx_col} in rlz {idx_row}

    RepairClass_dict = {key: None for key in NonEmptyCompName_List}  # each key having a list with length = num_rlz
    ##---- Get the RC for each comp per rlz
    for CompName_this in NonEmptyCompName_List:
        RepairClass_dict[CompName_this] = map_comp_RC(CountDamagedQty[CompName_this], CompName_this)

    # %%
    # Determine Sys Initial Functionlaity State
    # `intput`: The rules that mapping the worst-case RC into sysDS and FS (emergensy response phase) are encoded in `RC_to_sysDS` and `RC_to_FS`, respectively.
    # `output`: **FS_rlz** and **sysDS_rlz** are lists recording mapped IFS and sysDS 

    # %%
    FS_rlz= []
    sysDS_rlz = []

    for rlz_idx in range(num_rlz):
        # Get the max RC for each realization across all components
        maxRC_perrlz = max(RC_perComp[rlz_idx] for RC_perComp in RepairClass_dict.values())
        # Assign FS and sysDS based on the worst-case RC
        FS_rlz.append(RC_to_FS[maxRC_perrlz][0])
        sysDS_rlz.append(RC_to_sysDS[maxRC_perrlz][0])

    #print(FS_rlz)
    #plt.hist(sysDS_rlz)

    # %%
    # Sampled closed lane # in the Initial FS stage
    # 
    # `function`: `rd_num_byMean` and `sample_closedlanenum`
    # `input`: PMF of closed lane numbers under a FS and original lane numbers. This has been encapsulated in the function `sample_closedlannum`. 
    # `output`: **ClosedLaneNum_Initial** (a list of closed # of lanes during the emergency response phase for each rlz)

    # %%
    random.seed(1223)
    np.random.seed(1223)

    ClosedLaneNum_Initial = []
    ClosedLaneNum_Initial = [sample_closedlanenum('Initial', FS_scalar, lane_before = num_lanes_before) for FS_scalar in FS_rlz]

    # %%
    # Impeding factors
    # `input`: Impeding_dataset
    # `function`: sample_order_IF()
    # `outputs`: **IF_sampled_list** & **IF_sum_list**
    # `Note`: There is triggeing probabilities defined for two impeding factors: `Permitting` and `In-depth inspection`.

    # %%
    random.seed(1223)
    np.random.seed(1223)

    emergency_protocol_flag_list = [1 if item >=3 else 0 for item in sysDS_rlz]
    IF_sampled_list, IF_sum_list = sample_order_IF(sysDS_rlz, Impeding_dataset,emergency_protocol_flag_list)

    # %%
    def sample_order_IF(sysDS_rlz_input, Impeding_dataset_input, emergency_protocol_flag_input):
        # emergency_protocol_flag=1 means it is triggered
        IF_sampled_list_output = {key: [None]*len(sysDS_rlz_input) for key in Impeding_dataset_input.keys()}
        IF_sum_list_output = [None]*len(sysDS_rlz_input)

        random.seed(1223)
        np.random.seed(1223)

        for SysDS_idx, SysDS in enumerate(sysDS_rlz_input):
            if SysDS not in range(0,5):
                raise ValueError("SysDS not in [0,4]")
            elif SysDS == 0: # system no damage
                IF_sum_list_output[SysDS_idx] = 0       
                for IFName,_ in Impeding_dataset_input[1].items():
                    IF_sampled_list_output[IFName][SysDS_idx] = 0
            else:    
                #Sampling individual impeding factors 
                for IFName,bounds_list in Impeding_dataset_input.items():
                    # EP not triggered, not affect functionality 
                    if SysDS in [0,1] and emergency_protocol_flag_input[SysDS_idx]!=1:
                        lower_bound, upper_bound = bounds_list[0]
                    #EP not triggered, affect functionality
                    elif SysDS in [2,3,4] and emergency_protocol_flag_input[SysDS_idx]!=1:
                        lower_bound, upper_bound = bounds_list[1]
                    #EP triggered, bridge not in complete DS
                    elif SysDS in [2,3] and emergency_protocol_flag_input[SysDS_idx]==1:
                        lower_bound, upper_bound = bounds_list[2]
                    # EP triggered, bridge in complete DS
                    elif SysDS ==4 and emergency_protocol_flag_input[SysDS_idx]==1:
                        lower_bound, upper_bound = bounds_list[3]

                    IF_sampled_list_output[IFName][SysDS_idx] = random.uniform(lower_bound, upper_bound)

                # The triggering probability of permitting is 30%
                if (np.random.uniform(0, 1) > .3):
                    IF_sampled_list_output['Permitting'][SysDS_idx] = 0

                # The triggering probability of in-depth inspection dependes on sysDS
                if (SysDS == 0 or 4): threshold = 0
                if (SysDS == 1): threshold = .1
                if (SysDS == 2): threshold = 1
                if (SysDS == 3): threshold = .6   

                if (np.random.uniform(0, 1) > threshold):
                    IF_sampled_list_output['InDepInsp'][SysDS_idx] = 0

                #Order the sampled impeding factors and calculate the sum
                if emergency_protocol_flag_input[SysDS_idx]!=1: # Sequencing under non-emergency response
                    IF_sum_list_output[SysDS_idx] = IF_sampled_list_output['IniInsp'][SysDS_idx] + \
                    IF_sampled_list_output['InDepInsp'][SysDS_idx]+\
                    max(IF_sampled_list_output['Financing'][SysDS_idx], IF_sampled_list_output['Contractor'][SysDS_idx]+IF_sampled_list_output['Design'][SysDS_idx]+IF_sampled_list_output['Permitting'][SysDS_idx])

                else: # Sequencing under emergency response
                    IF_sum_list_output[SysDS_idx] = IF_sampled_list_output['IniInsp'][SysDS_idx] + \
                    IF_sampled_list_output['InDepInsp'][SysDS_idx]+\
                    max(IF_sampled_list_output['Contractor'][SysDS_idx], IF_sampled_list_output['Permitting'][SysDS_idx]+IF_sampled_list_output['Design'][SysDS_idx])

        return IF_sampled_list_output,IF_sum_list_output

    # %%
    # ## Replacement Duration
    # `function`: **sample_replacementdur**
    # `input`: replacement duration and worker number bounds, `Worker_Replace`
    # `outputs`: one realization in  **RepDur_sampled_comp_rlz**

    # %%
    # detetermine median bridge replacement duration based on worker assignment and bridge geometry
    if num_span == 1: repla_durbound = RepDur_bridge_singlespan; repla_workerbound = RepDur_bridge_singlespan_WorkerBound
    if num_span == 2: repla_durbound = RepDur_bridge_twospan; repla_workerbound = RepDur_bridge_twospan_WorkerBound
    if (num_span > 2) and (height <=30): repla_durbound = RepDur_bridge_multispan_l30; repla_workerbound = RepDur_bridge_multispan_l30_WorkerBound
    if (num_span > 2) and (height >30 and height <= 100):  repla_durbound = RepDur_bridge_multispan_g30_l100; repla_workerbound = RepDur_bridge_multispan_g30_l100_WorkerBound
    if (num_span > 2) and (height > 100):  repla_durbound = RepDur_bridge_multispan_g30_l100; repla_workerbound = RepDur_bridge_multispan_g100_WorkerBound
    repldur_min,repldur_max = repla_durbound
    replworker_max, replworker_min = repla_workerbound

    # %%
    # Repair Duration
    # 
    # `function`: **sample_comp_repairdur** and **order_comp_repairdur**
    # `outputs`: one rlz in **RepDur_sum_rlz** and **RepDur_sampled_comp_rlz**

    # %%
    random.seed(1223)
    np.random.seed(1223)

    RepDur_sum_rlz = [None for _ in range(num_rlz)] # total repair/replacement durations per rlz
    RepDur_sampled_comp_rlz = [{CompName:None for CompName in RepDur_comp_dict} for _ in range(num_rlz)] # initialize the list with all Nones

    for rlz_idx, sysDS in enumerate(sysDS_rlz):
        if sysDS == 4: # bridge is unrepairable
            RepDur_sampled_comp_rlz[rlz_idx] = 'Complete' # if replaced, no need to disaggregate the time onto each component
            RepDur_sum_rlz[rlz_idx] = sample_replacementdur(Worker_Replace,repldur_min, repldur_max, replworker_max, replworker_min,
                                                            WorkHour_replacement, num_concrete_pour_replacement, dispersion_assigned)


        else: # bridge is repairable
            # DamageSample_Comp_Qty_rlz is a dict with CompName keys and values = sampled damage under the current rlz_idx(with the same format as DamageSample_Comp_Qty)
            DamageSample_Comp_Qty_rlz = {CompName: [DmSample_perqty[rlz_idx] for DmSample_perqty in DmSample] for CompName, DmSample in DamageSample_Comp_Qty.items()}
            #print(DamageSample_Comp_Qty_rlz)
            RepDur_sampled_comp_rlz[rlz_idx] = sample_comp_repairdur(
                    DamageSample_Comp_Qty_rlz, RepDur_comp_dict, RepDur_WorkerBound_dict, 
                    WorkerAllo_percrew, NumCrew_percomp, WorkHour_repairable, 
                    ConcreteCuringTime_comp_dict,  ColSuperMatType_dict,
                    dispersion_assigned)
            RepDur_sum_rlz[rlz_idx] = order_comp_repairdur(RepDur_sampled_comp_rlz[rlz_idx],CompName_List)



    # %%
    # FS During Reopening Stage and closed lane number
    # 
    # `input`: 
    # **RC_to_sysDS** a rule that stipulate the FS tag and FS name. The first five are for both stages and the last three for reopneing stage. 
    # **RepairClass_dict**:  component-level RS that were obtain earlier.
    # **RepDur_sampled_comp_rlz**: Sampled component repair duration (if applicable) per rlz.
    # **FS_rlz**: the FS determined in the Initial phase per rlz. 
    #
    #  `output`:
    # **FS_rlz_Reopening** sampled FS per rlz during reopening stage.
    # **ReopeningTriggeringFlag_rlz** indicating whether reopening phase is triggered in each rlz.
    # **ClosedLaneNum_Reopening** (a list of closed # of lanes for each rlz)


    # %%
    ##---- Sampling reopening FS
    FS_rlz_Reopening=[]
    ReopeningTriggeringFlag_rlz = []

    for rlz_idx in range(num_rlz):
        RC_comp_thisrlz  = {CompName: RClist[rlz_idx] for CompName, RClist in RepairClass_dict.items()}
        RepDur_sampled_thisrlz = RepDur_sampled_comp_rlz[rlz_idx]
        FS_rlz_Reopening_thisrlz,ReopeningTriggeringFlag_thisrlz =\
                            decisiontree_reopeningFS(RC_comp_thisrlz,
                            RepDur_sampled_thisrlz, FS_rlz[rlz_idx],
                            DecTreeProb_SuperAppro, DecTreeProb_AbutRelated)
        FS_rlz_Reopening.append(FS_rlz_Reopening_thisrlz)
        ReopeningTriggeringFlag_rlz.append(ReopeningTriggeringFlag_thisrlz)

    # %%
    ##---- Closed lane # sampling under reopening stage
    ClosedLaneNum_Reopening = []
    weight_restriction_tag_Reopening = []
    for rlz_idx in  range(num_rlz):
        closedlane_reopening_thisrlz, weight_restriction_tag_thisrlz = sample_closedlanenum(
            'Reopening', FS_rlz_scalar = FS_rlz_Reopening[rlz_idx], 
            lane_before = num_lanes_before, closed_lane_IFS_rlz_scalar =  ClosedLaneNum_Initial[rlz_idx])

        ClosedLaneNum_Reopening.append(closedlane_reopening_thisrlz)
        weight_restriction_tag_Reopening.append(weight_restriction_tag_thisrlz)

    #ClosedLaneNum_Reopening = [sample_closedlanenum('Reopening', FS_rlz_scalar = FS_rlz_Reopening[rlz_idx], lane_before = num_lanes_before, closed_lane_IFS_rlz_scalar =  ClosedLaneNum_Initial[rlz_idx]) for rlz_idx in  range(num_rlz)]

    # %%
    # Save the results to local directionary 

    # %%
    data= { #change  fullydepen, indep, partiallydepen
        'DamageSample_Comp_Qty': DamageSample_Comp_Qty,
        'FS_rlz': FS_rlz,
        'sysDS_rlz': sysDS_rlz,
        'RepairClass_dict': RepairClass_dict,
        'ClosedLaneNum_Initial': ClosedLaneNum_Initial,
        'FS_rlz_Reopening': FS_rlz_Reopening,
        'ClosedLaneNum_Reopening': ClosedLaneNum_Reopening,
        'IF_sampled_list': IF_sampled_list,
        'IF_sum_list': IF_sum_list,
        'RepDur_sum_rlz':RepDur_sum_rlz ,
        'RepDur_sampled_comp_rlz':RepDur_sampled_comp_rlz
    }


    # %%
    import pickle 

    with open('Results.pkl', 'wb') as file: # change file name
        pickle.dump((data), file) # change variable name

    print("Analysis is done.")
    
    if return_data:
        return data

    # %%

    

