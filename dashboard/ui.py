"""Shared UI helpers: list pages, form pages and a generic admin CRUD factory."""
from django import forms
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from accounts.models import User
from accounts.permissions import admin_required

def nsof(request):
    rm = request.resolver_match
    return "mobile:" if rm and rm.namespace == "mobile" else ""

def staff_choices():
    return [(u.pk, str(u)) for u in User.objects.filter(role="staff")]

def style(form):
    for f in form.fields.values():
        if isinstance(f, forms.DateTimeField):
            f.widget = forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M")
            f.input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"]
        elif isinstance(f, forms.DateField):
            f.widget = forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")
        n = type(f.widget).__name__
        f.widget.attrs["class"] = "form-select" if "Select" in n else "form-check-input" if n == "CheckboxInput" else "form-control"
    return form

def back(request, default):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, {request.get_host()}):
        return redirect(nxt)
    return redirect(default)

def val(o, a):
    *chain, last = a.split(".")
    for p in chain:
        o = getattr(o, p, None)
        if o is None:
            return "—"
    d = getattr(o, f"get_{last}_display", None)
    v = d() if d else getattr(o, last, None)
    if callable(v):
        v = v()
    if v is None or v == "":
        return "—"
    return ("Yes" if v else "No") if isinstance(v, bool) else v

def list_page(request, title, qs, cols, row, search=(), filters=(), add=None, extra=(), keep=()):
    q = request.GET.get("q", "").strip()
    if q and search:
        cond = Q()
        for f in search:
            cond |= Q(**{f + "__icontains": q})
        qs = qs.filter(cond)
    fl = []
    for p, label, choices in filters:
        v = request.GET.get(p, "")
        if v:
            qs = qs.filter(**{p: v})
        fl.append({"name": p, "label": label, "cur": v, "choices": list(choices() if callable(choices) else choices)})
    if not qs.ordered:
        qs = qs.order_by("-pk")
    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    rows = []
    for o in page:
        r = row(o)
        r["cells"] = [(c, "status" in h.lower()) for c, h in zip(r["cells"], cols)]
        rows.append(r)
    qd = request.GET.copy(); qd.pop("page", None)
    return render(request, "base/crud_list.html", dict(
        title=title, cols=cols, rows=rows, q=q, filters=fl, page=page, add=add, extra=extra,
        qs=qd.urlencode(), keep=[(k, request.GET.get(k)) for k in keep if request.GET.get(k)]))

def form_page(request, title, form, back_url, info=""):
    return render(request, "base/crud_form.html", dict(title=title, form=style(form), back=back_url, info=info))

def crud(slug, model, *, extra=None, cols, fields=None, form_class=None, search=(), filters=(), qs=None, add=True,
         readonly=False, detail=None, soft_delete=None, on_save=None, title=None):
    title = title or model._meta.verbose_name_plural.title()
    base = qs or (lambda: model.objects.all())
    Form = form_class or (modelform_factory(model, fields=fields) if fields else None)

    @admin_required
    def lst(request):
        ns = nsof(request)
        def row(o):
            r = {"cells": [val(o, a) for _, a in cols]}
            if detail:
                r["view"] = reverse(ns + detail, args=[o.pk])
            if not readonly:
                r["edit"] = reverse(ns + f"{slug}_edit", args=[o.pk])
                r["delete"] = reverse(ns + f"{slug}_delete", args=[o.pk])
            return r
        return list_page(request, title, base(), [h for h, _ in cols], row, search, filters,
                         add=reverse(ns + f"{slug}_new") if add and not readonly else None,
                         extra=[(l, reverse(ns + n)) for l, n in (extra or [])])

    @admin_required
    def edit(request, pk=None):
        ns = nsof(request)
        obj = get_object_or_404(base(), pk=pk) if pk else None
        form = Form(request.POST or None, request.FILES or None, instance=obj)
        if request.method == "POST" and form.is_valid():
            o = form.save(commit=False)
            if on_save:
                on_save(o, request, obj is None)
            o.save(); form.save_m2m()
            messages.success(request, f"{model._meta.verbose_name.title()} saved.")
            return redirect(ns + f"{slug}_list")
        return form_page(request, ("Edit " if pk else "Add ") + model._meta.verbose_name.title(), form, reverse(ns + f"{slug}_list"))

    @admin_required
    def delete(request, pk):
        ns = nsof(request)
        if request.method == "POST":
            obj = get_object_or_404(base(), pk=pk)
            try:
                if soft_delete:
                    soft_delete(obj); messages.success(request, "Record deactivated.")
                else:
                    obj.delete(); messages.success(request, "Record deleted.")
            except ProtectedError:
                messages.error(request, "Cannot delete: this record is referenced by other data.")
        return redirect(ns + f"{slug}_list")

    out = [path(f"{slug}/", lst, name=f"{slug}_list")]
    if not readonly:
        if add:
            out.append(path(f"{slug}/new/", edit, name=f"{slug}_new"))
        out += [path(f"{slug}/<int:pk>/edit/", edit, name=f"{slug}_edit"),
                path(f"{slug}/<int:pk>/delete/", delete, name=f"{slug}_delete")]
    return out
