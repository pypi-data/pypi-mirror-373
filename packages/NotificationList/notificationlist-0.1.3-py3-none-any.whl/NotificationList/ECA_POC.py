#Runs on a folder of files to find Stackable tables and regex hits
import os
import sys
from time import time
from datetime import timedelta, datetime
from io import StringIO
from types import CoroutineType
from openpyxl import workbook
import xlrd
import pandas as pd
import numpy as np
import re
import multiprocessing as mp
import networkx 
from networkx.algorithms.components.connected import connected_components 
from networkx.algorithms.centrality.current_flow_betweenness import edge_current_flow_betweenness_centrality
import openpyxl
import csv
from tqdm import tqdm
import warnings
import Excel_Data as ED
import ECA_Definitions as ECA

warnings.filterwarnings('ignore')
maxInt =  500000 #sys.maxsize
csv.field_size_limit(maxInt)


############################
##### Global Variables #####
############################
datapath_in_path = r"C:\Users\HP\OneDrive\Desktop\Development\TestingMaterial\Natives\\"
datapath_out_str = r"C:\Users\HP\OneDrive\Desktop\Development\TestingMaterial\Natives\\Output\\"
# datapath_out_str = r"C:\Users\HP\OneDrive\Desktop\Development\TestingMaterial\Natives\\Stats\\"
NbProcesses_int = 1
projectname_str = "Project_Name"
only_tables_bool = False #run on only potential tables in excels, csvs, and tsvs

#File Path creation
if not os.path.exists(datapath_in_path):
    print("Datapath file location does not exist")
if not os.path.exists(datapath_out_str):
    os.makedirs(datapath_out_str)
if not os.path.exists(datapath_out_str):
    os.makedirs(datapath_out_str)

tstart_time = time()
tstart2_time = time() 
############################
### End Global Variables ###
############################


def printelaps():
    global tstart_time
    global tstart2_time
    print( "ELAPS TOT:" + str(timedelta(seconds=(time() - tstart_time))).split('.')[0] + " ELAPS DIFF: " + str(timedelta(seconds=(time() - tstart2_time))).split('.')[0] ); tstart2_time = time()


def printelaps2():
    global tstart_time
    global tstart2_time
    print ( "ELAPS TOT:" + str(timedelta(seconds=(time() - tstart_time))).split('.')[0] + " ELAPS DIFF: " + str(timedelta(seconds=(time() - tstart2_time))).split('.')[0] ); tstart2_time = time()


def analyze_files_func(dataworker):
    datapath_out_str = dataworker["datapathOut"]
    datapath_out_str = dataworker["StatFile"]
    NbProcesses_int = dataworker["ProcessNo"]
    print("Process: " + str(NbProcesses_int) + " | Files: " + str(len(dataworker["FilesIn"])))
    filecnt_int = 0
    fileprintcnt_int = 100
    stat_dict = {}
    with open(datapath_out_str + "Group_Col_Table_"+ NbProcesses_int +".dat",'w') as file:
        file.write("\xfeGroupNo\xfe\x14\xfeTable_Columns\xfe\n")
    for filename in tqdm(dataworker["FilesIn"]):
        filecnt_int +=1
        processed_file = False
        #if filecnt_int % fileprintcnt_int = 0: print(filecnt_int)
        curfilename = str(filename[filename.rfind('\\')+1:filename.rfind(".",filename.rfind('\\')+1)])
        filename_value = str(curfilename)
        fileext_value = str(filename[filename.rfind('.')+1:])
        try:
            if fileext_value.lower() in ['xls','xlsx','xlsm','xlsb']:
                    temp_stat_dict = ECA.eca_excel_funct(filename,datapath_out_str,NbProcesses_int)
                    processed_file = True
            elif fileext_value.lower() in ['csv','tsv','txt']:
                    temp_stat_dict = ECA.eca_delimited_file_func(filename,datapath_out_str,NbProcesses_int)
                    processed_file = True
            elif only_tables_bool == False:
                    temp_stat_dict = ECA.eca_text_func(filename,datapath_out_str,NbProcesses_int)
                    processed_file = True
        except Exception as e:
            temp_stat_dict = {
            "FileName": filename_value
            ,"Extension": fileext_value
            ,"Sheet Name": np.nan
            ,"Key Columns": np.nan
            ,"First Row Columns": np.nan
            ,"Table Columns": np.nan
            ,"Table Columns Mapping": np.nan
            ,"Table Number of Rows": np.nan
            ,"Total Number of Columns": np.nan
            ,"Total Number of Rows": np.nan
            ,"Processing Notes": str(e)
            ,"Table Group": np.nan
            ,"Name Identifier": np.nan
            ,"Name Count": np.nan
            ,"Address Identifier": np.nan
            ,"Address Count": np.nan
            ,"DOB Identifier": np.nan
            ,"DOB Count": np.nan
            ,"SSN Identifier": np.nan
            ,"SSN Count": np.nan
            ,"TIN Identifier": np.nan
            ,"TIN Count": np.nan
            ,"Phone Number Identifier": np.nan
            ,"Phone Count": np.nan
            ,"Driver's License Identifier": np.nan
            ,"Driver's License Count": np.nan
                                }
            print(filename,str(e))
        
        #Updating Stats Dictionary
        if processed_file == True:
            if len(stat_dict) == 0:
                    for k,v in temp_stat_dict.items():
                        stat_dict[k] = v
            else:
                    for k,v in temp_stat_dict.items():
                        for n in v:
                            stat_dict[k].append(n)
    return stat_dict


def to_graph(l):
    G = networkx.Graph()
    for part in l:
        # each sublist is a bunch of nodes
        G.add_nodes_from(part)
        # it also imlies a number of edges:
        G.add_edges_from(to_edges(part))
    return G


def to_edges(l):
    """ 
        treat `l` as a Graph and returns it's edges 
        to_edges(['a','b','c','d']) -> [(a,b), (b,c),(c,d)]
    """
    it = iter(l)
    last = next(it)

    for current in it:
        yield last, current
        last = current  


if __name__ == "__main__":
    printelaps()
    starttime_str = str(datetime.now())
    pool = mp.Pool(NbProcesses_int)

    runn_all_files_bool = True
    files_to_do_list = []
    if runn_all_files_bool == False:
        with open(r'\\Bitsandbytes.global\ls\Incident Response\Active Projects\ProjectFolder\Target_Files\TagetFilesList.txt','r') as file:
            for line in file:
                    files_to_do_list.append(line.strip('\n').lower())

    if not os.path.exists(datapath_in_path):
        print("Datapath file location does not exist")
        exit()
    if not os.path.exists(datapath_out_str):
        os.makedirs(datapath_out_str)
    if not os.path.exists(datapath_out_str):
        os.makedirs(datapath_out_str)
    filelist_dict = {} # list by Process, ex fileList[2] = [file1, file2, ...] for Process 2

    for i in range(NbProcesses_int):
        filelist_dict[i] = []
    i = 0

    if NbProcesses_int > 1:
        print("Processing files by bytes size")
        total_bytes_int = 0
        for root, subdirs, files in os.walk(datapath_in_path):
            for filename in files:
                    if (filename.lower() in files_to_do_list) or (runn_all_files_bool == True):
                        total_bytes_int += os.path.getsize(os.path.join(root, filename))
        total_bytes_ratio_int = total_bytes_int / NbProcesses_int
        print("Total bytes: ",total_bytes_int)
        print("Total bytes per process: ",total_bytes_ratio_int)
        current_bytes_int = 0
        for root, subdirs, files in os.walk(datapath_in_path):
            for filename in files:
                    if (filename.lower() in files_to_do_list) or (runn_all_files_bool == True):
                        filelist_dict[i].append(os.path.join(root, filename))
                        current_bytes_int += os.path.getsize(os.path.join(root, filename))
                        if current_bytes_int > total_bytes_ratio_int and i < NbProcesses_int:
                            current_bytes_int = 0
                            i += 1
    else:
        for root, subdirs, files in os.walk(datapath_in_path):
            for filename in files:
                    if (filename[0:filename.rfind(".")].lower() in files_to_do_list) or (runn_all_files_bool == True):
                        filelist_dict[i].append(os.path.join(root, filename))
                        i +=1
                        if i > NbProcesses_int-1:
                            i = 0
    dataworker = []       
    for i in range(NbProcesses_int):
        dataworker.append( {
            "FilesIn": filelist_dict[i],
            "datapathOut": datapath_out_str,
            "ProjectName": projectname_str,
            "StatFile": datapath_out_str,
            "ProcessNo": str(i+1),
                })

    sd = pool.map(analyze_files_func,dataworker)

    fullstat_dict = {}
    for s in sd:
        for k,v in s.items():
            if k in fullstat_dict.keys():
                    fullstat_dict[k] += v
            else:
                    fullstat_dict[k] = v

    for k,v in fullstat_dict.items():
        print(str(k),len(v))
    
    df = pd.DataFrame.from_dict(fullstat_dict,orient='columns')
    groupno_dict = {}
    groupno_matching_dict = {}
    #Combine groups from processes
    print("Creating Table Groups")
    for i in range(1,NbProcesses_int+1):
        with open(datapath_out_str + "Group_Col_Table_"+ str(i) +".dat",'r') as file:
            file_opened_bool = False
            while file_opened_bool == False:
                    try:
                        csv.field_size_limit(maxInt)
                        r = csv.reader(file, delimiter='\x14', quotechar='\xfe')
                        file_opened_bool = True
                    except:
                        maxInt = int(maxInt/10)
            lncnt_int = 1
            for line in r:
                    if lncnt_int == 1:lncnt_int +=1;continue
                    lncnt_int +=1
                    if len(groupno_dict) == 0:
                        groupno_dict[line[0]] = line[1]
                        groupno_matching_dict[line[0]] = [line[0]]
                    else:
                        if not line[1] in groupno_dict.values():
                            groupno_dict[line[0]] = line[1]
                            groupno_matching_dict[line[0]] = [line[0]]
                        else:
                            for k,v in groupno_dict.items():
                                if v == line[1]:
                                        groupno_matching_dict[k] += [line[0]]
                                        break
        os.remove(datapath_out_str + "Group_Col_Table_"+ str(i) +".dat")
    #Creating Stack Tables Folder
    if not os.path.exists(datapath_out_str + "Grouped_Tables"):
        os.makedirs(datapath_out_str + "Grouped_Tables")
    started_groups_list = []
    #Writing one table columns master list
    with open(datapath_out_str + "All_Group_Col_Table.dat",'w+') as file:
        file.write("\xfeGroupNo\xfe\x14\xfeTable_Columns\xfe\n")
        for key, value in groupno_dict.items():
            file.write("\xfe" + key + "\xfe\x14\xfe" + value + "\xfe\n")
    print("Creating Stacked Files")
    #Combining stacked tables based on new master groups
    for stackedfile in os.listdir(datapath_out_str):
        if stackedfile.find("Group") > -1:
            curfilegroup = str(stackedfile[stackedfile.rfind('_')+1:stackedfile.rfind(".",stackedfile.rfind('_')+1)])
            for key, value in groupno_matching_dict.items():
                    if curfilegroup in value:
                        if key in started_groups_list:
                            concat_df = pd.read_csv(datapath_out_str + stackedfile,delimiter=',', dtype=str, keep_default_na=False, skipinitialspace=True,encoding='utf-8')
                            with open(datapath_out_str + "Grouped_Tables\\" + "Group" + "_" + str(key) + ".csv", 'a+', newline ='\n',encoding='utf-16') as file:
                                concat_df.to_csv(file,index=False,header=False,encoding='utf-16',quoting=csv.QUOTE_ALL)
                            os.remove(datapath_out_str + stackedfile)
                        else:
                            concat_df = pd.read_csv(datapath_out_str + stackedfile,delimiter=',', dtype=str, keep_default_na=False, skipinitialspace=True,encoding='utf-8-sig')
                            concat_df.to_csv(datapath_out_str + "Grouped_Tables\\" + "Group" + "_" + str(key) + ".csv",header=True,index=False,quoting=csv.QUOTE_ALL,encoding='utf-16')
                            os.remove(datapath_out_str + stackedfile)
                            started_groups_list.append(key)
                        break
    # print(df)
    print("Writing Stats to file")
    for index, row in df.iterrows():
        if row['Table Columns Mapping'] in groupno_dict.values():
            for k,v in groupno_dict.items():
                    if v == row['Table Columns Mapping']:
                        df.at[index,'Table Group'] = k
    groupcnt_col_int = df.columns.get_loc("Table Group") + 1
    df.insert(groupcnt_col_int,"Group Count",'')
    df["Group Count"] = df.groupby('Table Group')['Table Group'].transform('count')

    #Get groups of Files in the same group
    tempdf = df[['Table Group','FileName']].copy()
    tempdf['Table Group'] = tempdf['Table Group'].replace('',np.nan)
    tempdf = tempdf.dropna()
    tempdf = tempdf[tempdf['Table Group'] != ""]
    if len(tempdf) > 0:
        tempdf = tempdf.groupby(['Table Group'])['FileName'].agg(';'.join).reset_index()
        tempdf['RA_index'] = tempdf['FileName'].apply(lambda x: x.split(';'))
        masterlist = tempdf['RA_index'].tolist()
        tempdf2 = pd.DataFrame(columns = ['RA_explode','RA_index'])
        tempdf2['RA_explode'] = masterlist
        tempdf2['RA_explode'] = tempdf2['RA_explode'].apply(lambda x: set(x))
        sets = tempdf2['RA_explode'].tolist()
        G = to_graph(sets)
        sets = (list(connected_components(G)))

        df.insert(groupcnt_col_int+1,"WorkFlow Groups",'')
        df.insert(groupcnt_col_int+2,"WorkFlow Group Count",'')
        df.insert(groupcnt_col_int+3,"Files Represnted in Workflow Group",'')
        grpno = 1
        grouping_dict = {}
        for s in sets:
            for i in s:
                    if not i in grouping_dict.keys():
                        cntrl_list = df[df['FileName'] == i].index.tolist()
                        for x in cntrl_list:
                            df.at[x,'WorkFlow Groups'] = grpno
                        grouping_dict[i] = grpno
            grpno +=1
        df["WorkFlow Group Count"] = df.groupby('WorkFlow Groups')['WorkFlow Groups'].transform('count')
        filecount_dict = df.groupby('WorkFlow Groups')['FileName'].apply(list).to_dict()
        df["Files Represnted in Workflow Group"] = df["WorkFlow Groups"].apply(lambda x: len(set(filecount_dict[x])))

        del tempdf2
    del tempdf

    os.remove(datapath_out_str+"All_Group_Col_Table.dat")
    os.remove(datapath_out_str+"ConCat_Columns.csv")
    
    df.sort_values(['WorkFlow Groups','Table Group','FileName'], ascending=[True,True,True], inplace=True)
    df.to_excel(datapath_out_str+"!Header_Analysis.xlsx",sheet_name="Header_Analysis",header=True,index=False)
    df = pd.read_excel(datapath_out_str+"!Header_Analysis.xlsx",dtype=str)
    df = df.rename(columns={'FileName':'DocID', 'Total Number of Columns':'ColumnCount', 'Total Number of Rows': 'RowCount', 'Processing Notes':'Comments', 'Table Group':'Group_No.', 'Group Count':'FileCount'})
    df = df[['DocID', 'Extension', 'Sheet Name', 'Key Columns', 'ColumnCount', 'RowCount', 'Comments', 'Group_No.', 'FileCount']]
    df.to_excel(datapath_out_str+"!Header_Analysis.xlsx",sheet_name="Header_Analysis",header=True,index=False)

    print ("Start:" + starttime_str + "   End Time:" + str(datetime.now()))
    printelaps2()