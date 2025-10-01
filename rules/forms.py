from django import forms
from .models import Rule, SiteRule
from customer_sites.models import Site


class SiteRuleForm(forms.ModelForm):
    """Form for managing site-specific rule configurations"""
    
    class Meta:
        model = SiteRule
        fields = ['rule', 'enabled', 'priority', 'custom_pattern']
        widgets = {
            'rule': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white'
            }),
            'enabled': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'priority': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white',
                'min': '1',
                'max': '1000'
            }),
            'custom_pattern': forms.Textarea(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white font-mono',
                'rows': 3,
                'placeholder': 'Enter custom regex pattern (optional)'
            })
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        if tenant:
            # Filter rules to only show available ones for this tenant
            self.fields['rule'].queryset = Rule.objects.filter(is_global=True)
            
            # Add help text
            self.fields['priority'].help_text = 'Lower numbers = higher priority (1-1000)'
            self.fields['custom_pattern'].help_text = 'Override the default pattern for this site (optional)'


class BulkRuleAssignmentForm(forms.Form):
    """Form for bulk assigning rules to multiple sites"""
    
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
        })
    )
    
    rules = forms.ModelMultipleChoiceField(
        queryset=Rule.objects.filter(is_global=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
        })
    )
    
    enabled = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
        })
    )
    
    priority = forms.IntegerField(
        initial=100,
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        })
    )

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        
        if tenant:
            self.fields['sites'].queryset = Site.objects.filter(tenant=tenant, is_active=True)


class RuleSearchForm(forms.Form):
    """Form for searching and filtering rules"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500',
            'placeholder': 'Search rules...'
        })
    )
    
    category = forms.ChoiceField(
        choices=[
            ('', 'All Categories'),
            ('injection', 'Injection Attacks'),
            ('xss', 'Cross-Site Scripting'),
            ('traversal', 'Path Traversal'),
            ('injection', 'Command Injection'),
            ('rate_limit', 'Rate Limiting'),
            ('other', 'Other'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        })
    )
    
    severity = forms.ChoiceField(
        choices=[
            ('', 'All Severities'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500'
        })
    )
