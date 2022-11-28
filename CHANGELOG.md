# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project's packages adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Update icon url

### Added

- Add logo url

## [0.9.1] - 2022-11-24

### Fixed

- Remove proxyProtocol filed from gateway policy which prevented routing traffic other than HTTP

## [0.9.0] - 2022-11-07

### Changed

- Bump version to 2.12.2 with vendir ([#40](https://github.com/giantswarm/linkerd2-multicluster-app/pull/40)).
- add registry switch to allow installations to automatically set the image registry based on location.
- Replace hard-coded image name with values ([#41https://github.com/giantswarm/linkerd2-multicluster-app/pull/41]()).
- Rename app as `linkerd-multicluster` ([#42](https://github.com/giantswarm/linkerd-multicluster-app/pull/42))

## [0.8.0] - 2022-09-21

### Changed

- Upgrade to 2.11.4

## [0.7.0] - 2022-07-04

### Added

- First version of Linkerd mutlicluster link chart.

[Unreleased]: https://github.com/giantswarm/linkerd-multicluster-app/compare/v0.9.1...HEAD
[0.9.1]: https://github.com/giantswarm/linkerd-multicluster-app/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/giantswarm/linkerd-multicluster-app/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/giantswarm/linkerd2-multicluster-app/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/giantswarm/linkerd2-multicluster-app/compare/v0.7.0...v0.7.0
