import pandas as pd
import time


def get_last_pass_external_id(packet_data_path, df_packet=None):
    df_packet = pd.read_csv(packet_data_path) if df_packet is None else df_packet
    last_location = max(df_packet[df_packet['status_offline'] == 1]['tag_run_location'])
    external_id = df_packet[df_packet['tag_run_location'] == last_location]['external_id'].unique()
    if len(external_id) != 1:
        raise Exception(f'Could not extract last external id since external id is not specified or several external ids'
                        f' on the same location: {external_id}')
    return external_id[0]


def delete_entry_from_specific_external_id(packet_data_path, run_data_path, external_id, new_file_suffix='_edit'):
    df_packet = pd.read_csv(packet_data_path)
    df_run = pd.read_csv(run_data_path)

    i_to_remove = df_packet[df_packet['external_id'] == external_id].index
    if len(i_to_remove) == 0:
        raise Exception('could not find the specifies external id')
    df_packet_edit = df_packet.drop(list(range(min(i_to_remove), len(df_packet))))

    if df_packet_edit.empty:
        df_run['total_run_tested'] = 0
        df_run['total_run_passed_offline'] = 0
        df_run['total_run_responding_tags'] = 0
    else:
        df_run['total_run_tested'] = \
            len(df_packet_edit['tag_run_location'][df_packet_edit['fail_bin_str'] != 'BAD_PRINTING'].unique())
        df_run['total_run_passed_offline'] = \
            len(df_packet_edit[df_packet_edit['status_offline'] == 1]['tag_run_location'].unique())
        df_run['total_run_responding_tags'] = \
            len(df_packet_edit['adv_address'][df_packet_edit['packet_status'] == 'good'].unique())
    cur_comments = df_run['comments'][0] if not pd.isnull(df_run['comments'][0]) else ''
    last_external_id = get_last_pass_external_id(packet_data_path, df_packet)
    df_run['comments'] = cur_comments + f'.del:{external_id[-4:]}-{last_external_id[-4:]}' \
                                        f'@{time.strftime("%d%m%y_%H%M%S")}'
    packet_data_path = packet_data_path.replace('.CSV', '.csv')
    run_data_path = run_data_path.replace('.CSV', '.csv')
    df_packet_edit.to_csv(packet_data_path.replace('.csv', f'{new_file_suffix}.csv'), index=False)
    df_run.to_csv(run_data_path.replace('.csv', f'{new_file_suffix}.csv'), index=False)
    return df_run, df_packet_edit


def update_test_vars(self, new_df, df_packet_edit):
    self.test_data['tag_run_location'] = new_df['total_run_tested'][0]
    self.run_data['total_run_responding_tags'] = new_df['total_run_responding_tags'][0]
    self.run_data['total_run_tested'] = new_df['total_run_tested'][0]
    self.run_data['total_run_passed_offline'] = new_df['total_run_passed_offline'][0]
    self.run_data['comments'] = new_df['comments'][0]
    self.all_tags = df_packet_edit['adv_address'].unique().tolist()
    self.all_selected_tags = df_packet_edit['selected_tag'].unique().tolist()


if __name__ == '__main__':
    FILE_PATH = 'C:/Users/shunit/eclipse-workspace/post_process_testing/offline/duplication1'
    commmon_run_name = '02jx_20221224_203102'
    packet_data_path = f"{FILE_PATH}/{commmon_run_name}@packets_data.csv"
    run_data_path = f"{FILE_PATH}/{commmon_run_name}@run_data.csv"

    last_external_id = get_last_pass_external_id(packet_data_path)
    print(last_external_id)

    external_id_to_delete = last_external_id
    new_df = delete_entry_from_specific_external_id(packet_data_path, run_data_path,
                                                    external_id=external_id_to_delete, new_file_suffix='_edit')
    print(new_df)
    print('done')
