# A Template to Clipboard Utility

Templates to your clipboard: because sometimes you *just* can't be bothered to
type it again. While this utility was created as an exercise to relearn `typer`
(which is great, though really all CLI tools should be "rewritten in Rust") and
a few other tools (and whack this out as quickly as possible), but hopefully
it's at least of some use to some folks. Eventually, the idea is to also
leverage [template strings](https://peps.python.org/pep-0750/) once those become
available, because really that is a great idea.

## Installation

The recommended installation path is via the `uv tool` interface, installing via
the GH link or PyPI, as you please:

```sh
uv tool install tmplcl
```

```sh
uv tool install git+https://github.com/delfanbaum/tmplcl
```

## Usage

This package provides two executable commands: `tmplcl` and `tcl`. `tmplcl` is
the "app" version of the tool, allowing you to perform all the expected CRUD
tasks such as creating, listing, deleting, and updating your various templates.
`tcl` is essentially just a shortcut for `tmplcl copy TEMPLATE_ID`, because who
wants to do all that typing.

The usage for each is as follows:

```console
tmplcl --help
                                                                              
 Usage: tmplcl [OPTIONS] COMMAND [ARGS]...                                    
                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.    │
│ --show-completion             Show completion for the current shell, to    │
│                               copy it or customize the installation.       │
│ --help                        Show this message and exit.                  │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────╮
│ copy     Copies the requested template to your clipboard                   │
│ delete   Deletes the template with the provided identifier                 │
│ add      Adds a template with the provided identifier and string           │
│ list     Lists all available templates, including a preview of each        │
│ show     Displays the full text of a given template                        │
│ update   Updates a given template with a new string                        │
╰────────────────────────────────────────────────────────────────────────────╯
```

```console
tcl --help
                                                                              
 Usage: tcl [OPTIONS] TEMPLATE                                                
                                                                              
 Finds a template by its id and copies the resultant string to the clipboard  
                                                                              
                                                                              
╭─ Arguments ────────────────────────────────────────────────────────────────╮
│ *    template      TEXT  [default: None] [required]                        │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                │
╰────────────────────────────────────────────────────────────────────────────╯
```

## Data Storage

Following the [XDG Base Directory
Specification](https://specifications.freedesktop.org/basedir-spec/latest/),
data will stored in `$XDG_DATA_HOME/tmplcl`. 

If you would like to define your templates manually, it's all just JSON, so open
up `$XDG_DATA_HOME/tmplcl/data.json` and have at it. The schema is roughly
as follows:

```json
{
  "description": "The model for the templates copied over to the clipboard. Contains the\ntemplate identifier as well as the template string.\n\nNote that the id may contain only alphanumeric characters or `-` and `_`",
  "properties": {
    "identifier": {
      "minLength": 1,
      "pattern": "^[a-zA-Z0-9_-]+$",
      "title": "Identifier",
      "type": "string"
    },
    "template": {
      "minLength": 1,
      "title": "Template",
      "type": "string"
    }
  },
  "required": [
    "identifier",
    "template"
  ],
  "title": "Template",
  "type": "object"
}
```


## Development

To get started, run `uv sync`.

## The Future

Eventually, the goal is to support these "templates" as actual... templates.
Like, being able to run `tcl my_template foo` where `my_template` is `"My
favorite food is {}` and `"My favorite food is foo"` gets put on your clipboard.
But that'll be a 0.1.2 thing.
