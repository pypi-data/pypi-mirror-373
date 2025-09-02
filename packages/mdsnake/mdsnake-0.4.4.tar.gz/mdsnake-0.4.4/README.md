![pylint rated 10.00/10](https://img.shields.io/badge/pylint-10.00-green)
![version 0.4.4](https://img.shields.io/badge/version-v0.4.4-green)

# mdsnake

A library with a cli, that can view markdown files, without having to commit to github. If you forget markdown syntax as well, it will help you with that!

# Compatibility

Works on Linux, macOS, and Windows which requires Python **3.10** and above

# Installing

```
pip install mdsnake
```

# Commands

Views the markdown file in your console

```
mdsnake view README.md
```

Views the markdown file on a localhost

```
mdsnake view README.md --web
```

Converts markdown files to html/pdf

**Note:** Setting a name is optional

```
mdsnake view README.md html --name output.pdf
mdsnake view README.md html --name output.pdf
```

Creates a table of markdown syntax so you don't forget

```
mdsnake syntax
```
