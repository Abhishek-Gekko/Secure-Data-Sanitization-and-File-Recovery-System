# 🔐 Integrated Secure Data Erasure & Advanced File Recovery Tool

## SIH 2026 — Digital Forensics & Data Sanitization

An integrated digital forensics prototype designed to securely sanitize data, recover deleted files, verify sanitization effectiveness, measure recovery quality, maintain a tamper-evident audit trail, and generate a consolidated forensic report.

---

# 📌 Problem Statement

### Design and Development of an Integrated Secure Data Erasure and Advanced File Recovery Tool for Digital Forensics and Data Sanitization.

The objective of this project is to build a unified platform that combines:

- Secure data sanitization
- File and folder deletion
- Disk-image sanitization
- Filesystem analysis
- Deleted-file recovery
- Raw file carving
- Fragmented-file reconstruction
- Recovery validation
- Recovery confidence scoring
- Recoverability scoring
- Before/after sanitization comparison
- Sanitization verification
- Tamper-evident audit logging
- Automated forensic reporting
- Sanitization certificate generation

The prototype is designed as a focused **2–3 day MVP** using controlled test disk images.

---

# 🎯 Core Project Objective

The main idea of the project is:

> **Don't just erase data. Prove what was recoverable before sanitization — and prove what remains afterward.**

Instead of simply performing data deletion, the system creates a closed forensic loop:

```text
RECOVER
   ↓
MEASURE
   ↓
BASELINE
   ↓
SANITIZE
   ↓
RECOVER AGAIN
   ↓
COMPARE
   ↓
VERIFY
   ↓
REPORT
```

This makes the system capable of demonstrating the effectiveness of sanitization using measurable recovery evidence.

---

# 🏗️ Overall System Architecture

```text
                         ┌─────────────────────────────┐
                         │      USER / INVESTIGATOR    │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │       UNIFIED GUI           │
                         │  Forensic Data Management    │
                         │          Platform            │
                         └──────────────┬──────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              │                         │                         │
              ▼                         ▼                         ▼
    ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
    │     TEAM 1       │      │     TEAM 2       │      │     TEAM 3       │
    │   SANITIZATION   │      │  FILE RECOVERY   │      │  INTELLIGENCE &  │
    │   & FILE ERASE   │      │  & FILE CARVING  │      │   VERIFICATION   │
    └────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
             │                         │                         │
             ▼                         ▼                         ▼
      ┌──────────────┐        ┌──────────────┐        ┌────────────────┐
      │ File Eraser  │        │ Sleuth Kit   │        │ Recovery Score │
      │ Folder Eraser│        │ Recovery     │        │ Baseline       │
      │ Image Eraser │        │ Raw Carving  │        │ Comparison     │
      │ Media Class. │        │ Reconstruction│        │ Verification   │
      └──────────────┘        │ Validation   │        │ Audit Trail    │
                              └──────────────┘        │ Reporting      │
                                                     └────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │     CONSOLIDATED RESULT     │
                         │                             │
                         │ Recovery + Sanitization +   │
                         │ Verification + Audit +       │
                         │ Certificate / Report        │
                         └─────────────────────────────┘
```

---

# 👥 Team Structure

The project is divided into three major teams:

| Team | Module | Primary Responsibility |
|------|--------|------------------------|
| Team 1 | Data Sanitization & File Sanitization | Securely remove data |
| Team 2 | File Recovery | Find, recover, reconstruct and validate files |
| Team 3 | Algorithm / Forensic Intelligence & Verification | Score, compare, verify, audit and report |

Each team develops its own module while following common:

- Design concepts
- Visual language
- Data structures
- Integration contracts

The project lead connects all modules into one unified prototype.

---

# 🧹 TEAM 1 — DATA SANITIZATION & FILE SANITIZATION

## 📌 Purpose

Team 1 is responsible for securely removing data and implementing the sanitization layer of the prototype.

The sanitization module is capable of handling:

- Individual files
- Folders
- Controlled disk images

It also classifies the target storage medium and recommends an appropriate sanitization approach.

---

# 🧩 Team 1 Modules

## 1. File Sanitization

Responsible for sanitizing individual files.

### Features

- File sanitization/deletion
- Target identification
- SHA-256 hash capture before sanitization
- Sanitization method selection
- Sanitization status
- Timestamp recording
- Explicit confirmation before destructive operation

---

## 2. Folder Sanitization

Responsible for sanitizing folders and their contents.

### Features

- Folder selection
- File enumeration
- File sanitization
- Folder-level result reporting
- Target information
- Timestamp
- Sanitization status

---

## 3. Controlled Disk-Image Sanitization

Responsible for demonstrating sanitization against controlled forensic disk images.

The MVP should use test disk images rather than automatically sanitizing physical devices.

Example:

```text
Controlled Disk Image
        │
        ▼
Target Identification
        │
        ▼
SHA-256 Capture
        │
        ▼
Sanitization Method
        │
        ▼
Sanitization
        │
        ▼
Result
```

---

## 4. Storage Media Classification

The system identifies the target medium as:

- HDD
- SSD/NVMe
- USB/Flash
- Disk Image
- Unknown

The classifier is used to recommend an appropriate sanitization approach.

---

## 5. Sanitization Method Recommendation

The system provides a sanitization recommendation based on the target medium.

```text
                 Target
                    │
                    ▼
            Media Classification
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
         HDD       SSD      USB/Flash
          │         │         │
          └─────────┼─────────┘
                    │
                    ▼
          Recommended Method
```

The MVP primarily demonstrates classification and recommendation for physical media rather than automatically wiping real physical devices.

---

## 6. Sanitization Safety Layer

Destructive operations must include safety controls.

### Safety requirements

- Explicit user confirmation
- Display target path
- Display SHA-256 before sanitization
- Prevent accidental system-disk targeting
- Controlled test-image operation by default

---

# 🔎 TEAM 2 — FILE RECOVERY

## 📌 Purpose

Team 2 is responsible for finding, reconstructing, recovering, and validating deleted or otherwise recoverable files.

The recovery module combines:

- Sleuth Kit filesystem analysis
- Filesystem metadata analysis
- Deleted-file identification
- Filesystem-based recovery
- Raw file carving
- Fragmented-file reconstruction
- Recovery validation

---

# 🧩 Team 2 Modules

## 1. Disk Image Analysis

Analyzes the provided forensic disk image.

Responsibilities include:

- Identifying partitions
- Identifying filesystems
- Extracting filesystem information
- Locating relevant evidence

---

## 2. Sleuth Kit Integration

The project uses **The Sleuth Kit (TSK)** for filesystem-level forensic analysis.

Important tools include:

```text
mmls
fsstat
fls
istat
```

General workflow:

```text
Disk Image
    │
    ▼
   mmls
    │
    ▼
Partition Information
    │
    ▼
  fsstat
    │
    ▼
Filesystem Information
    │
    ▼
   fls
    │
    ▼
Deleted File Identification
    │
    ▼
Metadata / Inode Analysis
    │
    ▼
Recovery
```

---

# 3. Deleted File Identification

The system identifies files that are marked as deleted but whose data may still exist in the disk image.

Information may include:

- Filename
- Inode
- File size
- Location
- Allocation status
- Deleted status
- Filesystem evidence

---

# 4. Filesystem-Based File Recovery

Deleted files identified through filesystem metadata can be recovered using Sleuth Kit-based methods.

```text
Deleted File
     │
     ▼
Filesystem Metadata
     │
     ▼
Locate Data Blocks
     │
     ▼
Extract Data
     │
     ▼
Recovered Artifact
```

---

# 5. Raw File Carving

Raw file carving operates directly on the disk-image bytes.

This approach is useful when filesystem metadata is:

- Missing
- Damaged
- Unavailable
- Insufficient

The carving engine searches for file signatures and extracts file data based on file structure.

---

# 📂 Initial File-Carving Formats

The initial MVP targets:

| File Type | Extension |
|-----------|-----------|
| JPEG | `.jpg`, `.jpeg` |
| PNG | `.png` |
| PDF | `.pdf` |
| Microsoft Word | `.docx` |
| ZIP | `.zip` |

---

# 🧩 Raw File Carving Pipeline

```text
Disk Image
    │
    ▼
Read Raw Bytes
    │
    ▼
Search File Signatures
    │
    ▼
Identify File Header
    │
    ▼
Determine File Structure
    │
    ▼
Locate Appropriate End Marker
    │
    ▼
Extract File
    │
    ▼
Validate File
    │
    ▼
Generate Metadata
```

---

# 6. Fragmented File Reconstruction

A file may be stored in multiple non-contiguous locations on a disk.

Example:

```text
[FILE HEADER]
[FILE DATA]
[RANDOM DATA]
[RANDOM DATA]
[FILE DATA]
[FILE DATA]
[FILE END]
```

The system attempts to reconstruct fragmented files where sufficient structural information is available.

Possible evidence:

- File signatures
- File structure
- Filesystem metadata
- Block/cluster information
- Structural markers
- Validation results

---

# 7. Recovered File Validation

A recovered file is not automatically considered valid just because bytes were extracted.

The validation layer checks whether the recovered data represents a usable file.

Possible checks include:

- File signature verification
- Structural validation
- Parser validation
- Successful decoding
- Successful opening
- File size verification
- SHA-256 calculation
- Integrity status

```text
Recovered Artifact
       │
       ▼
Signature Check
       │
       ▼
Structure Check
       │
       ▼
Parser Validation
       │
       ▼
Integrity Check
       │
       ▼
VALID / PARTIAL / INVALID
```

---

# 8. Recovery Metadata

Each recovered artifact should contain metadata such as:

```json
{
    "file_name": "recovered_001.jpg",
    "file_type": "JPEG",
    "source_image": "carving.img",
    "offset": 1048576,
    "size": 245760,
    "recovery_method": "raw_carving",
    "validation_status": "VALID",
    "sha256": "..."
}
```

This metadata becomes evidence for Team 3.

---

# 🧠 TEAM 3 — ALGORITHM / FORENSIC INTELLIGENCE & VERIFICATION

## 📌 Purpose

Team 3 converts recovery and sanitization results into measurable and explainable forensic evidence.

Team 3 is responsible for:

- Recovery confidence
- Recoverability scoring
- Baseline creation
- Before/after comparison
- Sanitization verification
- Audit trail
- Reporting
- Certificate generation

---

# 🧩 Team 3 Modules

## 1. Explainable Recovery Confidence

The system produces a recovery confidence score supported by understandable evidence.

Possible evidence includes:

- Valid file signature
- Structural checks
- Parser validation
- Filesystem evidence
- Successful file decoding
- Integrity checks

The goal is not just:

```text
FILE FOUND
```

but:

```text
FILE FOUND
     │
     ├── Valid Signature
     ├── Valid Structure
     ├── Parser Passed
     ├── Filesystem Evidence
     └── Integrity Passed
              │
              ▼
       RECOVERY CONFIDENCE
```

---

# 2. Recoverability Score

The project defines a **Recoverability Score**.

This score summarizes how recoverable an artifact is rather than simply reporting that the file was found.

Example conceptual model:

```text
Filesystem Evidence
        +
Signature Validity
        +
Structural Validity
        +
Parser Validation
        +
Integrity
        │
        ▼
Recoverability Score
```

The exact scoring algorithm is project-defined.

---

# 3. Pre-Sanitization Recovery Baseline

Before sanitization, the system performs recovery and records the identified artifacts.

Example:

```text
                  BEFORE SANITIZATION
                           │
                           ▼
                    Analyze Image
                           │
                           ▼
                    Recover Files
                           │
                           ▼
                     Validate Files
                           │
                           ▼
                   Calculate Scores
                           │
                           ▼
                  CREATE BASELINE
```

The baseline records what was recoverable before sanitization.

---

# 4. Post-Sanitization Recovery

After Team 1 sanitizes the target, Team 2 performs recovery again.

```text
Baseline
   │
   ▼
Sanitization
   │
   ▼
Post-Sanitization Image
   │
   ▼
Recovery
   │
   ▼
Validation
   │
   ▼
Post-Sanitization Results
```

---

# 5. Before/After Comparison

Team 3 compares:

```text
BEFORE SANITIZATION
        │
        ▼
Recovered Artifacts
        │
        ▼
Recovery Baseline
        │
        │
        ▼
SANITIZATION
        │
        ▼
AFTER SANITIZATION
        │
        ▼
Recovered Artifacts
        │
        ▼
Comparison
```

The system determines whether previously identified artifacts remain recoverable.

---

# 6. Sanitization Verification

The system verifies the sanitization outcome based on the defined recovery procedure.

The verification statement is:

> **"No previously identified artifacts were recovered under the defined verification procedure."**

The system can produce:

```text
BEFORE
   │
   ├── Artifact A
   ├── Artifact B
   └── Artifact C
        │
        ▼
   SANITIZATION
        │
        ▼
AFTER
   │
   ├── Artifact A ❌
   ├── Artifact B ❌
   └── Artifact C ❌
        │
        ▼
     VERIFICATION
        │
        ▼
       PASS
```

If previously identified artifacts remain recoverable, the verification result can be marked as **FAIL**.

---

# 7. Tamper-Evident Audit Trail

The system maintains a hash-chained audit trail.

Example:

```text
Event 1
   │
   ▼
Hash 1
   │
   ▼
Event 2 + Hash 1
   │
   ▼
Hash 2
   │
   ▼
Event 3 + Hash 2
   │
   ▼
Hash 3
```

If an earlier recorded event is modified, the hash chain becomes inconsistent.

This provides an integrity mechanism for the recorded workflow.

> This is a tamper-evident audit mechanism and **not blockchain**.

---

# 8. Automated Forensic Report

The system generates a consolidated report containing:

- Target information
- Recovery findings
- Recovery metadata
- Recovery confidence
- Recoverability score
- Sanitization details
- Before/after results
- Verification outcome
- Audit integrity
- Final status

---

# 9. Sanitization Certificate

The system can generate a sanitization certificate/report containing the final verification outcome.

Example:

```text
==================================================
          SANITIZATION CERTIFICATE
==================================================

Target              : carving.img

Pre-Sanitization
Artifacts Recovered : 5

Sanitization Status : COMPLETED

Post-Sanitization
Artifacts Recovered : 0

Verification        : PASS

Audit Integrity     : VALID

Statement:
No previously identified artifacts were recovered
under the defined verification procedure.

==================================================
```

---

# 🔄 COMPLETE SYSTEM WORKFLOW

The complete integrated workflow is:

```text
                    ┌────────────────────┐
                    │  TEST DISK IMAGE   │
                    └─────────┬──────────┘
                              │
                              ▼
                         ┌─────────┐
                         │ ANALYZE │
                         └────┬────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ FIND DELETED FILES │
                    └─────────┬──────────┘
                              │
                              ▼
                         ┌─────────┐
                         │ RECOVER │
                         └────┬────┘
                              │
                              ▼
                         ┌──────────┐
                         │ VALIDATE │
                         └────┬─────┘
                              │
                              ▼
                ┌────────────────────────────┐
                │ CALCULATE RECOVERY         │
                │ CONFIDENCE & SCORE         │
                └─────────────┬──────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ CREATE BASELINE  │
                    └────────┬─────────┘
                             │
                             ▼
                       ┌────────────┐
                       │ SANITIZE   │
                       └─────┬──────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ RECOVER AGAIN   │
                    └────────┬────────┘
                             │
                             ▼
                   ┌───────────────────┐
                   │ COMPARE BEFORE /  │
                   │ AFTER             │
                   └────────┬──────────┘
                            │
                            ▼
                       ┌──────────┐
                       │ VERIFY   │
                       └────┬─────┘
                            │
                            ▼
                  ┌─────────────────────┐
                  │ GENERATE REPORT &   │
                  │ CERTIFICATE         │
                  └─────────────────────┘
```

---

# 🔗 TEAM INTEGRATION

The three teams operate as a closed-loop system.

```text
                    TEAM 2
                 FILE RECOVERY
                       │
                       │ Recovery Evidence
                       ▼
                    TEAM 3
              INTELLIGENCE & VERIFY
                       │
                       │ Baseline
                       ▼
                    TEAM 1
                 SANITIZATION
                       │
                       │ Sanitized Target
                       ▼
                    TEAM 2
                 FILE RECOVERY
                       │
                       │ Post-Recovery Evidence
                       ▼
                    TEAM 3
              COMPARE & VERIFY
                       │
                       ▼
                  FINAL REPORT
```

---

# 📊 Integration Responsibility

| Stage | Responsible Team | Main Output |
|-------|------------------|-------------|
| Analyze test image | Team 2 | Filesystem/evidence information |
| Find deleted files | Team 2 | Recovered artifacts |
| Validate recovery | Team 2 | Validated recovery results |
| Calculate confidence/score | Team 3 | Confidence + recoverability metrics |
| Create baseline | Team 3 | Pre-sanitization evidence baseline |
| Sanitize target | Team 1 | Sanitization result |
| Recover again | Team 2 | Post-sanitization recovery results |
| Verify & compare | Team 3 | Before/after verification |
| Generate report | Team 3 | Tamper-evident report/certificate |

---

# 🖥️ UNIFIED GUI

The final prototype is intended to expose all major capabilities through one unified interface.

Suggested navigation:

```text
┌─────────────────────────────────────────────────────┐
│             SECURE FORENSIC PLATFORM                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Dashboard                                          │
│                                                     │
│  ├── Evidence / Disk Image                          │
│  │                                                   │
│  ├── File Recovery                                  │
│  │     ├── Filesystem Analysis                      │
│  │     ├── Deleted Files                            │
│  │     ├── Raw File Carving                         │
│  │     ├── Reconstruction                           │
│  │     └── Validation                               │
│  │                                                   │
│  ├── Sanitization                                   │
│  │     ├── File Sanitization                        │
│  │     ├── Folder Sanitization                      │
│  │     ├── Disk Image Sanitization                  │
│  │     └── Media Classification                     │
│  │                                                   │
│  ├── Analysis & Verification                        │
│  │     ├── Recovery Confidence                      │
│  │     ├── Recoverability Score                     │
│  │     ├── Baseline                                │
│  │     ├── Before/After Comparison                  │
│  │     └── Sanitization Verification                │
│  │                                                   │
│  ├── Audit Trail                                    │
│  │                                                   │
│  └── Reports & Certificates                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

# 📁 Suggested Repository Structure

```text
integrated-secure-forensic-tool/
│
├── README.md
│
├── frontend/
│   ├── dashboard/
│   ├── recovery/
│   ├── sanitization/
│   ├── verification/
│   ├── audit/
│   └── reports/
│
├── backend/
│   ├── api/
│   ├── recovery/
│   ├── sanitization/
│   ├── verification/
│   ├── audit/
│   └── reporting/
│
├── recovery/
│   ├── sleuthkit/
│   ├── carving/
│   ├── reconstruction/
│   ├── validation/
│   └── signatures/
│
├── sanitization/
│   ├── file/
│   ├── folder/
│   ├── disk-image/
│   └── media-classifier/
│
├── intelligence/
│   ├── confidence/
│   ├── scoring/
│   ├── baseline/
│   └── comparison/
│
├── audit/
│   └── hash-chain/
│
├── reports/
│
├── certificates/
│
├── test-data/
│
├── disk-images/
│
└── docs/
```

> The final repository structure can be modified according to the implementation architecture.

---

# 🧪 TESTING STRATEGY

The MVP should primarily use controlled test disk images.

## Test Scenario 1 — Deleted File Recovery

```text
Create File
     │
     ▼
Store File
     │
     ▼
Delete File
     │
     ▼
Create Disk Image
     │
     ▼
Analyze Image
     │
     ▼
Find Deleted File
     │
     ▼
Recover
     │
     ▼
Validate
```

---

# Test Scenario 2 — Raw File Carving

```text
Create Test File
     │
     ▼
Place Data in Disk Image
     │
     ▼
Remove Filesystem Reference
     │
     ▼
Raw Scan
     │
     ▼
Detect Signature
     │
     ▼
Carve
     │
     ▼
Validate
```

---

# Test Scenario 3 — Sanitization Verification

```text
Create Test Image
       │
       ▼
Recover Files
       │
       ▼
Create Baseline
       │
       ▼
Sanitize Image
       │
       ▼
Recover Again
       │
       ▼
Compare Results
       │
       ▼
Verify
       │
       ▼
Generate Certificate
```

---

# Test Scenario 4 — Multiple File Formats

The test image can contain:

```text
carving.img
│
├── image.jpg
├── image.png
├── document.pdf
├── document.docx
└── archive.zip
```

The recovery engine attempts to identify and recover each supported artifact.

---

# 📊 Example Final Result

```text
========================================================
                 FORENSIC ANALYSIS RESULT
========================================================

TARGET
--------------------------------------------------------
Disk Image          : carving.img
SHA-256             : <hash>

PRE-SANITIZATION
--------------------------------------------------------
Files Identified    : 5
Files Recovered     : 5
Files Validated     : 5

Recovery Confidence : <score>
Recoverability      : <score>

SANITIZATION
--------------------------------------------------------
Method              : <method>
Status              : COMPLETED

POST-SANITIZATION
--------------------------------------------------------
Files Recovered     : 0
Previously Identified
Artifacts Recovered : 0

VERIFICATION
--------------------------------------------------------
Result              : PASS

Statement:
No previously identified artifacts were recovered
under the defined verification procedure.

AUDIT
--------------------------------------------------------
Audit Chain         : VALID

FINAL STATUS
--------------------------------------------------------
SANITIZATION        : VERIFIED
========================================================
```

---

# 🔐 SECURITY & SAFETY BOUNDARY

The MVP should operate on **controlled test disk images by default**.

## Mandatory Safety Rules

- Never automatically target system disks.
- Never automatically target `/dev/sda`.
- Never automatically target `/dev/nvme*`.
- Destructive operations require explicit confirmation.
- Display the target path before sanitization.
- Display the SHA-256 hash before sanitization.
- Use controlled test images for destructive demonstrations.
- Do not perform destructive operations on real user data.

---

# ⚠️ SSD / NVMe Limitation

The prototype should not claim universal or permanent deletion, particularly for:

- SSD
- NVMe
- Flash-based storage

For physical storage types, the MVP should primarily demonstrate:

```text
MEDIA CLASSIFICATION
        +
METHOD RECOMMENDATION
```

rather than automatically wiping real physical devices.

---

# 🧠 AI/ML Scope

AI/ML is intentionally **not included in the working MVP** due to the short development window.

It can be presented as a future enhancement.

Potential future applications include:

- Intelligent artifact classification
- Advanced recovery prioritization
- Fragmented-file prediction
- Automated evidence classification
- Anomaly detection
- Recovery success prediction

---

# ⭐ PROJECT UNIQUE SELLING POINTS

## 1. Primary USP

> **Don't just erase data. Prove what was recoverable before sanitization — and prove what remains afterward.**

---

## 2. Explainable Recovery Confidence

Recovery confidence is supported by understandable forensic evidence such as:

- Valid file signatures
- Structural checks
- Parser validation
- Filesystem evidence

---

## 3. Recoverability Score

A project-defined metric that describes how recoverable an artifact is rather than simply reporting that a file was found.

---

## 4. Before/After Verification

The system establishes a recovery baseline before sanitization and compares it with post-sanitization recovery results.

---

## 5. Tamper-Evident Audit Trail

Hash-chained audit events make changes to recorded workflow information detectable.

This is an audit-integrity mechanism and **not blockchain**.

---

## 6. Automated Reporting & Certificate

The system generates a consolidated result containing:

- Target information
- Sanitization details
- Recovery findings
- Verification outcome
- Audit integrity
- Certificate/report

---

# 🚧 MVP Scope

The working MVP focuses on:

### Team 1

- File sanitization
- Folder sanitization
- Controlled disk-image sanitization
- Storage-media classification
- Sanitization method recommendation
- Safety controls
- SHA-256 capture
- Sanitization reporting

### Team 2

- Sleuth Kit integration
- Filesystem analysis
- Deleted-file identification
- Deleted-file recovery
- Raw file carving
- JPEG recovery
- PNG recovery
- PDF recovery
- DOCX recovery
- ZIP recovery
- Fragmented-file reconstruction
- Recovery validation
- Recovery metadata

### Team 3

- Explainable recovery confidence
- Recoverability Score
- Pre-sanitization baseline
- Post-sanitization comparison
- Sanitization verification
- PASS/FAIL determination
- Hash-chained audit trail
- Audit integrity verification
- Automated forensic report
- Sanitization certificate

---

# 🚫 MVP Limitations

The prototype does not claim:

- Universal file recovery
- Guaranteed fragmented-file recovery
- Universal filesystem support
- Permanent deletion on all storage technologies
- Automatic wiping of real physical system drives
- Commercial forensic-suite capabilities
- AI/ML-based recovery during the MVP

---

# 🔮 Future Enhancements

Possible future improvements include:

- More filesystem support
- More file formats
- Advanced fragmented-file reconstruction
- Advanced file parsers
- Parallel carving
- Large-image optimization
- Duplicate artifact detection
- Advanced evidence visualization
- Advanced recovery scoring
- AI/ML-assisted artifact classification
- Additional storage sanitization standards
- Enterprise-scale reporting
- Cloud-based forensic investigation
- Case management
- Multi-user investigator workflows

---

# 🛠️ Technology Stack

The prototype may use the following technologies:

## Operating System

- Linux
- Ubuntu
- WSL2

## Digital Forensics

- The Sleuth Kit
- `mmls`
- `fsstat`
- `fls`
- `istat`

## File Recovery

- Raw byte scanning
- File signatures
- Magic bytes
- File structure analysis
- File carving
- File reconstruction
- File validation

## Security

- SHA-256
- Hash-chained audit logs
- Integrity verification

## Application

- Unified GUI
- Backend/API
- JSON-based metadata
- Automated reporting

---

# 📜 Evidence & Audit Model

The system maintains evidence throughout the entire workflow.

```text
TARGET
  │
  ├── Target Path
  ├── Target Type
  └── SHA-256
        │
        ▼
RECOVERY EVIDENCE
  │
  ├── File Type
  ├── Offset
  ├── Size
  ├── Recovery Method
  ├── Validation
  └── Hash
        │
        ▼
SANITIZATION RESULT
  │
  ├── Method
  ├── Status
  └── Timestamp
        │
        ▼
POST-RECOVERY EVIDENCE
        │
        ▼
COMPARISON
        │
        ▼
VERIFICATION
        │
        ▼
AUDIT TRAIL
        │
        ▼
FINAL REPORT
```

---

# 📌 Final System Concept

The entire platform can be summarized as:

```text
┌─────────────────────────────────────────────────────────────┐
│                  INTEGRATED FORENSIC TOOL                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    CONTROLLED TEST IMAGE                   │
│                              │                              │
│                              ▼                              │
│                       FILE RECOVERY                         │
│                              │                              │
│                    ┌─────────┴─────────┐                    │
│                    │                   │                    │
│                    ▼                   ▼                    │
│               SLEUTH KIT          RAW CARVING               │
│                    │                   │                    │

---

# 👨‍💻 Team Responsibilities Summary

```text
┌─────────────────────────────────────────────────────────────┐
│                         TEAM 1                              │
│                DATA SANITIZATION                            │
│                                                             │
│  FILE ERASE → FOLDER ERASE → IMAGE SANITIZATION            │
│              → MEDIA CLASSIFICATION                        │
│              → METHOD RECOMMENDATION                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         TEAM 2                              │
│                     FILE RECOVERY                            │
│                                                             │
│  ANALYZE → FIND → RECOVER → CARVE → RECONSTRUCT             │
│                     → VALIDATE                              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         TEAM 3                              │
│             FORENSIC INTELLIGENCE & VERIFICATION             │
│                                                             │
│  SCORE → BASELINE → COMPARE → VERIFY → AUDIT → REPORT       │
└─────────────────────────────────────────────────────────────┘
```

---

# 🏁 Final Outcome

The final prototype brings all three teams together into one closed-loop forensic platform.

```text
             RECOVER WHAT EXISTS
                     │
                     ▼
             MEASURE RECOVERY
                     │
                     ▼
             RECORD BASELINE
                     │
                     ▼
              SANITIZE DATA
                     │
                     ▼
            ATTEMPT RECOVERY
                     │
                     ▼
             COMPARE RESULTS
                     │
                     ▼
              VERIFY RESULT
                     │
                     ▼
            PROVE THE OUTCOME
                     │
                     ▼
          GENERATE REPORT/CERTIFICATE
```

The goal is not merely to erase data or recover files independently.

The goal is to provide an **evidence-driven, measurable, and verifiable workflow for data sanitization and forensic file recovery**.

---

# 📄 License

This project is developed for educational, research, and **Smart India Hackathon (SIH) 2026** prototype purposes.
=======
# Secure Data Sanitization and File Recovery

A Python 3.10+ forensic utility core for controlled file wiping, byte-image
carving, fragmented/metadata extent reconstruction, and independent evidence
verification.

## Core use

```python
from app.sanitization import dod_5220_22_m
from app.recovery import carve_file
from app.algorithms.verification import verify_recovery

# Explicit confirmation is required for every irreversible overwrite.
wipe = dod_5220_22_m("evidence-copy.bin", confirm=True)

artifacts = carve_file("disk-image.raw", output_dir="recovered")
verification = verify_recovery("recovered/carved_0001_512.pdf", baseline_hash="...")
```

Available wipe methods are `zero`, `random`, `dod_5220_22_m`, `nist_clear`,
and `nist_purge`. Passing `delete=True, nullify_metadata=True` performs the
rename/timestamp/unlink stage after the final verification. Wipes are limited
to existing non-symlink regular files; raw-device writes are deliberately not
supported by this library.

Each operation returns dataclasses from `app.models`, with a 0–100 score,
verdict, and component-level evidence in `details`.

