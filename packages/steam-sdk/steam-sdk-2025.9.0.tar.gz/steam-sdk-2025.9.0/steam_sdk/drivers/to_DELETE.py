
ANSYS_path, directory, jobname, memory, reserve, input_file, output_file, n_processors = 'fdsfsd', 'efohi', 'fwhui', '123', '54', 'ndwuofn', 'dfsljh', 4

callString = ('\"{}\" -p ansys -dir \"{}\" -j \"{}\" -s noread '
              '-m {} -db {} -t -d win32 -b -i \"{}\" -o \"{}\" -smp -np {}'
              ).format(ANSYS_path, directory, jobname, memory, reserve, input_file, output_file, n_processors)
callString2 = f'\"{ANSYS_path}\" -p ansys -dir \"{directory}\" -j \"{jobname}\" -s noread -m {memory} -db {reserve} -t -d win32 -b -i \"{input_file}\" -o \"{output_file}\" -smp -np {n_processors}'

print(callString)
print(callString2)
print(callString==callString2)
print(f'String to call:\n{callString}')