from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime

from app.core.constants import DEFAULT_NO_ANSWER
from app.core.logger import logger


class GuardrailService:
    """
    Enterprise Guardrail Service.

    Features
    --------
    ✔ Prompt Injection Detection
    ✔ Question Validation
    ✔ Context Validation
    ✔ Output Validation
    ✔ Hallucination Detection
    ✔ Toxicity Detection
    ✔ PII Detection
    ✔ Secret Detection
    ✔ Rate Limiting
    ✔ Audit Logging
    """

    MAX_QUESTION_LENGTH = 1000

    MAX_REQUESTS = 20

    WINDOW_SECONDS = 60

    def __init__(self):

        self.request_tracker = defaultdict(list)

    # ==========================================================
    # Prompt Injection
    # ==========================================================

    BLOCKED_PATTERNS = [

        r"ignore previous instructions",

        r"ignore all instructions",

        r"developer prompt",

        r"system prompt",

        r"reveal prompt",

        r"jailbreak",

        r"bypass",

        r"disable safety",

        r"forget previous",

        r"show hidden prompt",
    ]

    def validate_question(
        self,
        question: str,
    ):

        question = question.strip()

        if not question:

            return False, "Question cannot be empty."

        if len(question) > self.MAX_QUESTION_LENGTH:

            return False, "Question is too long."

        lower = question.lower()

        for pattern in self.BLOCKED_PATTERNS:

            if re.search(pattern, lower):

                self.audit_log(
                    "PROMPT_INJECTION",
                    question,
                )

                return False, "Unsafe prompt detected."

        return True, ""

    # ==========================================================
    # Context
    # ==========================================================

    def validate_context(
        self,
        chunks,
    ):

        if not chunks:

            return False, DEFAULT_NO_ANSWER

        return True, ""

    # ==========================================================
    # Output Validation
    # ==========================================================

    def validate_answer(
        self,
        answer,
    ):

        if not answer:

            return DEFAULT_NO_ANSWER

        if len(answer.strip()) < 5:

            return DEFAULT_NO_ANSWER

        return answer

    # ==========================================================
    # Hallucination Detection
    # ==========================================================

    def check_hallucination(
        self,
        answer,
        chunks,
    ):

        context = " ".join(

            chunk["chunk_text"].lower()

            for chunk in chunks

        )

        words = answer.lower().split()

        matched = sum(

            1

            for word in words

            if word in context

        )

        score = matched / max(len(words), 1)

        logger.info(
            "Hallucination Score : %.2f",
            score,
        )

        return score >= 0.40

    # ==========================================================
    # Toxicity Detection
    # ==========================================================

    TOXIC_WORDS = {

        "hate",

        "kill",

        "terrorist",

        "bomb",

        "abuse",

        "racist",

        "stupid",

        "idiot",

        "moron",
    }

    def detect_toxicity(
        self,
        text,
    ):

        text = text.lower()

        for word in self.TOXIC_WORDS:

            if word in text:

                self.audit_log(
                    "TOXIC_CONTENT",
                    word,
                )

                return True

        return False

    # ==========================================================
    # PII Detection
    # ==========================================================

    EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}"

    PHONE_REGEX = r"\b\d{10}\b"

    AADHAAR_REGEX = r"\b\d{4}\s?\d{4}\s?\d{4}\b"

    PAN_REGEX = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

    def mask_pii(
        self,
        text,
    ):

        text = re.sub(
            self.EMAIL_REGEX,
            "[EMAIL]",
            text,
        )

        text = re.sub(
            self.PHONE_REGEX,
            "[PHONE]",
            text,
        )

        text = re.sub(
            self.AADHAAR_REGEX,
            "[AADHAAR]",
            text,
        )

        text = re.sub(
            self.PAN_REGEX,
            "[PAN]",
            text,
        )

        return text

    # ==========================================================
    # Secret Detection
    # ==========================================================

    SECRET_PATTERNS = [

        r"sk-[A-Za-z0-9]{20,}",

        r"AIza[0-9A-Za-z-_]{35}",

        r"ghp_[A-Za-z0-9]{36}",

        r"AKIA[0-9A-Z]{16}",

        r"-----BEGIN PRIVATE KEY-----",
    ]

    def detect_secrets(
        self,
        text,
    ):

        for pattern in self.SECRET_PATTERNS:

            if re.search(pattern, text):

                self.audit_log(
                    "SECRET_DETECTED",
                    pattern,
                )

                return True

        return False

    # ==========================================================
    # Rate Limiting
    # ==========================================================

    def allow_request(
        self,
        session_id,
    ):

        now = datetime.utcnow().timestamp()

        requests = self.request_tracker[session_id]

        requests[:] = [

            t

            for t in requests

            if now - t < self.WINDOW_SECONDS

        ]

        if len(requests) >= self.MAX_REQUESTS:

            self.audit_log(
                "RATE_LIMIT",
                session_id,
            )

            return False

        requests.append(now)

        return True

    # ==========================================================
    # Audit Log
    # ==========================================================

    def audit_log(
        self,
        event,
        value,
    ):

        logger.warning(
            "[GUARDRAIL] %s : %s",
            event,
            value,
        )