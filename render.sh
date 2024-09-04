pandoc --filter pandoc-crossref --citeproc --number-sections \
    -s 'thesis.md' \
    -o 'thesis.pdf' \
    --csl=http://raw.githubusercontent.com/citation-style-language/styles/master/ieee.csl
