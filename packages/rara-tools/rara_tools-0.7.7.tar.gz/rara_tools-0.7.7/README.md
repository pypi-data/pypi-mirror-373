# RaRa Tools

![Py3.10](https://img.shields.io/badge/python-3.10-green.svg)
![Py3.11](https://img.shields.io/badge/python-3.11-green.svg)
![Py3.12](https://img.shields.io/badge/python-3.12-green.svg)

**`rara-tools`** is a Python library containing various generic tools used by components of Kata.

---

## ✨ Features

- Elasticsearch index & document operations
- S3 file management operations
- Task reporting to Core API
- Converting SIERRA API responses to Pymarc compatible JSON

---

## ⚡ Quick Start

Get started with `rara-tools` in just a few steps:

1. **Install the Package**  
   Ensure you're using Python 3.10 or above, then run:

   ```bash
   pip install rara-tools
   ```

2. **Import and Use**  
   Example usage to download a folder from S3:

   ```python
   from rara_tools.s3 import S3Files

   s3 = S3Files(
        url="your-s3-address",
        access_key = "xxx",
        secret_key = "yyy",
        bucket = "my-sad-bucket"
   )

   s3.download("my-folder-in-s3")
   ```

---

## ⚙️ Installation Guide

Follow the steps below to install the `rara-tools` package, either via `pip` or locally.

---

### Installation via `pip`

<details><summary>Click to expand</summary>

1. **Set Up Your Python Environment**  
   Create or activate a Python environment using Python **3.10** or above.

2. **Install the Package**  
    Run the following command:

   ```bash
   pip install rara-tools
   ```

   </details>

---

### Local Installation

Follow these steps to install the `rara-tools` package locally:

<details><summary>Click to expand</summary>

1. **Clone the Repository**  
   Clone the repository and navigate into it:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above. E.g:

   ```bash
   conda create -n py310 python==3.10
   conda activate py310
   ```

3. **Install Build Package**  
   Install the `build` package to enable local builds:

   ```bash
   pip install build
   ```

4. **Build the Package**  
   Run the following command inside the repository:

   ```bash
   python -m build
   ```

5. **Install the Package**  
   Install the built package locally:

   ```bash
   pip install .
   ```

</details>

---

## 🚀 Testing Guide

Follow these steps to test the `rara-tools` package.

### How to Test

<details><summary>Click to expand</summary>

1. **Clone the Repository**  
   Clone the repository and navigate into it:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Set Up Python Environment**  
   Create or activate a Python environment using Python 3.10 or above.

3. **Install Build Package**  
   Install the `build` package:

   ```bash
   pip install build
   ```

4. **Build the Package**  
   Build the package inside the repository:

   ```bash
   python -m build
   ```

5. **Install with Testing Dependencies**  
   Install the package along with its testing dependencies:

   ```bash
   pip install .[testing]
   ```

6. **Run Tests**  
   Run the test suite from the repository root:

   ```bash
   python -m pytest -v tests
   ```

---

</details>
