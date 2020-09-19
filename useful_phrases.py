from docx import Document


def doc_to_dict(my_doc, my_dict):
    next_key = "None"
    for paragraph in my_doc.paragraphs:
        if paragraph.style.name.startswith("Heading"):  # == "Heading 3" or == "Heading 2"
            next_key = paragraph.text
            my_dict[next_key] = paragraph.text + "\n\n"
        else:
            my_dict[next_key] += paragraph.text + "\n"


def get_useful_phrase():
    useful_phrases_dict = {}
    doc_to_dict(Document("useful phrases.docx"), useful_phrases_dict)
    return useful_phrases_dict


if __name__ == '__main__':
    get_useful_phrase()
