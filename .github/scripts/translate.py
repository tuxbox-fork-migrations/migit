
# .github/scripts/translate.py

from googletrans import Translator

def translate_readme(input_text, target_lang):
    translator = Translator()
    translated = translator.translate(input_text, dest=target_lang)
    return translated.text

if __name__ == "__main__":
    input_text = open("README.md", "r").read()
    target_lang = "en"  # Ziel-Sprachcode für Englisch
    translated_text = translate_readme(input_text, target_lang)

    with open("README_en.md", "w") as outfile:
        outfile.write(translated_text)
