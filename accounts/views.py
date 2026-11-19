
from django.contrib import messages
from django.contrib.auth import views as auth_views, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect


class RoleLoginView(auth_views.LoginView):
    template_name = "base/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.role == "admin":
            return "/admin-portal/"
        return "/staff/"


@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password updated successfully.")
        return redirect("/")
    for f in form.fields.values():
        f.widget.attrs["class"] = "form-control"
    return render(request, "base/change_password.html", {"form": form})
