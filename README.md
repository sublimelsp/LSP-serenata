# LSP-serenata
> PHP support for Sublime's LSP plugin using [Serenata](https://gitlab.com/Serenata/Serenata).

### Getting started

- Install [LSP](https://packagecontrol.io/packages/LSP) and `LSP-serenata` from Package Control.
- Restart Sublime.

#### Configuration

Configure the Serenata language server by accessing `Preferences > Package Settings > LSP > Servers > LSP-serenata`.

Several options can be set for example when `php` is not in your `PATH`, these `settings` are supported:

**phpPath**
Name of the PHP binary in your `PATH` or an absolute path to the PHP binary. You can use `${home}` to reference your user's home directory. The default is `php`.

**memoryLimit**
This option is passed to directly to PHP as `memory_limit`, please see the [PHP documentation](https://www.php.net/manual/en/ini.core.php#ini.memory-limit). The default is `1024M` for 1GB of allowed memory.

### Reporting issues

This package provides only a client implementation, for any server related bugs please report them [here](https://gitlab.com/Serenata/Serenata/issues).
