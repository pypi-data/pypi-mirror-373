import json
import logging
from typing import Tuple, Dict, Any

from ray import serve

from folder_classifier.dto import FolderClassificationRequest, FolderClassification
from folder_classifier.util import build_folder, render_tree

SYSTEM_PROMPT = r"""
You are a strict text classifier. Provide a single JSON object with exactly two keys: "category" and "reasoning".
- "category": either "matter" or "other" (lowercase).
- "reasoning": 1–2 short explanation referencing the key rule(s) that decided it.
No markdown (no backticks or code blocks) or any extra text outside the JSON. No chain-of-thought explanations or extra keys. If uncertain, choose "other".
""".strip()

USER_PROMPT_TEMPLATE = r"""
Task: Classify the root folder as 'matter' or 'other'.

Decision rules (apply in order):
1) If there are no files with extension anywhere in the tree , classify as 'other'. 
2) If the root folder appears to be a container of multiple matters , classify as 'other'.
3) If the root folder is or ends with a common subfolder name or descriptor found inside legal matters (e.g.,"Email", "Summons" "Emails", "Documents", "Correspondence", "Drafts", "Pleadings", "Court Documents", "Billing", or similar descriptive folder types), classify as 'other' even if it contains legal documents.
4) If the root folder is a subfolder of a matter, classify as other
5) If the root folder name matches any Matter Folder Naming Pattern and there is at least one file with an extension anywhere in the tree (including subfolders), and there is at least one file, subfolder, or filename that directly and unambiguously references a legal, client-matter, or professional context—for example, a legal document type, an initial or core legal document, clear legal terminology, a jurisdiction/court reference, the name of a law firm or legal/financial professional, or an activity specific to legal work—classify as 'matter'.
Do not classify as 'matter' if the folder only contains general business documents (e.g., invoices, estimates, generic correspondence) and there are no strong indicators of legal, client, or matter-related content as defined above
6) If the root folder name very compellingly looks like a matter folder e.g (11206 - AcmeX Pty v Acme Corp), classify as 'matter' even if the documents are not initial/core/legal documents.
7) If none of the above apply, classify as 'other'.

Matter Folder Naming Patterns (case-insensitive; separators like space, hyphen, underscore are fine):
• Matter number alone or combined with a client/surname/company (e.g., "12345", "12345 Smith", "Smith - Contract Dispute").
• Client name/surname/company/business name, optionally with matter type or client reference (e.g., "Brown – Lease Review", "Jones Family – Estate").
• Common file-number prefixes/suffixes (e.g., "MAT-1234", "CLT001", "2025-0001", "ACME_2024_Lease").
• Suggested regex-style hints (not strict requirements):
  - Numeric ID: ^\d{4,}$
  - Prefixed ID: ^(MAT|CLT|FILE|CASE|REF)[-_]?\d{3,}
  - Name + type: ^[A-Za-z].*(Lease|Contract|Estate|Dispute|Sale|Acquisition|Conveyance|Family|Probate|Litigation).*

Initial or Core Documents (early-stage client docs):
• File Cover Sheet
• Cost Agreement / Costs Disclosure
• Retainer Instructions / Engagement Letter
• Onboarding Questionnaire / Client Intake Form

Legal Document Types (non-exhaustive):
• Contract, Deed, Agreement, Will
• Affidavit, Statement
• Brief to Counsel, Advice
• Court Forms, Pleadings, Subpoena, Orders, Judgment, Undertaking

Subfolder Indicators (often—but not always—present in matters):
• Correspondence / Emails
• File Notes / Attendance Notes
• Searches / Certificates
• Court Documents / Evidence / Disclosure / Discovery
• Drafts / Final / Signed / Executed
• Billing / Invoices / Time Records

File Naming Patterns (helpful signals):
• Dates in YYYYMMDD or DDMMYYYY.
• Legal terminology (e.g., "Letter to other side", "Draft_Affidavit_v3").
• Versioning (v1, v2, Final, Executed, Signed).
• Jurisdiction or court references (e.g., NSWSC, VCAT, Family Court, FCFCOA).

Definitions/assumptions:
• "Document" = a file (e.g., .pdf, .docx, .rtf, .txt, .xlsx, .msg/.eml). Folders are not documents.
• Treat "templates" or "precedents" as weak signals unless clearly client/matter-specific.
• Evaluate only the content shown in the tree—do not infer from outside knowledge.

Output format (JSON only, no extra text):
{"category": "<matter|other>", "reasoning": "<1–2 short explanation referencing the key rule(s) that decided it>"}
ROOT FOLDER:
{root_folder}
FOLDER TREE:
{folder_tree}
""".strip()


FOLDER_CLASSIFICATION_SCHEMA = FolderClassification.model_json_schema()


class FolderClassifier:
    def __init__(self, app_name: str, deployment: str, model: str):
        self.logger = logging.getLogger(__name__)
        self.model_handle = serve.get_deployment_handle(app_name=app_name, deployment_name=deployment)
        self.model = model
        self.logger.info(f"Successfully initialized Folder Classifier with remote Ray model: {self.model}")

    async def predict(self, request: FolderClassificationRequest) -> Tuple[str, str]:
        content = ""
        try:
            chat_completion_request = self._to_chat_completion_request(request)
            response = await self.model_handle.create_chat_completion_internal.remote(chat_completion_request)
            response_dict = json.loads(response.body)
            content = response_dict["choices"][0]["message"]["content"]
            result = FolderClassification.model_validate_json(content)
        except Exception as ex:
            self.logger.warning(f"Failed to parse response: {content}\n{ex}")
            if '"category": "matter"' in content:
                result = FolderClassification(category="matter", reasoning="NA")
            else:
                result = FolderClassification(category="other", reasoning="NA")
        return result.category, result.reasoning

    def _to_chat_completion_request(self, request: FolderClassificationRequest) -> Dict[str, Any]:
        input_paths = request.items
        folder = build_folder(input_paths)
        root_folder = folder.name
        folder_tree = render_tree(folder)
        chat_completion_request = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.
                                                replace("{root_folder}", root_folder).
                                                replace("{folder_tree}", folder_tree)}
            ],
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.8,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "FolderClassification",
                    "schema": FOLDER_CLASSIFICATION_SCHEMA,
                    "strict": True,
                },
            }
        }
        return chat_completion_request





