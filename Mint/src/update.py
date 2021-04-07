#!/usr/bin/env python
# coding: utf-8

# In[1]:


try:
    import pandas as pd
    import numpy as np
    import os
    from datetime import datetime as dt
    import re
    
    import sys
    sys.path.insert(1, '../src/')
    from mint import  *

    import warnings
    warnings.filterwarnings("ignore")
    
except ImportError:
    input('Unable to import packages.  Press enter to close:')


file_loc = '../data/raw/Transactional Data/'
file_loc1 = '../data/raw/Budget Template.xlsx'


# In[2]:


fin = combine_csv_files(file_loc)
fin['Date'] = pd.to_datetime(fin['Date'])
fin.columns = fin.columns.str.replace(r"[ ]","_")
fin['Month'] = fin['Date']




fin = fin.groupby(['Date', 'Month', 'Category', 'Description', 
                   'Account_Name','Transaction_Type'], 
                  as_index=False).agg({'Amount':'sum', 
                                        'Original_Description':"count"})

fin.rename({'Original_Description':'Count'}, axis=1, inplace=True)
fin.rename({'Category':'Sub_Category'}, axis=1, inplace=True)





fin = fin[(fin['Date'] > '2017-06-30')]




fin['Sub_Category'].replace('Credit Card Payment', 'Transfer', inplace=True)
fin = fin[~fin['Sub_Category'].str.contains('Wedding Reimbursement', na=False)]
fin = fin[~fin['Sub_Category'].str.contains('Wedding expenses', na=False)]
fin1 = fin




fin1 = fin1[~fin1['Sub_Category'].str.contains('Transfer', na=False)]
fin1 = fin1.loc[fin1['Sub_Category'].str[:2] != "EM"]


# In[3]:


exp = pd.read_excel(file_loc1, sheet_name='Exp Ref')
exp.rename({'Sub-Category':'Sub_Category'}, axis=1, inplace=True)
fin1 = fin1.set_index('Sub_Category')
exp.set_index('Sub_Category', inplace=True)
exp.columns = exp.columns.str.replace(r"[ ]","_")




fin1 = fin1.join(exp, how="left").fillna("Research")
fin1.reset_index(inplace=True)


# In[4]:


fin2 = fin1.loc[fin1['Expense_Type_Factor']=='Research']
print(fin2[['Date', 'Sub_Category', 'Description', 'Category', 'Amount']].head(25))


input("ERROR UPDATE: IF LINE ITEM APPEARS, GO BACK TO MINT.COM AND MAKE CORRECTIONS \n"
      "Otherwise, Press Enter to Continue:")


# In[5]:


fin1.loc[fin1['Budget']=='Est', 'Forecast_Amount'] = fin1['Amount']
fin1.loc[fin1['Budget']!='Est', 'Forecast_Amount'] = 0

fin1['Forecast_Amount'] = pd.to_numeric(fin1['Forecast_Amount'].astype(str).replace('[^0-9]]', "").copy())

fin1['Expense_Type_Factor'] = pd.to_numeric(fin1['Expense_Type_Factor'].astype(str).replace('[^0-9]]', "").copy())


# In[6]:


fin1['Budget_Amount'] = fin1['Expense_Type_Factor']*fin1['Forecast_Amount']


fin1.loc[fin1['Transaction_Type']=='credit', 'Amount'] = fin1['Amount']
fin1.loc[fin1['Transaction_Type']=='debit', 'Amount'] = fin1['Amount']*-1


# In[7]:


fin1.rename({'Sub_Category':'Sub-Category'}, axis=1, inplace=True)

fin1.set_index('Date', inplace=True)
fin1.columns = fin1.columns.str.replace(r"[_]"," ")




fin1 = fin1[['Month', 'Sub-Category', 'Description', 'Account Name',
       'Transaction Type', 'Count', 'Category Number',
       'Sub-Category Number', 'Category', 'Budget', 'Expense Type',
       'Expense Type Factor', 'Forecast Amount', 'Budget Amount', 'Amount']]


# In[8]:


em = fin.loc[fin['Sub_Category'].str[:2] == "EM"]
em.set_index('Date', inplace=True)
em.columns = em.columns.str.replace(r"[_]"," ")
em.rename({'Sub Category':'Sub-Category'}, axis=1, inplace=True)
em = em[['Month', 'Sub-Category', 'Description', 'Account Name',
       'Transaction Type', 'Count', 'Amount']]


# In[9]:


trfr = fin.loc[fin['Sub_Category'] == "Transfer"]

trfr['Amount'] = trfr.loc[trfr['Amount']<0, ' Amount'] = trfr['Amount']*-1


# In[10]:


trfr.loc[trfr['Transaction_Type']!='debit', 'Transfer_Type'] = str('In')
trfr.loc[trfr['Transfer_Type']!='In', 'Transfer_Type'] = str('Out')


# In[11]:


trfr.set_index('Date', inplace=True)
trfr.columns = trfr.columns.str.replace(r"[_]"," ")


# In[12]:


trfr.rename({'Sub Category':'Sub-Category'}, axis=1, inplace=True)


# In[13]:


df = trfr[['Month', 'Sub-Category', 'Description', 'Account Name',
       'Transaction Type', 'Count', 'Amount', 'Transfer Type']]


# In[14]:


amt = fin1
amt.reset_index(inplace=True)
amt = amt.groupby(['Date'], 
                  as_index=False).agg({'Amount':'sum'})
# amt.Date.value_counts()


# In[15]:


amt['Cash'] = amt.Amount.shift(1)

beg_balance = 9255.58
amt.Cash.fillna(beg_balance, inplace=True)

amt['Cash'] = amt['Cash'].cumsum(axis=0)


# In[16]:


# L = amt['Cash'].tolist()

# def add_one_by_one(L):
#     new_L = []
#     for elt in L:
#         if len(new_L)>0:
#             new_L.append(new_L[-1]+elt)
#         else:
#             new_L.append(elt)
#     return new_L

# new_L = add_one_by_one(L)

# amt['Cash'] = new_L
# amt.head(3)


# In[17]:


amt.set_index('Date',inplace=True)
fin1.set_index('Date', inplace=True)
fin = fin1.join(amt['Cash']).fillna('Research')


# In[18]:


fin.to_csv('../data/final/financial_transactions.csv')
df.to_csv('../data/final/transfer_report.csv')
em.to_csv('../data/final/em_report.csv')


# In[19]:


input("Press Enter to Close:")


# In[ ]:




