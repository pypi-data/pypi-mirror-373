import os
from steam_sdk.drivers.DriverLEDET import DriverLEDET

if __name__ == "__main__":
    dLEDET = DriverLEDET(
        path_exe         ='\\\\eosproject-smb\eos\project\s\steam\sw\snapshots\ledet\LEDET.exe',
        path_folder_LEDET='F:\Dropbox\Working files\MainFolderSimulations\LEDET_Analytical',
        verbose=True)
    nameMagnet = 'MQXF_P1P4'
    simsToRun  = '0'
    # dLEDET.run_LEDET(nameMagnet, simsToRun)

    if os.path.isdir('\\\\eosproject-smb'):
        print('hger1')

    if os.path.isfile('\\\\eosproject-smb\eos\project\s\steam\sw\snapshots\ledet\LEDET.exe'):
        print('hger2')

    if os.path.isdir('\\\\eosproject-smb\eos'):
        print('hger3')