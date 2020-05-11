# CoreNLP-NER-tagger
Simple curses console application to label words for training CoreNLP NER classifier.

CoreNLP's NER classifier can be trained using a tok file. Tok files are a two column tab separated format. The word token in the first column and the class labels in the second column.

More information about the training process is available [https://nlp.stanford.edu/software/crf-faq.shtml#a|here] and [https://nlp.stanford.edu/software/CRF-NER.html|here].

## Usage

Prepare the input text to be one word per line using CoreNLP, e.g.

``` bash
java -cp stanford-ner.jar edu.stanford.nlp.process.PTBTokenizer jane-austen-emma-ch1.txt > jane-austen-emma-ch1.tok
```

Then use ner-tagger.py to allow you to quickly classify each line of the file:

``` bash
python ner-tagger.py jane-austen-emma-ch1.tok jane-austen-tagged.tok
```

## Behaviour

Currently the tool will default all entries to 'O' which means it will be ignored.
The tool is hardcoded to support tagging as ORGANISATION by pressing 'o' or PERSON by pressing 'p'.

Adjacent words with the same label are considered to be the same entity.

## Limitations

The labels are currently hardcoded.
The tool doesn't support save and resume, you need to complete the file in one sitting.