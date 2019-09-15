from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.test import TestCase

from demoscene.models import Membership, Nick, Releaser


class TestGroupsIndex(TestCase):
    fixtures = ['tests/gasman.json']

    def test_get(self):
        response = self.client.get('/groups/')
        self.assertEqual(response.status_code, 200)


class TestShowGroup(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.raww_arse = Releaser.objects.get(name='Raww Arse')
        self.gasman = Releaser.objects.get(name='Gasman')

    def test_get(self):
        response = self.client.get('/groups/%d/' % self.raww_arse.id)
        self.assertEqual(response.status_code, 200)

    def test_redirect_to_scener(self):
        response = self.client.get('/groups/%d/' % self.gasman.id)
        self.assertRedirects(response, '/sceners/%d/' % self.gasman.id)

    def test_get_history(self):
        response = self.client.get('/groups/%d/history/' % self.raww_arse.id)
        self.assertEqual(response.status_code, 200)


class TestCreateGroup(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_get(self):
        response = self.client.get('/groups/new/')
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/groups/new/', {
            'name': 'Limp Ninja',
            'abbreviation': '',
            'nick_variant_list': '',
        })
        limp_ninja = Releaser.objects.get(name='Limp Ninja')
        self.assertRedirects(response, '/groups/%d/' % limp_ninja.id)


class TestAddMember(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.papaya_dezign = Releaser.objects.get(name='Papaya Dezign')
        self.laesq = Releaser.objects.get(name='LaesQ')

    def test_locked(self):
        response = self.client.get('/groups/%d/add_member/' % self.papaya_dezign.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/groups/%d/add_member/' % self.hooy_program.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/groups/%d/add_member/' % self.hooy_program.id, {
            'scener_nick_search': 'laesq',
            'scener_nick_match_id': self.laesq.primary_nick.id,
            'scener_nick_match_name': 'laesq',
            'is_current': 'on'
        })
        self.assertRedirects(response, '/groups/%d/?editing=members' % self.hooy_program.id)
        self.assertEqual(1, Membership.objects.filter(member=self.laesq, group=self.hooy_program).count())


class TestRemoveMember(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.gasman = Releaser.objects.get(name='Gasman')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.papaya_dezign = Releaser.objects.get(name='Papaya Dezign')
        self.laesq = Releaser.objects.get(name='LaesQ')

    def test_locked(self):
        response = self.client.get('/groups/%d/remove_member/%d/' % (self.papaya_dezign.id, self.laesq.id))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/groups/%d/remove_member/%d/' % (self.hooy_program.id, self.gasman.id))
        self.assertEqual(response.status_code, 200)

    def test_ex_member(self):
        response = self.client.post('/groups/%d/remove_member/%d/' % (self.hooy_program.id, self.gasman.id), {
            'deletion_type': 'ex_member',
        })
        self.assertRedirects(response, '/groups/%d/?editing=members' % self.hooy_program.id)
        self.assertFalse(Membership.objects.get(member=self.gasman, group=self.hooy_program).is_current)

    def test_remove(self):
        response = self.client.post('/groups/%d/remove_member/%d/' % (self.hooy_program.id, self.gasman.id), {
            'deletion_type': 'full',
        })
        self.assertRedirects(response, '/groups/%d/?editing=members' % self.hooy_program.id)
        self.assertEqual(Membership.objects.filter(member=self.gasman, group=self.hooy_program).count(), 0)

    def test_post_invalid(self):
        response = self.client.post('/groups/%d/remove_member/%d/' % (self.hooy_program.id, self.gasman.id), {
            'deletion_type': 'blah',
        })
        self.assertEqual(response.status_code, 200)


class TestEditMembership(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.gasman = Releaser.objects.get(name='Gasman')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.papaya_dezign = Releaser.objects.get(name='Papaya Dezign')
        self.laesq = Releaser.objects.get(name='LaesQ')

    def test_locked(self):
        membership = Membership.objects.get(member=self.laesq, group=self.papaya_dezign)
        response = self.client.get('/groups/%d/edit_membership/%d/' % (self.papaya_dezign.id, membership.id))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        membership = Membership.objects.get(member=self.gasman, group=self.hooy_program)
        response = self.client.get('/groups/%d/edit_membership/%d/' % (self.hooy_program.id, membership.id))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        membership = Membership.objects.get(member=self.gasman, group=self.hooy_program)
        response = self.client.post('/groups/%d/edit_membership/%d/' % (self.hooy_program.id, membership.id), {
            'scener_nick_search': 'gasman',
            'scener_nick_match_id': self.gasman.primary_nick.id,
            'scener_nick_match_name': 'gasman',
        })
        self.assertRedirects(response, '/groups/%d/?editing=members' % self.hooy_program.id)
        self.assertFalse(Membership.objects.get(member=self.gasman, group=self.hooy_program).is_current)


class TestAddSubgroup(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.papaya_dezign = Releaser.objects.get(name='Papaya Dezign')

    def test_locked(self):
        response = self.client.get('/groups/%d/add_subgroup/' % self.papaya_dezign.id)
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/groups/%d/add_subgroup/' % self.hooy_program.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/groups/%d/add_subgroup/' % self.hooy_program.id, {
            'subgroup_nick_search': 'papaya dezign',
            'subgroup_nick_match_id': self.papaya_dezign.primary_nick.id,
            'subgroup_nick_match_name': 'papaya dezign',
            'is_current': 'on'
        })
        self.assertRedirects(response, '/groups/%d/?editing=subgroups' % self.hooy_program.id)
        self.assertEqual(1, Membership.objects.filter(member=self.papaya_dezign, group=self.hooy_program).count())


class TestRemoveSubgroup(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.papaya_dezign = Releaser.objects.get(name='Papaya Dezign')
        self.raww_arse = Releaser.objects.get(name='Raww Arse')

    def test_locked(self):
        Membership.objects.create(member=self.hooy_program, group=self.papaya_dezign)
        response = self.client.get('/groups/%d/remove_subgroup/%d/' % (self.papaya_dezign.id, self.hooy_program.id))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        response = self.client.get('/groups/%d/remove_subgroup/%d/' % (self.raww_arse.id, self.papaya_dezign.id))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/groups/%d/remove_subgroup/%d/' % (self.raww_arse.id, self.papaya_dezign.id), {
            'yes': 'yes',
        })
        self.assertRedirects(response, '/groups/%d/?editing=subgroups' % self.raww_arse.id)
        self.assertEqual(Membership.objects.filter(member=self.papaya_dezign, group=self.raww_arse).count(), 0)


class TestEditSubgroup(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.papaya_dezign = Releaser.objects.get(name='Papaya Dezign')
        self.raww_arse = Releaser.objects.get(name='Raww Arse')

    def test_locked(self):
        membership = Membership.objects.create(member=self.hooy_program, group=self.papaya_dezign)
        response = self.client.get('/groups/%d/edit_subgroup/%d/' % (self.papaya_dezign.id, membership.id))
        self.assertEqual(response.status_code, 403)

    def test_get(self):
        membership = Membership.objects.get(member=self.papaya_dezign, group=self.raww_arse)
        response = self.client.get('/groups/%d/edit_subgroup/%d/' % (self.raww_arse.id, membership.id))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        membership = Membership.objects.get(member=self.papaya_dezign, group=self.raww_arse)
        response = self.client.post('/groups/%d/edit_subgroup/%d/' % (self.raww_arse.id, membership.id), {
            'subgroup_nick_search': 'papaya dezign',
            'subgroup_nick_match_id': self.papaya_dezign.primary_nick.id,
            'subgroup_nick_match_name': 'papaya dezign',
        })
        self.assertRedirects(response, '/groups/%d/?editing=subgroups' % self.raww_arse.id)
        self.assertFalse(Membership.objects.get(member=self.papaya_dezign, group=self.raww_arse).is_current)


class TestConvertToScener(TestCase):
    fixtures = ['tests/gasman.json']

    def setUp(self):
        self.user = User.objects.create_superuser(username='testuser', email='testuser@example.com', password='12345')
        self.client.login(username='testuser', password='12345')
        self.hooy_program = Releaser.objects.get(name='Hooy-Program')
        self.fairlight = Releaser.objects.create(name='Fairlight', is_group=True)
        fairlight_nick = Nick.objects.get(name='Fairlight')
        fairlight_nick.abbreviation = 'FLT'
        fairlight_nick.save()

    def test_unconvertable(self):
        response = self.client.get('/groups/%d/convert_to_scener/' % self.hooy_program.id)
        self.assertRedirects(response, '/groups/%d/' % self.hooy_program.id)

    def test_get(self):
        response = self.client.get('/groups/%d/convert_to_scener/' % self.fairlight.id)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        response = self.client.post('/groups/%d/convert_to_scener/' % self.fairlight.id, {
            'yes': 'yes',
        })
        self.assertRedirects(response, '/sceners/%d/' % self.fairlight.id)
        self.assertFalse(Releaser.objects.get(name='Fairlight').is_group)
