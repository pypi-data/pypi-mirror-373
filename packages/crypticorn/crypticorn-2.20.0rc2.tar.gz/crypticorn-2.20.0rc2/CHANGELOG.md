## Python API Client Changelog

The changelog only documents changes to the client code. For changes to the underlying APIs, see the API Changelogs.

<!-- changelog-insertion -->

## v2.20.0-rc.2 (2025-09-01)

### Features

- Latest auth api changes
  ([`e9f12fb`](https://github.com/crypticorn-ai/api-client-python/commit/e9f12fb7a484850084bfc0ad2ae7ebc1fbd80bef))


## v2.20.0-rc.1 (2025-09-01)

### Bug Fixes

- Pin openapi-generator to 7.14 resolving import errors
  ([`6037037`](https://github.com/crypticorn-ai/api-client-python/commit/60370371e3c80cca0e073f460f7ab198b732800b))

### Chores

- Update changelog configuration for semantic release
  ([`0e948a1`](https://github.com/crypticorn-ai/api-client-python/commit/0e948a132678b4df995bd76e6cfd326f19aaa13a))

### Documentation

- Add versioning section with SDK version details
  ([`c7b46ad`](https://github.com/crypticorn-ai/api-client-python/commit/c7b46ad3774d8d78ca61f34999e9129b45da20cc))

### Features

- Add dex API support
  ([`b78b7e4`](https://github.com/crypticorn-ai/api-client-python/commit/b78b7e4837fa89d71c0552e6845e7301920ed91e))

- Add notification API support
  ([`b038b6f`](https://github.com/crypticorn-ai/api-client-python/commit/b038b6f8135f994e3e6f570b95bc030e39975805))

### Refactoring

- Remove deprecation notices in client service properties (they won't be refactor to methods, see
  versioning section)
  ([`954ff4b`](https://github.com/crypticorn-ai/api-client-python/commit/954ff4b75985dc7db91ba72053f315cc8b01f1ed))


## v2.19.0 (2025-07-20)


## v2.19.0-rc.2 (2025-07-18)

### Bug Fixes

- Change verify api key request
  ([`bb0798b`](https://github.com/crypticorn-ai/api-client/commit/bb0798b14439a5681e267663ebca905d843cce7e))


## v2.19.0-rc.1 (2025-06-23)

### Documentation

- Document deprecation changes
  ([`9b545d1`](https://github.com/crypticorn-ai/api-client/commit/9b545d1911a81b39c52352f4bb28a2d284268b13))

### Features

- Deprecate `common` module in favor for a new package
  ([`5c29d01`](https://github.com/crypticorn-ai/api-client/commit/5c29d016db255dab5c92ddc3fdc636ea9c48e1f1))

- Deprecate subclients access by property in favor for methods to support versioning. Supported in
  the next major release
  ([`8e6d826`](https://github.com/crypticorn-ai/api-client/commit/8e6d82666a056771ff3e14d0f8ee2bc147047c49))

- Support versioned APIs
  ([`4a95dac`](https://github.com/crypticorn-ai/api-client/commit/4a95dacd3fcfd3d78e1c216036e9f8e842d73a53))


## v2.18.0 (2025-06-19)

### Features

- Add basic authentication method
  ([`2cc025b`](https://github.com/crypticorn-ai/api-client/commit/2cc025b462e6bdf1c2043440752be49e27560426))

- Return authentication methods in response headers
  ([`24082a8`](https://github.com/crypticorn-ai/api-client/commit/24082a8dea3431f14e375e6b9063d3be2fd9ec61))

### Refactoring

- Move metrics endpoint under admin route and allow jwt and api key auth
  ([`cb88335`](https://github.com/crypticorn-ai/api-client/commit/cb8833537628510b6fe07f19fbfb7a79be5881a3))

### Testing

- Extend authentication tests
  ([`d68b8be`](https://github.com/crypticorn-ai/api-client/commit/d68b8be3608cf9322dcd77a011abfab24cbcd9b2))


## v2.17.0 (2025-06-19)


## v2.17.0-rc.7 (2025-06-18)

### Bug Fixes

- Fixes basic auth in metrics endpoint
  ([`f31d689`](https://github.com/crypticorn-ai/api-client/commit/f31d68974c29815e4443ac35989187506c5231b6))


## v2.17.0-rc.6 (2025-06-18)

### Features

- Support basic auth authentication for special usecases
  ([`1fca041`](https://github.com/crypticorn-ai/api-client/commit/1fca04140edac991257b9e1e43ebc0c3ad867454))


## v2.17.0-rc.5 (2025-06-08)

### Features

- Add new convenience classes for paginating, sorting and filtering query params
  ([`854e3bb`](https://github.com/crypticorn-ai/api-client/commit/854e3bb459a8d76352ee9d9172f9578a045d1452))

### Testing

- Update pagination tests
  ([`6378348`](https://github.com/crypticorn-ai/api-client/commit/6378348fa531e1d037f3373422b3ee7245ff2d08))


## v2.17.0-rc.4 (2025-06-06)

### Features

- Add `last` attribute and helper functions to paginated responses
  ([`fe29d0c`](https://github.com/crypticorn-ai/api-client/commit/fe29d0cb1da60c0fa2dc86f9f0ec54e8d035293d))

### Refactoring

- Add message to invalid_bearer exception
  ([`5578140`](https://github.com/crypticorn-ai/api-client/commit/557814099f6c37ce015c0ad8e5989266f332e834))

### Testing

- Update websocket authentication test
  ([`4f727d5`](https://github.com/crypticorn-ai/api-client/commit/4f727d545ab7275e7f3dc8e45b1ed2f0270e4038))


## v2.17.0-rc.3 (2025-06-05)

### Bug Fixes

- Fixes bearer auth in websocket
  ([`cb2f5f0`](https://github.com/crypticorn-ai/api-client/commit/cb2f5f07be25b8009f734de0d4bfdd4dd8b5c357))


## v2.17.0-rc.2 (2025-06-05)

### Documentation

- Document SyncClient support
  ([`8935d22`](https://github.com/crypticorn-ai/api-client/commit/8935d221afe6cb6da2529a05341e104b98bb9fbb))

### Features

- Add support for pagination, sorting and filtering query parameters
  ([`3afcf2b`](https://github.com/crypticorn-ai/api-client/commit/3afcf2bb8eff65a1c38c738f19e7480550f91798))

- Add support for synchronous usage with `SyncClient`. Both API clients are compatible with each
  other.
  ([`02e7622`](https://github.com/crypticorn-ai/api-client/commit/02e7622669bd590a853b12c9aa10183db06a73f1))

- Deprecate ApiClient for Async and SyncClient
  ([`a00b450`](https://github.com/crypticorn-ai/api-client/commit/a00b4502197fb2287aca893042d197d5f9811076))

### Testing

- Improve tests for pagination query params
  ([`de1f82a`](https://github.com/crypticorn-ai/api-client/commit/de1f82ae6f5461e172459ec4558dd29c0b2646ad))


## v2.17.0-rc.1 (2025-06-01)

### Features

- Add metrics router
  ([`9b4a9bd`](https://github.com/crypticorn-ai/api-client/commit/9b4a9bd33e16d70d4338f7d458e2d405cb1d22dd))


## v2.16.0 (2025-05-31)

### Features

- Add new scope for DEX AI Signals
  ([`8b566f1`](https://github.com/crypticorn-ai/api-client/commit/8b566f1203268bfa898e9b03e32468f4611ebccc))

### Refactoring

- Make order field in pagination model optional and improve the data validation
  ([`d3e3a6f`](https://github.com/crypticorn-ai/api-client/commit/d3e3a6f8e1752f38ab51d1fbc74d976968ef3c1c))

### Testing

- Update pagination tests
  ([`1692b8d`](https://github.com/crypticorn-ai/api-client/commit/1692b8d02c99c9592c19e612c82ed128de95213d))


## v2.15.0 (2025-05-27)

### Features

- Deprecate `InternalExchange` and move enum members to `Exchange`
  ([`5a4cea7`](https://github.com/crypticorn-ai/api-client/commit/5a4cea7695f862a2bc66bf921749f973117452cb))


## v2.14.0 (2025-05-26)

### Bug Fixes

- Fixes error code value
  ([`182d4d7`](https://github.com/crypticorn-ai/api-client/commit/182d4d7a92289b66914816a90e707739dba4af1c))

### Continuous Integration

- Cleanup on failure in release step
  ([`dff5ee4`](https://github.com/crypticorn-ai/api-client/commit/dff5ee4b25832ed8b6944213325e7a6d658a2491))

### Features

- Allow custom http client injection
  ([`1a4cd0c`](https://github.com/crypticorn-ai/api-client/commit/1a4cd0cdd68d39a950f547d22721409e022c896a))


## v2.13.3 (2025-05-26)

### Bug Fixes

- Fixes logging import error
  ([`5df42ef`](https://github.com/crypticorn-ai/api-client/commit/5df42ef9835a397ed6162dcb1c1ad4ab67badd4e))


## v2.13.2 (2025-05-26)

### Bug Fixes

- Temporary fix disabling the custom http session
  ([`613fc6f`](https://github.com/crypticorn-ai/api-client/commit/613fc6ff4d55fea322839cb879871a57c9fbc8d3))


## v2.13.1 (2025-05-26)

### Bug Fixes

- Update error code levels and types
  ([`9266c4b`](https://github.com/crypticorn-ai/api-client/commit/9266c4bc85adb879ab3b978ce7835a192147a825))

### Performance Improvements

- Decrease client startup time by using a shared http session across all subclients
  ([`dd41a60`](https://github.com/crypticorn-ai/api-client/commit/dd41a6079bd6568e074cbaebb1d4eda629a9b179))

centralize aiohttp.ClientSession in ApiClient

### Refactoring

- Return specific exceptions for api key / bearer only endpoints
  ([`52c77ce`](https://github.com/crypticorn-ai/api-client/commit/52c77ce73e880bdc08394a3f754c7f9bf0f81e6d))


## v2.13.0 (2025-05-23)

### Features

- New endpoint in metrics client (get symbol mappings for any pair)
  ([`a1f3b6a`](https://github.com/crypticorn-ai/api-client/commit/a1f3b6a31df3d8e6c148fa087d6ab158842c82dc))


## v2.12.1 (2025-05-22)

### Bug Fixes

- New error codes
  ([`d499bc8`](https://github.com/crypticorn-ai/api-client/commit/d499bc853c695da19aa5671ff786c27dcdd52fbf))


## v2.12.0 (2025-05-21)

### Features

- Adding custom crypticorn exception for internal usage
  ([`d63e166`](https://github.com/crypticorn-ai/api-client/commit/d63e16615b656128ac41ba921edf4d92aba1390f))


## v2.11.9 (2025-05-18)

### Bug Fixes

- Update status code on actions endpoints
  ([`0c1ff41`](https://github.com/crypticorn-ai/api-client/commit/0c1ff417c1bc976cb63537c5ab0ba127585e46d4))


## v2.11.8 (2025-05-18)

### Bug Fixes

- New error code `object_locked`
  ([`d2c79a1`](https://github.com/crypticorn-ai/api-client/commit/d2c79a1c8e77c5801981b5fe2c4f0c99d9ef0943))


## v2.11.7 (2025-05-18)

### Bug Fixes

- Add stricter data validation on trade api
  ([`e174a85`](https://github.com/crypticorn-ai/api-client/commit/e174a85e023634c0fc23679c1778e5e074c2ed07))


## v2.11.6 (2025-05-17)

### Bug Fixes

- Add hyperliquid to trading exchange
  ([`2ed06bc`](https://github.com/crypticorn-ai/api-client/commit/2ed06bc2ff4b07eda022af06954bd817975214be))


## v2.11.5 (2025-05-15)

### Bug Fixes

- Klines OHLCV response fields can be None
  ([`2c10e38`](https://github.com/crypticorn-ai/api-client/commit/2c10e38b4cd1f5304f276978b658a619e4cec171))


## v2.11.4 (2025-05-15)

### Bug Fixes

- Fixes dist build
  ([`3913bd7`](https://github.com/crypticorn-ai/api-client/commit/3913bd74a12d50727197efe72a68f36c9165c068))


## v2.11.3 (2025-05-15)

### Bug Fixes

- Fixes ci permission error copying static folder to dist
  ([`10f801b`](https://github.com/crypticorn-ai/api-client/commit/10f801b6f760c3f7de12fe830f9d3dc6895dde67))


## v2.11.2 (2025-05-15)

### Bug Fixes

- Fixes ohlc dataframe response
  ([`a334782`](https://github.com/crypticorn-ai/api-client/commit/a33478251a80e6255a9d4c0a2c43d701403c3399))


## v2.11.1 (2025-05-15)

### Bug Fixes

- Fixes dataframe conversion for get_available_exchanges_fmt
  ([`4c85d67`](https://github.com/crypticorn-ai/api-client/commit/4c85d67386fbda1b50a237df10a10a8eb2fb3531))

### Build System

- Include static files in dist
  ([`1b07130`](https://github.com/crypticorn-ai/api-client/commit/1b071302cb2f15f086b7812152cde8d425c2de9d))

### Continuous Integration

- Run test only on dev/main
  ([`dcc59e1`](https://github.com/crypticorn-ai/api-client/commit/dcc59e16e8138761c76da0cc936db7738058ac19))

### Documentation

- Document scope structure
  ([`fe0dca0`](https://github.com/crypticorn-ai/api-client/commit/fe0dca0d41ce79d0c1809a3d457a52a182cf37c4))

- Update docstring example `configure` method
  ([`30f59b3`](https://github.com/crypticorn-ai/api-client/commit/30f59b37b5fe3ae8f22ee0a5e72e9a7274dee23c))

### Refactoring

- Make merge-env script template more robust
  ([`1314f71`](https://github.com/crypticorn-ai/api-client/commit/1314f718fd4299a37e55424b3ea14c573f746aeb))

### Testing

- Add expiration to test api keys
  ([`2e4044f`](https://github.com/crypticorn-ai/api-client/commit/2e4044f05caa2ae35fe9cadc05eeed8f65d0049b))


## v2.11.0 (2025-05-13)

### Bug Fixes

- Use strenum as backport for python < 3.11
  ([`a14589b`](https://github.com/crypticorn-ai/api-client/commit/a14589b7c70a07b2a896526ee373d1136e07c675))

### Continuous Integration

- Test on all supported python versions
  ([`63e8006`](https://github.com/crypticorn-ai/api-client/commit/63e8006d2e226ddcf139f5ce25bd7edfc9a99ca3))

### Features

- Add support for python 3.9
  ([`d4ca2d2`](https://github.com/crypticorn-ai/api-client/commit/d4ca2d2723091756b31a70c1d851c0ab746b9bde))

### Refactoring

- Update type annotations to use Union for compatibility
  ([`4476864`](https://github.com/crypticorn-ai/api-client/commit/4476864fc52be5516e2d187254669b28da6d9202))


## v2.10.3 (2025-05-12)

### Bug Fixes

- Improve market cap symbols df response
  ([`23fac22`](https://github.com/crypticorn-ai/api-client/commit/23fac222e0af61bb8663f99d058ef5f37a7a675a))


## v2.10.2 (2025-05-12)

### Bug Fixes

- Convert market metrics service models to use unix ts
  ([`d6c9564`](https://github.com/crypticorn-ai/api-client/commit/d6c95644aea7a239a8ffc91afb3d48db3f56b03c))

### Chores

- Add --url flag to client generation scripts
  ([`a8ebed2`](https://github.com/crypticorn-ai/api-client/commit/a8ebed2ded196ea132db236417c6c6962f4dbeb2))


## v2.10.1 (2025-05-12)

### Bug Fixes

- Fixes optional symbol in get_marketcap_symbols function
  ([`3522a09`](https://github.com/crypticorn-ai/api-client/commit/3522a097cb159d638c717b26f9d607e813d210a9))

### Build System

- Include static files in the structure in the distribution
  ([`eb87ab4`](https://github.com/crypticorn-ai/api-client/commit/eb87ab44edb7558b09835ffe092d4a4d9517b79d))

### Refactoring

- Remove usage of deprecated `ExcludeEnumMixin`
  ([`bf4f4fb`](https://github.com/crypticorn-ai/api-client/commit/bf4f4fb4dc092a9909a6e536c5e5455244e13aac))


## v2.10.0 (2025-05-09)

### Build System

- Include info .md files and license in distribution
  ([`3c3d065`](https://github.com/crypticorn-ai/api-client/commit/3c3d0655b67478f98d970e7ad218e8947b8a9ec0))

### Continuous Integration

- Fix typo in testing workflow
  ([`e0fd734`](https://github.com/crypticorn-ai/api-client/commit/e0fd73450efda0c41ed583a771e0b6774e6a8dbd))

- Properly read env vars
  ([`6d25286`](https://github.com/crypticorn-ai/api-client/commit/6d252865986b974789831e91cedd45e9a594ebbc))

- Update test workflow
  ([`97b7b8b`](https://github.com/crypticorn-ai/api-client/commit/97b7b8b76691e91d788030e603e2fc65ac7ba8c8))

### Features

- Add new init template to the CLI for generating a env merging script
  ([`7e3a71a`](https://github.com/crypticorn-ai/api-client/commit/7e3a71a0f67eceb1ab1f8545eeba0a390736e129))

- Add version command in the CLI (crypticorn version)
  ([`289eef4`](https://github.com/crypticorn-ai/api-client/commit/289eef48fa51f771c9b461206a93470f35ce2369))


## v2.9.0 (2025-05-08)

### Build System

- Add python-semantic-release as an dev dependency
  ([`72dfc09`](https://github.com/crypticorn-ai/api-client/commit/72dfc092b7b4fde231e6c62d3bcca33ec270bf30))

### Features

- Use regex pattern in /dependencies endpoint
  ([`7a7792f`](https://github.com/crypticorn-ai/api-client/commit/7a7792f33460b5fe4404d6f46ab680cca204a8f5))


## v2.9.0-rc.1 (2025-05-08)

### Bug Fixes

- Capture and format warnings in logging output
  ([`5a1d317`](https://github.com/crypticorn-ai/api-client/commit/5a1d31721507dae015e9d9568579e91b12906ee4))

- Use `contextlib.asynccontextmanager` for starlette lifespan
  ([`c253dd1`](https://github.com/crypticorn-ai/api-client/commit/c253dd133dff5073f355ed8f93c0be1814b739f2))

### Documentation

- Update docstrings and module descriptions
  ([`c80f306`](https://github.com/crypticorn-ai/api-client/commit/c80f30614641f09366ca3566295e9bce8eee828d))

### Features

- Add deprecation warnings in call and in-code support
  ([`b3100e6`](https://github.com/crypticorn-ai/api-client/commit/b3100e69874b8fca439778351c2834b5ae2b91b6))

- Provide default openapi tags from the status and admin router
  ([`e8ef966`](https://github.com/crypticorn-ai/api-client/commit/e8ef966bc9ee60a17ef8842a041d5e1800c32d93))


## v2.8.2 (2025-05-08)

### Bug Fixes

- Hotfix response type error
  ([`7cc14fc`](https://github.com/crypticorn-ai/api-client/commit/7cc14fcced66441d9e320ad754a164ca016cda26))


## v2.8.1 (2025-05-07)

### Bug Fixes

- Replace deprecatet pkg_resource with native importlib.metadata
  ([`e9c49e7`](https://github.com/crypticorn-ai/api-client/commit/e9c49e75a29fd4d5657772c091fa918776e7c480))


## v2.8.0 (2025-05-07)


## v2.8.0-rc.8 (2025-05-07)

### Bug Fixes

- Use root logger of the client with specific child logger as option
  ([`2f8cde2`](https://github.com/crypticorn-ai/api-client/commit/2f8cde2659f22704c5c4310f3ec9a07cbd1d4cef))


## v2.8.0-rc.7 (2025-05-07)

### Bug Fixes

- Pass args to the override function in hive data download
  ([`7bb3e29`](https://github.com/crypticorn-ai/api-client/commit/7bb3e2997f79da8e4e55b42a1a699a75fe1f985f))


## v2.8.0-rc.6 (2025-05-07)

### Bug Fixes

- Fixes logging file handler import error
  ([`0a9edb1`](https://github.com/crypticorn-ai/api-client/commit/0a9edb1ee3083ec98edc9529efa3158e69c4541c))


## v2.8.0-rc.5 (2025-05-07)

### Bug Fixes

- Fixes missing os import in logging
  ([`1670c9f`](https://github.com/crypticorn-ai/api-client/commit/1670c9f1afec1e772fdfaea0c6178c782c209889))

### Documentation

- Update documentation
  ([`0eba005`](https://github.com/crypticorn-ai/api-client/commit/0eba0058cf8cdd813d3b80eef8c72ca12a181399))


## v2.8.0-rc.4 (2025-05-05)

### Bug Fixes

- Remove @deprecated decorator from ExcludeEnumMixin to avoid enum inheritance error
  ([`3d8b63d`](https://github.com/crypticorn-ai/api-client/commit/3d8b63d638fa77045d2189fe099a6c2ca740c105))


## v2.8.0-rc.3 (2025-05-05)

### Bug Fixes

- Deprecate ExcludeEnumMixin
  ([`ae57fb2`](https://github.com/crypticorn-ai/api-client/commit/ae57fb22ff410432ce28a9c0af3a02fa9f51104f))


## v2.8.0-rc.2 (2025-05-05)

### Bug Fixes

- Add psutil as dependency
  ([`23cf77e`](https://github.com/crypticorn-ai/api-client/commit/23cf77ea002a2d6f8e31cd858a2dcc1890b8d8c1))

- Centralize cors middleware
  ([`e5aa2d6`](https://github.com/crypticorn-ai/api-client/commit/e5aa2d60254076848530a6d5b9a349058ee45ac7))

- Run logging configuration in init of the library
  ([`8b725e1`](https://github.com/crypticorn-ai/api-client/commit/8b725e18154d184c8593b8de086b0a789b6e180c))

### Features

- Provide lifespan event for fastapi apps to configure logging on startup
  ([`9a2e1c4`](https://github.com/crypticorn-ai/api-client/commit/9a2e1c45d87ad1581c0e1646689eba6ca0876564))


## v2.8.0-rc.1 (2025-05-04)

### Features

- Add router with admin endpoints
  ([`0d38178`](https://github.com/crypticorn-ai/api-client/commit/0d381784f91cab776ca1ee3b8407433dae4421c3))

- Configure formatted logging
  ([`f8c35e9`](https://github.com/crypticorn-ai/api-client/commit/f8c35e900bcf4a279cc8e046e58935ec5c5c62ee))


## v2.7.5 (2025-05-04)

### Bug Fixes

- Log errors and exceptions
  ([`578d6d3`](https://github.com/crypticorn-ai/api-client/commit/578d6d3176e07a7d4cb87e79617d67ab2e1d62de))

### Build System

- Include changelog in build
  ([`a78acb7`](https://github.com/crypticorn-ai/api-client/commit/a78acb7a18a957cfefa8e64ce593b13ddcd4fae7))


## v2.7.4 (2025-05-04)

### Bug Fixes

- Include cli templates in build
  ([`8d46b4c`](https://github.com/crypticorn-ai/api-client/commit/8d46b4c6bc6bd413a86d1661a4ae9647ed66755c))

### Documentation

- Update README and add license
  ([`1876008`](https://github.com/crypticorn-ai/api-client/commit/187600869b9248aef2b66e881711ddfb96a01538))


## v2.7.3 (2025-05-03)

### Bug Fixes

- Fixes attribute bug in http exception handling
  ([`a90b593`](https://github.com/crypticorn-ai/api-client/commit/a90b593bfa3e08a1703a7e2e1fc8a7bb8ac456e3))


## v2.7.2 (2025-05-03)

### Bug Fixes

- Add write:pay:now to default scopes
  ([`8375248`](https://github.com/crypticorn-ai/api-client/commit/83752484e3570a1f39eacda4223100d7f3fbadd0))


## v2.7.1 (2025-05-02)

### Bug Fixes

- Use pydantic instead of json response in api wrappers
  ([`ddd623b`](https://github.com/crypticorn-ai/api-client/commit/ddd623b28cb542ae6dd1bab02044c682cac206af))


## v2.7.0 (2025-05-01)

### Features

- Add download functionality for hive download data endpoint
  ([`ee09d17`](https://github.com/crypticorn-ai/api-client/commit/ee09d177a28f3879e549eb3044c24b5e6197a528))


## v2.6.0 (2025-04-30)

### Features

- Add admin flag on auth verify response and user by username endpoint
  ([`3f27fba`](https://github.com/crypticorn-ai/api-client/commit/3f27fba655e15a42a947ad1c67bcf4319c3daed6))

- Add common pagination query parameters
  ([`4157137`](https://github.com/crypticorn-ai/api-client/commit/415713725541bb4a180f11de12fea2c3071c5f55))

- Add common webscoket error handling
  ([`334a450`](https://github.com/crypticorn-ai/api-client/commit/334a45054797616fdd8bb917381e189bb64e4678))

### Testing

- Add api key generation and remove duplicate tests
  ([`d60a890`](https://github.com/crypticorn-ai/api-client/commit/d60a89071fe7bc25025fbdf2298cb560d9fbdfb8))


## v2.5.3 (2025-04-29)

### Bug Fixes

- Use ExceptionContent in throw utilities
  ([`b38ebf1`](https://github.com/crypticorn-ai/api-client/commit/b38ebf1443d1df126f7e1014b5c25f1e17f56fdc))


## v2.5.2 (2025-04-29)

### Bug Fixes

- Only allow type ApiError in throw utility functions
  ([`7604342`](https://github.com/crypticorn-ai/api-client/commit/7604342baa6dd2bee816ae446dfcc08edb298ddb))

### Build System

- Clean generated code before regenerating
  ([`b563024`](https://github.com/crypticorn-ai/api-client/commit/b56302497e79e2a64e7403d15a0f3d3bd3233b63))


## v2.5.1 (2025-04-27)

### Bug Fixes

- Integrate exception handling in auth handler
  ([`b7835ef`](https://github.com/crypticorn-ai/api-client/commit/b7835efef54adbd021ecce27c002c5e5501cb99c))

### Build System

- Exclude shared classes and enums from openapi to reduce duplication upon client generation
  ([`1987864`](https://github.com/crypticorn-ai/api-client/commit/1987864392397d7ee74ddb9ecbfb61c6d83134dc))

### Continuous Integration

- Run codecov workflow on push and pull request
  ([`cf2bc16`](https://github.com/crypticorn-ai/api-client/commit/cf2bc165d04b855839812ea626a3647b17a91458))

### Refactoring

- Improve sub package registration in ApiClient to reduce redundance
  ([`bdea044`](https://github.com/crypticorn-ai/api-client/commit/bdea044a6bc5180daed59b9a504866d2f519ae05))

- Integrate custom exception handling in auth handler
  ([`3f997e2`](https://github.com/crypticorn-ai/api-client/commit/3f997e23c1493296deaab23063b709d08702d5af))

### Testing

- Add jwt generation function
  ([`c2bc90f`](https://github.com/crypticorn-ai/api-client/commit/c2bc90fb878656642787755330a99c6b9056f14c))

- Update exception assertions with latest changes auth handler
  ([`4c220e5`](https://github.com/crypticorn-ai/api-client/commit/4c220e5bd31d1a7fd64d0f302044acfd4d4927e9))


## v2.5.0 (2025-04-26)


## v2.5.0-rc.5 (2025-04-26)

### Features

- Add details field to `ExceptionContent` to support additional details about the error
  ([`3ae6bc5`](https://github.com/crypticorn-ai/api-client/commit/3ae6bc57ae4e1e8a23c46511cdc5bf9c1eadc40d))

### Refactoring

- Rename exception class names
  ([`7f50e11`](https://github.com/crypticorn-ai/api-client/commit/7f50e114ceee596dcf3e25d3decfe78c849ad22e))


## v2.5.0-rc.4 (2025-04-26)

### Bug Fixes

- Remove wrong media type from `exception_response`
  ([`34920f0`](https://github.com/crypticorn-ai/api-client/commit/34920f0a51eded25e64324654d711e8716ee707c))


## v2.5.0-rc.3 (2025-04-26)

### Bug Fixes

- Fixes TypeError bug in deprecated decorator
  ([`4344581`](https://github.com/crypticorn-ai/api-client/commit/4344581f2737377334d2ab0203c8872e0acdfadb))

### Features

- Add exception handler and improve custom exception
  ([`64c05ea`](https://github.com/crypticorn-ai/api-client/commit/64c05eafd011556b49786034d58a4de264438bfd))


## v2.5.0-rc.2 (2025-04-25)

### Bug Fixes

- Enforce stricter types on Http Exception and improve descriptions and doc string
  ([`0941780`](https://github.com/crypticorn-ai/api-client/commit/094178099ca1d01d763f41cce6ac898cbc77a9a3))


## v2.5.0-rc.1 (2025-04-25)

### Build System

- Update generation script to catch fallback if local server is not running
  ([`b5e9a16`](https://github.com/crypticorn-ai/api-client/commit/b5e9a16092c836bea38657b7ddab252945696848))

### Chores

- Deprecate is_equal function
  ([`b3b3094`](https://github.com/crypticorn-ai/api-client/commit/b3b309428dc078673a5b1718a7075855bce0c098))

### Features

- Add custom Http Exception class with shared error codes
  ([`aa0d851`](https://github.com/crypticorn-ai/api-client/commit/aa0d8515936ea65951608a9704f8d840069ac15d))


## v2.4.7 (2025-04-17)

### Bug Fixes

- Raise custom WebsockeError in ws auth dependencies
  ([`94f8b62`](https://github.com/crypticorn-ai/api-client/commit/94f8b62593d3f44785b11812102c3a4ab9195073))

### Performance Improvements

- Make pandas an optional dependency to decrease package size
  ([`cb942c7`](https://github.com/crypticorn-ai/api-client/commit/cb942c74d5d7836f9cab1beb2b1d5ee6a9be4d4e))


## v2.4.6 (2025-04-13)

### Bug Fixes

- Fixes config override bug
  ([`58c096b`](https://github.com/crypticorn-ai/api-client/commit/58c096b98a738c2c318768bae9f28ddb100fe127))

### Documentation

- Extend usage section
  ([`2887872`](https://github.com/crypticorn-ai/api-client/commit/28878720eeb0ad7461165402c5521258c1c7dc0e))


## v2.4.5 (2025-04-13)

### Bug Fixes

- Fixes fallback bug with pydantic
  ([`70d1257`](https://github.com/crypticorn-ai/api-client/commit/70d125723c7e707f765892270e6aa6977b5b25a5))


## v2.4.4 (2025-04-12)

### Bug Fixes

- Auth fixes on auth module
  ([`7c3ed5d`](https://github.com/crypticorn-ai/api-client/commit/7c3ed5d460e464939716361014514baff50d380d))

### Documentation

- Update advanced usage section
  ([`1c804bf`](https://github.com/crypticorn-ai/api-client/commit/1c804bf6eddceb19c31a553c1ff98b31fdd8cbc0))


## v2.4.3 (2025-04-12)

### Bug Fixes

- Fix utils import
  ([`29cc346`](https://github.com/crypticorn-ai/api-client/commit/29cc346c2ff835f8732644fbe21aadf62153c1d0))


## v2.4.2 (2025-04-12)

### Bug Fixes

- Add global utils and add http error mapping
  ([`c3ce565`](https://github.com/crypticorn-ai/api-client/commit/c3ce565446535038f196f65b9fdf276a6ce71563))


## v2.4.1 (2025-04-12)

### Bug Fixes

- Add market metrics scopes
  ([`2dc0b4f`](https://github.com/crypticorn-ai/api-client/commit/2dc0b4f1761d5bae07c946448a820d1fc9814288))

### Documentation

- Update structure section
  ([`cc77abc`](https://github.com/crypticorn-ai/api-client/commit/cc77abc19b5813e335356f4539654e04b8ba2014))


## v2.4.0 (2025-04-12)

### Features

- Add enum fallbacks, enum validation mixin and enum tests
  ([`63bd61c`](https://github.com/crypticorn-ai/api-client/commit/63bd61cd826f9de1aec40d5f877d82126b59fbf8))

- Start cli support for initializing files from templates
  ([`5411d12`](https://github.com/crypticorn-ai/api-client/commit/5411d12704605e6d6af46477ff74e1ac44abd259))


## v2.3.0 (2025-04-11)

### Features

- Add exchange and market enums
  ([`8ad2d7d`](https://github.com/crypticorn-ai/api-client/commit/8ad2d7dc982261f3e710c3e61755ea9613d982c3))


## v2.2.3 (2025-04-11)

### Bug Fixes

- Update error codes
  ([`3121fb0`](https://github.com/crypticorn-ai/api-client/commit/3121fb0bb4d05a6d62083d806fbc636761254448))


## v2.2.2 (2025-04-09)

### Bug Fixes

- Refactor generated model name by partial_model and add to init file
  ([`e663848`](https://github.com/crypticorn-ai/api-client/commit/e6638483bdeb01121749b579268493c7c67227dc))


## v2.2.1 (2025-04-09)

### Bug Fixes

- Add pydantic decorator that makes all fields of a model optional
  ([`1ae4432`](https://github.com/crypticorn-ai/api-client/commit/1ae44325194be3ca86eb72be5d3edc2442dd00cc))


## v2.2.0 (2025-04-09)

### Bug Fixes

- Fix import issues (fixes #22) and add auth module to main client
  ([`7f3f7c2`](https://github.com/crypticorn-ai/api-client/commit/7f3f7c2120af053b916aaa045444331998986f7d))

### Documentation

- Update README with configuration and response type sections
  ([`a9fbccf`](https://github.com/crypticorn-ai/api-client/commit/a9fbccfed254573d3e62332901704f39d8a6777f))

### Features

- Add module based configuration options for the client
  ([`553400c`](https://github.com/crypticorn-ai/api-client/commit/553400c642d3da4459daa4fa9b56588e9f519581))


## v2.1.6 (2025-04-08)

### Bug Fixes

- Add market metrics module
  ([`2954702`](https://github.com/crypticorn-ai/api-client/commit/29547025a0226bca1b9da9cfff5c89d3ed30f497))


## v2.1.5 (2025-04-08)

### Bug Fixes

- Update auth and trade module
  ([`df936b6`](https://github.com/crypticorn-ai/api-client/commit/df936b6eb76179a3eac6d7997c82ef30e74de860))


## v2.1.4 (2025-04-08)

### Bug Fixes

- Refactor api errors
  ([`885a20e`](https://github.com/crypticorn-ai/api-client/commit/885a20ec839dcf14fb4ec8d946cea76dcb15a65e))


## v2.1.3 (2025-04-08)

### Bug Fixes

- Use SecurityScopes class instead of list[Scope]
  ([`b41c718`](https://github.com/crypticorn-ai/api-client/commit/b41c718acc108e05b307abb399137c2fc30e56fd))


## v2.1.2 (2025-04-08)

### Bug Fixes

- Allow scopes to be set as strings
  ([`600babb`](https://github.com/crypticorn-ai/api-client/commit/600babb87c93aeecdc42aa19ebff1076a76404ea))


## v2.1.1 (2025-04-08)

### Bug Fixes

- Remove three unused scopes
  ([`3167308`](https://github.com/crypticorn-ai/api-client/commit/3167308b3df0c68b8e4c134841b437f40315a8e9))


## v2.1.0 (2025-04-07)

### Features

- Add api key authorization and websocket auth support
  ([`adeb8bd`](https://github.com/crypticorn-ai/api-client/commit/adeb8bdf42ed3da1b63b430f291e920e97d62d14))

### Refactoring

- Rename scopes and make requirements more strict
  ([`abf53a6`](https://github.com/crypticorn-ai/api-client/commit/abf53a6de46703a3ac2b0c66c101ec58ae8928f2))


## v2.0.1 (2025-04-06)

### Bug Fixes

- Refactor Scopes and Exception handling in auth client
  ([`8e9a64a`](https://github.com/crypticorn-ai/api-client/commit/8e9a64aa091cc3c840230ad2a7167c98426ae5c9))

### Build System

- Fix ci syntax and ssh errors
  ([`9ecfaa4`](https://github.com/crypticorn-ai/api-client/commit/9ecfaa4f09dfa4ae1667f9c1b9307d2623288f5f))

- Separate ci and update package config and deps
  ([`5367f2a`](https://github.com/crypticorn-ai/api-client/commit/5367f2a79028ed1f5e2c05ddded91a9ddbd0d9fa))

- Update ci
  ([`799fd96`](https://github.com/crypticorn-ai/api-client/commit/799fd962529b0120b290c3f5c253e9050b40a41b))

### Documentation

- Update Readme
  ([`39825b1`](https://github.com/crypticorn-ai/api-client/commit/39825b1506c2d5663ae8eecc6f73f8d6bed5692e))


## v2.0.0 (2025-04-06)

### Build System

- Add psr build_command
  ([`b661846`](https://github.com/crypticorn-ai/api-client/commit/b6618464c7d7727d34ab4a448f2e0104fcf4f3cc))

- Fix ci-cd
  ([`6edcb36`](https://github.com/crypticorn-ai/api-client/commit/6edcb3611673f191ec482e9d40614c7c2d2b59f3))

- Fix signing error in ci
  ([`0dcbf22`](https://github.com/crypticorn-ai/api-client/commit/0dcbf22892dbc17297cf9b91b35d62ec205a76ea))

- Fixes pypi packages dir
  ([`a25a458`](https://github.com/crypticorn-ai/api-client/commit/a25a4580c6a656e30d55b52c837480b833cb9aab))

- Update ci cd and configure PSR
  ([`e5d6fa5`](https://github.com/crypticorn-ai/api-client/commit/e5d6fa5d2ff4355f59fd4c92e4b9bed77fcae2d8))

BREAKING CHANGE: add several more backend api clients and restructure the modules


## v1.0.0 (2024-11-27)

### Continuous Integration

- Trigger workflow on PRs and changes to public folder (close #4)
  ([`08b9317`](https://github.com/crypticorn-ai/api-client/commit/08b931780ac872c6034883cd5ab83d2c7b380414))

### Features

- Add get Economics News
  ([`81575b1`](https://github.com/crypticorn-ai/api-client/commit/81575b18a7c925c5dafe18bd9e15807a282134e3))

- Add get Economics News
  ([`ccbfb7a`](https://github.com/crypticorn-ai/api-client/commit/ccbfb7a3d857ff5d531ec06f3b9df05b63f8dbf3))

- Add get Economics News
  ([`bc6574d`](https://github.com/crypticorn-ai/api-client/commit/bc6574dcadcdc9d05e860fde0aa285a4e7dcba32))
