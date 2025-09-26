from django import forms
from .models import Job
from user_profiles.models import Skill

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'job_type', 'experience_level', 
                 'work_location', 'salary_min', 'salary_max', 'visa_sponsorship', 
                 'skills_required', 'description', 'requirements']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job location'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'work_location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary (optional)',
                'step': '0.01'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary (optional)',
                'step': '0.01'
            }),
            'visa_sponsorship': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'skills_required': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job description',
                'rows': 6
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job requirements',
                'rows': 4
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make salary fields optional
        self.fields['salary_min'].required = False
        self.fields['salary_max'].required = False
        # Make skills_required optional
        self.fields['skills_required'].required = False
        self.fields['skills_required'].queryset = Skill.objects.all().order_by('name')


class JobSearchForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Job title keywords'
        })
    )
    
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'City, State, or Remote'
        })
    )
    
    job_type = forms.ChoiceField(
        choices=[('', 'Any Type')] + Job.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    experience_level = forms.ChoiceField(
        choices=[('', 'Any Level')] + Job.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    work_location = forms.ChoiceField(
        choices=[('', 'Any Location')] + Job.WORK_LOCATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    salary_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum salary',
            'step': '0.01'
        })
    )
    
    salary_max = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum salary',
            'step': '0.01'
        })
    )
    
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].queryset = Skill.objects.all().order_by('name')
