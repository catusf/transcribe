import os
from opencc import OpenCC


def convert_traditional_to_simplified(input_dir, output_dir):
    # Initialize the converter
    converter = OpenCC("t2s")

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Process each file in the input directory
    for filename in os.listdir(input_dir):
        input_filepath = os.path.join(input_dir, filename)

        # Check if the file is a .txt or .srt file
        if os.path.isfile(input_filepath) and (
            filename.endswith(".txt") or filename.endswith(".srt")
        ):
            # Read the content of the file
            with open(input_filepath, "r", encoding="utf-8") as file:
                traditional_text = file.read()

            # Convert to simplified Chinese
            simplified_text = converter.convert(traditional_text)
            simplified_text = simplified_text.replace("v̌", "ǚ")

            if simplified_text == traditional_text:
                print("*** No changes")
                continue

            # Define the output file path
            output_filepath = os.path.join(output_dir, filename)

            # Write the simplified text to the new file
            with open(output_filepath, "w", encoding="utf-8") as file:
                file.write(simplified_text)

            print(
                f"Converted {filename} to Simplified Chinese and saved to {output_filepath}"
            )


# Example usage
input_directory = "./downloads/subs"
output_directory = "./downloads/subs"
convert_traditional_to_simplified(input_directory, output_directory)
