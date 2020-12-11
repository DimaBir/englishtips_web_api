import torch
import numpy as np

from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from pytorch_pretrained_bert import BertTokenizer, BertConfig
from pytorch_pretrained_bert import BertAdam, BertForSequenceClassification

from logic.coloring.wordiness import find_wordiness


def prepare_data(sentence):
    sentence = "[CLS] " + sentence + " [SEP]"
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    tokenized_sent = tokenizer.tokenize(sentence)

    # Set the maximum sequence length. The longest sequence in our training set is 47, but we'll leave room on the end anyway.
    # In the original paper, the authors used a length of 512.
    MAX_LEN = 128

    # Use the BERT tokenizer to convert the tokens to their index numbers in the BERT vocabulary
    input_id = tokenizer.convert_tokens_to_ids(tokenized_sent)

    # Pad our input tokens
    input_id = pad_sequences([input_id], maxlen=MAX_LEN, dtype="long", truncating="post", padding="post")

    # Create attention masks
    attention_masks = []

    # Create a mask of 1s for each token followed by 0s for padding
    for seq in input_id:
        seq_mask = [float(i > 0) for i in seq]
        attention_masks.append(seq_mask)

    sentence_input = torch.tensor(input_id)
    sentence_mask = torch.tensor(attention_masks)
    sentence_label = torch.tensor(np.empty(1, dtype=int))

    validation_data = TensorDataset(sentence_input, sentence_mask, sentence_label)
    validation_sampler = SequentialSampler(validation_data)
    return DataLoader(validation_data, sampler=validation_sampler, batch_size=1)


def evaluate_model(dataloader, model, device):
    # Put model in evaluation mode to evaluate loss on the validation set
    model.eval()

    # Evaluate data for one epoch
    for batch in dataloader:
        # Add batch to GPU
        batch = tuple(t.to(device) for t in batch)
        # Unpack the inputs from our dataloader
        b_input_ids, b_input_mask, b_labels = batch
        # Telling the model not to compute or store gradients, saving memory and speeding up validation
        with torch.no_grad():
            # Forward pass, calculate logit predictions
            logits = model(b_input_ids.type(torch.LongTensor), token_type_ids=None, attention_mask=b_input_mask)

        # Move logits and labels to CPU
        logits = logits.detach().cpu().numpy()
        return np.argmax(logits, axis=1).flatten()


def predict_class(sentence, model, device):
    result = None
    sentence_dataloader = prepare_data(sentence=sentence)
    pred_label = evaluate_model(dataloader=sentence_dataloader, model=model, device=device)

    threshold = 0.2
    factor = 1.9
    delta = 0.02
    num_of_wordiness = 0
    wordiness_dict = find_wordiness(sentence)
    for index in range(len(wordiness_dict)):
        num_of_wordiness = num_of_wordiness + len(wordiness_dict[index]['Indexes'])
    res = num_of_wordiness / len(sentence.split())

    if pred_label == 1 and res >= threshold:
        result = "Wordy"
    elif pred_label == 1 and res < threshold:
        result = "Clear" if res < threshold / factor + delta else "Wordy"
    elif pred_label == 0 and res < threshold:
        result = "Clear"
    elif pred_label == 0 and res >= threshold:
        result = "Wordy" if threshold*factor-delta < res else "Clear"
        # TODO: Deal with "A few inches of snow is necessary to go sledding."

    return result


def init():
    print("Initializing model and device")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_save_name = r".\NLP\model\best_0.9_checkpoint.pth"
    path = F"{model_save_name}"

    # Load BertForSequenceClassification, the pretrained BERT model with a single linear classification layer on top.
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)
    model.load_state_dict(torch.load(path, map_location=torch.device('cpu')))
    print("Finished model and device initialization")
    return model, device