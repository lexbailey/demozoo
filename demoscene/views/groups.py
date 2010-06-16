from demoscene.shortcuts import *
from demoscene.models import Releaser, Nick
from demoscene.forms import GroupForm, GroupAddMemberForm, NickForm, NickFormSet

from django.contrib import messages
from django.contrib.auth.decorators import login_required

def index(request):
	groups = Releaser.objects.filter(is_group = True).order_by('name')
	return render(request, 'groups/index.html', {
		'groups': groups,
	})

def show(request, group_id):
	group = get_object_or_404(Releaser, is_group = True, id = group_id)
	return render(request, 'groups/show.html', {
		'group': group,
	})

@login_required
def edit(request, group_id):
	group = get_object_or_404(Releaser, is_group = True, id = group_id)
	if request.method == 'POST':
		primary_nick = group.primary_nick
		primary_nick_form = NickForm(request.POST, prefix = 'primary_nick', instance = primary_nick)
		alternative_nicks_formset = NickFormSet(request.POST, prefix = 'alternative_nicks', queryset = group.alternative_nicks)
		if primary_nick_form.is_valid() and alternative_nicks_formset.is_valid():
			primary_nick_form.save() # may indirectly update name of Releaser and save it too
			alternative_nicks = alternative_nicks_formset.save(commit = False)
			for nick in alternative_nicks:
				nick.releaser = group
				nick.save()
			messages.success(request, 'Group updated')
			return redirect('group', args = [group.id])
	else:
		primary_nick_form = NickForm(prefix = 'primary_nick', instance = group.primary_nick)
		alternative_nicks_formset = NickFormSet(prefix = 'alternative_nicks', queryset = group.alternative_nicks)
	
	return render(request, 'groups/edit.html', {
		'group': group,
		'primary_nick_form': primary_nick_form,
		'alternative_nicks_formset': alternative_nicks_formset,
	})

@login_required
def create(request):
	if request.method == 'POST':
		group = Releaser(is_group = True)
		form = GroupForm(request.POST, instance = group)
		if form.is_valid():
			form.save()
			messages.success(request, 'Group added')
			return redirect('group', args = [group.id])
	else:
		form = GroupForm()
	return render(request, 'groups/create.html', {
		'form': form,
	})

@login_required
def add_member(request, group_id):
	group = get_object_or_404(Releaser, is_group = True, id = group_id)
	if request.method == 'POST':
		form = GroupAddMemberForm(request.POST)
		if form.is_valid():
			if form.cleaned_data['scener_id'] == 'new':
				scener = Releaser(name = form.cleaned_data['scener_name'], is_group = False)
				scener.save()
			else:
				# TODO: test for blank scener_id (as sent by non-JS)
				scener = Releaser.objects.get(id = form.cleaned_data['scener_id'], is_group = False)
			group.members.add(scener)
			return redirect('group', args = [group.id])
	else:
		form = GroupAddMemberForm()
	return render(request, 'groups/add_member.html', {
		'group': group,
		'form': form,
	})

@login_required
def remove_member(request, group_id, scener_id):
	group = get_object_or_404(Releaser, is_group = True, id = group_id)
	scener = get_object_or_404(Releaser, is_group = False, id = scener_id)
	if request.method == 'POST':
		if request.POST.get('yes'):
			group.members.remove(scener)
		return redirect('group', args = [group.id])
	else:
		return render(request, 'groups/remove_member.html', {
			'group': group,
			'scener': scener,
		})

def autocomplete(request):
	query = request.GET.get('q')
	limit = request.GET.get('limit', 10)
	new_option = request.GET.get('new_option', False)
	if query:
		# TODO: search on nick variants, not just group names
		groups = Releaser.objects.filter(
			is_group = True, name__istartswith = query)[:limit]
	else:
		groups = Releaser.objects.none()
	return render(request, 'groups/autocomplete.txt', {
		'query': query,
		'groups': groups,
		'new_option': new_option,
	}, mimetype = 'text/plain')
	