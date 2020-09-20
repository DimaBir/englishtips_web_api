from googletrans import Translator


def google_translate(text, target_language="he"):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    result = translation.text

    return result


if __name__ == '__main__':
    translated_words = google_translate(["Hello how are you?", "Hey I want to look on this"], "he")
