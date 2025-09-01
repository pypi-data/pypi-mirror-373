# cp-tool
A command-line interface (CLI) for creating competitive programming problem files.

## Installation with pip
To install cp-tool with pip, use the following command:

```bash
pip install cptool-py
```

## Installation with nix flakes
To install cp-tool as a nix flake, add the following input to your configuration:

```nix
{
  inputs = {
    cp-tool.url = "github:smntic/cp-tool";
  };
}
```

Then you can install it either through either your NixOS or home-manager configuration.

**NixOS**
```nix
environment.systemPackages = [
  inputs.cp-tool.packages.${pkgs.system}.cptool-py
];
```

**home-manager**
```nix
home.packages = [
  inputs.cp-tool.packages.${pkgs.system}.cptool-py
];
```

## Configuration
To set up your templates, copy them to `~/.local/share/cp-tool/template.<extension>`.  
Alternatively, you can define a custom template path with the `--template-path` argument.

## Usage
```bash
cpt <commands> [args]
```

## Commands
- **Create a Problem:**
  ```bash
  cpt problem <name>
  ```
  Creates a folder containing a template for the specified problem name.

- **Create a Contest:**
  ```bash
  cpt contest <num_problems> <name>
  ```
  Creates a folder with `<num_problems>` problem files.

- **Create or Replace a Template:**
  ```bash
  cpt template <file>
  ```
  Creates a new template file or replaces an existing one with the specified name.

If the names contains special characters like '(', you can wrap the entire  name in quotes: "Codeforces Round (Div. 2)"

## Arguments
- **File Extension:**
  ```bash
  --extension=<ext> or -e=<ext>
  ```
  Use this parameter to specify the file extension for the templates and problem files.
  The extension defaults to 'cpp'.

- **Template Path:**
  ```bash
  --template-path=<path> or -t=<path>
  ```
  Use this paramter to specify the path to a directory containing all your
  template files. Otherwise defaults to '~/.local/share/cp-tool'

## Automatic Directory Change
To avoid manually changing directories to the newly created folders, you can run the command with:
```bash
source cpt <arguments>
```
Alternatively, you can create an alias in your shell profile to make `cpt` execute with `source` automatically:
```bash
alias cpt='source cpt'
```
