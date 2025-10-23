from django import forms
from .models import JobSeekerProfile, WorkExperience, Education, Skill, Link

class HeadlineForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = ['headline']
        widgets = {
            'headline': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['title', 'company', 'location', 'start_date', 'end_date', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['school', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'school': forms.TextInput(attrs={'class': 'form-control'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }
        
class SkillsForm(forms.Form):
    skills = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Enter your skills separated by commas (e.g., Python, Django, SQL)',
        required=False
    )

class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['name', 'url']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'class': 'form-control'}),
        }

class ProfilePrivacyForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        fields = [
            'is_headline_public', 
            'is_experience_public', 
            'is_education_public', 
            'is_skills_public', 
            'is_links_public'
        ]
        widgets = {
            'is_headline_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_experience_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_education_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_skills_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_links_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
