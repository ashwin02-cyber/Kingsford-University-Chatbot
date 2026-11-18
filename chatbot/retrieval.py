import re
from django.db.models import Q
from website.models import (
    Department, Programme, AdmissionInfo, FeeInfo,
    Announcement, Event, KnowledgeDocument
)

def retrieve_approved_information(user_query: str) -> str:
    """
    Selects relevant active records from the database by topic and keyword
    matching, returning them as a formatted 'Approved University Information' context string.
    Follows FR-033.
    """
    query_lower = user_query.lower()
    retrieved_sections = []

    # 1. Topic Mapping for KnowledgeDocument
    topic_keywords = {
        'overview': ['about', 'overview', 'profile', 'ranking', 'naac', 'statistics', 'students', 'size', 'campus', 'kingsford'],
        'vision_mission': ['vision', 'mission', 'values', 'goals', 'aim', 'philosophy'],
        'history': ['history', 'founded', 'established', 'origin', 'heritage', 'background', 'milestone', '1994', '2008'],
        'leadership': ['leadership', 'chancellor', 'vice chancellor', 'vice-chancellor', 'registrar', 'dean', 'head', 'administration', 'governance', 'pendelton', 'eleanor'],
        'accreditation': ['accreditation', 'naac', 'nba', 'nirf', 'rating', 'grade', 'recognition', 'iso'],
        'calendar': ['calendar', 'academic year', 'semester', 'holiday', 'vacation', 'break', 'term', 'dates', 'commencement'],
        'exams': ['exam', 'examination', 'grade', 'grading', 'cgpa', 'attendance', 'supplementary', 'revaluation', 'marks', 'passing'],
        'hostel': ['hostel', 'accommodation', 'dorm', 'room', 'mess', 'dining', 'residence', 'residential', 'stay', 'food'],
        'scholarship': ['scholarship', 'financial aid', 'fee waiver', 'concession', 'merit', 'sports quota', 'ews', 'discount'],
        'library': ['library', 'books', 'journals', 'reading room', 'ieee', 'digital library', 'borrow', 'raman'],
        'facilities': ['facilities', 'facility', 'labs', 'laboratory', 'sports', 'gym', 'pool', 'swimming', 'wifi', 'cafeteria', 'clinic', 'hospital', 'doctor', 'ground'],
        'contact': ['contact', 'email', 'phone', 'telephone', 'call', 'number', 'helpline', 'address', 'location', 'reach', 'office', 'hours', 'direction'],
    }

    matched_topics = set()
    for topic, keywords in topic_keywords.items():
        if any(kw in query_lower for kw in keywords):
            matched_topics.add(topic)

    # Always retrieve contact information so KAI can provide official contacts when data is missing
    matched_topics.add('contact')

    # If general or introductory query, add overview
    if any(g in query_lower for g in ['hi', 'hello', 'kingsford', 'tell me about', 'what is', 'help']):
        matched_topics.add('overview')

    # Query KnowledgeDocuments
    matched_docs = KnowledgeDocument.objects.filter(is_active=True, topic__in=matched_topics)
    if matched_docs.exists():
        doc_texts = []
        for doc in matched_docs:
            doc_texts.append(f"### {doc.title} ({doc.get_topic_display()})\n{doc.content}")
        retrieved_sections.append("## Institutional Knowledge & Policies:\n" + "\n\n".join(doc_texts))

    # 2. Programme & Course Retrieval
    prog_keywords = ['course', 'program', 'programme', 'degree', 'b.tech', 'm.tech', 'bba', 'mba', 'b.sc', 'm.sc', 'b.a', 'm.a', 'engineering', 'management', 'science', 'arts', 'ug', 'pg', 'undergraduate', 'postgraduate', 'curriculum', 'duration', 'eligibility']
    if any(kw in query_lower for kw in prog_keywords) or 'department' in query_lower:
        progs_qs = Programme.objects.filter(is_active=True).select_related('department').prefetch_related('fees')

        # Filter by department if mentioned
        for dept in Department.objects.all():
            if dept.name.lower() in query_lower or any(word in query_lower for word in dept.name.lower().split() if len(word) > 4):
                progs_qs = progs_qs.filter(department=dept)
                break

        # Filter by level
        if 'pg' in query_lower or 'postgraduate' in query_lower or 'master' in query_lower:
            progs_qs = progs_qs.filter(level='PG')
        elif 'ug' in query_lower or 'undergraduate' in query_lower or 'bachelor' in query_lower:
            progs_qs = progs_qs.filter(level='UG')

        progs = list(progs_qs[:8])
        if progs:
            prog_lines = []
            for p in progs:
                fee_summary = ", ".join([f"{f.fee_type}: {f.currency} {f.amount}" for f in p.fees.all() if f.amount is not None]) or "Fee not yet listed"
                prog_lines.append(
                    f"- **{p.name}** ({p.level}, Duration: {p.duration}, Department: {p.department.name})\n"
                    f"  Eligibility: {p.eligibility}\n"
                    f"  Description: {p.description}\n"
                    f"  Fees: {fee_summary}"
                )
            retrieved_sections.append("## Available Academic Programmes:\n" + "\n\n".join(prog_lines))

    # 3. Fee Structure Retrieval
    if any(kw in query_lower for kw in ['fee', 'fees', 'tuition', 'cost', 'charge', 'price', 'deposit', 'expenses']):
        general_fees = FeeInfo.objects.filter(programme__isnull=True)
        fee_lines = []
        for gf in general_fees:
            fee_lines.append(f"- **{gf.fee_type}**: {gf.currency} {gf.amount if gf.amount is not None else 'N/A'} ({gf.notes})")
        if fee_lines:
            retrieved_sections.append("## General Institutional Fee Schedule:\n" + "\n".join(fee_lines))

    # 4. Admissions Information & FAQs
    if any(kw in query_lower for kw in ['admission', 'apply', 'application', 'eligibility', 'deadline', 'document', 'faq', 'procedure', 'entrance']):
        adm_items = AdmissionInfo.objects.all().order_by('category', 'display_order')
        adm_lines = []
        for item in adm_items:
            # Check relevance
            cat_display = item.get_category_display()
            date_str = f" (Deadline: {item.deadline_date})" if item.deadline_date else ""
            adm_lines.append(f"[{cat_display}] {item.title}{date_str}: {item.content}")
        if adm_lines:
            retrieved_sections.append("## Admissions Rules, Deadlines, Documents & FAQs:\n" + "\n".join(adm_lines))

    # 5. Announcements & Upcoming Events
    if any(kw in query_lower for kw in ['announcement', 'notice', 'circular', 'news', 'update', 'event', 'events', 'summit', 'fest', 'hackathon']):
        anns = Announcement.objects.filter(is_published=True).order_by('-published_at')[:4]
        evs = Event.objects.all().order_by('start_datetime')[:4]

        ann_lines = [f"- [{a.category}] {a.title} ({a.published_at.strftime('%Y-%m-%d')}): {a.body}" for a in anns]
        ev_lines = [f"- {e.title} (Date: {e.start_datetime.strftime('%Y-%m-%d %H:%M')}, Venue: {e.venue}): {e.description}" for e in evs]

        news_text = ""
        if ann_lines:
            news_text += "### Recent Announcements:\n" + "\n".join(ann_lines) + "\n\n"
        if ev_lines:
            news_text += "### Upcoming Events:\n" + "\n".join(ev_lines)
        if news_text:
            retrieved_sections.append("## Campus Notices & Events:\n" + news_text)

    if not retrieved_sections:
        # Fallback to basic overview and contact
        fallback_docs = KnowledgeDocument.objects.filter(is_active=True, topic__in=['overview', 'contact'])
        retrieved_sections.append(
            "## Basic Kingsford University Information:\n" +
            "\n\n".join([f"### {d.title}\n{d.content}" for d in fallback_docs])
        )

    header = "=== Approved University Information (Official Verified Records) ===\n"
    footer = "\n=== End of Approved University Information ==="
    return header + "\n\n".join(retrieved_sections) + footer
