# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## Unreleased

### Added

- `parse` command, with ...
   - `rollseries` subcommand, which reads a series of rolls as input and ouputs
     Roll Events
- `plot` command, with ...
   - `pdf` subcommand, which reads a stream of Roll Events and plots a
     probability density function of them
- `simulate` command, which takes the given odds of rolling each number,
  simulates a bunch of rolls based on that distribution, and outputs the
resulting rolls
- `statistics` command, which reads a stream of Roll Events and outputs
  statistics about them
