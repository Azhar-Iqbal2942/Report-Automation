from datetime import datetime
import pandas as pd
import numpy as np
import openpyxl
import schedule
import time

import config


DESIGN_PERCENTAGE_PRESSURE_LEFT_UNDERSLUICE = {
    'EP-A': [28.47], 'EP-B': [19.50], 'EP-C': [18.59], 'EP-D': [31.78], 'EP-E': [5.62]
}

DESIGN_PERCENTAGE_PRESSURE_MAIN_WEIR = {
    'EP-A': [70.63], 'EP-B': [56.27], 'EP-C': [43.07], 'EP-D': [31.78], 'EP-E': [5.62]
}
DESIGN_PERCENTAGE_PRESSURE_OLD_RIGHT_UNDERSLUICE = {
    'EP-A': [36.59], 'EP-B': [33.34], 'EP-C': [24.64], 'EP-D': [20.61], 'EP-E': [3.19]
}
DESIGN_PERCENTAGE_PRESSURE_ADDITIONAL_BAYS = {
    'EP-A': [43.59], 'EP-B': [41.60], 'EP-C': [35.34], 'EP-D': [24.04], 'EP-E': [7.41]
}
DESIGN_PERCENTAGE_PRESSURE_NEW_RIGHT_UNDERSLUICE = {
    'EP-A': [43.59], 'EP-B': [41.60], 'EP-C': [35.34], 'EP-D': [24.04], 'EP-E': [6.73]
}

left_undersluice_columns = ['EP(1)', 'EP(2)', 'EP(3)']
main_weir_columns = ['EP(4)', 'EP(5)', 'EP(6)', 'EP(7)', 'EP(8)', 'EP(11)', 'EP(12)', 'EP(13)', 'EP(14)', 'EP(15)', 'EP(16)', 'EP(17)',
                     'EP(18)', 'EP(19)', 'EP(20)', 'EP(21)', 'EP(22)', 'EP(23)', 'EP(9)', 'EP(9)', 'EP(26)', 'EP(27)', 'EP(28)', 'EP(29)', 'EP(30)']
old_right_undersluice_columns = [
    'EP(31)', 'EP(32)', 'EP(33)', 'EP(34)', 'EP(35)']
additional_bays_columns = ['EP(36)', 'EP(37)', 'EP(38)', 'EP(39)', 'EP(40)']
new_right_undersluice_columns = [
    'EP(41)', 'EP(42)', 'EP(43)', 'EP(44)', 'EP(45)']
SAFE_HGL_LEVEL = []


path_excel = config.excel_path
path_loc = config.dat_path
conn = config.conn


def generate_report():
    data = str(datetime.now())
    u_date = data[:19]
    #
    left_undersluice(u_date)
    main_weir(u_date)
    old_right_undersluice(u_date)
    additional_bays(u_date)
    left_undersluice(u_date)
    SAFE_HGL_LEVEL.append(u_date)
    append_safe_hgl_level()

    # context = {
    #     'form': DateForm(), 'date': date, 'time': time,
    #     'RL_left': left_rp, 'DPP_left': left_dpp, 'WL_left': left_wl,
    #     'RL_main': main_rp, 'DPP_main': main_dpp, 'WL_main': main_wl, 'bay_no': [1, 9, 18, 28, 37],
    #     'RL_old': old_rp, 'DPP_old': old_dpp, 'WL_old': old_wl,
    #     'RL_additional': additional_rp, 'DPP_additional': additional_dpp, 'WL_additional': additional_wl,
    #     'RL_nr': new_right_rp, 'DPP_nr': new_right_dpp, 'WL_nr': new_right_wl
    # }

    # return render(request, 'report/report.html', context)


###############################################################################################
def left_undersluice(u_date):
    wl = left_undersluice_wl_builder(u_date)
    dpp = left_undersluice_dpp_builder()
    ep_list = get_ep_list(u_date, left_undersluice_columns)
    report_list = left_undersluice_report_builder(wl, dpp, ep_list)
    return report_list.values, dpp, wl


def main_weir(u_date):
    wl = main_weir_wl_builder(u_date)
    dpp = main_weir_dpp_builder()
    ep_list = get_ep_list(u_date, main_weir_columns)
    report_list = main_weir_report_builder(wl, dpp, ep_list)
    chunk_list = np.split(report_list.values, 5)
    return chunk_list, dpp, wl


def old_right_undersluice(u_date):
    wl = old_right_undersluice_wl_builder(u_date)
    dpp = old_right_undersluice_dpp_builder()
    ep_list = get_ep_list(u_date, old_right_undersluice_columns)
    report_list = old_right_undersluice_report_builder(wl, dpp, ep_list)
    return report_list.values, dpp, wl


def new_right_undersluice(u_date):
    wl = new_right_undersluice_wl_builder(u_date)
    dpp = new_right_undersluice_dpp_builder()
    ep_list = get_ep_list(u_date, new_right_undersluice_columns)
    report_list = new_right_undersluice_report_builder(wl, dpp, ep_list)
    return report_list.values, dpp, wl


def additional_bays(u_date):
    wl = additional_bays_wl_builder(u_date)
    dpp = additional_bays_dpp_builder()
    ep_list = get_ep_list(u_date, additional_bays_columns)
    report_list = additional_bays_report_builder(wl, dpp, ep_list)
    return report_list.values, dpp, wl


###################################################################################################


def left_undersluice_wl_builder(u_input):
    df = pd.read_sql_query(f'SELECT * FROM SC.dbo.WLS', conn)
    df['dt'] = df['dt'].values.astype('<M8[m]')
    filt = (df['dt'] == str(u_input))
    df = df[filt][['W5', 'W4']]
    df['Average_up'] = round((df['W5']), 2)
    df['Average_down'] = round((df['W4']), 2)
    df['Head Across'] = round((df['Average_up'] - df['Average_down']), 2)
    return df.values[0]


def left_undersluice_dpp_builder():
    pd.DataFrame(DESIGN_PERCENTAGE_PRESSURE_LEFT_UNDERSLUICE).values[0]


def left_undersluice_report_builder(wl, dpp, ep_list):
    return ep_table(wl, dpp, ep_list, 3, [2, 4])


def main_weir_wl_builder(u_input):
    df = pd.read_sql_query(f'SELECT * FROM SC.dbo.WLS', conn)
    df['dt'] = df['dt'].values.astype('<M8[m]')
    filt = (df['dt'] == str(u_input))
    df = df[filt][['W5', 'W6', 'W7', 'W8']]
    df['Average_up'] = round((df['W5'] + df['W7'])/2, 2)
    df['Average_down'] = round((df['W6'] + df['W8'])/2, 2)
    df['Head Across'] = round((df['Average_up'] - df['Average_down']), 2)

    return df.values[0]


def main_weir_dpp_builder():
    return pd.DataFrame(DESIGN_PERCENTAGE_PRESSURE_MAIN_WEIR).values[0]


def main_weir_report_builder(wl, dpp, ep_list):
    return ep_table(wl, dpp, ep_list, 3, [4, 6])


def old_right_undersluice_wl_builder(u_input):
    df = pd.read_sql_query(f'SELECT * FROM SC.dbo.WLS', conn)
    df['dt'] = df['dt'].values.astype('<M8[m]')
    filt = (df['dt'] == str(u_input))
    df = df[filt][['W9', 'W10']]
    df['Average_up'] = round((df['W9']), 2)
    df['Average_down'] = round((df['W10']), 2)
    df['Head Across'] = round((df['Average_up'] - df['Average_down']), 2)
    return df.values[0]


def old_right_undersluice_dpp_builder():
    return pd.DataFrame(DESIGN_PERCENTAGE_PRESSURE_OLD_RIGHT_UNDERSLUICE).values[0]


def old_right_undersluice_report_builder(wl, dpp, ep_list):
    return ep_table(wl, dpp, ep_list, 3, [2, 4])


def new_right_undersluice_wl_builder(u_input):
    df = pd.read_sql_query(f'SELECT * FROM SC.dbo.WLS', conn)
    df['dt'] = df['dt'].values.astype('<M8[m]')
    filt = (df['dt'] == str(u_input))

    df = df[filt][['W13', 'W14']]
    df['Average_up'] = round((df['W13']), 2)
    df['Average_down'] = round((df['W14']), 2)
    df['Head Across'] = round((df['Average_up'] - df['Average_down']), 2)
    return df.values[0]


def new_right_undersluice_dpp_builder():
    return pd.DataFrame(DESIGN_PERCENTAGE_PRESSURE_NEW_RIGHT_UNDERSLUICE).values[0]


def new_right_undersluice_report_builder(wl, dpp, ep_list):
    return ep_table(wl, dpp, ep_list, 3, [2, 4])


def additional_bays_wl_builder(u_input):
    df = pd.read_sql_query(f'SELECT * FROM SC.dbo.WLS', conn)
    df['dt'] = df['dt'].values.astype('<M8[m]')
    filt = (df['dt'] == str(u_input))

    df = df[filt][['W11', 'W13', 'W12', 'W14']]
    df['Average_up'] = round((df['W11'] + df['W13'])/2, 2)
    df['Average_down'] = round((df['W12'] + df['W14'])/2, 2)
    df['Head Across'] = round((df['Average_up'] - df['Average_down']), 2)
    return df.values[0]


def additional_bays_dpp_builder():
    # print(pd.DataFrame(DPP_AB).values[0])
    return pd.DataFrame(DESIGN_PERCENTAGE_PRESSURE_ADDITIONAL_BAYS).values[0]


def additional_bays_report_builder(wl, dpp, ep_list):
    return ep_table(wl, dpp, ep_list, 3, [4, 6])


def get_ep_list(u_input, ep_col_list):
    """ 
    Return Values of passed EP column
    Format : 2020-10-17 10:43:00

    """
    df = pd.read_csv(path_loc, skiprows=1)
    filt = (df['TIMESTAMP'] == str(u_input))
    print(df[filt][ep_col_list].values[0])
    return df[filt][ep_col_list].values[0]


def ep_table(wl, dpp, ep_list, repeat_no, seq_no):
    df_table = pd.DataFrame(
        columns=['Safe_HGL_Level', 'Piezometer_Water_Level'])
    average_up = wl[seq_no[0]]
    head_across = wl[seq_no[1]]
    index = 0
    ep_counter = 0

    for i in range(repeat_no):
        if index >= 5:
            index = 0

        shl = round(average_up - (head_across -
                                  (dpp[index] * head_across/100)), 2)
        SAFE_HGL_LEVEL.append(shl)
        pwl = round(float(ep_list[ep_counter]), 2)
        df_table = df_table.append(
            {'Safe_HGL_Level': shl, 'Piezometer_Water_Level': pwl}, ignore_index=True)

        index += 1
        ep_counter += 1

    return df_table

#############################################################################################


def append_safe_hgl_level():
    wb = openpyxl.load_workbook(path_excel)
    sheet = wb['Sheet1']
    # sheet[2] getting specific row and update value
    sheet.append(SAFE_HGL_LEVEL)


##################################################################################################
# schedule.every(10).seconds.do(generate_report)
schedule.every().hour.do(generate_report)

while True:
    schedule.run_pending()
    time.sleep(1)
