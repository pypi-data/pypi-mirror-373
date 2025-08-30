# AWS Infrastructure with CDKTF (Python)

This project uses the **Cloud Development Kit for Terraform (CDKTF)** with **Python** to define and deploy AWS infrastructure using named AWS profiles via `~/.aws/credentials` and `~/.aws/config`.

---

## ✅ Prerequisites

### 1. Install Required Tools

Make sure the following tools are installed:

* **Node.js** (v16 or later)
* **npm**
* **Terraform CLI**
* **Python 3.7+**
* **AWS CLI**

#### macOS Example:

```bash
brew install node
brew install terraform
brew install python
brew install awscli
```

### 2. Install CDKTF CLI

```bash
npm install -g cdktf-cli
```

### 3a. Configure AWS CLI (Option 1 - Use AWS Provided Tooling)

```bash
aws configure --profile myprofile
```

This creates or updates the following files:

`~/.aws/credentials`:

```ini
[myprofile]
aws_access_key_id=YOUR_ACCESS_KEY
aws_secret_access_key=YOUR_SECRET_KEY
```

`~/.aws/config`:

```ini
[profile myprofile]
region=us-west-2
output=json
```


### 3b. Configure AWS CLI (Option 2 - Use Open Source AWS Login - Recommended)


#### 3b - 1. Clone the code repo from Fahad Zain Jawaid
```bash
git clone https://github.com/fahadzainjawaid/awsIdentityTools
```

You can follow the ReadMe on the repo above to get latest usage and setup guides.

---

## 🚀 Getting Started

### 1. Install the package

```bash
pip install pip install BBAWSLightsailMiniV1a
```

### 2. Set Up Python Environment & Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
export PIPENV_VERBOSITY=-1
pip install -r requirements.txt
```

### 3. Install AWS Provider Bindings

```bash
cdktf get
```

### 4. Synthesize Terraform Configuration

```bash
cdktf synth
```

### 5. Review the Plan

```bash
cdktf plan
```

### 6. Deploy the Infrastructure

```bash
cdktf deploy
```

### 7. Destroy the Infrastructure (if needed)

```bash
cdktf destroy
```

## 🛠 Useful Commands

| Command         | Description                     |
| --------------- | ------------------------------- |
| `cdktf get`     | Install provider bindings       |
| `cdktf synth`   | Generate Terraform JSON config  |
| `cdktf plan`    | Preview planned changes         |
| `cdktf deploy`  | Deploy infrastructure to AWS    |
| `cdktf destroy` | Destroy deployed infrastructure |

---

## 📁 .gitignore Suggestions

```gitignore
.venv/
cdktf.out/
.terraform/
__pycache__/
*.pyc
```

---

## 📝 Notes

* To install additional Python packages:

  ```bash
  pip install <package>
  pip freeze > requirements.txt
  ```

* To suppress pipenv verbosity in environments where pipenv is used:

  ```bash
  export PIPENV_VERBOSITY=-1
  ```

---

## 📚 References

* [CDK for Terraform Documentation](https://developer.hashicorp.com/terraform/cdktf)
* [AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
