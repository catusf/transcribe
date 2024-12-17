import os


def remove_duplicates(lines):
    if not lines:
        return lines
    line_dict = set()
    new_lines = [lines[0]]
    for line in lines[1:]:
        if not line.strip():
            continue
        if line not in line_dict:
            line_dict.add(line)
            new_lines.append(line)

    print(f"Lines removed: {len(lines)-len(new_lines)}")
    return new_lines


def process_text_files(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()

            new_lines = remove_duplicates(lines)

            print(filename)

            # Add filename without extension at the beginning
            filename_without_ext = os.path.splitext(filename)[0]
            remove_text = " - HocTT"
            headed = (
                "//HocTT/"
                + filename_without_ext[: filename_without_ext.find(remove_text)]
            )

            new_lines.insert(0, headed + "\n")

            with open(file_path, "w", encoding="utf-8") as file:
                file.writelines(new_lines)


# Usage
folder_path = "./downloads/subs"  # Replace with the path to your folder
process_text_files(folder_path)
