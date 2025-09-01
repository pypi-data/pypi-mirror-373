# 🌍 DigitalMeve — The .MEVE Standard  

![Quality](https://github.com/BACOUL/digitalmeve/actions/workflows/quality.yml/badge.svg?branch=main&t=202508301200)
[![Tests](https://github.com/BACOUL/digitalmeve/actions/workflows/tests.yml/badge.svg?branch=main&t=202508301200)](https://github.com/BACOUL/digitalmeve/actions/workflows/tests.yml)
[![publish](https://github.com/BACOUL/digitalmeve/actions/workflows/publish.yml/badge.svg?branch=main&v=1)](https://github.com/BACOUL/digitalmeve/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/digitalmeve.svg?cacheSeconds=600)](https://pypi.org/project/digitalmeve/)
[![Python versions](https://img.shields.io/pypi/pyversions/digitalmeve.svg?cacheSeconds=600)](https://pypi.org/project/digitalmeve/)
[![Downloads](https://static.pepy.tech/badge/digitalmeve/month)](https://pepy.tech/project/digitalmeve)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)  

---

## ✅ Status  

- Current version: **1.6.1**  
- Release page: [Releases](../../releases)  
- Tests: ![Tests](https://github.com/BACOUL/digitalmeve/actions/workflows/tests.yml/badge.svg?branch=main&t=202508301200)

## 📑 Table of Contents  

- [🚀 Vision](#-vision)  
- [🔑 Levels of Certification](#-levels-of-certification)  
- [📂 Format Specification — MEVE/1](#-format-specification--meve1)  
- [🛡 Security](#-security)  
- [📊 Use Cases](#-use-cases)  
- [📜 Roadmap](#-roadmap)  
- [📢 Communication](#-communication)  
- [⚖ License](#-license)  
- [🛠 Contributing](#-contributing)  
- [✅ Status](#-status)  
- [📚 Documentation](#-documentation)  
- [🌟 Final Goal](#-final-goal)---

**The first universal format to prove, certify and verify the authenticity of any digital document.**  
DigitalMeve introduces `.meve` (Memory Verified), a simple and universal way to **timestamp, hash, and certify documents**.  

---

## 🚀 Vision  

DigitalMeve creates a new universal certification format: **`.meve` (Memory Verified)**.  
A lightweight and human-readable file proving in **2 seconds**:  

1. The existence of a document at a given date.  
2. The integrity of the document (via SHA-256 hash).  
3. The authenticity of the issuer (Personal / Pro / Official).  

**Goal**: make `.meve` the **“PDF of digital proof”** worldwide.  

---

## 🔑 Levels of Certification  

- **Personal** → Self-certification (existence proof only).  
- **Pro** → Email verified (identity linked to a real professional).  
- **Official** → DNS verified / institution (official certification).  

⚡ Certification level is always **computed automatically by DigitalMeve**, never declared manually. Impossible to fake.  

---

## 📂 Format Specification — MEVE/1  

Example of `.meve` structure:

MEVE/1 Status: Official | Pro | Personal Issuer: <identity> Certified: DigitalMeve (dns|email|self) Time: <UTC timestamp> Hash-SHA256: <document hash> ID: <short unique code> Signature: <Ed25519 base64> Meta: <filename> • <size bytes> • <mime> Doc-Ref: <optional internal reference>
---

## 🛡 Security  

- **Tamper-proof**: if the document changes (even one comma), the hash changes and the `.meve` becomes invalid.  
- **Metadata embedding**: JSON proof can be embedded in the file metadata OR generated as a sidecar `.meve.json`.  
- **Scalable**: fallback `.meve.json` for large files (>50 MB).  
- **Detection**: verification instantly detects any fraud attempt.  

---

## 📊 Use Cases  

### 🧑‍💻 Individuals  
- Proof of creation (art, photos, manuscripts).  
- Secure timestamp (testament, private agreements).  
- Evidence of damages (video/photo insurance).  

### 👔 Professionals  
- Certified invoices, quotes, contracts.  
- Proof of authorship (designs, code).  
- Intellectual property pre-proof (before patents).  

### 🏛 Institutions  
- Universities → certified diplomas.  
- Governments → official documents.  
- Courts & notaries → judgments, legal contracts.  

---

## 📜 Roadmap  

### Phase 1 (MVP, 1–2 months)  
- Generator `.meve` (site + script).  
- Verifier `.meve` (drag & drop site).  
- SHA-256 hash + UTC timestamp + Ed25519 signature.  

### Phase 2 (6 months)  
- Pro email verification.  
- Official DNS verification.  
- Export certified PDF with DigitalMeve footer.  
- Public API for third-party integration.  

### Phase 3 (1–2 years)  
- International standardization (ISO/AFNOR).  
- Integrations in ERP / CRM / Universities.  
- Large-scale adoption.  

---

## 📢 Communication  

**Slogan**:  
👉 *“DigitalMeve — The first online platform that certifies and verifies the authenticity of your documents.”*  

**Pitch**:  
“Your documents, certified and verifiable in 2 seconds, anywhere in the world.”  

**Channels**:  
- Clear landing page (Framer).  
- Explainer videos (EN/FR).  
- Live demo (upload → verify).  
- LinkedIn / YouTube / Twitter campaigns.  

---

## ⚖ License  

This repository is licensed under the **MIT License**.  
See [LICENSE](./LICENSE) for details.  

---

## 🛠 Contributing  

We welcome contributions!  
- Open issues for bugs or feature requests.  
- Submit pull requests with clear commits.  
- Follow the contribution guidelines in [CONTRIBUTING.md](./CONTRIBUTING.md).  

---

## ✅ Status  

- Current version: **0.1.2**  
- Release page: [Releases](../../releases)  
- Tests: ![Tests](https://github.com/BACOUL/digitalmeve/actions/workflows/tests.yml/badge.svg)  

---

## 📚 Documentation  

- [Specification](./docs/specification.md)  
- [Security](./docs/security.md)  
- [Examples](./docs/examples.md)  
- [Roadmap](./docs/roadmap.md)  
- [Generator Guide](./docs/generator-guide.md)  
- [Verification Guide](./docs/verification-guide.md)



---

## 🌟 Final Goal  

Make **.MEVE the universal format of digital certification**:  
- Free for individuals.  
- Subscription/API for professionals.  
- License for institutions.  

**DigitalMeve — Trust in every file.**
