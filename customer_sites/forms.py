from django import forms
from .models import Site


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = [
            'name',
            'domain',
            'ip',
            'port',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white',
                'placeholder': 'My Website',
            }),
            'domain': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white',
                'placeholder': 'example.com',
                'spellcheck': 'false',
            }),
            'ip': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white font-mono',
                'placeholder': '203.0.113.10',
                'inputmode': 'numeric',
            }),
            'port': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 '
                         'shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 '
                         'dark:text-white',
                'min': 1,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded '
                         'focus:ring-blue-500',
            }),
        }


