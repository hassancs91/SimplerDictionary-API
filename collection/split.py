def split_file(input_file_path, output_folder, max_words=1000):
    import os

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(input_file_path, 'r') as file:
        lines = file.readlines()

    file_count = 0
    for i in range(0, len(lines), max_words):
        file_count += 1
        with open(os.path.join(output_folder, f'split_{file_count}.txt'), 'w') as output_file:
            output_file.writelines(lines[i:i + max_words])

if __name__ == "__main__":
    INPUT_FILE = './collection/full_collection.txt'  # Replace with your input file path
    OUTPUT_FOLDER = './collection/splits'  # Replace with your desired output folder path
    split_file(INPUT_FILE, OUTPUT_FOLDER)
