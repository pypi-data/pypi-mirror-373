"""This file is only for yield because the listener log writes only the first packet of each adva
so from here we can all the packets a tag transmitted."""

from os.path import isfile
import re
from wiliot_core import PacketList, Packet
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception as e:
    print(f'could not import tkinter: {e}')


def browse_window():
    root = tk.Tk()
    root.withdraw()
    log_path = filedialog.askopenfilename(title="Select a LOG file", filetypes=[("LOG files", "*.log")])

    if log_path:
        packet_list = lines_to_packet_list(log_path)
        csv_path = log_path[:-4] + '.csv'
        packet_list.to_csv(csv_path)
        print('File saved')
    else:
        print("No file selected")


def lines_to_packet_list(log_path=None):
    packet_list = PacketList()
    seen_advas = set()
    if log_path is None:
        print('no log path was found. Export csv failed')
        return
    try:
        if isfile(log_path):
            f = open(log_path, 'r')
            lines = f.readlines()
            string_value = "'raw': 'process_packet(\""
            for line in lines:
                if string_value in line or 'is_valid_tag_packet:True' in line:
                    if string_value in line:
                        re_match = re.search("process_packet\(\"(\w+)\"", line)
                        if re_match:
                            packet_raw = str(re_match.groups()[0])
                        else:
                            print("Pattern did not match!")
                            continue
                    else:
                        re_match = re.search(",packet:(\w+)", line)
                        packet_raw = str(re_match.groups(1)[0])

                    if 'time_from_start:' in line:
                        re_match = re.search("time_from_start:(\d+.\d+)", line)
                        packet_time = float(re_match.groups(1)[0])
                    else:
                        re_match = re.search(r"'time': (\d+)\.(\d+),", line)
                        if re_match:
                            packet_time = float(re_match.group(1))
                        else:
                            continue
                    current_packet = Packet(raw_packet=packet_raw, time_from_start=packet_time)
                    if current_packet.packet_data['adv_address'] not in seen_advas:
                        packet_list.append(current_packet)
                        seen_advas.add(current_packet.packet_data['adv_address'])
            f.close()
        return packet_list
    except Exception as e:
        print('export packets from log was failed due to: {}'.format(e))
        return None, None


if __name__ == '__main__':
    browse_window()

