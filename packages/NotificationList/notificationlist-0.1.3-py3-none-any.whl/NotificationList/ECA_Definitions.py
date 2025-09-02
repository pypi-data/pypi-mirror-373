#Used for ECA script. Finds tables and regex hits in files
import Excel_Data as ED
import pandas as pd
import numpy as np
import re
import csv

eca_stat_dict = {
          "FileName":[]
          ,"Extension":[]
          ,"Sheet Name":[]
          ,"Key Columns":[]
          ,"First Row Columns":[]
          ,"Table Columns":[]
          ,"Table Columns Mapping":[]
          ,"Table Number of Rows":[]
          ,"Total Number of Columns":[]
          ,"Total Number of Rows":[]
          ,"Processing Notes":[]
          ,"Table Group":[]
          ,"Name Identifier":[]
          ,"Name Count":[]
          ,"Address Identifier":[]
          ,"Address Count":[]
          ,"DOB Identifier":[]
          ,"DOB Count":[]
          ,"SSN Identifier":[]
          ,"SSN Count":[]
          ,"TIN Identifier":[]
          ,"TIN Count":[]
          ,"Phone Number Identifier":[]
          ,"Phone Count":[]
          ,"Driver's License Identifier":[]
          ,"Driver's License Count":[]
          }

TableGroupNo_int = 1

def eca_excel_funct(file_path,datapath_out_str,NbProcesses_int):
     temp_eca_stat_dict = {}
     for k in eca_stat_dict:
          temp_eca_stat_dict[k] = []
     curfilename_str = str(file_path[file_path.rfind('\\')+1:file_path.rfind(".",file_path.rfind('\\')+1)])
     filename_value = str(curfilename_str)
     fileext_value = str(file_path[file_path.rfind('.')+1:])
     ShtNme_value = np.nan
     keyclm_value = np.nan
     firstrowclms_value = np.nan
     tableclm_value = np.nan
     tablemapclm_value = np.nan
     tablerowcnt_value = np.nan
     clmno_value = np.nan
     totalrowcnt_value = np.nan
     ProcessNotes_value = np.nan
     TableGroup_value = np.nan
     NameId_value = np.nan
     NameCnt_value = np.nan
     DOBId_value = np.nan
     DOBCnt_value = np.nan
     AddressId_value = np.nan
     AddressCnt_value = np.nan
     SSNId_value = np.nan
     SSNCnt_value = np.nan
     TINId_value = np.nan
     TINCnt_value = np.nan
     PhoneId_value = np.nan
     PhoneCnt_value = np.nan
     DLId_value = np.nan
     DLCnt_value = np.nan
     try:
          open_workbook = pd.read_excel(open(file_path,'rb'),sheet_name=None, index_col=None, dtype=str, keep_default_na=False, engine='openpyxl')
     except Exception as e:
          exception_msg = str(e)
          try:
               open_workbook = pd.read_excel(open(file_path,'rb'),sheet_name=None, index_col=None, dtype=str, keep_default_na=False, engine='xlrd')
          except Exception as e:
               exception_msg = exception_msg + '|' + str(e)
               try:
                    open_workbook = pd.read_excel(open(file_path,'rb'),sheet_name=None, index_col=None, dtype=str, keep_default_na=False, engine='pyxlsb')
               except Exception as e:
                    exception_msg = exception_msg + '|' + str(e)
                    filename_value = str(curfilename_str)
                    ProcessNotes_value = "Error Opening File"
                    temp_eca_stat_dict["FileName"].append(filename_value)
                    temp_eca_stat_dict["Extension"].append(fileext_value)
                    temp_eca_stat_dict["Sheet Name"].append(ShtNme_value)
                    temp_eca_stat_dict["Key Columns"].append(keyclm_value)
                    temp_eca_stat_dict["First Row Columns"].append(firstrowclms_value)
                    temp_eca_stat_dict["Table Columns"].append(tableclm_value)
                    temp_eca_stat_dict["Table Columns Mapping"].append(tablemapclm_value)
                    temp_eca_stat_dict["Table Number of Rows"].append(tablerowcnt_value)
                    temp_eca_stat_dict["Total Number of Columns"].append(clmno_value)
                    temp_eca_stat_dict["Total Number of Rows"].append(totalrowcnt_value)
                    temp_eca_stat_dict["Processing Notes"].append(ProcessNotes_value + "\n" + exception_msg)
                    temp_eca_stat_dict["Table Group"].append(TableGroup_value)
                    temp_eca_stat_dict["Name Identifier"].append(NameId_value)
                    temp_eca_stat_dict["Name Count"].append(NameCnt_value)
                    temp_eca_stat_dict["Address Identifier"].append(AddressId_value)
                    temp_eca_stat_dict["Address Count"].append(AddressCnt_value)
                    temp_eca_stat_dict["DOB Identifier"].append(DOBId_value)
                    temp_eca_stat_dict["DOB Count"].append(DOBCnt_value)
                    temp_eca_stat_dict["SSN Identifier"].append(SSNId_value)
                    temp_eca_stat_dict["SSN Count"].append(SSNCnt_value)
                    temp_eca_stat_dict["TIN Identifier"].append(TINId_value)
                    temp_eca_stat_dict["TIN Count"].append(TINCnt_value)
                    temp_eca_stat_dict["Phone Number Identifier"].append(PhoneId_value)
                    temp_eca_stat_dict["Phone Count"].append(PhoneCnt_value)
                    temp_eca_stat_dict["Driver's License Identifier"].append(DLId_value)
                    temp_eca_stat_dict["Driver's License Count"].append(DLCnt_value)
                    return temp_eca_stat_dict
            
     for name, sheet in open_workbook.items():
          compiling_dict = eca_findtable_func(filename_value,fileext_value,sheet,name,datapath_out_str,NbProcesses_int)
          for k,v in compiling_dict.items():
               temp_eca_stat_dict[k].append(v[0])
     return temp_eca_stat_dict

def eca_text_func(file_path,datapath_out_str,NbProcesses_int):
     temp_eca_stat_dict = {}
     for k in eca_stat_dict:
          temp_eca_stat_dict[k] = []
     curfilename_str = str(file_path[file_path.rfind('\\')+1:file_path.rfind(".",file_path.rfind('\\')+1)])
     filename_value = str(curfilename_str)
     fileext_value = str(file_path[file_path.rfind('.')+1:])
     ShtNme_value = np.nan
     keyclm_value = np.nan
     firstrowclms_value = np.nan
     tableclm_value = np.nan
     tablemapclm_value = np.nan
     tablerowcnt_value = np.nan
     clmno_value = np.nan
     totalrowcnt_value = np.nan
     ProcessNotes_value = np.nan
     TableGroup_value = np.nan
     NameId_value = np.nan
     NameCnt_value = np.nan
     DOBId_value = np.nan
     DOBCnt_value = np.nan
     AddressId_value = np.nan
     AddressCnt_value = np.nan
     SSNId_value = np.nan
     SSNCnt_value = np.nan
     TINId_value = np.nan
     TINCnt_value = np.nan
     PhoneId_value = np.nan
     PhoneCnt_value = np.nan
     DLId_value = np.nan
     DLCnt_value = np.nan
     cnt = 0
     with open(file_path, 'rb') as file:
          file = file.read()
          namecnt = len([*re.finditer(ED.name_rx,file)])
          #print(*re.findall(ED.name_rx,file))
          ssncnt = len([*re.finditer(ED.ssn_rx,file)])
          dobcnt = len([*re.finditer(ED.dates_rx,file)])
          tincnt = len([*re.finditer(ED.TINNumber_rx,file)])
          addresscnt = len([*re.finditer(ED.btc_address_rx,file)]) + len([*re.finditer(ED.street_address_rx,file)]) + len([*re.finditer(ED.po_box_rx,file)])
          phonecnt = len([*re.finditer(ED.phonenumber_rx,file)])
          dlcnt = len([*re.finditer(ED.driverslience_rx,file)])

          if file_path.lower().endswith(".txt") or file_path.lower().endswith(".msg"): cr = b'\n' 
          else: cr = b'\r'
          for line in file.split(cr):
               for n in (ED.Firstname + ED.middlename + ED.lastname + ED.Fullname):
                    if n in str(line): NameId_value = n
               for n in (ED.tinnumber):
                    if n in str(line): TINId_value = n
               for n in (ED.ssn):
                    if n in str(line): SSNId_value = n
               for n in (ED.dob):
                    if n in str(line): DOBId_value = n
               for n in (ED.address + ED.address2):
                    if n in str(line): AddressId_value = n
               for n in (ED.driverslicence):
                    if n in str(line): DLId_value = n
               cnt +=1
          
          if namecnt > 0: 
               NameCnt_value = namecnt
          if addresscnt > 0: 
               AddressCnt_value = addresscnt
          if ssncnt > 0: 
               SSNCnt_value = ssncnt
          if dobcnt > 0: 
               DOBCnt_value = dobcnt
          if tincnt > 0: 
               TINCnt_value = tincnt
          if phonecnt > 0: PhoneCnt_value = phonecnt
          if dlcnt > 0: DLCnt_value = dlcnt
     totalrowcnt_value = cnt
     temp_eca_stat_dict["FileName"].append(filename_value)
     temp_eca_stat_dict["Extension"].append(fileext_value)
     temp_eca_stat_dict["Sheet Name"].append(ShtNme_value)
     temp_eca_stat_dict["Key Columns"].append(keyclm_value)
     temp_eca_stat_dict["First Row Columns"].append(firstrowclms_value)
     temp_eca_stat_dict["Table Columns"].append(tableclm_value)
     temp_eca_stat_dict["Table Columns Mapping"].append(tablemapclm_value)
     temp_eca_stat_dict["Table Number of Rows"].append(tablerowcnt_value)
     temp_eca_stat_dict["Total Number of Columns"].append(clmno_value)
     temp_eca_stat_dict["Total Number of Rows"].append(totalrowcnt_value)
     temp_eca_stat_dict["Processing Notes"].append(ProcessNotes_value)
     temp_eca_stat_dict["Table Group"].append(TableGroup_value)
     temp_eca_stat_dict["Name Identifier"].append(NameId_value)
     temp_eca_stat_dict["Name Count"].append(NameCnt_value)
     temp_eca_stat_dict["Address Identifier"].append(AddressId_value)
     temp_eca_stat_dict["Address Count"].append(AddressCnt_value)
     temp_eca_stat_dict["DOB Identifier"].append(DOBId_value)
     temp_eca_stat_dict["DOB Count"].append(DOBCnt_value)
     temp_eca_stat_dict["SSN Identifier"].append(SSNId_value)
     temp_eca_stat_dict["SSN Count"].append(SSNCnt_value)
     temp_eca_stat_dict["TIN Identifier"].append(TINId_value)
     temp_eca_stat_dict["TIN Count"].append(TINCnt_value)
     temp_eca_stat_dict["Phone Number Identifier"].append(PhoneId_value)
     temp_eca_stat_dict["Phone Count"].append(PhoneCnt_value)
     temp_eca_stat_dict["Driver's License Identifier"].append(DLId_value)
     temp_eca_stat_dict["Driver's License Count"].append(DLCnt_value)
     return temp_eca_stat_dict



def eca_delimited_file_func(file_path,datapath_out_str,NbProcesses_int):
     temp_eca_stat_dict = {}
     for k in eca_stat_dict:
          temp_eca_stat_dict[k] = []
     curfilename_str = str(file_path[file_path.rfind('\\')+1:file_path.rfind(".",file_path.rfind('\\')+1)])
     filename_value = str(curfilename_str)
     fileext_value = str(file_path[file_path.rfind('.')+1:])
     ShtNme_value = np.nan
     keyclm_value = np.nan
     firstrowclms_value = np.nan
     tableclm_value = np.nan
     tablemapclm_value = np.nan
     tablerowcnt_value = np.nan
     clmno_value = np.nan
     totalrowcnt_value = np.nan
     ProcessNotes_value = np.nan
     TableGroup_value = np.nan
     NameId_value = np.nan
     NameCnt_value = np.nan
     DOBId_value = np.nan
     DOBCnt_value = np.nan
     AddressId_value = np.nan
     AddressCnt_value = np.nan
     SSNId_value = np.nan
     SSNCnt_value = np.nan
     TINId_value = np.nan
     TINCnt_value = np.nan
     PhoneId_value = np.nan
     PhoneCnt_value = np.nan
     DLId_value = np.nan
     DLCnt_value = np.nan

     
     delim = ''
     if file_path.lower().endswith(".csv"): delim = ','
     elif file_path.lower().endswith(".tsv"): delim = '\x09'
     try:
          with open(file_path, 'r',encoding='utf-8') as f2:
               line_cnt_int = 0
               for line in f2:
                    if (not file_path.lower().endswith(".csv")) and (not file_path.lower().endswith(".tsv")):
                         delim = csv.Sniffer().sniff(line).delimiter
                    clms = line.strip('\n').split(delim)
                    clmno_value = len(clms)
                    blank_col_cnt_int = 0
                    for i in clms:
                         if i != i or i == '': blank_col_cnt_int +=1

                    if (blank_col_cnt_int / clmno_value) < .5: break
                    line_cnt_int +=1
               try:
                    df = pd.read_csv(file_path,delimiter=delim,dtype=str,skiprows=line_cnt_int,keep_default_na=False, skipinitialspace=True, index_col=False)
                    return eca_findtable_func(filename_value,fileext_value,df,np.nan,datapath_out_str,NbProcesses_int)
               except:
                    print("Could not process as pandas")
                    return eca_text_func(file_path,datapath_out_str,NbProcesses_int)
     except:
          return eca_text_func(file_path,datapath_out_str,NbProcesses_int)


def eca_findtable_func(filename_value,fileext_value,sheet,name,datapath_out_str,NbProcesses_int):
     # Resetting Stat Dict Items
     temp_eca_stat_dict = {}
     for k in eca_stat_dict:
          temp_eca_stat_dict[k] = []
     ShtNme_value = name
     keyclm_value = np.nan
     firstrowclms_value = np.nan
     tableclm_value = np.nan
     tablemapclm_value = np.nan
     tablerowcnt_value = np.nan
     clmno_value = np.nan
     totalrowcnt_value = len(sheet.values)
     ProcessNotes_value = np.nan
     TableGroup_value = np.nan
     NameId_value = np.nan
     NameCnt_value = np.nan
     DOBId_value = np.nan
     DOBCnt_value = np.nan
     AddressId_value = np.nan
     AddressCnt_value = np.nan
     SSNId_value = np.nan
     SSNCnt_value = np.nan
     TINId_value = np.nan
     TINCnt_value = np.nan
     PhoneId_value = np.nan
     PhoneCnt_value = np.nan
     DLId_value = np.nan
     DLCnt_value = np.nan
     #########

     colcnt = 0
     allclms = []
     uncnt =0 
     #print(sheet)
     f = False
     not_a_table_bool = False
     if len(sheet.columns) > 0:
          for i in sheet:
               if str(i).replace('\xa0',' ') in ED.keyclms:  
                    if f == False:
                         keyclm_value = str(i)
                         f = True
                    else:
                         keyclm_value = keyclm_value + ";" + str(i)
               if "Unnamed" in str(i): 
                    uncnt += 1
                    allclms.append("[Blank Column Header in Original]")
               else:
                    allclms.append(i)
               colcnt +=1
          #Check for df with only 2 columsn
          firstrowclms_value = str(allclms)
          lookforheader = False
          if uncnt > 0:
               if uncnt/colcnt > .49: 
                    lookforheader = True
          tempkeyclms_str = ""
          mapclm_list = []
          tableclms_list = []
          if lookforheader == True:
               droprow_list = []
               droprow_int = -1
               for i in sheet.values:
                    uncnt = 0
                    tempkeyclms_str = ""
                    tableclms_list = []
                    mapclm_list = []
                    droprow_int += 1
                    droprow_list.append(droprow_int)
                    for j in i:
                         if str(j).replace('\xa0',' ') in ED.keyclms: 
                                   if tempkeyclms_str == "":
                                        tempkeyclms_str = str(j)
                                        f = True
                                   else:
                                        tempkeyclms_str = tempkeyclms_str + ";" + str(j)
                         if j == '' or j != j: 
                              uncnt += 1
                              tableclms_list.append("[Blank Column Header in Original]")
                         else:
                              tableclms_list.append(j)
                         mapclm_list.append(map_keycol_func(j))
                    if uncnt/colcnt < .50: 
                         tablerowcnt_value = len(sheet.values)-droprow_int+1
                         if tempkeyclms_str != "": 
                              keyclm_value = tempkeyclms_str
                         ProcessNotes_value = "Skipped rows: " + str(droprow_int+1)
                         sheet = sheet.drop(index=droprow_list)
                         sheet.columns = tableclms_list
                         break
                    if droprow_int > (len(sheet.values)/2): 
                         ProcessNotes_value = "No Table found"
                         tempkeyclms_str = ""
                         tableclms_list = []
                         mapclm_list = []
                         not_a_table_bool = True
                         break
          # continues after header has been established
          if len(tableclms_list) == 0:
               tableclms_list = allclms
               for c in allclms:
                    mapclm_list.append(map_keycol_func(c))
          #writes stacted file
          if not_a_table_bool == False:
               stackedtable_func(sheet,filename_value,name,tableclms_list,mapclm_list,datapath_out_str,NbProcesses_int)
               
          #Renaming duplicate columns so pandas doesn't error out
          if len(set(tableclms_list)) != len(tableclms_list): 
               falcon = []
               cnt = 1
               for itm in tableclms_list:
                    if not itm in falcon: 
                         falcon.append(itm)
                    else:
                         falcon.append(str(itm) + "_RADUPE" + str(cnt))
                         cnt += 1
               tableclms_list = falcon

          tableclm_value = str(tableclms_list)
          tablemapclm_value = str(mapclm_list)
          if tempkeyclms_str != "": keyclm_value = tempkeyclms_str
          if 'RADatabaseCtrolNo' in sheet.columns:
               sheet.columns = ['RADatabaseCtrolNo', 'RADatabaseCtrolNo_Sht_Row']+ tableclms_list
          else:
               sheet.columns = tableclms_list
          # Get counts of specific items
          ssnfound_bool = False
          for col in tableclms_list:
               headerfound_bool = False
               if ssnfound_bool == False:
                    if re.search(ED.ssn_header_regx_str,str(col)) and SSNId_value != SSNId_value:
                         sheet[col] = sheet[col].astype(str)
                         SSNId_value = str(col)
                         SSNCnt_value = sheet[col].str.count(ED.reg_ssn_str).sum()
                         headerfound_bool = True
                         ssnfound_bool = True
               if headerfound_bool == False:
                    if re.search(ED.dob_header_regx_str,str(col)) and DOBCnt_value != DOBCnt_value:
                              sheet[col] = sheet[col].astype(str)
                              DOBId_value = str(col)
                              DOBCnt_value = sheet[col].str.count(ED.reg_dates_str).sum()
                              headerfound_bool = True
                    elif re.search(ED.tinnumber_header_regx_str,str(col)) and TINId_value != TINId_value:
                         sheet[col] = sheet[col].astype(str)
                         TINId_value = str(col)
                         TINCnt_value = sheet[col].str.count(ED.TINNumber_str).sum()
                         headerfound_bool = True
                    elif ((re.search(ED.Firstname_header_regx_str,str(col))) or (re.search(ED.middlename_header_regx_str,str(col))) or (re.search(ED.lastname_header_regx_str,str(col))) or (re.search(ED.Fullname_header_regx_str,str(col)))) and NameId_value != NameId_value:
                         sheet[col] = sheet[col].astype(str)
                         NameId_value = str(col)
                         NameCnt_value = sheet[col].str.count(r'^[a-zA-Z]').sum()
                         headerfound_bool = True
                    elif ((re.search(ED.address_header_regx_str,str(col))) or (re.search(ED.address2_header_regx_str,str(col))) or (re.search(ED.addcity_header_regx_str,str(col))) or (re.search(ED.addstate_header_regx_str,str(col))) or (re.search(ED.addzip_header_regx_str,str(col)))) and AddressId_value != AddressId_value:
                         sheet[col] = sheet[col].astype(str)
                         AddressId_value = str(col)
                         AddressCnt_value = sheet[col].str.count(r'^\w').sum()

          firstrowclms_value = str(allclms)
          clmno_value = str(colcnt)
          if lookforheader == False: tablerowcnt_value = totalrowcnt_value
     else:
          ProcessNotes_value = "No Information Captured"


     #Writing to dict after each sheet
     temp_eca_stat_dict["FileName"].append(filename_value)
     temp_eca_stat_dict["Extension"].append(fileext_value)
     temp_eca_stat_dict["Sheet Name"].append(ShtNme_value)
     temp_eca_stat_dict["Key Columns"].append(keyclm_value)
     temp_eca_stat_dict["First Row Columns"].append(firstrowclms_value)
     temp_eca_stat_dict["Table Columns"].append(tableclm_value)
     temp_eca_stat_dict["Table Columns Mapping"].append(tablemapclm_value)
     temp_eca_stat_dict["Table Number of Rows"].append(tablerowcnt_value)
     temp_eca_stat_dict["Total Number of Columns"].append(clmno_value)
     temp_eca_stat_dict["Total Number of Rows"].append(totalrowcnt_value)
     temp_eca_stat_dict["Processing Notes"].append(ProcessNotes_value)
     temp_eca_stat_dict["Table Group"].append(TableGroup_value)
     temp_eca_stat_dict["Name Identifier"].append(NameId_value)
     temp_eca_stat_dict["Name Count"].append(NameCnt_value)
     temp_eca_stat_dict["Address Identifier"].append(AddressId_value)
     temp_eca_stat_dict["Address Count"].append(AddressCnt_value)
     temp_eca_stat_dict["DOB Identifier"].append(DOBId_value)
     temp_eca_stat_dict["DOB Count"].append(DOBCnt_value)
     temp_eca_stat_dict["SSN Identifier"].append(SSNId_value)
     temp_eca_stat_dict["SSN Count"].append(SSNCnt_value)
     temp_eca_stat_dict["TIN Identifier"].append(TINId_value)
     temp_eca_stat_dict["TIN Count"].append(TINCnt_value)
     temp_eca_stat_dict["Phone Number Identifier"].append(PhoneId_value)
     temp_eca_stat_dict["Phone Count"].append(PhoneCnt_value)
     temp_eca_stat_dict["Driver's License Identifier"].append(DLId_value)
     temp_eca_stat_dict["Driver's License Count"].append(DLCnt_value)
     return temp_eca_stat_dict


def map_keycol_func(col):
     if col != col or str(col) == '': return "[Blank Column Header in Original]"
     elif str(col) in ED.ssn:return "SSN"
     elif str(col) in ED.tinnumber:return "Tax ID"
     elif str(col) in ED.Firstname:return "First Name"
     elif str(col) in ED.middlename:return "Middle Name"
     elif str(col) in ED.lastname:return "Last Name"
     elif str(col) in ED.Fullname:return "Full Name"
     elif str(col) in ED.suffix:return "Suffix"
     elif str(col) in ED.dob:return "DOB"
     elif str(col) in ED.address:return "Address"
     elif str(col) in ED.address2:return "Address2"
     elif str(col) in ED.addcity:return "City"
     elif str(col) in ED.addstate:return "State"
     elif str(col) in ED.addzip:return "Zip"
     elif str(col) in ED.dod:return "Date of Death"
     elif str(col) in ED.Businessname:return "Business Name"
     elif str(col) in ED.Phone:return "Home Phone"
     else: return col

def trim_string_func(str):
     if type(str).__name__ != 'str':
          return str
     else:
          return str.strip()


def stackedtable_func(df,curfilename_str,shtcount,newcols,mapclm_list,outfile_path,NbProcesses_int):
     df.insert(0, "RADatabaseCtrolNo_Sht_Row",str(curfilename_str) + "_" + str(shtcount) + "_")
     df.insert(0, "RADatabaseCtrolNo",str(curfilename_str))
     df["DeleteIndexer"] = df.index
     df["DeleteIndexer"] = df["DeleteIndexer"].apply(lambda x: '{0:0>6}'.format(str(x)))
     df["RADatabaseCtrolNo_Sht_Row"] = df["RADatabaseCtrolNo_Sht_Row"] + df["DeleteIndexer"].astype(str)
     del df["DeleteIndexer"]
     groupno_dict = {}
     with open(outfile_path + "Group_Col_Table_"+ NbProcesses_int +".dat",'r') as file:
          r = csv.reader(file, delimiter='\x14', quotechar='\xfe')
          lncnt_int = 1
          for line in r:
               if lncnt_int == 1:lncnt_int +=1;continue
               lncnt_int +=1
               groupno_dict[int(line[0])] = line[1]

          
     clncnt = 0
     #print(df)
     if len(df.columns) > 1:
          for g in df.columns:
               df[g] = df[g].apply(lambda x: trim_string_func(x))
          found = False
          if str(mapclm_list) in groupno_dict.values():
               for k, f in groupno_dict.items():
                    if str(mapclm_list) == f:
                         with open(outfile_path + "Stacked_Table_Group" + "_" + str(k) + ".csv", 'a+', newline ='\n',encoding='utf-8') as file:
                                   df.to_csv(file,index=False,header=False,encoding='utf-8-sig',quoting=csv.QUOTE_ALL)
                         found = True
                         print ("found stacked file in group " + str(k))
                         #write columns to file
                         with open(outfile_path + "ConCat_Columns.csv", 'a+', newline ='\n',encoding='utf-8') as file:
                              writecols = []
                              for c in newcols:
                                        writecols.append(str(c).replace('\n'," ").strip())
                              csv_writer = csv.writer(file)
                              csv_writer.writerow([str(curfilename_str) + "_group:" + str(k)] + writecols)
                         break
          else:
               lastgourpno_int = int(NbProcesses_int) * 10000
               for key in groupno_dict.keys():
                    lastgourpno_int = key + 1
               with open(outfile_path + "Group_Col_Table_"+ NbProcesses_int +".dat",'a+') as file:
                    file.write("\xfe"+str(lastgourpno_int) + "\xfe\x14\xfe"+ str(mapclm_list) + "\xfe\n")
               df.to_csv(outfile_path + "Stacked_Table_Group" + "_" + str(lastgourpno_int) + ".csv",header=True,index=False,quoting=csv.QUOTE_ALL,encoding='utf-8')
               with open(outfile_path + "ConCat_Columns.csv", 'a+', newline ='\n',encoding='utf-8') as file:
                    writecols = []
                    for c in newcols:
                         writecols.append(str(c).replace('\n'," ").strip())
                    csv_writer = csv.writer(file)
                    csv_writer.writerow([str(curfilename_str) + "_group:" + str(lastgourpno_int)] + writecols)
