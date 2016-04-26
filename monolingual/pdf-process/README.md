# PDF processing

Work on processing/segmentation of monolingual pdf files.

## 1. Text Cleaning

* Skip non-textual line (TOCs, table data, code snippets...)
* Remove lines without text in greek
* Skip repeating headers/footers
* Normalize multiple whitespace chars/newlines

## 2. Paragraph Splitting/Assembling

Chunkize text, challenging for pdf format.

* Algorithmically decide how to group input text lines.
* Ignore interspersed figure captions
 
## 3. Segmentation of chunks

Produce 1-line-per-segment text files.

Notable issues:

* Incomplete sentences, due to PDF formatting (nothing can be done here)
* Some captions still survive.
* Bibliographies (cannot recognize automatically).
* Mathematical/other characters not removed (maybe necessary to do before consuming).

