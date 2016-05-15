from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from lana_dashboard.lana_data.models import Institution
from lana_dashboard.usermanagement.forms import ContactInformationForm


def login(request):
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			auth_login(request, form.get_user())
			return HttpResponseRedirect(reverse('main-index'))
	else:
		form = AuthenticationForm(request)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-md-2 offset-md-3'
	form.helper.field_class = 'col-md-4'
	form.helper.html5_required = True
	form.helper.add_input(Submit("submit", "Login"))

	return render(request, 'login.html', {
		'form': form,
	})


def logout(request):
	auth_logout(request)
	return HttpResponseRedirect(reverse('main-index'))


@login_required
def show_user_profile(request, username):
	user = get_object_or_404(get_user_model(), username=username)
	institutions = Institution.objects.all().filter(owners__username=username).order_by('code')
	return render(request, 'user_profile.html', {
		'profile': user,
		'info': user.contact_information if hasattr(user, 'contact_information') else None,
		'institutions': institutions,
	})


@login_required
def edit_user_profile(request, username):
	user = get_object_or_404(get_user_model(), username=username)
	if user.username != request.user.username:
		raise PermissionDenied

	instance = user.contact_information if hasattr(user, 'contact_information') else None

	if request.method == "POST":
		form = ContactInformationForm(instance=instance, data=request.POST)
		if form.is_valid():
			info = form.save(commit=False)
			info.user = user
			info.save()
			if not instance:
				user.contact_information = info
				user.save()
			return HttpResponseRedirect(reverse('usermanagement:profile', kwargs={'username': user.username}))
	else:
		form = ContactInformationForm(instance=instance)

	form.helper = FormHelper()
	form.helper.form_class = 'form-horizontal'
	form.helper.label_class = 'col-xs-4 col-md-3 col-lg-2'
	form.helper.field_class = 'col-xs-8 col-lg-7 col-xl-6'
	form.helper.html5_required = True
	form.helper.add_input(Submit("submit", "Save"))

	return render(request, 'user_profile_edit.html', {
		'profile': user,
		'form': form,
	})
