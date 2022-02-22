import pandas as pd
import os
import pygsheets
import subprocess
import argparse


#* Set up universal variables
banks = {
        'amex' : 'activity',
        'chase' : 'Chase',
        'boa' : 'stmt'
}
keep_cols = ['Amount','Category','Description']

def get_recent_file(bank):
    file_list = list()
    file_folder = '/Users/blakelattier/Downloads'
    for path, dirname, fname in os.walk(file_folder):
        for n in fname:
            if n.startswith(banks[bank]) and n.lower().endswith('.csv'):
                file_list.append([n, os.path.getmtime(os.path.join(file_folder,n))])
    file_df = pd.DataFrame(data = file_list, columns = ['Name','Date'])
    file_df['Date'] = pd.to_datetime(file_df['Date'], unit='s')
    file_df = file_df.sort_values('Date', ascending=False)
    file_name = file_df.iloc[0,0]
    return file_name

#* Set up arguments to pass the terminial run
parser = argparse.ArgumentParser()
parser.add_argument('--amex', help = 'Run if a new file is available for Amex | input Run')
parser.add_argument('--chase', help = 'Run if a new file is available for Chase | input Run')
parser.add_argument('--boa', help = 'Run if a new file is available for BOA | input Run')
args = parser.parse_args()
run_amex = args.amex
run_chase = args.chase
run_boa = args.boa



#* Run scenarios for files downloaded
final_transactions = pd.DataFrame(data=None, columns=keep_cols)
if run_amex == 'Run':
    new_download = get_recent_file('amex')
    transactions = pd.read_csv(os.path.join('/Users/blakelattier/Downloads',new_download))
    transactions['Category'] = 'Null'
    transactions['Description'] = transactions['Description'] + '-AMEX'
    amex_transactions = transactions[keep_cols]
    final_transactions = pd.concat([final_transactions,amex_transactions], ignore_index=True)


if run_chase == 'Run':
    new_download = get_recent_file('chase')
    transactions = pd.read_csv(os.path.join('/Users/blakelattier/Downloads',new_download))
    transactions['Description'] = transactions['Description'] + '-CHASE'
    transactions['Amount'] = transactions['Amount'] * -1
    chase_transactions = transactions[keep_cols]
    final_transactions = pd.concat([final_transactions,chase_transactions], ignore_index=True)

if run_boa == 'Run':
    new_download = get_recent_file('boa')
    transactions = pd.read_csv(os.path.join('/Users/blakelattier/Downloads',new_download))
    transactions['Category'] = 'Null'
    transactions['Description'] = transactions['Description'] + '-BOA'
    boa_transactions = transactions[keep_cols]
    #TODO finish this processing




# remove excess spaces from description
for index, row in final_transactions.iterrows():
    final_transactions.loc[index,'Description'] = " ".join(row['Description'].split()) # I think this preserves the dataframe integrity and actually changes the original dataframe

service_file = os.path.join(os.getcwd(), 'gsuite_key.json')
gc = pygsheets.authorize(service_account_file=service_file) # authorize worksheet connection
worksheet = '1SQt8c8TJ33mCht1ITAlixAhP6RSJO5u7RyLeG575Tjg'
budget_sheet = gc.open_by_key(worksheet) # connect to the worksheet
inputs_sheet = budget_sheet.worksheet_by_title('Expense Inputs')

inputs_sheet.set_dataframe(final_transactions, start = 'A1')



# #* Run the helper file to correctly log the transactions
#subprocess.run('python budget_helper.py', shell = True)
