import shutil

if __name__ == "__main__":
    FLAG_OVERWRITE = False

    list_files_to_overwrite =[
        [r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\output\run_parsim_conductor\MBRB_1.xlsx', r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\references\run_parsim_conductor\MBRB_reference_1.xlsx'],
        [r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\output\run_parsim_sweep\LEDET\MBRB_9997.xlsx', r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\references\run_parsim_sweep\LEDET\MBRB_reference_9997.xlsx'],
        [r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\output\run_parsim_sweep\LEDET\MBRB_9998.xlsx', r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\references\run_parsim_sweep\LEDET\MBRB_reference_9998.xlsx'],
        [r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\output\run_parsim_conductor\MBRB_2.xlsx', r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\references\run_parsim_conductor\MBRB_reference_2.xlsx'],
        [r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\output\run_parsim_sweep\LEDET\generic_busbar_9997.yaml', r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\references\run_parsim_sweep\LEDET\generic_busbar_reference_9997.yaml'],
        [r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\output\run_parsim_sweep\LEDET\generic_busbar_9998.yaml', r'F:\Dropbox\gitlab\steam_sdk\tests\analyses\references\run_parsim_sweep\LEDET\generic_busbar_reference_9998.yaml'],
    ]

    # Substitute the reference files with the output files - THIS IS A VERY DANGEROUS THING TO DO -
    if FLAG_OVERWRITE:
        print('*** Substitute the reference files with the output files *** THIS IS A VERY DANGEROUS THING TO DO ***')
        for pair in list_files_to_overwrite:
            file_SOURCE = pair[0]
            file_TARGET = pair[1]

            shutil.copyfile(file_SOURCE, file_TARGET)
            print(f'File {file_TARGET} copied to file {file_SOURCE}.')