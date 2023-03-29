# Intro

This repository contains code and measured data for evaluation of testing frameworks for Ethereum Blockchain Applications.

In this repository you will find the following:
* `test_projects.py`: Python script to run the test projects and measure times
* `test_tests_config.json`: JSON file containing the configuration for the test projects
* `test_results.csv`: CSV file containing the measured times
* `v3_core`: Directory with rewritten tests for [v3-core](https://github.com/Uniswap/v3-core) 
* `README.md`: This readme

# Methodology

Testing was done with 4 different testing frameworks, namely Woke, Brownie and Ape which are frameworks written in Python and Hardhat+Ethers.js which was used in the original tests.
Three different development chains, namely Anvil, Ganache and Hardhat.
As for the tests, popular Uniswap-v3 project and its [v3-core](https://github.com/Uniswap/v3-core)  was chosen and it's tests partly rewritten and repurposed for each of the python resulting in 271 tests.

Tests were conducted on a VM n2d-standard-4 instance in Google Cloud, equipped with four cores of AMD Rome, 16 GB RAM, and an HDD disk. The system ran a Debian OS with kernel version 5.10.162-1 and Python 3.10.11. All tests were executed under similar load conditions on the virtual machine.

All Python frameworks have their requirements files in `v3_core` directory. As for the TypeScript tests, packages in `package.json` were installed.

# Results

The results of the tests in seconds are shown in the following table:

|         | Brownie | Woke   | Ape    | Hardhat & Ethers.js |
|---------|---------|--------|--------|---------------------|
| Anvil   | 33.341  | 3.520  | 51.285 | 11.627              |
| Ganache | 49.467  | 16.467 | 68.222 | 112.636             |
| Hardhat | 53.267  | 21.176 | 67.831 | 18.315              |

# Necessary modifications

It was necessary to modify Brownie's `network\rpc\anvil.py` to allow us to specify two additional arguments for Anvil and also to fix an issue where PIPE output was not being read correctly thus resulting in hangs when deploying large contracts. The modified file is included in this repository as `modified_anvil.py` in the `v3_core` directory.
