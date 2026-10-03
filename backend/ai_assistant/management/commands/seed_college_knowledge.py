from django.core.management.base import BaseCommand
from ai_assistant.models import KnowledgeCategory, KnowledgeItem, FAQItem
from ai_assistant.services.rag_service import sync_knowledge_to_workspace
from django.conf import settings


class Command(BaseCommand):
    help = 'Seeds realistic college knowledge base for NMC College'

    def handle(self, *args, **options):
        self.stdout.write("Seeding NMC College knowledge base...")

        # 1. Categories
        categories_data = [
            ('GENERAL', 'General Information', 'College profile, address, campus overview, and contact info', 1),
            ('DEPARTMENTS', 'Departments & Courses', 'Academic departments, degrees offered, and syllabi', 2),
            ('FACULTY', 'Faculty & HODs', 'Heads of Departments and faculty profiles', 3),
            ('ADMISSIONS', 'Admissions & Eligibility', 'Admission requirements, eligibility criteria, and documents', 4),
            ('FEES', 'Fees & Scholarships', 'Fee structures, exam fees, payment deadlines, and concessions', 5),
            ('EXAMS', 'Examinations & Results', 'Internal exams, semester assessments, and grading rules', 6),
            ('CALENDAR', 'Academic Calendar & Dates', 'Semester commencement, holidays, and exam schedules', 7),
            ('TIMINGS', 'College Timings', 'Class hours, office hours, and library timings', 8),
            ('RULES', 'Rules & Regulations', 'Attendance policy, dress code, and campus guidelines', 9),
            ('FACILITIES', 'Campus Facilities & Labs', 'Computer labs, library, Wi-Fi, transport, and sports', 10),
            ('HOSTEL', 'Hostel & Mess', 'Accommodation, mess timings, rules, and hostel warden contact', 11),
            ('PLACEMENTS', 'Placements & Careers', 'Placement cell, recruiters, and placement training', 12),
            ('FAQ', 'Frequently Asked Questions', 'Quick answers to common student inquiries', 13),
        ]

        cat_objs = {}
        for code, name, desc, order in categories_data:
            cat, _ = KnowledgeCategory.objects.get_or_create(
                code=code,
                defaults={'name': name, 'description': desc, 'display_order': order}
            )
            cat_objs[code] = cat

        # 2. Knowledge Items
        items_data = [
            # GENERAL
            (
                'GENERAL',
                'NMC College Address & Contact Information',
                (
                    "• *College Name*: Nehru Memorial College (Autonomous) / NMC College\n"
                    "• *Address*: Puthanampatti - 621 007, Musiri Taluk, Tiruchirappalli District, Tamil Nadu, India.\n"
                    "• *Phone*: +91 4327 234227, +91 4327 234827\n"
                    "• *Email*: principal@nmc.ac.in, admission@nmc.ac.in\n"
                    "• *Official Website*: https://www.nmc.ac.in\n"
                    "• *Principal*: Dr. K. Radhakrishnan, M.Sc., Ph.D."
                ),
                'address, location, contact, phone, email, website, principal, where is college'
            ),
            # TIMINGS
            (
                'TIMINGS',
                'Official College Timings & Working Hours',
                (
                    "• *Regular Class Timings*: 9:30 AM to 4:00 PM (Monday to Friday)\n"
                    "• *Administrative Office Hours*: 9:00 AM to 5:00 PM (Monday to Saturday, 2nd Saturday holiday)\n"
                    "• *Central Library Hours*: 8:30 AM to 6:00 PM on all working days\n"
                    "• *Lunch Break*: 1:00 PM to 1:45 PM"
                ),
                'timings, college timings, office hours, working hours, library timings, lunch break'
            ),
            # DEPARTMENTS & HODs
            (
                'DEPARTMENTS',
                'Academic Departments & Courses Offered',
                (
                    "NMC College offers Undergraduate, Postgraduate, and Research programmes across multiple departments:\n"
                    "1. *Master of Computer Applications (MCA)* - 2 Year PG Degree\n"
                    "2. *Department of Computer Science* - B.Sc. CS, M.Sc. CS, Ph.D.\n"
                    "3. *Department of Data Science & AI* - B.Sc. Data Science\n"
                    "4. *Department of Electronics & Communication* - B.Sc., M.Sc.\n"
                    "5. *Department of Mathematics* - B.Sc., M.Sc., Ph.D.\n"
                    "6. *Department of Commerce & Management* - B.Com, B.Com CA, BBA, M.Com\n"
                    "7. *Department of Physics & Chemistry* - B.Sc., M.Sc."
                ),
                'departments, courses, mca, computer science, data science, commerce, degrees'
            ),
            (
                'FACULTY',
                'HOD of MCA Department & Faculty Details',
                (
                    "• *Department*: Master of Computer Applications (MCA)\n"
                    "• *Head of the Department (HOD)*: *Dr. M. Muralidharan, M.C.A., M.Phil., Ph.D.*\n"
                    "• *HOD Cabin*: PG Block, First Floor, Room No. 204\n"
                    "• *Department Email*: hod.mca@nmc.ac.in\n"
                    "• *Key Faculty Members*:\n"
                    "  - Dr. S. Senthil Kumar (Associate Professor - Cloud Computing & AI)\n"
                    "  - Prof. P. Kavitha (Assistant Professor - Web Technologies & Full Stack)\n"
                    "  - Dr. R. Anitha (Assistant Professor - Data Structures & Python)"
                ),
                'mca hod, hod of mca, head of mca, mca faculty, muralidharan, mca department head'
            ),
            (
                'FACULTY',
                'List of Department Heads (HODs)',
                (
                    "• *MCA*: Dr. M. Muralidharan (hod.mca@nmc.ac.in)\n"
                    "• *Computer Science*: Dr. K. Mani (hod.cs@nmc.ac.in)\n"
                    "• *Data Science*: Prof. T. Saravanan (hod.ds@nmc.ac.in)\n"
                    "• *Mathematics*: Dr. V. Balasubramanian (hod.maths@nmc.ac.in)\n"
                    "• *Commerce*: Dr. N. Rajendran (hod.commerce@nmc.ac.in)\n"
                    "• *Physics*: Dr. A. Venkatesan (hod.physics@nmc.ac.in)"
                ),
                'hods, department heads, list of hods, cs hod, hod contacts'
            ),
            # MCA SUBJECTS
            (
                'DEPARTMENTS',
                'MCA Curriculum and Subjects (Semester-wise)',
                (
                    "The MCA program is a 2-year (4-semester) autonomous curriculum:\n\n"
                    "• *Semester 1*:\n"
                    "  - Advanced Data Structures and Algorithms\n"
                    "  - Object-Oriented Software Engineering (Java & Design Patterns)\n"
                    "  - Relational Database Management Systems (RDBMS & SQL)\n"
                    "  - Python Programming & Data Analysis\n"
                    "  - Data Structures & DB Lab\n\n"
                    "• *Semester 2*:\n"
                    "  - Full Stack Web Development (React & Node.js)\n"
                    "  - Advanced Operating Systems & Cloud Computing\n"
                    "  - Machine Learning Fundamentals\n"
                    "  - Mobile Application Development (Flutter/Android)\n"
                    "  - Full Stack Development Lab\n\n"
                    "• *Semester 3*:\n"
                    "  - Artificial Intelligence & Deep Learning\n"
                    "  - Cyber Security & Cryptography\n"
                    "  - Big Data Analytics & NoSQL\n"
                    "  - DevOps & Microservices Architecture\n"
                    "  - AI & Cloud Capstone Lab\n\n"
                    "• *Semester 4*:\n"
                    "  - 6-Month Full-Time Industry Internship & Project Dissertation"
                ),
                'mca subjects, mca syllabus, subjects in mca, mca courses, what are the mca subjects, curriculum'
            ),
            # ADMISSIONS & DOCUMENTS
            (
                'ADMISSIONS',
                'Documents Required for Admission',
                (
                    "Students seeking admission must submit original and photocopies of:\n"
                    "1. *10th (SSLC) Marksheet*\n"
                    "2. *12th (HSC) Marksheet*\n"
                    "3. *Undergraduate Degree Marksheets & Provisional Certificate* (for PG / MCA applicants)\n"
                    "4. *Transfer Certificate (TC)* and Conduct Certificate from the last attended institution\n"
                    "5. *Community Certificate* (BC / MBC / SC / ST candidates)\n"
                    "6. *Aadhaar Card* copy\n"
                    "7. *Passport Size Photos* (5 copies)\n"
                    "8. *Migration Certificate* (for other university/state students)\n"
                    "9. *TANCET Score Card* (for Government quota MCA admissions)"
                ),
                'documents required for admission, admission documents, certificates needed, tc, eligibility'
            ),
            (
                'ADMISSIONS',
                'MCA Admission Eligibility Criteria',
                (
                    "• *Eligibility*: Passed BCA / Bachelor Degree in Computer Science Engineering or equivalent degree OR Passed B.Sc. / B.Com / B.A. with Mathematics at 10+2 level or at Graduation level.\n"
                    "• *Minimum Marks*: At least 50% marks (45% in case of candidates belonging to reserved category) in the qualifying degree.\n"
                    "• *Admission Modes*: Merit Quota through TANCET counselling or Management Quota."
                ),
                'mca eligibility, admission criteria, mca qualification, tancet'
            ),
            # FEES
            (
                'FEES',
                'College & Examination Fee Structure',
                (
                    "• *MCA Tuition Fee*: ₹28,000 per semester\n"
                    "• *Semester Examination Fee*: *₹1,500* per semester (Theory: ₹150/paper, Practical: ₹250/paper, Marksheet: ₹150)\n"
                    "• *Admission / Registration Fee (One-time)*: ₹2,000\n"
                    "• *College Bus / Transport Fee*: ₹6,000 to ₹12,000 per year (depending on boarding route)\n"
                    "• *Hostel Fee*: ₹35,000 per semester (inclusive of boarding and south Indian mess meals)\n"
                    "• *Payment Methods*: Can be paid online via the College ERP student portal or at the Central Bank of India campus branch."
                ),
                'fee, fees, exam fee, examination fee, tuition fee, mca fee, bus fee, hostel fee, how much fee'
            ),
            # ACADEMIC CALENDAR
            (
                'CALENDAR',
                'Academic Calendar & Semester Dates (2026)',
                (
                    "• *Semester Commencement Date*: *July 15, 2026* for Odd Semester (and *December 10, 2026* for Even Semester)\n"
                    "• *First Internal Assessment (CIA-I)*: August 24 - 28, 2026\n"
                    "• *Second Internal Assessment (CIA-II)*: October 12 - 16, 2026\n"
                    "• *Model Practical Examinations*: October 26 - 30, 2026\n"
                    "• *End Semester Examinations (Theory)*: November 9 - 28, 2026\n"
                    "• *Winter Vacation*: December 1 - 9, 2026"
                ),
                'semester start, when does semester start, academic calendar, exam dates, internal exam, reopening'
            ),
            # RULES
            (
                'RULES',
                'College Rules, Attendance, and Code of Conduct',
                (
                    "• *Attendance*: Minimum *75% attendance* is strictly mandatory to appear for autonomous end semester examinations.\n"
                    "• *Dress Code*: Formal attire required. Laboratory coats mandatory during chemistry/physics labs. College ID card must be worn around the neck at all times inside campus.\n"
                    "• *Mobile Phones*: Mobile phone usage inside lecture classrooms and examination halls is strictly prohibited.\n"
                    "• *Ragging*: Anti-Ragging regulations are strictly enforced with zero tolerance."
                ),
                'attendance, rules, dress code, id card, mobile policy, regulations, 75%'
            ),
            # FACILITIES
            (
                'FACILITIES',
                'Campus Facilities & Infrastructure',
                (
                    "• *Computing Labs*: 6 high-tech air-conditioned computer labs equipped with over 450 modern desktop systems, high-speed 1 Gbps leased line internet, and GPU AI research servers.\n"
                    "• *Library*: Over 75,000 books, subscriptions to IEEE, ACM, Springer, DELNET digital libraries, and OPAC catalogue search.\n"
                    "• *Sports Complex*: Cricket ground, synthetic basketball court, volleyball, indoor badminton courts, and gym.\n"
                    "• *Canteen*: Hygienic cafeteria serving vegetarian and non-vegetarian south Indian food and snacks from 8:00 AM to 6:00 PM.\n"
                    "• *Hostel*: Separate on-campus hostels for boys and girls with 24/7 security, solar water heaters, and Wi-Fi."
                ),
                'facilities, campus, labs, computer lab, library, sports, canteen, gym, wifi'
            ),
            # PLACEMENTS
            (
                'PLACEMENTS',
                'Placements & Training Cell',
                (
                    "• *Placement Record*: Over 85% placement rate for MCA and Computer Science graduates.\n"
                    "• *Top Recruiters*: Tata Consultancy Services (TCS), Infosys, Wipro, Cognizant, Zoho, HCL Technologies, Hexaware, and Tech Mahindra.\n"
                    "• *Average Package*: ₹4.2 LPA (Highest package: ₹8.5 LPA).\n"
                    "• *Training*: Regular aptitude training, mock technical interviews, and soft skill workshops organized by the Training & Placement Cell."
                ),
                'placements, jobs, recruiters, zoho, tcs, salary, package, campus interview'
            ),
        ]

        for cat_code, title, content, tags in items_data:
            KnowledgeItem.objects.update_or_create(
                category=cat_objs[cat_code],
                title=title,
                defaults={
                    'content': content,
                    'tags': tags,
                    'is_active': True,
                    'priority': 10
                }
            )

        # 3. FAQs (covering all common student questions)
        faqs_data = [
            (
                'FACULTY',
                'Who is the HOD of MCA?',
                'The Head of the Department (HOD) of MCA is *Dr. M. Muralidharan, M.C.A., M.Phil., Ph.D.* His cabin is located on the First Floor of the PG Block (Room No. 204). You can reach him at hod.mca@nmc.ac.in.',
                'who is the hod of mca, mca hod, head of department mca, muralidharan'
            ),
            (
                'GENERAL',
                'What is the college address?',
                'The official address of NMC College is:\n*Nehru Memorial College (Autonomous)*\nPuthanampatti - 621 007, Musiri Taluk, Tiruchirappalli District, Tamil Nadu, India.\nContact Numbers: +91 4327 234227 / 234827.',
                'what is the college address, college location, address, where is the college'
            ),
            (
                'DEPARTMENTS',
                'What are the MCA subjects?',
                'The MCA program covers key subjects across 4 semesters including: *Advanced Data Structures & Algorithms*, *Object-Oriented Software Engineering with Java*, *RDBMS & SQL*, *Python & Data Analysis*, *Full Stack Web Development (React & Node.js)*, *Machine Learning*, *Cloud Computing*, *Artificial Intelligence*, and a final semester 6-month industry internship.',
                'what are the mca subjects, mca syllabus, mca courses, subjects in mca'
            ),
            (
                'CALENDAR',
                'When does the semester start?',
                'The Odd Semester commences on *July 15, 2026*. The Even Semester commences on *December 10, 2026*. Classes begin promptly at 9:30 AM.',
                'when does the semester start, semester reopening, college start date, semester dates'
            ),
            (
                'FEES',
                'What is the exam fee?',
                'The semester examination fee is *₹1,500* per semester. The fee breakdown is: Theory papers ₹150 each, Practical papers ₹250 each, and Marksheet fee ₹150. Exam fees must be paid through the student ERP portal.',
                'what is the exam fee, examination fee, exam fees, how much is exam fee'
            ),
            (
                'ADMISSIONS',
                'What documents are required for admission?',
                'The documents required for admission are:\n1. 10th (SSLC) Marksheet\n2. 12th (HSC) Marksheet\n3. UG Degree Marksheets & Provisional Certificate (for PG/MCA)\n4. Transfer Certificate (TC)\n5. Conduct Certificate\n6. Community Certificate\n7. Aadhaar Card copy\n8. 5 Passport size photographs\n9. Migration Certificate (if from outside Bharathidasan University).',
                'what documents are required for admission, admission documents, certificates needed for admission'
            ),
            (
                'DEPARTMENTS',
                'Tell me about the college departments.',
                'NMC College has several prominent departments offering UG, PG, and Ph.D. degrees:\n• *Computer Applications (MCA)*\n• *Computer Science & Data Science*\n• *Electronics & Communication*\n• *Commerce & Business Administration (B.Com, BBA)*\n• *Mathematics*\n• *Physics & Chemistry*\nAll departments feature dedicated labs, smart classrooms, and experienced doctorates.',
                'tell me about the college departments, college departments, departments list, what departments are there'
            ),
            (
                'TIMINGS',
                'What are the college timings?',
                'The regular college timings are *9:30 AM to 4:00 PM* from Monday to Friday. The administrative office operates from *9:00 AM to 5:00 PM*. The central library is open from *8:30 AM to 6:00 PM*.',
                'what are the college timings, college timing, office hours, timing, working hours'
            ),
            (
                'RULES',
                'What is the minimum attendance required for exams?',
                'A minimum of *75% attendance* is strictly required to be eligible for autonomous semester examinations. Students with attendance between 65% and 74% must apply for condonation with medical certificates.',
                'attendance percentage, minimum attendance, attendance for exams'
            ),
            (
                'HOSTEL',
                'What are the hostel details and fees?',
                'The college provides separate on-campus hostels for boys and girls. The hostel fee is *₹35,000 per semester* which includes accommodation and food. Facilities include 24/7 security, purified drinking water, Wi-Fi, and recreation rooms.',
                'hostel, hostel fees, hostel timings, accommodation, girls hostel, boys hostel'
            ),
        ]

        for cat_code, q, a, kw in faqs_data:
            FAQItem.objects.update_or_create(
                question=q,
                defaults={
                    'category': cat_objs[cat_code],
                    'answer': a,
                    'keywords': kw,
                    'is_active': True,
                    'priority': 10
                }
            )

        # 4. Sync files to OpenClaw workspace
        workspace_dir = settings.BASE_DIR / 'openclaw_college_agent'
        sync_knowledge_to_workspace(workspace_dir)

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded {KnowledgeCategory.objects.count()} categories, "
            f"{KnowledgeItem.objects.count()} knowledge items, and {FAQItem.objects.count()} FAQs!"
        ))
