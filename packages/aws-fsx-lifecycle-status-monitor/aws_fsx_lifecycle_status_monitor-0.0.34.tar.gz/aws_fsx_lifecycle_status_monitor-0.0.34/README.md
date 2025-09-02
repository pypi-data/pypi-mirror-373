# AWS FSx Life Cycle Status Monitor

The documentation is available [here](https://stefanfreitag.github.io/AWS-FSx-Lifecycle-Status-Monitor/).

## How to run

### Tests

* Execute the unit tests under `./test`

  ```shell
  yarn test
  ```
* Execute integration tests under `.integ-tests`

  ```shell
  yarn integ-runner --directory ./integ-tests  --update-on-failed --parallel-regions eu-central-1
  ```
