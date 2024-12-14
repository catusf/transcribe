import xlwings as xw
import jieba
import re
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import pinyin_jyutping

# Open the Excel file and select the sheet
file_path = 'Changed_files_report-Translated.xlsx'
app = xw.App(visible=False)
workbook = xw.Book(file_path)
sheet = workbook.sheets[0]

# Constants
MODEL_DIR = "./downloads/m2m100_model"
LOADED_MODEL = False
model, tokenizer = None, None

# Initialize Pinyin generator
pinyin_generator = pinyin_jyutping.PinyinJyutping()

# Function to set up the model and tokenizer
def setup_model(MODEL_DIR):
    """
    Sets up the translation model and tokenizer. Loads them from the local directory if available,
    otherwise downloads them and saves them locally.

    Parameters:
    MODEL_DIR (str): The directory where the model and tokenizer are saved.

    Returns:
    model (M2M100ForConditionalGeneration): The translation model.
    tokenizer (M2M100Tokenizer): The tokenizer for the model.
    """
    global LOADED_MODEL

    if LOADED_MODEL:
        print('Offline translation model loaded already.')
        return model, tokenizer
    
    print('Loading offline translation model...')
    
    if not os.path.exists(MODEL_DIR):
        # Load the model and tokenizer from Hugging Face
        print(f"Downloading and saving the model and tokenizer to {MODEL_DIR}")
        model = M2M100ForConditionalGeneration.from_pretrained('facebook/m2m100_418M')
        tokenizer = M2M100Tokenizer.from_pretrained('facebook/m2m100_418M')

        # Save model and tokenizer locally
        model.save_pretrained(MODEL_DIR)
        tokenizer.save_pretrained(MODEL_DIR)
        print(f"Model and tokenizer saved locally at {MODEL_DIR}")
    else:
        # Load the model and tokenizer from the local directory
        print(f"Loading model and tokenizer from {MODEL_DIR}")
        model = M2M100ForConditionalGeneration.from_pretrained(MODEL_DIR)
        tokenizer = M2M100Tokenizer.from_pretrained(MODEL_DIR)

    print('Offline translation model loaded.')

    LOADED_MODEL = True
    return model, tokenizer

# Function to perform the translation
def offline_translate(text, from_lang, to_lang):
    """
    Translates text from one language to another using a pre-loaded model and tokenizer.
    
    Parameters:
    text (str): The input text to translate
    from_lang (str): The source language code (e.g., 'zh')
    to_lang (str): The target language code (e.g., 'en')

    Returns:
    str: The translated text
    """
    global model, tokenizer
    model, tokenizer = setup_model(MODEL_DIR)
    tokenizer.src_lang = from_lang
    
    # Tokenize the input text
    encoded_text = tokenizer(text, return_tensors='pt')
    
    # Generate the translation by setting the forced beginning of the sentence to the target language
    generated_tokens = model.generate(**encoded_text, forced_bos_token_id=tokenizer.get_lang_id(to_lang))
    
    # Decode the translated tokens to get the output text
    translated_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    
    return translated_text[0]

# Read data from column H (assuming it starts from H2 to the last non-empty cell)
column_h = sheet.range('H2:H' + str(sheet.range('H' + str(sheet.cells.last_cell.row)).end('up').row)).value

# Initialize lists to store the processed data for columns M, N, O, P, S
column_m = []
column_n = []
column_o = []
column_p = []
column_s = []

# Process each cell in column H
for text in column_h:
    if text is not None:
        # Extract only Chinese characters
        chinese_text = ''.join(re.findall(r'[一-鿿]', str(text)))
        words = list(jieba.cut(chinese_text))
        column_m.append(';'.join(words))  # Join the segmented words with ';' for column M
        column_n.append(offline_translate(chinese_text, 'zh', 'en'))  # Translate to English for column N
        column_o.append(offline_translate(chinese_text, 'zh', 'vi'))  # Translate to Vietnamese for column O
        pinyin_text = pinyin_generator.pinyin(chinese_text)
        column_p.append(pinyin_text)  # Get Pinyin for column P
        column_s.append(pinyin_generator.pinyin(';'.join(words)))  # Get Pinyin for column M in column S
    else:
        column_m.append('')
        column_n.append('')
        column_o.append('')
        column_p.append('')
        column_s.append('')

# Write results to columns M, N, O, P, S, starting from M2, N2, O2, P2, and S2
sheet.range('M2').options(transpose=True).value = column_m
sheet.range('N2').options(transpose=True).value = column_n
sheet.range('O2').options(transpose=True).value = column_o
sheet.range('P2').options(transpose=True).value = column_p
sheet.range('S2').options(transpose=True).value = column_s

# Save and close the workbook
output_path = 'Processed_Changed_files_report.xlsx'
workbook.save(output_path)
workbook.close()
app.quit()

print(f"Processed file saved to {output_path}")
