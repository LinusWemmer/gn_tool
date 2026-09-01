# Define the input and output file names
input_file_name = 'movierbare_Substantive.txt'
output_file1_name = 'movierbare_Substantive_in_Komposita.txt'
output_file2_name = 'movierbare_Substantive_in_Komposita_alternativ.txt'

# Open the input file for reading and output file for writing
with open(input_file_name, 'r', encoding='utf-8') as input_file, open(output_file1_name, 'w', encoding='utf-8') as output_file1, open(output_file2_name, 'w', encoding='utf-8') as output_file2:
    # Read each line from the input file
    for line in input_file:
        # Remove any trailing whitespaces including new line character
        line = line.rstrip()

        # Check the ending of the line and modify accordingly
        if line == "Freund":
            output_file1.write(line + 'es' + '\n')
            output_file2.write(line + 'e' + '\n')
        elif line == "Dieb":
            output_file1.write(line + 'es' + '\n')
            output_file2.write(line + 's' '\n')
        elif line == "Arzt":
            output_file1.write(line + '\n')
            output_file2.write('Ärzte' + '\n')
        elif line == "Kapitän" or line.endswith('är'):
            output_file1.write(line + 's' + '\n')
            output_file2.write('%' + line + '\n')
        elif line == "Bischof" or line == "Anwalt" or line == "Herzog":
            output_file1.write(line + 's' + '\n')
            output_file2.write('%' + line + '\n')
        elif line == "Graf" or line == "Held" or line == "Zar":
            output_file1.write(line + 'en' + '\n')
            output_file2.write('%' + line + '\n')
        elif line == "General" or line == "Papst":
            output_file1.write(line + '\n')
            output_file2.write('%' + line + '\n')
        elif line == "Gott":
            output_file1.write(line + 'es' + '\n')
            output_file2.write('Götter' + '\n')
        elif line == "Chef" or line == "Riese" or line == "Koch" or line == "Ire" or line == "Pate" or line == "Same" or line == "Bote" or line == "Ober" or line == "Hirt" or line == "Wart" or line == "Elfe" or line.lower().endswith('rat') or line.lower().endswith('wirt'):
            output_file1.write('%' + line + '\n')
            output_file2.write('%' + line + '\n')
        elif line == "Ungar":
            output_file1.write(line + 'n' + '\n')
            output_file2.write('%' + line + '\n')
        elif line == "König" or line == "Kaiser" or line.endswith == "ar":
            output_file1.write(line + 's' + '\n')
            output_file2.write(line + '\n')
        elif line.endswith('chef'):
            output_file1.write(line + '\n')
            output_file2.write('%' + line + '\n')
        elif line.endswith('er') or line.endswith('eur'):
            # Write the line as is
            output_file1.write(line + '\n')
            output_file2.write('%' + line + '\n')
        elif line.endswith('e'):
            # Add 'n' at the end of the line
            output_file1.write(line + 'n' + '\n')
            output_file2.write('%' + line + '\n')
        else:
            # Add 'en' at the end of the line
            output_file1.write(line + 'en' + '\n')
            output_file2.write('%' + line + '\n')

# Notify that the script has completed processing
print("Processing completed. The output is saved in '{}'".format(output_file1_name))

