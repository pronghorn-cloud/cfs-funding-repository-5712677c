# Children and Family Services Funding Portal - Client Pain Points Summary

## Source Documents Reviewed

1. **project-overview.docx** - Copilot summary of a Teams conversation between stakeholders (Kelly, Jenna, and team) describing the portal requirements.
2. **vulnerability-management-control-policy.docx** - GoA Cybersecurity Division control policy for IT vulnerability management (scanning, patching, remediation of IT systems).
3. **CS0404-vulnerability-management.docx** - GoA Cybersecurity Services 2023-2027 service plan for IT vulnerability scanning and remediation.

> **Note:** The two knowledge_docs are GoA **IT cybersecurity** policies governing vulnerability scanning, patching, and remediation of government systems. They are not directly related to social vulnerability or client services management. They may inform the security and compliance requirements of any application built on GoA infrastructure, but they do not describe the social services workflow or client pain points. The pain points below are derived from the project overview.

---

## Project Context

**Children and Family Services (CFS)** needs an online portal for **women's shelters** to request new or additional government funding. The portal will also incorporate a **community needs assessment tool** powered by a social vulnerability index (originally developed by KPMG) to help prioritize funding based on regional need.

---

## Core Pain Points

### 1. Informal, Ad-Hoc Funding Request Process
- The current process for shelters to request funding is **email-based and unstructured**.
- There are no standardized forms, intake workflows, or tracking mechanisms.
- Both new and existing shelters lack a formal channel to submit requests.

### 2. Lack of Transparency and Consistency in Funding Decisions
- Funding decisions are not made against a **consistent, data-driven framework**.
- There is no standardized scoring or evaluation process for comparing requests.
- The current approach makes it difficult to demonstrate **equity and fairness** in how funding is allocated across regions.

### 3. Static, Manually-Maintained Vulnerability Data
- The KPMG vulnerability index uses **83 indicators across six categories**:
  - Demographics
  - Safety from Violence
  - Income & Housing Security
  - Family & Community Support
  - Mental Health Support
  - Justice System
- The current data underpinning the index is **static and manually collected**.
- Data comes from multiple disparate sources (GOA Health, Environics, CFS, StatsCan, SCSS, Recovery Alberta, Justice) with no automated ingestion.
- There is no mechanism to **regularly refresh** the data, meaning decisions may be based on outdated information.

### 4. No Centralized Application Tracking
- Applicant organizations have no way to **track the status** of their submissions.
- CFS staff lack a unified dashboard to **manage, score, and compare** applications.
- There is no feedback loop to communicate decisions or required changes back to applicants.

### 5. Inadequate Reporting for Decision-Makers
- CFS cannot easily generate **minister-ready briefing packages** or recommendations.
- Reports for **Treasury Board submissions** require manual compilation.
- The lack of structured data makes it difficult to produce consistent, defensible reports.

### 6. Disconnected Community Needs Assessment
- The existing KPMG BI tool is **static and not interactive**.
- There are no heat maps or visualizations overlaying vulnerability scores with charity/nonprofit data.
- Decision-makers lack tools to **visually compare regional needs** when evaluating funding requests.

### 7. Non-Technical User Accessibility
- Many end users (both shelter operators and some CFS staff) are **non-technical**.
- The system needs clear documentation, guided workflows, and intuitive UI to ensure adoption.
- User testing and support are emphasized as critical to success.

---

## Desired Outcomes

| Outcome | Description |
|---|---|
| **Formalized intake** | Guided, dynamic online forms for organizations to submit funding requests with supporting documents |
| **Data-driven prioritization** | Funding requests scored against the social vulnerability index to identify areas of greatest need |
| **Reviewer dashboard** | CFS staff can score, compare, and manage applications in a unified interface |
| **Automated data feeds** | Regular, automated ingestion from government and third-party data sources |
| **Interactive visualization** | Heat maps and overlays showing vulnerability scores, charity/nonprofit locations, and regional comparisons |
| **Ministerial reporting** | One-click generation of briefing packages and Treasury Board recommendations |
| **Application transparency** | Applicants can track status and receive feedback on their submissions |

---

## Phasing (as described by stakeholders)

- **MVP (Phase 1):** Front-end portal for funding intake and application tracking.
- **Phase 2+:** Community needs assessment tool, analytics, automated data feeds, interactive visualizations.
- **Target launch:** April (aligned with new fiscal year), timeline flexible based on stakeholder availability.

---

## Compliance Considerations

The GoA cybersecurity policies reviewed (vulnerability-management-control-policy.docx, CS0404) establish that any application built on GoA infrastructure must comply with:
- Regular vulnerability scanning (infrastructure and web application)
- Remediation timelines based on risk criticality
- Change and patch management processes
- Security incident handling and response procedures
- Information controller and custodian accountability frameworks

These will need to be factored into the application's architecture, deployment, and ongoing operations.
