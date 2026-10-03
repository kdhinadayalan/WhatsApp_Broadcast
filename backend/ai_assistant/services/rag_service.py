import os
import re
import logging
from pathlib import Path
from django.db.models import Q
from ai_assistant.models import KnowledgeCategory, KnowledgeItem, FAQItem, KnowledgeDocument

logger = logging.getLogger(__name__)

STOPWORDS = {
    'what', 'is', 'the', 'of', 'in', 'for', 'a', 'an', 'are', 'when', 'does',
    'who', 'tell', 'me', 'about', 'how', 'to', 'can', 'i', 'get', 'at', 'on',
    'by', 'with', 'from', 'our', 'my', 'please', 'give', 'do', 'any', 'there'
}


def clean_and_tokenize(text: str) -> list[str]:
    """Extract significant lowercase keywords from text."""
    if not text:
        return []
    words = re.findall(r'[a-zA-Z0-9]+', text.lower())
    return [w for w in words if len(w) > 1 and w not in STOPWORDS]


def extract_text_from_file(file_path: str) -> str:
    """Extract plain text from uploaded PDF, TXT, or Markdown documents."""
    path = Path(file_path)
    if not path.exists():
        return ""

    suffix = path.suffix.lower()
    text = ""

    if suffix in ['.txt', '.md', '.csv']:
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")

    elif suffix == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                content = page.extract_text()
                if content:
                    pages_text.append(f"--- Page {i+1} ---\n{content.strip()}")
            text = "\n\n".join(pages_text)
        except Exception as e:
            logger.error(f"Error extracting PDF text from {file_path}: {e}")
            # Fallback basic binary text extraction
            try:
                with open(path, 'rb') as f:
                    raw = f.read()
                    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', ' ', raw.decode('latin-1', errors='ignore'))
            except Exception:
                pass

    return text.strip()


def search_knowledge_base(query: str, top_k: int = 5) -> list[dict]:
    """
    Search KnowledgeItems, FAQs, and Documents using multi-factor relevance scoring.
    Returns ranked items with source, title, content, score, and category.
    """
    cleaned_query = query.strip()
    tokens = clean_and_tokenize(cleaned_query)
    lowered_query = cleaned_query.lower()

    scored_results = []

    # 1. Search FAQ Items
    faqs = FAQItem.objects.filter(is_active=True).select_related('category')
    for faq in faqs:
        score = 0
        q_lowered = faq.question.lower()
        ans_lowered = faq.answer.lower()
        kw_lowered = (faq.keywords or '').lower()

        # Exact phrase in question
        if lowered_query in q_lowered or q_lowered in lowered_query:
            score += 100
        # Token matches in question
        for token in tokens:
            if token in q_lowered:
                score += 20
            if token in kw_lowered:
                score += 15
            if token in ans_lowered:
                score += 5

        if score > 0:
            scored_results.append({
                'type': 'FAQ',
                'title': faq.question,
                'content': faq.answer,
                'category': faq.category.name if faq.category else 'General',
                'priority': faq.priority,
                'score': score + (faq.priority * 2),
            })

    # 2. Search Knowledge Items
    items = KnowledgeItem.objects.filter(is_active=True).select_related('category')
    for item in items:
        score = 0
        title_lowered = item.title.lower()
        content_lowered = item.content.lower()
        tags_lowered = (item.tags or '').lower()
        cat_lowered = item.category.name.lower()

        # Exact phrase in title or tags
        if lowered_query in title_lowered or title_lowered in lowered_query:
            score += 90
        if lowered_query in tags_lowered:
            score += 80

        # Token matches
        for token in tokens:
            if token in title_lowered:
                score += 25
            if token in tags_lowered:
                score += 20
            if token in cat_lowered:
                score += 15
            if token in content_lowered:
                score += 6

        if score > 0:
            scored_results.append({
                'type': 'Knowledge Base',
                'title': item.title,
                'content': item.content,
                'category': item.category.name,
                'priority': item.priority,
                'score': score + (item.priority * 2),
            })

    # 3. Search Knowledge Documents
    docs = KnowledgeDocument.objects.filter(is_indexed=True).select_related('category')
    for doc in docs:
        if not doc.extracted_text:
            continue
        score = 0
        doc_title = doc.title.lower()
        doc_text = doc.extracted_text.lower()

        for token in tokens:
            if token in doc_title:
                score += 20
            if token in doc_text:
                score += 4

        if score > 0:
            # Extract most relevant excerpt (up to 600 chars around matched token)
            excerpt = ""
            for token in tokens:
                idx = doc_text.find(token)
                if idx != -1:
                    start = max(0, idx - 100)
                    end = min(len(doc.extracted_text), idx + 500)
                    excerpt = doc.extracted_text[start:end].strip()
                    break
            if not excerpt:
                excerpt = doc.extracted_text[:500]

            scored_results.append({
                'type': 'Document Excerpt',
                'title': f"Document: {doc.title}",
                'content': excerpt,
                'category': doc.category.name if doc.category else 'Document',
                'priority': 0,
                'score': score,
            })

    # Sort descending by score
    scored_results.sort(key=lambda x: x['score'], reverse=True)
    return scored_results[:top_k]


def format_retrieved_context(results: list[dict]) -> str:
    """Format scored search results into a clean, markdown context block for the LLM."""
    if not results:
        return "NO RELEVANT COLLEGE INFORMATION FOUND IN KNOWLEDGE BASE."

    sections = []
    for idx, item in enumerate(results, 1):
        sections.append(
            f"--- SOURCE {idx}: [{item['type']}] {item['title']} (Category: {item['category']}) ---\n"
            f"{item['content']}"
        )
    return "\n\n".join(sections)


def sync_knowledge_to_workspace(workspace_dir: Path):
    """
    Export current active knowledge base and FAQs into structured markdown files
    inside the OpenClaw agent's workspace folder.
    """
    workspace_dir.mkdir(parents=True, exist_ok=True)
    knowledge_dir = workspace_dir / 'knowledge'
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    # 1. Main College Knowledge Catalog
    categories = KnowledgeCategory.objects.all().prefetch_related('items')
    main_doc = ["# NMC COLLEGE OFFICIAL KNOWLEDGE BASE\n"]
    main_doc.append("This document contains verified, authoritative information regarding NMC College.\n")

    for cat in categories:
        items = cat.items.filter(is_active=True)
        if not items.exists():
            continue
        main_doc.append(f"\n## Category: {cat.name}\n")
        for item in items:
            main_doc.append(f"### {item.title}\n{item.content}\nTags: {item.tags}\n")

    with open(knowledge_dir / 'COLLEGE_CATALOG.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(main_doc))

    # 2. FAQs Markdown File
    faqs = FAQItem.objects.filter(is_active=True).select_related('category')
    faq_doc = ["# NMC COLLEGE FREQUENTLY ASKED QUESTIONS (FAQS)\n"]
    for faq in faqs:
        cat_name = faq.category.name if faq.category else 'General'
        faq_doc.append(f"**Q: {faq.question}**\n*Category: {cat_name}*\n{faq.answer}\n")

    with open(knowledge_dir / 'FAQS.md', 'w', encoding='utf-8') as f:
        f.write("\n".join(faq_doc))

    logger.info(f"Knowledge files synced to OpenClaw workspace: {knowledge_dir}")
