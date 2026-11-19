import os
from django import forms
from .models import Document
MAGIC = (b"%PDF", b"\x89PNG", b"\xff\xd8")

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["doc_type", "file"]
    def clean_file(self):
        f = self.cleaned_data["file"]
        if os.path.splitext(f.name)[1].lower() not in {".pdf", ".jpg", ".jpeg", ".png"}:
            raise forms.ValidationError("Only PDF, JPG or PNG files are allowed.")
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError("File must be 5 MB or smaller.")
        head = f.read(4); f.seek(0)
        if not head.startswith(MAGIC):
            raise forms.ValidationError("File content does not match a PDF/JPG/PNG.")
        return f
