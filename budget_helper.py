import pygsheets
#from googleapiclient import discovery
import os
import datetime
import calendar
import logging
import pandas as pd
#from schedule import every, repeat, run_pending
import time
import pdb

#* Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')
file_handler = logging.FileHandler('budget.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#* Initialize static variables:
service_file = os.path.join(os.getcwd(), 'gsuite_key.json')
current_month_year = str(datetime.date.today().month) + '-' + str(datetime.date.today().year)
if datetime.date.today().month == 12:
     next_month_year = '1-' + str(datetime.date.today().year)
else:
    next_month_year = str(datetime.date.today().month + 1) + '-' + str(datetime.date.today().year)
current_day = str(datetime.date.today().day)
worksheet = '1SQt8c8TJ33mCht1ITAlixAhP6RSJO5u7RyLeG575Tjg'
days_in_month = calendar.monthrange(pd.to_datetime('now').year,
                                    pd.to_datetime('now').month)[1]


#* Create connection to google sheet
logger.info('Connecting to google sheet')
try: 
    gc = pygsheets.authorize(service_account_file=service_file)
    budget_sheet = gc.open_by_key(worksheet)
    logger.info('Successfully connected to google sheet')
except:
    logger.debug('issue connecting to google sheet, check the service file path')


#* Grab current expenses 
def retrieve_expenses(tab_name):
    expenses_tab = budget_sheet.worksheet_by_title(tab_name)
    expense_df = expenses_tab.get_as_df(start = 'A1', end = '*')
    pd.to_datetime(expense_df['Date']).dt.day
    expense_df = expense_df.loc[expense_df['Ready'] == 'TRUE']
    col_order = ['Date','Amount', 'Category','Description']
    expense_df = expense_df[col_order]
    expense_df.reset_index()
    return expense_df

#* Record expenses to the correct month tab 
def record_expenses(expense_df, tab_name):
    if expense_df.shape[0] > 0:
        # Create updated expense data
        log_start = 'K15'
        log_end = 'N115'
        curr_tab = budget_sheet.worksheet_by_title(tab_name)
        curr_expenses = curr_tab.get_as_df(start = log_start, end = log_end)
        final_df = pd.concat([curr_expenses, expense_df]).reset_index()
        logger.info(f'Recording {final_df.shape[0] - curr_expenses.shape[0]} expenses in {tab_name} tab')

        # Update range 
        curr_tab.set_dataframe(final_df, start = 'J15')

    else:
        logger.info('No new expenses, nothing to transfer')

#* Clear out expense tab after they've been recorded. 
def clear_interface(tab_name):
    expenses = budget_sheet.worksheet_by_title(tab_name)
    not_ready = expenses.get_as_df(start = 'A1', end = '*')
    not_ready = not_ready.loc[not_ready['Ready'] != 'TRUE']
    not_ready = not_ready[['Date','Amount','Category','Description']]
    expenses.clear(start = 'A2')
    expenses.set_dataframe(not_ready, start = 'A1')
    logger.info('Expenses Cleared')

#* Package run in one function
def run_expense_update():
    interface = 'Expense Inputs'
    expenses = retrieve_expenses(interface)
    record_expenses(expenses, current_month_year)
    clear_interface(interface)

def create_new_month():
    source_sheet = budget_sheet.id
    curr_tab = budget_sheet.worksheet_by_title(current_month_year).id
    budget_sheet.add_worksheet(title = next_month_year, rows = 150, src_tuple=(source_sheet, curr_tab))
    reload = gc.open_by_key(worksheet)
    reload.worksheet_by_title(next_month_year).clear(start = 'J15', end = 'P150')

    
run_expense_update()
logger.info('All finished! Expenses updated!')

if current_day == days_in_month - 1:
    create_new_month()
    logger.info('Created New Month Tab')


# @repeat(every(30).minutes)
# def main():
#     run_expense_update()
#     logger.info('All finished! Expenses updated!')
    
#     if current_day == days_in_month - 1:
#         create_new_month()
#         logger.info('Created New Month Tab')

# if __name__ == "__main__":
#     while True:
#         run_pending()
#         time.sleep(1)
