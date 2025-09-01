from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

try:
    import torch
except ModuleNotFoundErrorError:
    print(
        "[WARN] torch is not found. dtx will be limited in its functionality. If required, run pip install dtx[torch] to install full version of dtx."
    )


class HateSpeechClassifier:
    def __init__(self):
        super(HateSpeechClassifier, self).__init__()

    def __call__(self, input_ids, labels=None):
        outputs = self.model(input_ids)
        return outputs

    def from_text(self, text):
        input_ids = self.tokenizer(text, return_tensors="pt")["input_ids"]
        logits = self.__call__(input_ids).logits
        return 100 * float(torch.softmax(logits, dim=1)[:, 1].detach().numpy())


class HateBERT(HateSpeechClassifier):
    def __init__(self, model_path):
        """
        HateBERT files: https://huggingface.co/GroNLP/hateBERT
        """
        super(HateBERT, self).__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("GroNLP/hateBERT")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path
        ).eval()


class ToxDectRoBERTa(HateSpeechClassifier):
    def __init__(self):
        """
        ToxDectRoBERTa files: https://huggingface.co/Xuhui/ToxDect-roberta-large
        """
        super(ToxDectRoBERTa, self).__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("Xuhui/ToxDect-roberta-large")
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "Xuhui/ToxDect-roberta-large"
        ).eval()
