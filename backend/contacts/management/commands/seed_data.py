from django.core.management.base import BaseCommand
from contacts.models import Contact, ContactGroup
from wa_templates.models import MessageTemplate

class Command(BaseCommand):
    help = 'Seed initial data for development'

    def handle(self, *args, **kwargs):
        # Create groups
        groups_data = [
            {'name': 'All Students', 'group_type': 'ROLE', 'description': 'All active students'},
            {'name': 'All Staff', 'group_type': 'ROLE', 'description': 'All teaching & non-teaching staff'},
            {'name': 'All HODs', 'group_type': 'ROLE', 'description': 'All Heads of Department'},
            {'name': 'All Parents', 'group_type': 'ROLE', 'description': 'All registered parents'},
            {'name': 'CS Department', 'group_type': 'DEPARTMENT', 'description': 'Computer Science'},
            {'name': 'EC Department', 'group_type': 'DEPARTMENT', 'description': 'Electronics & Communication'},
            {'name': 'ME Department', 'group_type': 'DEPARTMENT', 'description': 'Mechanical Engineering'},
            {'name': '1st Year', 'group_type': 'CUSTOM', 'description': 'First year students'},
            {'name': '2nd Year', 'group_type': 'CUSTOM', 'description': 'Second year students'},
        ]
        for g in groups_data:
            ContactGroup.objects.get_or_create(name=g['name'], defaults=g)
        self.stdout.write(self.style.SUCCESS(f'Created {len(groups_data)} groups'))

        # Create sample contacts
        contacts_data = [
            {'name': 'Ravi Kumar', 'phone_number': '919876543210', 'role': 'STUDENT', 'department': 'CS', 'year_or_section': '2nd Year', 'enrollment_no': 'CS2024001'},
            {'name': 'Priya Sharma', 'phone_number': '919876543211', 'role': 'STUDENT', 'department': 'CS', 'year_or_section': '2nd Year', 'enrollment_no': 'CS2024002'},
            {'name': 'Amit Singh', 'phone_number': '919876543212', 'role': 'STUDENT', 'department': 'EC', 'year_or_section': '1st Year', 'enrollment_no': 'EC2025001'},
            {'name': 'Dr. Rajesh Verma', 'phone_number': '919876543220', 'role': 'HOD', 'department': 'CS'},
            {'name': 'Prof. Meena Devi', 'phone_number': '919876543221', 'role': 'STAFF', 'department': 'CS'},
            {'name': 'Prof. Suresh Nair', 'phone_number': '919876543222', 'role': 'STAFF', 'department': 'EC'},
            {'name': 'Mr. Kumar (Parent)', 'phone_number': '919876543230', 'role': 'PARENT', 'department': 'CS'},
        ]
        for c in contacts_data:
            contact, created = Contact.objects.get_or_create(
                phone_number=c['phone_number'], defaults=c
            )
            # Auto-add to role groups
            role_group_map = {
                'STUDENT': 'All Students',
                'STAFF': 'All Staff',
                'HOD': 'All HODs',
                'PARENT': 'All Parents',
            }
            role_group_name = role_group_map.get(c['role'])
            if role_group_name:
                group = ContactGroup.objects.get(name=role_group_name)
                group.members.add(contact)
            # Add to department group
            dept_map = {'CS': 'CS Department', 'EC': 'EC Department', 'ME': 'ME Department'}
            dept_group_name = dept_map.get(c.get('department', ''))
            if dept_group_name:
                try:
                    dept_group = ContactGroup.objects.get(name=dept_group_name)
                    dept_group.members.add(contact)
                except ContactGroup.DoesNotExist:
                    pass

        self.stdout.write(self.style.SUCCESS(f'Created {len(contacts_data)} contacts'))

        # Create sample templates
        templates_data = [
            {
                'name': 'Exam Schedule',
                'meta_template_name': 'exam_schedule',
                'category': 'UTILITY',
                'body_text': 'Dear Student, your {{1}} exams are scheduled starting from {{2}}. Please check your student portal for the detailed timetable. - NMC College',
                'param_count': 2,
                'sample_params': ['Mid-Semester', 'October 15, 2026'],
                'status': 'APPROVED',
            },
            {
                'name': 'Fee Reminder',
                'meta_template_name': 'fee_reminder',
                'category': 'UTILITY',
                'body_text': 'Dear {{1}}, this is a reminder that your {{2}} fee of Rs.{{3}} is due on {{4}}. Please pay through the college portal.',
                'param_count': 4,
                'sample_params': ['Student', 'Tuition', '50000', 'October 30, 2026'],
                'status': 'APPROVED',
            },
            {
                'name': 'General Announcement',
                'meta_template_name': 'general_announcement',
                'category': 'UTILITY',
                'header_text': 'NMC College Announcement',
                'body_text': '{{1}}',
                'param_count': 1,
                'sample_params': ['College will remain closed tomorrow due to heavy rain.'],
                'status': 'APPROVED',
            },
            {
                'name': 'Attendance Alert',
                'meta_template_name': 'attendance_alert',
                'category': 'UTILITY',
                'body_text': 'Dear {{1}}, your attendance in {{2}} is currently {{3}}%, which is below the required 75%. Please attend classes regularly.',
                'param_count': 3,
                'sample_params': ['Ravi Kumar', 'Data Structures', '65'],
                'status': 'APPROVED',
            },
            {
                'name': 'Holiday Notice',
                'meta_template_name': 'holiday_notice',
                'category': 'UTILITY',
                'body_text': 'Dear {{1}}, the college will remain closed on {{2}} due to {{3}}. Classes resume on {{4}}. Stay safe!',
                'param_count': 4,
                'sample_params': ['All', 'October 2', 'Gandhi Jayanti', 'October 3'],
                'status': 'APPROVED',
            },
        ]
        for t in templates_data:
            MessageTemplate.objects.get_or_create(
                meta_template_name=t['meta_template_name'], defaults=t
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(templates_data)} templates'))
        self.stdout.write(self.style.SUCCESS('Seed data complete!'))
