# cp-tool

A command-line interface (CLI) for creating competitive programming problem
files.

## Installation with pip

To install cp-tool with pip, use the following command:

```bash
pip install cptool-py
```

## Installation with nix flakes

To install cp-tool as a nix flake, add the following input to your
configuration:

```nix
{
  inputs = {
    cp-tool.url = "github:smntic/cp-tool";
  };
}
```

Then you can install it either through either your NixOS or home-manager
configuration.

### NixOS

```nix
environment.systemPackages = [
  inputs.cp-tool.packages.${pkgs.system}.cptool-py
];
```

### home-manager

```nix
home.packages = [
  inputs.cp-tool.packages.${pkgs.system}.cptool-py
];
```

## Configuration

To set up your templates, copy them to
`~/.local/share/cp-tool/template.<extension>`.  Alternatively, you can define a
custom template path with the `--template-folder` argument.

## Usage

```bash
cpt [args] <commands>
```

## Commands

- **Create a Problem:**

  ```bash
  cpt problem <name>
  ```

  Creates a folder containing a template for the specified problem name.

- **Create a Contest:**

  ```bash
  cpt contest <name> <mode>
  ```

  **Available modes:**
  - `alpha <num_problems>` -
      create `<num_problems>` problems indexed by A, B, C, ...
  - `numeric <num_problems>` -
      create `<num_problems>` problems indexed by 1, 2, 3, ...
  - `custom <problem_indices>` -
      create a custom list of problem indices, separated by spaces.

- **Create or Replace a Template:**

  ```bash
  cpt template <problem_names>
  ```

  Copies your template to create a new file for each problem.

If the names contain spaces or special characters like '(', you can wrap
the entire name in quotes, like `"Codeforces Round (Div. 2)"`.
CP-tool will automatically handle converting your strings into a nice, terminal-friendly
format.

## Arguments

- **File Extension:**

  ```bash
  -ex=, --extension=
  ```

  Use this parameter to specify the file extension for the templates and
  problem files. The extension defaults to `.cpp`. Other common examples include
  `.c` and `.py`.

- **Template Path:**

  ```bash
  -tf=, --template-folder=
  ```

  Specify the path to a folder containing all your template files. This defaults
  to the typical "user data directory" of your operating system. See `cpt -h`
  for more information.

## Automatic Directory Change

To avoid manually changing directories to the newly created folders, you can
run the command with:

```bash
source cpt <arguments>
```

Alternatively, you can create an alias in your shell profile to make `cpt`
execute with `source` automatically:

```bash
alias cpt='source cpt'
```
