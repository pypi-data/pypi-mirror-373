import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from collections import Counter
import re

# 示例数据
texts = [
    "I love watching football",
    "The game last night was thrilling",
    "NASA launched a new satellite",
    "Artificial intelligence is growing fast",
    "The movie was fantastic",
    "I enjoy romantic comedies"
]
labels = [0, 0, 1, 1, 2, 2]  # 0: Sports, 1: Tech, 2: Entertainment

# 分词 + 构建词表
def tokenize(text):
    return re.findall(r'\b\w+\b', text.lower())

tokenized = [tokenize(t) for t in texts]
vocab = {"<PAD>": 0, "<UNK>": 1}
for word in Counter(w for sent in tokenized for w in sent):
    vocab[word] = len(vocab)

# 编码文本
def encode(tokens):
    return torch.tensor([vocab.get(w, vocab["<UNK>"]) for w in tokens], dtype=torch.long)

encoded_texts = [encode(t) for t in tokenized]
padded_texts = pad_sequence(encoded_texts, batch_first=True, padding_value=0)
labels = torch.tensor(labels)


class TextDataset(Dataset):
    def __init__(self, texts, labels):
        self.texts = texts
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.texts[idx], self.labels[idx]


dataset = TextDataset(padded_texts, labels)
loader = DataLoader(dataset, batch_size=2, shuffle=True)

import torch.nn as nn


class LSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        embedded = self.embedding(x)  # [batch, seq, embed]
        output, (hn, _) = self.lstm(embedded)
        return self.fc(hn[-1])  # 使用最后一层的 hidden state


model = LSTMClassifier(vocab_size=len(vocab), embed_dim=64, hidden_dim=128, num_classes=3)

import torch.optim as optim

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 训练循环
for epoch in range(30):
    model.train()
    total_loss = 0
    for batch_x, batch_y in loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)

        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch + 1}, Loss: {total_loss:.4f}")




def predict(text):
    model.eval()
    tokens = tokenize(text)
    encoded = encode(tokens).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(encoded)
        pred = torch.argmax(logits, dim=1).item()
    return pred

print(predict("Last night I watched a great match"))  # 应输出接近体育类 - 0
