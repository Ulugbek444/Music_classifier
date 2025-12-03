

{'eval_loss': 1.0366945266723633,
 'eval_runtime': 51.6656,
 'eval_samples_per_second': 269.444,
 'eval_steps_per_second': 33.697,
 'epoch': 1.0}

{'eval_loss': 1.0366945266723633,
 'eval_macro_f1': 0.6347144061389928,
 'eval_weighted_f1': 0.6341243988006784,
 'eval_runtime': 54.684,
 'eval_samples_per_second': 254.572,
 'eval_steps_per_second': 31.837,
 'epoch': 1.0}

                   precision    recall  f1-score   support

       anger       0.53      0.64      0.58      2371
        fear       0.67      0.62      0.65      2080
         joy       0.67      0.58      0.62      3780
        love       0.66      0.73      0.69      2043
     sadness       0.65      0.65      0.65      3150
    surprise       0.65      0.59      0.62       497

    accuracy                           0.63     13921
   macro avg       0.64      0.64      0.63     13921
weighted avg       0.64      0.63      0.63     13921


tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
Что происходит внутри:
читается tokenizer.json / vocab.txt
подгружается:
WordPiece словарь
special tokens ([CLS], [SEP])
📌 Tokenizer НЕ учится, он фиксирован.

model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
Происходит:
читается config.json
загружаются веса модели
поднимается правильная архитектура:
BERT encoder
Classification head (Linear)
📌 Ты НЕ пересоздаёшь модель вручную — это правильно.

model.eval()
⚠️ ОЧЕНЬ ВАЖНО
Это переключает модель в inference mode:
❌ dropout выключен
❌ batchnorm фиксирован
✅ результаты стабильны
✅ быстрее
📌 Без этого инференс НЕ корректен.

inputs = tokenizer(
    text,
    return_tensors="pt",
    truncation=True,
    max_length=128
)

🔹 return_tensors="pt"
👉 возвращает torch.Tensor
{
  "input_ids": tensor([[101, 2023, ...]]),
  "attention_mask": tensor([[1, 1, ...]])
}
✅ Именно то, что ждёт PyTorch модель.

🔹 truncation=True
Если текст длиннее max_length:
обрезается
без ошибок
📌 Это важно для lyrics — они длинные.

🔹 max_length=128
Почему 128:
модель обучалась с 128 ✅
быстрее инференс ✅
меньше VRAM ✅
тексты песен очень повторяющиеся ✅
🔥 Абсолютно корректный выбор.

🔹 with torch.no_grad():
👉 Говорит PyTorch:
❌ не считать градиенты
❌ не хранить computation graph
✅ экономить память
✅ ускорять инференс
📌 Это обязательная конструкция для inference.

🔹 outputs = model(**inputs)
Модель возвращает объект типа:
SequenceClassifierOutput(
  logits=tensor([[...]]),
  hidden_states=None,
  attentions=None
)
📌 Нас интересует только logits.

🔹 probs = torch.softmax(outputs.logits, dim=1)
Почему softmax:
logits → не вероятности
softmax → вероятность по классам
сумма = 1 ✅
📌 dim=1, потому что:
[batch_size, num_classes]

🔹 pred_id = probs.argmax(dim=1).item()
🔹 confidence = probs.max().item()
argmax → индекс класса
max → уверенность
📌 Для одного текста:
pred_id = int
confidence = float

🔹 label = model.config.id2label[pred_id]
📌 Это:
маппинг из обучения
самое правильное место брать labels
❌ НЕ захардкожены
✅ переносимы
✅ безопасны

🔹 return label, confidence
("sadness", 0.87)