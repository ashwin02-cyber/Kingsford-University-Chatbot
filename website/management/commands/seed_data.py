import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from website.models import (
    Department, Programme, AdmissionInfo, FeeInfo,
    Announcement, Event, KnowledgeDocument
)

class Command(BaseCommand):
    help = "Seeds the Kingsford University database with idempotent sample data (Section 7 & FR-033)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Kingsford University sample data..."))

        # 1. 5 Departments
        departments_data = [
            {
                "name": "Department of Computer Science & Engineering",
                "description": "Excellence in computing, artificial intelligence, software engineering, and data sciences.",
                "head_name": "Prof. Dr. Alistair Vance",
            },
            {
                "name": "Department of Management & Business Studies",
                "description": "Leadership, strategic thinking, marketing, finance, and entrepreneurship education.",
                "head_name": "Prof. Dr. Meera Nambiar",
            },
            {
                "name": "Department of Mechanical & Civil Engineering",
                "description": "Foundational and advanced engineering in robotics, thermal sciences, and sustainable infrastructure.",
                "head_name": "Prof. Dr. Robert Chen",
            },
            {
                "name": "Department of Pure & Applied Sciences",
                "description": "Frontier research in physics, chemistry, computational mathematics, and biotechnology.",
                "head_name": "Prof. Dr. Sunita Kulkarni",
            },
            {
                "name": "Department of Humanities, Arts & Social Sciences",
                "description": "Critical inquiry, digital humanities, behavioral sciences, and international policy studies.",
                "head_name": "Prof. Dr. David Thorne",
            },
        ]

        created_depts = {}
        for dept in departments_data:
            obj, _ = Department.objects.update_or_create(
                name=dept["name"],
                defaults={
                    "description": dept["description"],
                    "head_name": dept["head_name"],
                }
            )
            created_depts[dept["name"]] = obj

        # 2. 14 Programmes (UG/PG)
        programmes_data = [
            # Computer Science
            {
                "department": created_depts["Department of Computer Science & Engineering"],
                "name": "B.Tech in Computer Science and Engineering",
                "level": "UG",
                "duration": "4 Years",
                "eligibility": "10+2 with Physics, Mathematics, and Chemistry with minimum 60% aggregate.",
                "description": "Comprehensive engineering curriculum covering algorithms, systems architecture, cloud computing, and cybersecurity.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Computer Science & Engineering"],
                "name": "B.Tech in Artificial Intelligence and Data Science",
                "level": "UG",
                "duration": "4 Years",
                "eligibility": "10+2 with Physics, Mathematics, and Computer Science/Chemistry with minimum 65% aggregate.",
                "description": "Specialized curriculum focusing on machine learning, deep learning, NLP, computer vision, and big data engineering.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Computer Science & Engineering"],
                "name": "M.Tech in Software Engineering & Cloud Computing",
                "level": "PG",
                "duration": "2 Years",
                "eligibility": "B.Tech/B.E. in CSE/IT or MCA with minimum 55% aggregate.",
                "description": "Advanced graduate programme in distributed architectures, microservices, cloud orchestration, and DevOps practices.",
                "is_active": True,
            },
            # Management
            {
                "department": created_depts["Department of Management & Business Studies"],
                "name": "Bachelor of Business Administration (BBA)",
                "level": "UG",
                "duration": "3 Years",
                "eligibility": "10+2 in any stream (Commerce, Science, Arts) with minimum 50% aggregate.",
                "description": "Undergraduate business programme developing foundational business acumen, marketing, human resources, and business analytics.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Management & Business Studies"],
                "name": "Master of Business Administration (MBA)",
                "level": "PG",
                "duration": "2 Years",
                "eligibility": "Bachelor's degree in any discipline with minimum 50% aggregate and valid national/university entrance score.",
                "description": "Flagship postgraduate programme offering specializations in Finance, Business Analytics, Marketing, and Operations.",
                "is_active": True,
            },
            # Mechanical & Civil
            {
                "department": created_depts["Department of Mechanical & Civil Engineering"],
                "name": "B.Tech in Mechanical Engineering",
                "level": "UG",
                "duration": "4 Years",
                "eligibility": "10+2 with Physics, Mathematics, and Chemistry with minimum 55% aggregate.",
                "description": "Core engineering branch emphasizing thermodynamics, CAD/CAM design, manufacturing technology, and automotive engineering.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Mechanical & Civil Engineering"],
                "name": "B.Tech in Civil and Environmental Engineering",
                "level": "UG",
                "duration": "4 Years",
                "eligibility": "10+2 with Physics, Mathematics, and Chemistry with minimum 55% aggregate.",
                "description": "Sustainable infrastructure development, structural engineering, smart water resources, and geotechnical analysis.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Mechanical & Civil Engineering"],
                "name": "M.Tech in Robotics and Automation",
                "level": "PG",
                "duration": "2 Years",
                "eligibility": "B.Tech/B.E. in Mechanical, Electrical, Mechatronics, or CSE with minimum 55% aggregate.",
                "description": "Interdisciplinary master's degree in industrial automation, robotic perception, kinematics, and cyber-physical systems.",
                "is_active": True,
            },
            # Science
            {
                "department": created_depts["Department of Pure & Applied Sciences"],
                "name": "B.Sc (Hons) in Physics with Computational Science",
                "level": "UG",
                "duration": "3 Years",
                "eligibility": "10+2 with Physics and Mathematics with minimum 55% aggregate.",
                "description": "Rigorous undergraduate training combining theoretical physics with computational simulations and data modeling.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Pure & Applied Sciences"],
                "name": "B.Sc (Hons) in Biotechnology & Bioinformatics",
                "level": "UG",
                "duration": "3 Years",
                "eligibility": "10+2 with Biology and Chemistry with minimum 55% aggregate.",
                "description": "Modern biological sciences exploring genetic engineering, bioprocess technology, and computational genomics.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Pure & Applied Sciences"],
                "name": "M.Sc in Applied Mathematics & Data Modeling",
                "level": "PG",
                "duration": "2 Years",
                "eligibility": "B.Sc in Mathematics, Statistics, or Computer Science with minimum 50% aggregate.",
                "description": "Advanced numerical analysis, statistical inference, financial mathematics, and predictive modeling.",
                "is_active": True,
            },
            # Arts & Humanities
            {
                "department": created_depts["Department of Humanities, Arts & Social Sciences"],
                "name": "B.A. (Hons) in English Literature & Digital Media",
                "level": "UG",
                "duration": "3 Years",
                "eligibility": "10+2 in any discipline with minimum 50% aggregate.",
                "description": "Literary analysis, cultural studies, digital journalism, and creative content architecture.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Humanities, Arts & Social Sciences"],
                "name": "B.A. in Psychology & Behavioral Studies",
                "level": "UG",
                "duration": "3 Years",
                "eligibility": "10+2 in any discipline with minimum 50% aggregate.",
                "description": "Exploration of cognitive psychology, social dynamics, psychopathology, and human behavioral research.",
                "is_active": True,
            },
            {
                "department": created_depts["Department of Humanities, Arts & Social Sciences"],
                "name": "M.A. in International Relations & Public Policy",
                "level": "PG",
                "duration": "2 Years",
                "eligibility": "Bachelor's degree in any discipline with minimum 50% aggregate.",
                "description": "Geopolitical studies, global governance, strategic diplomacy, and evidence-based public policy formulation.",
                "is_active": True,
            },
        ]

        created_progs = {}
        for prog in programmes_data:
            obj, _ = Programme.objects.update_or_create(
                department=prog["department"],
                name=prog["name"],
                defaults={
                    "level": prog["level"],
                    "duration": prog["duration"],
                    "eligibility": prog["eligibility"],
                    "description": prog["description"],
                    "is_active": prog["is_active"],
                }
            )
            created_progs[prog["name"]] = obj

        # 3. Admission Information (Procedure, Eligibility, Deadlines, Documents, 8 FAQs)
        admissions_data = [
            # Procedure
            {
                "category": "procedure",
                "title": "Step 1: Online Application Submission",
                "content": "Complete the digital application form on the Kingsford University website portal with your personal and academic credentials.",
                "deadline_date": None,
                "display_order": 1,
            },
            {
                "category": "procedure",
                "title": "Step 2: Document Verification",
                "content": "Upload certified scanned copies of academic transcripts, identity proof, and recommendation letters for institutional scrutiny.",
                "deadline_date": None,
                "display_order": 2,
            },
            {
                "category": "procedure",
                "title": "Step 3: Entrance & Merit Evaluation",
                "content": "Shortlisted candidates appear for Kingsford Scholastic Aptitude Test (KSAT) or are evaluated on national test percentiles (e.g. JEE/CAT/CUET).",
                "deadline_date": None,
                "display_order": 3,
            },
            {
                "category": "procedure",
                "title": "Step 4: Counseling & Provisional Admission",
                "content": "Attend the seat allocation counseling round, verify original certificates, and secure provisional admission with initial fee payment.",
                "deadline_date": None,
                "display_order": 4,
            },
            # Eligibility
            {
                "category": "eligibility",
                "title": "Undergraduate Eligibility Overview",
                "content": "Applicants must have passed higher secondary education (10+2 or equivalent) with minimum 50-65% aggregate depending on department and programme.",
                "deadline_date": None,
                "display_order": 5,
            },
            {
                "category": "eligibility",
                "title": "Postgraduate Eligibility Overview",
                "content": "Applicants must hold a recognized Bachelor's degree (3 or 4-year programme) with at least 50-55% aggregate marks or equivalent CGPA.",
                "deadline_date": None,
                "display_order": 6,
            },
            # Deadlines
            {
                "category": "deadline",
                "title": "Early Bird Scholarship Application Deadline",
                "content": "Last date to apply for early bird admission and merit fee concessions for academic year 2026-27.",
                "deadline_date": datetime.date(2026, 5, 31),
                "display_order": 7,
            },
            {
                "category": "deadline",
                "title": "Undergraduate Phase 1 Admissions Deadline",
                "content": "Final date for submitting application forms for all UG engineering, science, management, and arts programmes.",
                "deadline_date": datetime.date(2026, 6, 30),
                "display_order": 8,
            },
            {
                "category": "deadline",
                "title": "Postgraduate Admissions Deadline",
                "content": "Final date for postgraduate applications for M.Tech, MBA, M.Sc, and M.A. programmes.",
                "deadline_date": datetime.date(2026, 7, 15),
                "display_order": 9,
            },
            {
                "category": "deadline",
                "title": "International Students Application Deadline",
                "content": "Submission deadline for foreign nationals, PIO, and NRI quota applications.",
                "deadline_date": datetime.date(2026, 6, 15),
                "display_order": 10,
            },
            # Documents
            {
                "category": "document",
                "title": "Mandatory Application Documents",
                "content": "1. 10th Standard Mark Sheet and Passing Certificate\n2. 12th Standard Mark Sheet and Passing Certificate\n3. Bachelor's Degree Certificate and Grade Cards (for PG programmes)\n4. Valid Photo Identification (Aadhaar Card, Passport, or Voter ID)\n5. Transfer Certificate and Character/Conduct Certificate from last attended institution\n6. Four recent passport-sized color photographs\n7. Category / Reservation Certificate (if claiming quota benefits)\n8. Migration Certificate (for students from other boards/universities)",
                "deadline_date": None,
                "display_order": 11,
            },
            # 8 FAQs
            {
                "category": "faq",
                "title": "How do I apply for undergraduate admissions at Kingsford?",
                "content": "You can apply through our online admissions portal. Register an account, fill in personal and educational details, upload required mark sheets, and submit the nominal application processing fee online.",
                "deadline_date": None,
                "display_order": 12,
            },
            {
                "category": "faq",
                "title": "Can I apply for more than one programme concurrently?",
                "content": "Yes, candidates can submit preferences for up to 3 programmes within one application. Seat counseling will consider your highest preferred programme according to merit ranking.",
                "deadline_date": None,
                "display_order": 13,
            },
            {
                "category": "faq",
                "title": "What is the minimum aggregate percentage required for B.Tech in CSE?",
                "content": "For B.Tech in Computer Science and Engineering, candidates must have secured at least 60% aggregate in Physics, Mathematics, and Chemistry in their 10+2 board examinations.",
                "deadline_date": None,
                "display_order": 14,
            },
            {
                "category": "faq",
                "title": "Are scholarships available for first-year admitted students?",
                "content": "Yes. Kingsford offers generous merit scholarships: up to 100% tuition waiver for board/entrance toppers (>95%), 50% waiver for >90%, as well as need-based financial aid and sports quota concessions.",
                "deadline_date": None,
                "display_order": 15,
            },
            {
                "category": "faq",
                "title": "Is on-campus hostel accommodation guaranteed for outstation students?",
                "content": "Hostel rooms are allotted on a first-come, first-served basis during admission counseling. Outstation and international students receive priority allotment in our modern residential hostels.",
                "deadline_date": None,
                "display_order": 16,
            },
            {
                "category": "faq",
                "title": "What is the policy for fee refund if admission is cancelled?",
                "content": "Kingsford University strictly follows UGC refund norms: 100% refund (minus nominal processing fee) if cancelled 15 days or more before the formally announced commencement date of classes.",
                "deadline_date": None,
                "display_order": 17,
            },
            {
                "category": "faq",
                "title": "Are entrance test scores from national testing bodies accepted?",
                "content": "Yes. We accept valid scores from JEE Main for B.Tech, CAT/MAT/XAT for MBA, GATE for M.Tech, and CUET for general undergraduate and postgraduate admissions.",
                "deadline_date": None,
                "display_order": 18,
            },
            {
                "category": "faq",
                "title": "How can international or NRI students apply?",
                "content": "International and NRI candidates can apply directly through the International Students Office channel. Equivalent high school or baccalaureate credentials with AIU equivalence certificate are required.",
                "deadline_date": None,
                "display_order": 19,
            },
        ]

        for item in admissions_data:
            AdmissionInfo.objects.update_or_create(
                category=item["category"],
                title=item["title"],
                defaults={
                    "content": item["content"],
                    "deadline_date": item["deadline_date"],
                    "display_order": item["display_order"],
                }
            )

        # 4. FeeInfo per Programme and General Fees in ₹ (INR)
        fees_data = [
            # Programme Tuition Fees
            {
                "programme": created_progs["B.Tech in Computer Science and Engineering"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("185000.00"),
                "currency": "INR",
                "notes": "Includes access to high-performance computing clusters and cloud sandbox.",
            },
            {
                "programme": created_progs["B.Tech in Artificial Intelligence and Data Science"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("190000.00"),
                "currency": "INR",
                "notes": "Includes GPU lab hours and AI specialized workstation access.",
            },
            {
                "programme": created_progs["M.Tech in Software Engineering & Cloud Computing"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("140000.00"),
                "currency": "INR",
                "notes": "Graduate research and software testing lab access included.",
            },
            {
                "programme": created_progs["Bachelor of Business Administration (BBA)"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("125000.00"),
                "currency": "INR",
                "notes": "Includes business simulations, industry guest lectures, and seminar kits.",
            },
            {
                "programme": created_progs["Master of Business Administration (MBA)"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("245000.00"),
                "currency": "INR",
                "notes": "Includes case study materials, leadership bootcamps, and executive mentoring.",
            },
            {
                "programme": created_progs["B.Tech in Mechanical Engineering"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("150000.00"),
                "currency": "INR",
                "notes": "Includes robotics laboratory and workshop consumables.",
            },
            {
                "programme": created_progs["B.Tech in Civil and Environmental Engineering"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("140000.00"),
                "currency": "INR",
                "notes": "Includes survey equipment and geotechnical testing lab charges.",
            },
            {
                "programme": created_progs["M.Tech in Robotics and Automation"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("155000.00"),
                "currency": "INR",
                "notes": "Includes mechatronics prototyping lab and robotic arm access.",
            },
            {
                "programme": created_progs["B.Sc (Hons) in Physics with Computational Science"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("95000.00"),
                "currency": "INR",
                "notes": "Includes modern physics laboratory and computational simulation tools.",
            },
            {
                "programme": created_progs["B.Sc (Hons) in Biotechnology & Bioinformatics"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("110000.00"),
                "currency": "INR",
                "notes": "Includes wet lab consumables and bioinformatics database subscriptions.",
            },
            {
                "programme": created_progs["M.Sc in Applied Mathematics & Data Modeling"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("90000.00"),
                "currency": "INR",
                "notes": "Includes mathematical computing software licenses.",
            },
            {
                "programme": created_progs["B.A. (Hons) in English Literature & Digital Media"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("75000.00"),
                "currency": "INR",
                "notes": "Includes media studio access and digital editing lab.",
            },
            {
                "programme": created_progs["B.A. in Psychology & Behavioral Studies"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("80000.00"),
                "currency": "INR",
                "notes": "Includes experimental psychology laboratory assessments.",
            },
            {
                "programme": created_progs["M.A. in International Relations & Public Policy"],
                "fee_type": "Annual Tuition Fee",
                "amount": Decimal("85000.00"),
                "currency": "INR",
                "notes": "Includes policy simulation immersion and diplomatic study visits.",
            },
            # General Institutional Fees
            {
                "programme": None,
                "fee_type": "Hostel & Mess Fee (Standard Twin Sharing)",
                "amount": Decimal("75000.00"),
                "currency": "INR",
                "notes": "Per academic year. Includes 4 meals/day, high-speed Wi-Fi, electricity and housekeeping.",
            },
            {
                "programme": None,
                "fee_type": "Hostel & Mess Fee (Premium AC Single)",
                "amount": Decimal("110000.00"),
                "currency": "INR",
                "notes": "Per academic year. Air-conditioned private room with attached washroom and mess.",
            },
            {
                "programme": None,
                "fee_type": "Examination Fee",
                "amount": Decimal("4000.00"),
                "currency": "INR",
                "notes": "Per semester. Covers end-term examinations, grade card printing, and evaluation.",
            },
            {
                "programme": None,
                "fee_type": "One-Time Caution Deposit",
                "amount": Decimal("10000.00"),
                "currency": "INR",
                "notes": "Fully refundable upon completion of programme and clearance of library dues.",
            },
            {
                "programme": None,
                "fee_type": "Annual Sports & Gymnasium Facility Fee",
                "amount": Decimal("3500.00"),
                "currency": "INR",
                "notes": "Covers olympic swimming pool, indoor badminton, gym, and athletics track access.",
            },
        ]

        for fee in fees_data:
            FeeInfo.objects.update_or_create(
                programme=fee["programme"],
                fee_type=fee["fee_type"],
                defaults={
                    "amount": fee["amount"],
                    "currency": fee["currency"],
                    "notes": fee["notes"],
                }
            )

        # 5. Knowledge Documents (Approved University Information for KAI retrieval)
        knowledge_docs = [
            {
                "topic": "overview",
                "title": "Kingsford University Overview & Institutional Profile",
                "content": (
                    "Kingsford University is a premier, multidisciplinary higher education institution "
                    "dedicated to academic excellence, forward-looking scientific research, and future-ready education. "
                    "Institutional Statistics: NAAC A+ Accredited institution, offering 100+ UG and PG programmes, "
                    "housing 50+ cutting-edge research centres, and serving an active student body of over 15,000+ students. "
                    "Located across a sprawling 120-acre green campus in Knowledge Corridor, Tech City, "
                    "Kingsford balances rigorous foundational learning with modern digital skills and societal leadership."
                ),
                "keywords": "overview, statistics, naac, programmes, students, campus, ranking, accreditation, about kingsford",
            },
            {
                "topic": "vision_mission",
                "title": "Vision and Mission of Kingsford University",
                "content": (
                    "Vision: To be an internationally recognized center of academic innovation and transformative learning, "
                    "cultivating ethical leaders who address complex global challenges with creativity and empathy.\n"
                    "Mission:\n"
                    "1. Provide rigorous, experiential education that bridges foundational theoretical depth and applied industry practice.\n"
                    "2. Foster an inclusive and interdisciplinary research environment that advances scientific innovation and social equity.\n"
                    "3. Instill enduring values of civic responsibility, sustainability, and lifelong learning in every graduate."
                ),
                "keywords": "vision, mission, core values, philosophy, goals, ideals, objective",
            },
            {
                "topic": "history",
                "title": "History and Heritage of Kingsford University",
                "content": (
                    "Founded in 1994 as the Kingsford Institute of Advanced Technology, the institution emerged "
                    "with a foundational vision to empower young minds with engineering and scientific proficiency. "
                    "In 2008, following sustained academic distinction and research milestones, the institution was granted "
                    "full university status under the State Legislative Act. Over three decades, Kingsford has evolved "
                    "into a comprehensive university comprising five faculties, modern research labs, and an alumni network "
                    "spanning top global enterprises, academic institutions, and public service organizations."
                ),
                "keywords": "history, heritage, foundation, establishment, background, origin, milestone",
            },
            {
                "topic": "leadership",
                "title": "Leadership and University Administration",
                "content": (
                    "The governance of Kingsford University is steered by accomplished academicians and leaders:\n"
                    "- Chancellor: Dr. Eleanor Kingsford, prominent philanthropist and industrialist.\n"
                    "- Vice-Chancellor: Prof. Dr. Arthur Pendelton, renowned scientist and fellow of the Indian National Science Academy.\n"
                    "- Pro Vice-Chancellor (Academics): Prof. Dr. Rachel Vasudevan.\n"
                    "- Registrar: Dr. K. Ramanathan.\n"
                    "- Dean of Student Affairs: Prof. Michael Gallagher.\n"
                    "- Controller of Examinations: Dr. Savita Mukherjee."
                ),
                "keywords": "leadership, administration, chancellor, vice-chancellor, registrar, dean, governance, officials",
            },
            {
                "topic": "accreditation",
                "title": "Accreditations, Rankings and Achievements",
                "content": (
                    "Accreditation & Quality Benchmarks:\n"
                    "- National Assessment and Accreditation Council (NAAC): Re-accredited with an 'A+' Grade (CGPA 3.62).\n"
                    "- National Board of Accreditation (NBA): Engineering and management programmes are tier-1 accredited.\n"
                    "- NIRF Rankings: Positioned consistently in the Top 50 university band nationwide.\n"
                    "- ISO 9001:2015 certified for green campus sustainability and quality management systems.\n"
                    "- Member of the Association of Commonwealth Universities (ACU)."
                ),
                "keywords": "accreditation, naac, nba, nirf, ranking, achievement, awards, rating, quality",
            },
            {
                "topic": "scholarship",
                "title": "Scholarships and Financial Aid Schemes",
                "content": (
                    "Kingsford University ensures that financial constraints do not impede meritorious students:\n"
                    "1. Merit Scholarship: 100% tuition fee waiver for students scoring 95%+ in qualifying examination; "
                    "50% waiver for students scoring between 90% and 94.9%.\n"
                    "2. Economically Weaker Section (EWS) Need-Based Aid: Up to 50% tuition reduction for students "
                    "with certified family annual income under ₹3,50,000.\n"
                    "3. Sports Excellence Scholarship: 25% to 75% fee concession for student athletes representing at state, "
                    "national, or international tournaments.\n"
                    "4. Sibling Concession: 10% tuition discount when two or more siblings study concurrently.\n"
                    "Scholarship renewal requires maintaining a minimum 8.0 CGPA each academic year."
                ),
                "keywords": "scholarship, financial aid, fee waiver, concession, merit, sports scholarship, ews, funding",
            },
            {
                "topic": "calendar",
                "title": "Academic Calendar 2026-27",
                "content": (
                    "Key Academic Calendar Dates for 2026-2027:\n"
                    "- Fall / Odd Semester Commencement: August 3, 2026\n"
                    "- Mid-Semester Examination: October 12 - October 19, 2026\n"
                    "- Diwali / Fall Break: November 6 - November 10, 2026\n"
                    "- End-Semester Practical & Theory Exams: December 7 - December 23, 2026\n"
                    "- Winter Vacation: December 24, 2026 - January 10, 2027\n"
                    "- Spring / Even Semester Commencement: January 11, 2027\n"
                    "- Mid-Semester Examination: March 15 - March 22, 2027\n"
                    "- End-Semester Examination: May 17 - June 2, 2027\n"
                    "- Summer Internship & Recess: June 3 - July 31, 2027."
                ),
                "keywords": "calendar, academic year, semester dates, holidays, schedule, term dates, break, vacation",
            },
            {
                "topic": "exams",
                "title": "Examinations, Grading System and Evaluation Rules",
                "content": (
                    "Kingsford University operates on a continuous assessment and semester-end evaluation framework:\n"
                    "- Grading: 10-point CGPA scale (O: 10, A+: 9, A: 8, B+: 7, B: 6, C: 5, P: 4, F: 0).\n"
                    "- Attendance Rule: A minimum 75% classroom and laboratory attendance is mandatory to sit for end-semester exams.\n"
                    "- Evaluation Split: 40% Continuous Internal Evaluation (tests, quizzes, assignments, projects) + 60% Semester End Examination.\n"
                    "- Revaluation & Supplementary: Students may apply for answer script rechecking within 10 days of result announcement; supplementary exams are held in July."
                ),
                "keywords": "exams, examination, grading, results, marks, cgpa, attendance, evaluation, supplementary, pass marks",
            },
            {
                "topic": "hostel",
                "title": "Hostel and Student Residential Accommodation",
                "content": (
                    "Kingsford provides modern on-campus residential housing with 24/7 security and high-speed Wi-Fi:\n"
                    "- Boys Hostels: Oak House and Pine House.\n"
                    "- Girls Hostels: Maple House and Cedar House.\n"
                    "- Room Types: Twin sharing non-AC (₹75,000/year including mess) and single air-conditioned rooms (₹1,10,000/year).\n"
                    "- Dining: Multi-cuisine hygienic dining hall providing 4 meals a day (breakfast, lunch, evening snacks, dinner) with vegetarian and non-vegetarian selections.\n"
                    "- Amenities: Laundromat, study recreation lounge, fitness gym, solar water heating, and medical first-aid post with 24/7 on-call ambulance."
                ),
                "keywords": "hostel, accommodation, dorms, rooms, mess, food, residential, stay, boarding, facilities",
            },
            {
                "topic": "library",
                "title": "Sir C.V. Raman Central Library",
                "content": (
                    "The Sir C.V. Raman Central Library is a premier learning resource center spanning 4 floors:\n"
                    "- Holdings: Over 120,000 print monographs, 15,000+ peer-reviewed e-journals, and 500,000+ digital e-books.\n"
                    "- Digital Databases: Subscriptions to IEEE Xplore, ScienceDirect, ACM Digital Library, SpringerLink, JSTOR, and LexisNexis.\n"
                    "- Working Hours: 8:00 AM to 11:00 PM on weekdays; 24/7 open study wing during end-semester examination periods.\n"
                    "- Facilities: Dedicated PhD research carrels, multimedia audio-visual lab, RFID automated issue/return kiosks, and collaborative study pods."
                ),
                "keywords": "library, books, journals, study rooms, digital library, ieee, ebooks, reading room, timings",
            },
            {
                "topic": "facilities",
                "title": "Campus Facilities, Laboratories and Infrastructure",
                "content": (
                    "Kingsford University features state-of-the-art campus infrastructure:\n"
                    "- Advanced Computing Labs: 1,500+ high-end workstations with dedicated GPU clusters for AI research.\n"
                    "- Specialized Labs: Robotics & Automation Lab, Environmental Analysis Lab, High-Performance CAD Center, and Biotech Cleanrooms.\n"
                    "- Sports Complex: Olympic-sized swimming pool, indoor wooden badminton courts, synthetic basketball court, and full-size cricket/football ground.\n"
                    "- Campus Healthcare: University health clinic with resident physicians, emergency beds, and pharmacy.\n"
                    "- Food Court & Cafeteria: Diverse multi-cuisine outlets, bakeries, and organic juice bars.\n"
                    "- Connectivity: 10 Gbps fiber-optic Wi-Fi covering academic, hostel, and recreational zones."
                ),
                "keywords": "facilities, labs, infrastructure, sports, gym, cafeteria, wifi, health center, clinic, swimming pool, computer lab",
            },
            {
                "topic": "contact",
                "title": "Official University Contact Details and Location",
                "content": (
                    "Kingsford University Official Sample Contact Directory:\n"
                    "- Campus Address: Kingsford University Campus, Knowledge Corridor, Tech City, Sample State - 560000, India.\n"
                    "- General Inquiries: info@kingsford.example | Phone: +91 00000 00000\n"
                    "- Admissions Helpdesk: admissions@kingsford.example | Phone: +91 00000 00001\n"
                    "- Controller of Examinations: exams@kingsford.example | Phone: +91 00000 00002\n"
                    "- Student Affairs & Hostel Office: hostel@kingsford.example | Phone: +91 00000 00003\n"
                    "- Placement & Corporate Relations: placements@kingsford.example | Phone: +91 00000 00004\n"
                    "- Working Hours: Monday to Friday, 9:00 AM to 5:00 PM IST (Helpdesk available 24/7 via KAI)."
                ),
                "keywords": "contact, email, phone, helpline, address, location, office, support, reaching kingsford, hours",
            },
        ]

        for doc in knowledge_docs:
            KnowledgeDocument.objects.update_or_create(
                topic=doc["topic"],
                title=doc["title"],
                defaults={
                    "content": doc["content"],
                    "keywords": doc["keywords"],
                    "is_active": True,
                }
            )

        # 6. 6 Published Announcements (Dates in 2026-27)
        announcements_data = [
            {
                "title": "Admissions Open for Academic Year 2026-27: UG & PG Applications Live",
                "body": (
                    "Applications are now invited for all undergraduate and postgraduate programmes for the 2026-27 academic session. "
                    "Prospective candidates may apply online through the admissions portal before the specified deadlines. "
                    "Early bird merit scholarship considerations will be prioritized for applications received before May 31, 2026."
                ),
                "category": "Admission",
                "published_at": timezone.make_aware(datetime.datetime(2026, 5, 1, 9, 0)),
                "is_published": True,
            },
            {
                "title": "Merit and Need-Based Scholarship Applications Open for 2026-27",
                "body": (
                    "The University Scholarship Committee invites applications from eligible admitted students for the 2026-27 academic year. "
                    "Available schemes include Merit Scholarships (up to 100% tuition waiver), EWS Financial Aid, and Sports Excellence concessions. "
                    "Apply through the Student Affairs desk with supporting documents."
                ),
                "category": "Admission",
                "published_at": timezone.make_aware(datetime.datetime(2026, 5, 15, 10, 30)),
                "is_published": True,
            },
            {
                "title": "Kingsford University Re-Accredited with NAAC A+ Grade (CGPA 3.62)",
                "body": (
                    "Kingsford University has been successfully re-accredited with the prestigious 'A+' grade by the National Assessment and "
                    "Accreditation Council (NAAC) with an institutional score of 3.62. This milestone reflects our unwavering commitment to "
                    "high-quality pedagogy, research breakthroughs, and campus excellence."
                ),
                "category": "General",
                "published_at": timezone.make_aware(datetime.datetime(2026, 6, 10, 11, 0)),
                "is_published": True,
            },
            {
                "title": "Inauguration of New Centre for Artificial Intelligence and Quantum Systems",
                "body": (
                    "The university has inaugurated its flagship 25,000 sq.ft. Centre for Artificial Intelligence and Quantum Systems, "
                    "equipped with high-density GPU computing clusters and collaborative industry sandboxes for undergraduate and doctoral researchers."
                ),
                "category": "General",
                "published_at": timezone.make_aware(datetime.datetime(2026, 7, 20, 14, 0)),
                "is_published": True,
            },
            {
                "title": "Guidelines for Supplementary and Improvement Examinations 2026",
                "body": (
                    "The Examination Cell has released registration guidelines and schedule for the Supplementary and Grade Improvement "
                    "Examinations. Eligible students must submit their examination registration forms through the portal by September 30, 2026."
                ),
                "category": "Examination",
                "published_at": timezone.make_aware(datetime.datetime(2026, 9, 20, 10, 0)),
                "is_published": True,
            },
            {
                "title": "Schedule Released for Odd Semester End Examinations November-December 2026",
                "body": (
                    "The complete timetable for Odd Semester End Theory and Laboratory Examinations (UG & PG) has been officially released. "
                    "Examinations will commence on December 7, 2026. Hall tickets will be downloadable via the examination portal from November 25."
                ),
                "category": "Examination",
                "published_at": timezone.make_aware(datetime.datetime(2026, 10, 15, 16, 0)),
                "is_published": True,
            },
        ]

        for ann in announcements_data:
            Announcement.objects.update_or_create(
                title=ann["title"],
                defaults={
                    "body": ann["body"],
                    "category": ann["category"],
                    "published_at": ann["published_at"],
                    "is_published": ann["is_published"],
                }
            )

        # 7. 6 Upcoming Events (Dates in 2026-27, starting in the future relative to typical academic year)
        events_data = [
            {
                "title": "Kingsford Global Innovation & Tech Summit 2026",
                "description": "Three-day international symposium uniting global tech luminaries, enterprise architects, and university researchers exploring generative computing and sustainable technologies.",
                "venue": "Main University Auditorium & Exhibition Hall",
                "start_datetime": timezone.make_aware(datetime.datetime(2026, 9, 12, 9, 30)),
                "end_datetime": timezone.make_aware(datetime.datetime(2026, 9, 14, 17, 30)),
            },
            {
                "title": "Annual Inter-University Cultural Fest: KRONOS 2026",
                "description": "The largest cultural extravaganza of the region featuring musical concerts, theatrical dramas, art exhibitions, and competitive debates across 40+ universities.",
                "venue": "Campus Central Amphitheatre & Open Air Theatre",
                "start_datetime": timezone.make_aware(datetime.datetime(2026, 10, 22, 10, 0)),
                "end_datetime": timezone.make_aware(datetime.datetime(2026, 10, 24, 22, 0)),
            },
            {
                "title": "National Conference on Sustainable Energy & Green Materials",
                "description": "Scientific conference presenting peer-reviewed research papers on renewable solar photovoltaics, battery storage chemistry, and ecological urban construction.",
                "venue": "Sir C.V. Raman Science Complex Seminar Hall",
                "start_datetime": timezone.make_aware(datetime.datetime(2026, 11, 5, 9, 0)),
                "end_datetime": timezone.make_aware(datetime.datetime(2026, 11, 6, 18, 0)),
            },
            {
                "title": "Kingsford Annual Career Fair & Campus Placement Drive 2026",
                "description": "Flagship recruitment event connecting graduating undergraduate and master's students with over 150+ premier multinational corporations and technology startups.",
                "venue": "University Indoor Sports & Convention Arena",
                "start_datetime": timezone.make_aware(datetime.datetime(2026, 12, 4, 9, 0)),
                "end_datetime": timezone.make_aware(datetime.datetime(2026, 12, 5, 17, 0)),
            },
            {
                "title": "International Hackathon: HackKingsford 2027",
                "description": "A 36-hour non-stop student hackathon addressing social impact challenges in healthcare, clean energy, and accessible education with prizes worth ₹5,00,000.",
                "venue": "AI Innovation Sandbox & Computing Hub",
                "start_datetime": timezone.make_aware(datetime.datetime(2027, 1, 23, 9, 0)),
                "end_datetime": timezone.make_aware(datetime.datetime(2027, 1, 24, 21, 0)),
            },
            {
                "title": "University Sports Meet & Athletic Championship 2027",
                "description": "Inter-departmental track and field events, swimming competitions, football, basketball, and badminton championships celebrating athletic excellence.",
                "venue": "University Athletic Stadium & Olympic Aquatic Center",
                "start_datetime": timezone.make_aware(datetime.datetime(2027, 2, 18, 8, 30)),
                "end_datetime": timezone.make_aware(datetime.datetime(2027, 2, 20, 18, 0)),
            },
        ]

        for ev in events_data:
            Event.objects.update_or_create(
                title=ev["title"],
                defaults={
                    "description": ev["description"],
                    "venue": ev["venue"],
                    "start_datetime": ev["start_datetime"],
                    "end_datetime": ev["end_datetime"],
                }
            )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded sample data:\n"
            f"- {Department.objects.count()} Departments\n"
            f"- {Programme.objects.count()} Programmes\n"
            f"- {AdmissionInfo.objects.count()} Admission Info items (including 8 FAQs)\n"
            f"- {FeeInfo.objects.count()} Fee structure records\n"
            f"- {KnowledgeDocument.objects.count()} Knowledge documents for KAI\n"
            f"- {Announcement.objects.count()} Announcements\n"
            f"- {Event.objects.count()} Upcoming Events\n"
            f"All sample records marked and ready."
        ))
