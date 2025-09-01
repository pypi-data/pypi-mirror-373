# Getting started with journal-manager

Organize your MkDocs journals with ease, fostering focused learning one topic at a time.
[Read the docs](https://danoan.github.io/journal-manager/).

## What is journal-manager?

*journal-manager* is a command-line interface (CLI) application designed for the
organization of MkDocs notebooks and journals. *journal-manager* facilitates 
the prioritization of learning, one topic and one journal at time.

The terminal interface in combination with markdown text reduces distraction and 
improves productivity. *journal-manager* will be a valuable companion on your 
learning quest.

## Installation

```bash
$ git clone https://github.com/danoan/journal-manager
$ cd journal-manager
$ pip install .
```

## Setup

```bash
# Setup environment variable (e.g. in ~/.bashrc)
export JOURNAL_MANAGER_CONFIG_FOLDER="~/.config/journal-manager" 
```

```python
$ jm setup init
$ Enter the path of your default editor: nvim

default_journal_folder=/home/my-user/.config/journal-manager/journals
default_template_folder=/home/my-user/.config/journal-manager/templates
journal_data_filepath=/home/my-user/.config/journal-manager/journal_data.toml
template_data_filepath=/home/my-user/.config/journal-manager/template_data.toml

default_text_editor_path=nvim
```

## Usage

### Create and edit journals

```bash
$ jm journal create "nlp" 
$ jm journal
nlp:/home/my-user/.config/journal-manager/journals/nlp
$ jm journal edit nlp
```

### Create journal-manager template

```bash
$ jm template register "with-latex" "~/my-journal-manager-templates/with-latex"
$ jm template 
with-latex:/home/my-user/.config/journal-manager/templates/with-latex
$ jm journal create "statistics" --template-name "with-latex"
$ jm journal
nlp:/home/my-user/.config/journal-manager/journals/nlp
statistics:/home/my-user/.config/journal-manager/journals/statistics
```

### Build static web page

```bash
$ jm build --build-location "~/my-journal-web-page"
```




