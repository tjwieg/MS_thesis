pandoc --filter pandoc-crossref --citeproc --number-sections \
    -s 'thesis.md' \
    --highlight-style=tango \
    -o 'thesis.pdf' \
    --csl=http://raw.githubusercontent.com/citation-style-language/styles/master/ieee.csl
