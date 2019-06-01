import csv

from django.core.management.base import BaseCommand

from demoscene.models import Releaser, ReleaserExternalLink, Membership as DZMembership
from demoscene.utils.text import generate_search_title
from janeway.models import Author, Name


class Command(BaseCommand):
	"""Find cross-links between Janeway and Demozoo data"""
	def handle(self, *args, **kwargs):
		creation_count = 0

		dupes_file = open('janeway_dupes.csv', mode='w')
		dupes_csv = csv.writer(dupes_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		dupes_csv.writerow(['Scener', 'Janeway URL', 'Demozoo URLs'])

		for (index, author) in enumerate(Author.objects.all()):
			if (index % 100 == 0):
				print("processed %d authors" % index)

			# find releasers in the Demozoo data that match any of this author's names (excluding abbreviations)
			# and are of the right type (scener vs group)
			candidate_releaser_ids = list(Releaser.objects.filter(
				is_group=author.is_group,
				nicks__variants__search_title__in=[generate_search_title(name.name) for name in author.names.all()]
			).distinct().values_list('id', flat=True))
			# print("-> %d name matches found: %r" % (len(candidate_releaser_ids), candidate_releaser_ids))

			if not candidate_releaser_ids:
				continue

			if author.is_group:
				# get this group's member memberships
				member_ids = Author.objects.filter(group_memberships__group=author).values_list('janeway_id', flat=True)
				member_names = [
					generate_search_title(name.name)
					for name in Name.objects.filter(author__group_memberships__group=author)
				]

				member_demozoo_ids = list(ReleaserExternalLink.objects.filter(
					link_class='KestraBitworldAuthor', parameter__in=[str(id) for id in member_ids]
				).values_list('releaser_id', flat=True))
				# see if any candidate releasers have one or more matching members by ID
				matching_releaser_ids = set(DZMembership.objects.filter(
					group_id__in=candidate_releaser_ids,
					member_id__in=member_demozoo_ids
				).distinct().values_list('group_id', flat=True))

				# see if any candidate releasers have TWO or more matching members by name
				# (>=2 avoids false positives such as JP/Mayhem:
				#   http://janeway.exotica.org.uk/author.php?id=29340
				#   https://demozoo.org/sceners/40395/ )
				for candidate_releaser_id in candidate_releaser_ids:
					if candidate_releaser_id in matching_releaser_ids:
						# ignore ones which are already matched by member ID
						continue

					name_match_count = DZMembership.objects.filter(
						group_id=candidate_releaser_id,
						member__nicks__variants__search_title__in=member_names
					).distinct().values_list('member_id', flat=True).count()
					if name_match_count >= 2:
						print("group match: %s (%d) matches %d on %d member names" % (author.name, author.janeway_id, candidate_releaser_id, name_match_count))
						matching_releaser_ids.add(candidate_releaser_id)

			else:
				# get this author's group memberships
				group_ids = Author.objects.filter(
					is_group=True, member_memberships__member=author
				).values_list('janeway_id', flat=True)
				group_names = [
					generate_search_title(name.name)
					for name in Name.objects.filter(author__is_group=True, author__member_memberships__member=author)
				]

				group_demozoo_ids = list(ReleaserExternalLink.objects.filter(
					link_class='KestraBitworldAuthor', parameter__in=[str(id) for id in group_ids]
				).values_list('releaser_id', flat=True))
				# see if any candidate releasers have one or more matching groups by ID
				matching_releaser_ids = set(DZMembership.objects.filter(
					member_id__in=candidate_releaser_ids,
					group_id__in=group_demozoo_ids
				).distinct().values_list('member_id', flat=True))

				# see if any candidate releasers have TWO or more matching groups by name
				# (>=2 avoids false positives such as JP/Mayhem:
				#   http://janeway.exotica.org.uk/author.php?id=29340
				#   https://demozoo.org/sceners/40395/ )
				for candidate_releaser_id in candidate_releaser_ids:
					if candidate_releaser_id in matching_releaser_ids:
						# ignore ones which are already matched by member ID
						continue

					name_match_count = DZMembership.objects.filter(
						member_id=candidate_releaser_id,
						group__nicks__variants__search_title__in=group_names
					).distinct().values_list('group_id', flat=True).count()
					if name_match_count >= 2:
						print("scener match: %s (%d) matches %d on %d group names" % (author.name, author.janeway_id, candidate_releaser_id, name_match_count))
						matching_releaser_ids.add(candidate_releaser_id)

			if len(matching_releaser_ids) > 1:
				dupes_csv.writerow(
					[author.name.encode('utf-8'), 'http://janeway.exotica.org.uk/author.php?id=%d' % author.janeway_id]
					+ [
						'https://demozoo.org/%s/%d/' % ('groups' if author.is_group else 'sceners', id) for id in list(matching_releaser_ids)
					]
				)

			already_linked_releasers = list(ReleaserExternalLink.objects.filter(
				link_class='KestraBitworldAuthor', parameter=author.janeway_id
			).values_list('releaser_id', flat=True))

			for releaser_id in matching_releaser_ids:
				if releaser_id not in already_linked_releasers:
					ReleaserExternalLink.objects.create(
						releaser_id=releaser_id,
						link_class='KestraBitworldAuthor',
						parameter=author.janeway_id,
						source='janeway-automatch',
					)
					creation_count += 1

		dupes_file.close()

		print("%d cross-links created" % creation_count)
